const { test, after, before } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const { mkdtempSync, writeFileSync } = require('node:fs');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { spawn } = require('node:child_process');
const { RequestGuard } = require('./request-guard.cjs');

const directory = mkdtempSync(path.join(__dirname, '../runtime/guard-tests-'));
const credential = 'Bearer synthetic-account-a';
const hits = [];
const server = http.createServer(async (request, response) => {
  let body = '';
  for await (const chunk of request) body += chunk;
  const parsed = JSON.parse(body);
  hits.push({ route: request.url, model: parsed.model, tools: parsed.tools ?? [] });
  if (request.url === '/disconnect') return request.socket.destroy();
  if (request.url === '/redirect') {
    response.writeHead(307, { location: 'http://127.0.0.1:17442/forbidden' });
    return response.end();
  }
  if (request.url.startsWith('/status/')) {
    response.writeHead(Number(request.url.split('/').pop()));
    return response.end('{}');
  }
  if (request.url === '/slow') await new Promise(resolve => setTimeout(resolve, 250));
  response.setHeader('content-type', 'application/json');
  response.end(JSON.stringify({ model: parsed.model,
    ...(request.url === '/missing-usage' ? {} : { usage: { input_tokens: 4, output_tokens: 2 } }),
    ...(request.url === '/unexpected-tool' ? { tools_used: ['search'] } : {}), output: 'synthetic' }));
});
before(() => new Promise(resolve => server.listen(17441, '127.0.0.1', resolve)));
after(async () => {
  writeFileSync(path.join(directory, 'server-hits.json'), JSON.stringify(hits, null, 2));
  server.closeAllConnections();
  await new Promise(resolve => server.close(resolve));
  console.log(JSON.stringify({ fixture_directory: directory, local_http_hits: hits.length, real_model_calls: 0 }));
});
let sequence = 0;
function fixture(changes = {}) {
  const filename = path.join(directory, `${++sequence}.sqlite`);
  const gate = new RequestGuard(filename);
  const approval = { id: 'fixture', provider: 'local-fixture', workspace: 'synthetic-workspace', quota_scope: 'FIXTURE_EXCLUSIVE', mode: 'MOCK_FIXTURE', approved: true,
    approved_by: 'LOCAL_TEST_FIXTURE', cash_charge_usd: 0, paid_fallback_disabled: true,
    endpoint: 'http://127.0.0.1:17441/ok', region: 'local-mock', model: 'fixture-v1',
    roles: ['sample', 'judge', 'research', 'format-retry'], credential_ref: 'account-a',
    credential_sha256: createHash('sha256').update(credential).digest('hex'),
    expires_at: Date.now() + 60000, quota_expires_at: Date.now() + 60000,
    quota_evidence_ref: 'synthetic-quota', hard_stop_evidence_ref: 'synthetic-hard-stop',
    max_requests: 1, max_input_tokens: 512, max_output_tokens: 32, max_total_tokens: 1000,
    allowed_tools: [], ...changes };
  const request = { approval_id: approval.id, provider: approval.provider, workspace: approval.workspace, role: 'sample',
    endpoint: approval.endpoint, region: approval.region, model: approval.model,
    credential_ref: approval.credential_ref, headers: { authorization: credential },
    body: { model: approval.model, input: 'synthetic', max_output_tokens: 16 } };
  return { gate, filename, approval, request };
}
async function rejectedBeforeSend(changes, requestChanges, expected) {
  const f = fixture(changes);
  f.gate.registerMockApproval(f.approval);
  const before = hits.length;
  await assert.rejects(f.gate.request({ ...f.request, ...requestChanges }), expected);
  assert.equal(hits.length, before);
  assert.equal(f.gate.snapshot().attempts.length, 0);
  f.gate.close();
}

test('COST-01 missing approval and live endpoint fail before HTTP', async () => {
  const f = fixture();
  await assert.rejects(f.gate.request(f.request), /APPROVAL_MISSING/);
  assert.throws(() => f.gate.registerMockApproval({ ...f.approval, endpoint: 'https://api.invalid/v1' }), /LIVE_ENDPOINT_DISABLED/);
  f.gate.close();
});
test('COST-02 missing evidence, shared quota, expiry and quota expiry fail closed', async () => {
  for (const key of ['quota_evidence_ref', 'hard_stop_evidence_ref', 'credential_sha256']) {
    const f = fixture({ [key]: undefined });
    assert.throws(() => f.gate.registerMockApproval(f.approval), /INVALID_APPROVAL/);
    f.gate.close();
  }
  await rejectedBeforeSend({ expires_at: 1 }, {}, /APPROVAL_EXPIRED/);
  await rejectedBeforeSend({ quota_expires_at: 1 }, {}, /QUOTA_EXPIRED/);
  const f = fixture();
  f.gate.registerMockApproval(f.approval);
  assert.throws(() => f.gate.registerMockApproval(f.approval), /UNIQUE/);
  f.gate.close();
});
test('COST-03 twenty processes share one atomic slot across all roles', async () => {
  const f = fixture();
  f.gate.registerMockApproval(f.approval);
  const before = hits.length;
  const contenders = Array.from({ length: 20 }, (_, index) => new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [path.join(__dirname, 'request-contender.cjs'), f.filename,
      JSON.stringify({ ...f.request, role: f.approval.roles[index % 4] })], { env: process.env });
    let output = '';
    child.stdout.on('data', chunk => output += chunk);
    child.stderr.on('data', () => {});
    child.on('error', reject);
    child.on('close', code => code === 0 ? resolve(JSON.parse(output)) : reject(new Error(`child exit ${code}`)));
  }));
  const results = await Promise.all(contenders);
  assert.equal(results.filter(result => result.ok).length, 1);
  assert.equal(results.filter(result => result.code === 'REQUEST_LIMIT').length, 19);
  assert.equal(hits.length - before, 1);
  assert.equal(f.gate.snapshot().attempts.length, 1);
  writeFileSync(path.join(directory, 'concurrency.json'), JSON.stringify({ contenders: results, actual_hits: hits.length - before,
    ledger: f.gate.snapshot() }, null, 2));
  f.gate.close();
});
test('COST-04 input output thinking tools search providerOptions stream and budget limits', async () => {
  const bodies = [
    { input: 'x'.repeat(1000) }, { max_output_tokens: 33 }, { max_output_tokens: 0 },
    { thinking: { budget_tokens: 100000 } }, { tools: [{ type: 'web_search' }] },
    { providerOptions: { search: true } }, { tool_choice: 'auto' }, { stream: true },
    { max_tokens: 20 },
  ];
  for (const changes of bodies) {
    await rejectedBeforeSend({}, { body: { model: 'fixture-v1', input: 'synthetic', max_output_tokens: 16, ...changes } },
      /INPUT_LIMIT|OUTPUT_LIMIT|UNSUPPORTED_PARAMETER|TOOLS_OR_STREAM_DISABLED|AMBIGUOUS_OUTPUT_LIMIT/);
  }
  await rejectedBeforeSend({ max_total_tokens: 1 }, {}, /TOKEN_BUDGET/);
});
test('PRV-01 PRV-05 and COST-08 bind provider endpoint region model role and credential', async () => {
  for (const changes of [ { workspace: 'other-workspace' }, { provider: 'unknown' }, { model: 'paid-default' }, { region: 'other' },
    { endpoint: 'http://127.0.0.1:17441/other' }, { role: 'unapproved' }, { credential_ref: 'account-b' },
    { headers: { authorization: 'Bearer synthetic-account-b' } }, { headers: {} },
    { body: { model: 'other', input: 'synthetic', max_output_tokens: 16 } } ]) {
    await rejectedBeforeSend({}, changes, /TARGET_OR_ROLE_MISMATCH|CREDENTIAL_MISMATCH|MODEL_MISMATCH/);
  }
});
test('COST-05 401 403 429 5xx timeout disconnect redirect unknown usage halt without retry or refund', async () => {
  for (const route of ['/status/401', '/status/403', '/status/429', '/status/500', '/slow', '/disconnect', '/redirect', '/missing-usage', '/unexpected-tool']) {
    const f = fixture({ endpoint: `http://127.0.0.1:17441${route}`, max_requests: 3 });
    f.gate.registerMockApproval(f.approval);
    const before = hits.length;
    await assert.rejects(f.gate.request({ ...f.request, timeout_ms: route === '/slow' ? 30 : 1000 }));
    await assert.rejects(f.gate.request(f.request), /BATCH_HALTED/);
    assert.equal(hits.length - before, 1, route);
    const snapshot = f.gate.snapshot();
    assert.equal(snapshot.attempts[0].state, 'UNKNOWN_CHARGE');
    assert.ok(snapshot.attempts[0].reserved_tokens > 0);
    writeFileSync(path.join(directory, `failure-${sequence}.json`), JSON.stringify({ route, hits: hits.length - before, snapshot }, null, 2));
    f.gate.close();
  }
});
test('COST-09 revoke and emergency stop cancel in-flight and deny subsequent roles', async () => {
  for (const method of ['revoke', 'emergencyStop']) {
    const f = fixture({ endpoint: 'http://127.0.0.1:17441/slow', max_requests: 3 });
    f.gate.registerMockApproval(f.approval);
    const before = hits.length;
    const started = Date.now();
    const pending = f.gate.request(f.request);
    const result = assert.rejects(pending);
    while (hits.length === before && Date.now() - started < 2000) await new Promise(resolve => setTimeout(resolve, 5));
    assert.ok(hits.length > before, 'slow request reached fixture');
    f.gate[method](f.approval.id);
    await result;
    await assert.rejects(f.gate.request({ ...f.request, role: 'judge' }), /APPROVAL_REVOKED|EMERGENCY_STOP/);
    assert.equal(hits.length - before, 1);
    assert.equal(f.gate.snapshot().attempts[0].state, 'UNKNOWN_CHARGE');
    console.log(JSON.stringify({ method, stopped_within_ms: Date.now() - started }));
    f.gate.close();
  }
});
test('PRV-06 successful local fixture has explicit empty tools and bounded usage', async () => {
  const f = fixture();
  f.gate.registerMockApproval(f.approval);
  const data = await f.gate.request(f.request);
  assert.deepEqual(data.usage, { input_tokens: 4, output_tokens: 2 });
  assert.equal(f.gate.snapshot().attempts[0].state, 'SUCCEEDED');
  assert.deepEqual(hits.at(-1).tools, []);
  f.gate.close();
});

test('COST-05 process loss preserves the reservation and halts recovery', async () => {
  const f = fixture({ endpoint: 'http://127.0.0.1:17441/slow', max_requests: 3 });
  f.gate.registerMockApproval(f.approval);
  const before = hits.length;
  const child = spawn(process.execPath, [path.join(__dirname, 'request-contender.cjs'), f.filename, JSON.stringify(f.request)],
    { env: process.env, stdio: 'ignore' });
  const stopped = new Promise(resolve => child.on('close', resolve));
  const deadline = Date.now() + 2000;
  while (hits.length === before && Date.now() < deadline) await new Promise(resolve => setTimeout(resolve, 5));
  assert.equal(hits.length, before + 1);
  child.kill('SIGKILL');
  await stopped;
  const recovered = new RequestGuard(f.filename);
  await assert.rejects(recovered.request(f.request), /RECOVERY_UNKNOWN_CHARGE/);
  assert.equal(recovered.snapshot().attempts[0].state, 'UNKNOWN_CHARGE');
  assert.ok(recovered.snapshot().attempts[0].reserved_tokens > 0);
  writeFileSync(path.join(directory, 'crash-recovery.json'),JSON.stringify(recovered.snapshot(),null,2));
  recovered.close();
  f.gate.close();
});

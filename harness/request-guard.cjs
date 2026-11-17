const { AsyncLocalStorage } = require('node:async_hooks');
const { createHash, randomUUID } = require('node:crypto');
const { DatabaseSync } = require('node:sqlite');

const rawFetch = globalThis.fetch;
const networkPermission = new AsyncLocalStorage();

class GuardDenied extends Error {
  constructor(code) {
    super(code);
    this.name = 'GuardDenied';
    this.code = code;
  }
}

function deny(code) {
  throw new GuardDenied(code);
}

function positiveInteger(value) {
  return Number.isSafeInteger(value) && value > 0;
}

function endpointOf(value) {
  let url;
  try {
    url = new URL(value);
  } catch {
    deny('INVALID_ENDPOINT');
  }
  if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' ||
      url.port !== '17441' || url.username || url.password || url.search || url.hash || !url.port) {
    deny('LIVE_ENDPOINT_DISABLED');
  }
  return url;
}

class RequestGuard {
  constructor(filename, { now = Date.now } = {}) {
    this.now = now;
    this.controllers = new Map();
    this.db = new DatabaseSync(filename);
    this.db.exec(`
      PRAGMA busy_timeout=10000;
      PRAGMA journal_mode=WAL;
      CREATE TABLE IF NOT EXISTS approvals (
        id TEXT PRIMARY KEY, payload TEXT NOT NULL, halted TEXT
      );
      CREATE TABLE IF NOT EXISTS attempts (
        id TEXT PRIMARY KEY, approval_id TEXT NOT NULL, role TEXT NOT NULL, owner_pid INTEGER NOT NULL,
        started_at INTEGER NOT NULL, ended_at INTEGER, state TEXT NOT NULL,
        reserved_tokens INTEGER NOT NULL, input_bound INTEGER NOT NULL,
        output_bound INTEGER NOT NULL, input_used INTEGER, output_used INTEGER,
        body_sha256 TEXT NOT NULL, error_code TEXT
      );
      CREATE TABLE IF NOT EXISTS events (
        sequence INTEGER PRIMARY KEY, at INTEGER NOT NULL, kind TEXT NOT NULL,
        approval_id TEXT, attempt_id TEXT, detail TEXT
      );
    `);
    this.recoverAbandoned();
  }

  recoverAbandoned() {
    this.db.exec('BEGIN IMMEDIATE');
    try {
      const pending = this.db.prepare("SELECT id,approval_id,owner_pid FROM attempts WHERE state IN ('RESERVED','IN_FLIGHT')").all();
      for (const row of pending) {
        try {
          process.kill(row.owner_pid, 0);
        } catch (error) {
          if (error.code !== 'ESRCH') continue;
          this.db.prepare("UPDATE attempts SET state='UNKNOWN_CHARGE',ended_at=?,error_code='OWNER_PROCESS_LOST' WHERE id=?").run(this.now(), row.id);
          this.db.prepare("UPDATE approvals SET halted=coalesce(halted,'RECOVERY_UNKNOWN_CHARGE') WHERE id=?").run(row.approval_id);
          this.event('UNKNOWN_CHARGE', row.approval_id, row.id, 'OWNER_PROCESS_LOST');
        }
      }
      this.db.exec('COMMIT');
    } catch (error) {
      this.db.exec('ROLLBACK');
      throw error;
    }
  }

  event(kind, approvalId, attemptId, detail) {
    this.db.prepare('INSERT INTO events(at,kind,approval_id,attempt_id,detail) VALUES(?,?,?,?,?)')
      .run(this.now(), kind, approvalId ?? null, attemptId ?? null, detail ?? null);
  }

  registerMockApproval(approval) {
    endpointOf(approval.endpoint);
    if (approval.mode !== 'MOCK_FIXTURE' || approval.approved !== true ||
        approval.approved_by !== 'LOCAL_TEST_FIXTURE' || approval.cash_charge_usd !== 0 ||
        approval.paid_fallback_disabled !== true || !approval.quota_evidence_ref ||
        !approval.hard_stop_evidence_ref || !approval.credential_ref ||
        !/^[a-f0-9]{64}$/.test(approval.credential_sha256 ?? '') ||
        approval.quota_scope !== 'FIXTURE_EXCLUSIVE' || !approval.workspace || !approval.id || !approval.provider || !approval.model || approval.region !== 'local-mock' ||
        !Array.isArray(approval.roles) || approval.roles.length === 0 ||
        !Array.isArray(approval.allowed_tools) || approval.allowed_tools.length !== 0 ||
        !Number.isFinite(approval.expires_at) || !Number.isFinite(approval.quota_expires_at) ||
        !['max_requests', 'max_input_tokens', 'max_output_tokens', 'max_total_tokens']
          .every(key => positiveInteger(approval[key]))) {
      deny('INVALID_APPROVAL');
    }
    this.db.prepare('INSERT INTO approvals(id,payload) VALUES(?,?)')
      .run(approval.id, JSON.stringify(approval));
    this.event('MOCK_APPROVAL_REGISTERED', approval.id, null, 'No live authorization');
  }

  approval(id) {
    const row = this.db.prepare('SELECT payload,halted FROM approvals WHERE id=?').get(id);
    if (!row) deny('APPROVAL_MISSING');
    if (row.halted) deny(row.halted);
    const approval = JSON.parse(row.payload);
    if (approval.expires_at <= this.now()) deny('APPROVAL_EXPIRED');
    if (approval.quota_expires_at <= this.now()) deny('QUOTA_EXPIRED');
    return approval;
  }

  validate(approval, request) {
    const target = endpointOf(request.endpoint);
    if (target.href !== endpointOf(approval.endpoint).href ||
        request.workspace !== approval.workspace || request.provider !== approval.provider || request.model !== approval.model || request.region !== approval.region ||
        request.credential_ref !== approval.credential_ref ||
        !approval.roles.includes(request.role)) deny('TARGET_OR_ROLE_MISMATCH');
    const headers = new Headers(request.headers);
    const credentialHash = createHash('sha256').update(headers.get('authorization') ?? '').digest('hex');
    if (credentialHash !== approval.credential_sha256) deny('CREDENTIAL_MISMATCH');
    const body = request.body;
    if (!body || body.model !== request.model) deny('MODEL_MISMATCH');
    const supported = new Set(['model', 'input', 'prompt', 'messages', 'state', 'questions',
      'max_output_tokens', 'max_tokens', 'tools', 'tool_choice', 'temperature', 'stream']);
    if (Object.keys(body).some(key => !supported.has(key))) deny('UNSUPPORTED_PARAMETER');
    if ((body.tools && (!Array.isArray(body.tools) || body.tools.length > 0)) ||
        (body.tool_choice && body.tool_choice !== 'none') || body.stream === true) deny('TOOLS_OR_STREAM_DISABLED');
    const output = body.max_output_tokens ?? body.max_tokens;
    if (body.max_tokens !== undefined && body.max_output_tokens !== undefined) deny('AMBIGUOUS_OUTPUT_LIMIT');
    if (!positiveInteger(output) || output > approval.max_output_tokens) deny('OUTPUT_LIMIT');
    const input = { input: body.input, prompt: body.prompt, messages: body.messages,
      state: body.state, questions: body.questions };
    const inputBound = Buffer.byteLength(JSON.stringify(input), 'utf8') + 64;
    if (inputBound > approval.max_input_tokens) deny('INPUT_LIMIT');
    return { target, inputBound, output };
  }

  reserve(request) {
    this.db.exec('BEGIN IMMEDIATE');
    try {
      const approval = this.approval(request.approval_id);
      const limits = this.validate(approval, request);
      const used = this.db.prepare(`SELECT count(*) AS requests,
        coalesce(sum(reserved_tokens),0) AS tokens FROM attempts WHERE approval_id=?`).get(approval.id);
      if (used.requests >= approval.max_requests) deny('REQUEST_LIMIT');
      if (used.tokens + limits.inputBound + limits.output > approval.max_total_tokens) deny('TOKEN_BUDGET');
      const id = randomUUID();
      this.db.prepare(`INSERT INTO attempts
        (id,approval_id,role,owner_pid,started_at,state,reserved_tokens,input_bound,output_bound,body_sha256)
        VALUES(?,?,?,?,?,?,?,?,?,?)`).run(id, approval.id, request.role, process.pid, this.now(), 'RESERVED',
          limits.inputBound + limits.output, limits.inputBound, limits.output,
          createHash('sha256').update(JSON.stringify(request.body)).digest('hex'));
      this.event('RESERVED', approval.id, id, request.role);
      this.db.exec('COMMIT');
      return { id, approval, ...limits };
    } catch (error) {
      this.db.exec('ROLLBACK');
      this.event('DENIED', request.approval_id, null, error.code ?? 'VALIDATION_ERROR');
      throw error;
    }
  }

  halt(approvalId, reason) {
    this.db.prepare('UPDATE approvals SET halted=coalesce(halted,?) WHERE id=?').run(reason, approvalId);
    this.event('HALTED', approvalId, null, reason);
    for (const entry of this.controllers.values()) {
      if (entry.approvalId === approvalId) entry.controller.abort(new GuardDenied(reason));
    }
  }

  revoke(approvalId) {
    this.halt(approvalId, 'APPROVAL_REVOKED');
  }

  emergencyStop() {
    for (const row of this.db.prepare('SELECT id FROM approvals').all()) this.halt(row.id, 'EMERGENCY_STOP');
  }

  async request(request) {
    const reservation = this.reserve(request);
    const { id, approval, target } = reservation;
    const controller = new AbortController();
    this.controllers.set(id, { approvalId: approval.id, controller });
    const timeout = setTimeout(() => controller.abort(new GuardDenied('REQUEST_TIMEOUT')),
      Math.min(request.timeout_ms ?? 5000, 5000));
    const watch = setInterval(() => {
      try {
        this.approval(approval.id);
      } catch (error) {
        controller.abort(error);
      }
    }, 20);
    try {
      this.approval(approval.id);
      this.db.prepare('UPDATE attempts SET state=? WHERE id=?').run('IN_FLIGHT', id);
      this.event('HTTP_ATTEMPT', approval.id, id, target.origin + target.pathname);
      const response = await networkPermission.run({ host: target.hostname, port: Number(target.port) }, () =>
        rawFetch(target, { method: 'POST', headers: request.headers, body: JSON.stringify(request.body),
          redirect: 'error', signal: controller.signal }));
      if (!response.ok) deny(`HTTP_${response.status}`);
      const chunks = [];
      let size = 0;
      for await (const chunk of response.body ?? []) {
        size += chunk.length;
        if (size > 1_000_000) {
          controller.abort();
          deny('RESPONSE_LIMIT');
        }
        chunks.push(chunk);
      }
      const data = JSON.parse(Buffer.concat(chunks).toString('utf8'));
      const usage = data.usage;
      if (!usage || !Number.isSafeInteger(usage.input_tokens) || !Number.isSafeInteger(usage.output_tokens) ||
          usage.input_tokens < 0 || usage.output_tokens < 0) deny('USAGE_UNKNOWN');
      if (usage.input_tokens > reservation.inputBound || usage.output_tokens > reservation.output) deny('USAGE_LIMIT');
      if (data.tools_used?.length || data.search_queries?.length) deny('UNAUTHORIZED_TOOL_USAGE');
      if (data.model !== request.model) deny('REPORTED_MODEL_MISMATCH');
      this.approval(approval.id);
      this.db.prepare(`UPDATE attempts SET state='SUCCEEDED',ended_at=?,input_used=?,output_used=? WHERE id=?`)
        .run(this.now(), usage.input_tokens, usage.output_tokens, id);
      this.event('SUCCEEDED', approval.id, id, 'MOCK_FIXTURE');
      return data;
    } catch (error) {
      const code = error.code ?? error.cause?.code ?? 'UNKNOWN_TRANSPORT_FAILURE';
      this.db.prepare(`UPDATE attempts SET state='UNKNOWN_CHARGE',ended_at=?,error_code=? WHERE id=?`)
        .run(this.now(), String(code), id);
      this.event('UNKNOWN_CHARGE', approval.id, id, String(code));
      this.halt(approval.id, 'BATCH_HALTED');
      throw new GuardDenied(String(code));
    } finally {
      clearTimeout(timeout);
      clearInterval(watch);
      this.controllers.delete(id);
    }
  }

  snapshot() {
    return { attempts: this.db.prepare('SELECT * FROM attempts ORDER BY started_at,id').all(),
      events: this.db.prepare('SELECT * FROM events ORDER BY sequence').all(),
      approvals: this.db.prepare('SELECT id,halted FROM approvals ORDER BY id').all() };
  }

  close() {
    if (this.controllers.size) deny('REQUESTS_STILL_ACTIVE');
    this.db.close();
  }
}

module.exports = { RequestGuard, GuardDenied, networkPermission };

const fs = require('node:fs');
const net = require('node:net');
const dns = require('node:dns');
const { RequestGuard, GuardDenied, networkPermission } = require('./request-guard.cjs');

const stage = process.env.TUC_P0_STAGE;
if (!/^[a-f0-9]{64}$/.test(process.env.TUC_P0_POLICY_SHA256 ?? '')) throw new GuardDenied('P0_POLICY_MISSING');
if (!['runtime', 'quality', 'mock'].includes(stage)) throw new GuardDenied('P0_STAGE_MISSING');
if (stage !== 'quality' && process.env.TUC_P0_OFFLINE !== '1') throw new GuardDenied('P0_OFFLINE_REQUIRED');
if (stage === 'runtime') {
  for (const [key, expected] of Object.entries({
    SCRAPE_TARGETS: 'stub:stub', ONBOARDING_LLM_TARGET: 'stub:stub',
    TYPESAFE_API_KEY: 'stub', RUNS_PER_PROMPT: '1', DEPLOYMENT_MODE: 'local',
  })) {
    if (process.env[key] !== expected) throw new GuardDenied(`P0_CONFIG_${key}`);
  }
}

function event(kind, target) {
  const row = { at_utc: new Date().toISOString(), pid: process.pid, ppid: process.ppid,
    stage, kind, target, policy: process.env.TUC_P0_POLICY_SHA256 };
  if (process.env.TUC_P0_EGRESS_LOG) fs.appendFileSync(process.env.TUC_P0_EGRESS_LOG, JSON.stringify(row) + '\n');
}

event('POLICY_LOADED', process.argv[1] ?? 'node');
globalThis[Symbol.for('tuc.p0.policy-loaded')] = { stage, policy: process.env.TUC_P0_POLICY_SHA256 };
const originalConnect = net.Socket.prototype.connect;
net.Socket.prototype.connect = function (...args) {
  const first = Array.isArray(args[0]) ? args[0][0] : args[0];
  const options = typeof first === 'object' && first !== null ? first : { port: first, host: args[1] };
  const host = options.host ?? 'localhost';
  const port = Number(options.port);
  const permission = networkPermission.getStore();
  const database = stage === 'runtime' && host === '127.0.0.1' && port === 17332;
  const sitemap = stage === 'quality' && host === '127.0.0.1' && port === 17440;
  const mock = stage === 'mock' && host === permission?.host && port === permission?.port;
  if (!database && !sitemap && !mock) {
    event('SOCKET_DENIED', `${host}:${Number.isFinite(port) ? port : 'unix'}`);
    throw new GuardDenied('OUTBOUND_SOCKET_DENIED');
  }
  event('SOCKET_ALLOWED', `${host}:${port}`);
  return originalConnect.apply(this, args);
};

for (const object of [dns, dns.promises]) {
  for (const name of ['lookup', 'resolve', 'resolve4', 'resolve6', 'resolveAny']) {
    if (typeof object[name] !== 'function') continue;
    const original = object[name].bind(object);
    object[name] = (host, ...args) => {
      if (!['127.0.0.1', 'localhost', '::1'].includes(host)) {
        event('DNS_DENIED', host);
        throw new GuardDenied('DNS_DENIED');
      }
      return original(host, ...args);
    };
  }
}

const nativeFetch = globalThis.fetch;
let gate;
globalThis.fetch = async (input, init = {}) => {
  const request = new Request(input, init);
  const url = new URL(request.url);
  if (stage === 'quality' && url.origin === 'http://127.0.0.1:17440' &&
      url.pathname === '/sitemap.xml' && request.method === 'GET') {
    return nativeFetch(request);
  }
  if (stage !== 'mock' || !process.env.TUC_P0_LEDGER || request.method !== 'POST') {
    event('FETCH_DENIED', url.origin + url.pathname);
    throw new GuardDenied('LIVE_REQUEST_DISABLED');
  }
  const headers = new Headers(request.headers);
  const metadata = {};
  for (const key of ['approval_id', 'provider', 'workspace', 'role', 'model', 'region', 'credential_ref']) {
    const header = 'x-tuc-' + key.replaceAll('_', '-');
    metadata[key] = headers.get(header);
    headers.delete(header);
  }
  if (!metadata.approval_id) throw new GuardDenied('APPROVAL_MISSING');
  gate ??= new RequestGuard(process.env.TUC_P0_LEDGER);
  const data = await gate.request({ ...metadata, endpoint: url.href, headers: Object.fromEntries(headers),
    body: await request.json() });
  return Response.json(data);
};

require('node:module').syncBuiltinESMExports();

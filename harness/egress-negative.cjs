const assert = require('node:assert/strict');
const net = require('node:net');
const dns = require('node:dns');
const { spawnSync } = require('node:child_process');
(async () => {
  const results = [];
  for (const url of ['https://example.invalid/v1', 'http://127.0.0.1:17442/', 'http://[::1]:17442/']) {
    await assert.rejects(fetch(url), /LIVE_REQUEST_DISABLED/);
    results.push({ case: 'fetch', url, outcome: 'DENIED' });
  }
  assert.throws(() => dns.lookup('example.invalid', () => {}), /DNS_DENIED/);
  for (const target of [{ host: '127.0.0.1', port: 17442 }, { host: '::1', port: 17442 }, { path: '/tmp/unapproved.sock' }]) {
    assert.throws(() => net.connect(target), /OUTBOUND_SOCKET_DENIED/);
    results.push({ case: 'socket', target, outcome: 'DENIED' });
  }
  for (const args of [
    ['--noproxy', '*', 'http://127.0.0.1:17442/'],
    ['--noproxy', '*', 'http://[::1]:17442/'],
    ['--proxy', 'http://127.0.0.1:17442', 'http://example.invalid/'],
    ['--noproxy', '*', 'http://192.0.2.1:80/'],
  ]) {
    const result = spawnSync('/usr/bin/curl', ['--silent', '--show-error', '--max-time', '1', ...args],
      { env: { PATH: '/usr/bin:/bin' }, encoding: 'utf8' });
    assert.notEqual(result.status, 0);
    results.push({ case: 'native-child-with-cleared-environment', args, exit_code: result.status,
      stderr: result.stderr.trim() });
  }
  console.log(JSON.stringify({ results, external_requests: 0 }, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });

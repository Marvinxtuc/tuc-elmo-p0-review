const { RequestGuard } = require('./request-guard.cjs');
const gate = new RequestGuard(process.argv[2]);
gate.request(JSON.parse(process.argv[3])).then(
  () => console.log(JSON.stringify({ ok: true })),
  error => console.log(JSON.stringify({ ok: false, code: error.code })),
).finally(() => gate.close());

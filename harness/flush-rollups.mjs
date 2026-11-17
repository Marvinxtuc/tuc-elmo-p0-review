import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(path.join(root, "upstream/elmo/apps/worker/package.json"));
const { PgBoss } = require("pg-boss");
const approval = JSON.parse(await readFile(path.join(root, "approvals/A0.json"), "utf8"));
const database = new URL(process.env.DATABASE_URL);
if (!approval.approval_id || database.hostname !== "127.0.0.1" || database.pathname !== "/tuc_elmo_p0_test") {
  throw new Error("The manual rollup flush is outside A0 scope");
}
const boss = new PgBoss({ connectionString: process.env.DATABASE_URL });
try {
  await boss.start();
  const id = await boss.send("refresh-rollups", { source: "p0-manual-batch-finish" });
  console.log(JSON.stringify({ manual_rollup_job: id, external_model_requests: 0 }));
} finally {
  await boss.stop();
}

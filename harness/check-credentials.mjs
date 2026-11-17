import assert from "node:assert/strict";
import { createHash, randomBytes } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const run = JSON.parse(await readFile(path.join(root, "config/active-run.json"), "utf8")).path;
const restore = process.argv.includes("--restore");
if (restore) {
  const database = new URL(process.env.DATABASE_URL);
  assert(database.hostname === "127.0.0.1" && database.port === "17332");
  database.pathname = "/tuc_elmo_p0_restore";
  process.env.DATABASE_URL = database.toString();
}
const require = createRequire(path.join(root, "upstream/elmo/packages/lib/package.json"));
const { eq } = require("drizzle-orm");
const load = relative => import(pathToFileURL(path.join(root, "upstream/elmo", relative)).href);
const { db } = await load("packages/lib/src/db/db.ts");
const { secrets } = await load("packages/lib/src/db/schema.ts");
const { encryptCredential, decryptSecret, getKeyring } = await load("packages/lib/src/secrets/index.ts");
const canary = JSON.parse(await readFile(path.join(root, "secrets/canary.json"), "utf8")).value;
try {
  if (!restore) {
    const encryptedValue = await encryptCredential("OPENAI_API_KEY", canary);
    assert(!encryptedValue.includes(canary), "Plaintext was found in the encrypted value");
    await db.insert(secrets).values({ name: "OPENAI_API_KEY", encryptedValue });
  }
  const [row] = await db.select().from(secrets).where(eq(secrets.name, "OPENAI_API_KEY"));
  assert(row, "The canary row is missing");
  const keyring = getKeyring();
  const decrypted = await decryptSecret(row.encryptedValue, { keyring, aad: "secret:OPENAI_API_KEY" });
  assert(decrypted === canary, "Canary decryption failed");
  const wrongKeyring = { primary: randomBytes(32), byId: new Map([...keyring.byId.keys()].map(id => [id, randomBytes(32)])) };
  await assert.rejects(() => decryptSecret(row.encryptedValue, { keyring: wrongKeyring, aad: "secret:OPENAI_API_KEY" }));
  const result = { database: restore ? "tuc_elmo_p0_restore" : "tuc_elmo_p0_test", encrypted_at_rest: true,
    restored_canary_matches: restore, correct_key_decryption: true, wrong_key_rejected: true,
    encrypted_payload_sha256: createHash("sha256").update(row.encryptedValue).digest("hex") };
  await writeFile(path.join(run, restore ? "credentials-after-restore.json" : "credentials-before-backup.json"), JSON.stringify(result, null, 2) + "\n");
  console.log(JSON.stringify(result));
} finally {
  await db.$client.end();
}

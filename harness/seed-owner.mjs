import { randomUUID } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(path.join(root, "upstream/elmo/packages/lib/package.json"));
const { hashPassword } = require("better-auth/crypto");
const load = name => import(pathToFileURL(path.join(root, "upstream/elmo/packages/lib/src/db", name)).href);
const { db } = await load("db.ts");
const { user, account, member } = await load("schema.ts");
const fixture = JSON.parse(await readFile(path.join(root, "secrets/owner.json"), "utf8"));
try {
  const userId = randomUUID();
  await db.transaction(async tx => {
    await tx.insert(user).values({ id: userId, name: "P0 Test Owner", email: fixture.email, emailVerified: true, role: "admin" });
    await tx.insert(account).values({ id: randomUUID(), userId, accountId: userId, providerId: "credential", password: await hashPassword(fixture.password) });
    await tx.insert(member).values({ id: randomUUID(), userId, organizationId: "tuc-p0-internal", role: "admin", createdAt: new Date() });
  });
  console.log("Created one synthetic owner fixture using the upstream password hasher and the existing internal organization.");
} finally {
  await db.$client.end();
}

import { createRequire } from "node:module";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const run = JSON.parse(await readFile(path.join(root, "config/active-run.json"), "utf8")).path;
const require = createRequire(path.join(root, "upstream/elmo/e2e/package.json"));
const { chromium } = require("@playwright/test");
await mkdir(path.join(run, "screenshots"), { recursive: true });
const context = await chromium.launchPersistentContext(path.join(root, "runtime/browser-profile"), {
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
  viewport: { width: 1280, height: 850 },
  args: ["--disable-background-networking", "--disable-component-update", "--disable-sync"],
});
const requests = [];
const blocked = [];
await context.route("**/*", route => {
  const url = new URL(route.request().url());
  if (url.protocol === "data:" || (url.hostname === "127.0.0.1" && url.port === "17300")) {
    requests.push(url.origin + url.pathname);
    return route.continue();
  }
  blocked.push(url.origin + url.pathname);
  return route.abort();
});
const page = context.pages()[0] ?? await context.newPage();
const pageErrors = [];
const login = process.argv.includes("--login");
const view = process.argv.includes("--brand") ? "brand" : login ? "dashboard" : "entry";
page.on("pageerror", error => pageErrors.push(error.message));
try {
  const response = await page.goto("http://127.0.0.1:17300/", { waitUntil: "networkidle" });
  if (!response?.ok()) throw new Error(`Browser entry returned ${response?.status()}`);
  if (login && !page.url().includes("/app")) {
    const owner = JSON.parse(await readFile(path.join(root, "secrets/owner.json"), "utf8"));
    await page.getByLabel("Email", { exact: true }).fill(owner.email);
    await page.getByLabel("Password", { exact: true }).fill(owner.password);
    await page.getByRole("button", { name: /sign in/i }).click();
    await page.waitForURL(url => url.pathname.startsWith("/app"), { timeout: 20000 });
    await page.waitForLoadState("networkidle");
  }
  if (view === "brand") {
    await page.locator('a[href*="/brand/"]').first().click();
    await page.waitForLoadState("networkidle");
    await page.waitForFunction(() => document.body.innerText.includes("10 evaluations"), undefined, { timeout: 20000 });
  }
  await page.screenshot({ path: path.join(run, `screenshots/stub-${view}.png`), fullPage: true });
  const text = await page.locator("body").innerText();
  if (!text.includes("UPSTREAM_STUB")) throw new Error("The required stub label is missing");
  if (pageErrors.length > 0 || blocked.length > 0) throw new Error("Browser errors or unexpected external requests were observed");
  const result = { url: page.url(), text, inputs: await page.locator("input").evaluateAll(inputs => inputs.map(input => ({ name: input.name, type: input.type, placeholder: input.placeholder }))), pageErrors, requests, blocked };
  await writeFile(path.join(run, `browser-${view}.json`), JSON.stringify(result, null, 2) + "\n");
  console.log(JSON.stringify({ url: result.url, text: text.slice(0, 2200), inputs: result.inputs, pageErrors, blocked }, null, 2));
} finally {
  await context.close();
}

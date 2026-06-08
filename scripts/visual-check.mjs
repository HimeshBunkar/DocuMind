import { createRequire } from "node:module";
import { access, mkdir } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const bundledPlaywright = path.resolve(
  process.env.CODEX_PLAYWRIGHT_MODULE ??
    "C:/Users/hp5cd/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.60.0/node_modules/playwright/package.json"
);
const require = createRequire(bundledPlaywright);
const { chromium } = require("playwright");

const edgePath = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
let executablePath;
try {
  await access(edgePath);
  executablePath = edgePath;
} catch {
  executablePath = undefined;
}

const browser = await chromium.launch({ headless: true, executablePath });
const page = await browser.newPage({ viewport: { width: 1440, height: 980 } });
await page.goto("http://127.0.0.1:3000", { waitUntil: "networkidle" });
await page.getByRole("heading", { name: "Grounded answers with paragraph citations" }).waitFor();
await page.getByRole("heading", { name: "Ask DocuMind" }).waitFor();
await page.getByRole("heading", { name: "Sources" }).waitFor();

await mkdir(path.join(root, "work"), { recursive: true });
await page.screenshot({ path: path.join(root, "work", "documind-visual-check.png"), fullPage: true });
await browser.close();

console.log("visual check ok");

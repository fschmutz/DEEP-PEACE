// Photograph local HTML pages with Playwright (Chromium), 1280 px wide.
//
//   node capture.mjs NODE_MODULES_DIR MAX_HEIGHT page.html=out.png [...]
//
// NODE_MODULES_DIR is any node_modules that already has `playwright` and its
// Chromium installed — the template ships no Node dependencies of its own.
// Each pair is captured in a fresh browser context, in order, so a later page
// that embeds an earlier screenshot sees the file just written.
//
// Network: file:// and data: plus camo.githubusercontent.com, where GitHub's
// renderer proxies external badge images. The private workflow badge is
// replaced by render.py before capture, so github.com is not needed. Anything
// else is aborted, so a page cannot quietly phone out.

import { createRequire } from "node:module";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const [nodeModules, maxHeightArg, ...pairs] = process.argv.slice(2);
if (!nodeModules || !maxHeightArg || pairs.length === 0) {
  console.error("usage: node capture.mjs NODE_MODULES_DIR MAX_HEIGHT page.html=out.png [...]");
  process.exit(2);
}

const require = createRequire(join(resolve(nodeModules), "noop.js"));
const { chromium } = require("playwright");

const WIDTH = 1280;
const maxHeight = Number(maxHeightArg);
const ALLOWED = [/^file:/, /^data:/, /^https:\/\/camo\.githubusercontent\.com\//];

const browser = await chromium.launch();
try {
  for (const pair of pairs) {
    const [htmlPath, pngPath] = pair.split("=");
    const context = await browser.newContext({
      viewport: { width: WIDTH, height: 800 },
      deviceScaleFactor: 1,
      colorScheme: "light",
    });
    await context.route("**/*", (route) =>
      ALLOWED.some((re) => re.test(route.request().url())) ? route.continue() : route.abort(),
    );
    const page = await context.newPage();
    await page.goto(pathToFileURL(resolve(htmlPath)).href, { waitUntil: "networkidle" });
    const height = await page.evaluate(() => document.documentElement.scrollHeight);
    const clipHeight = Math.min(height, maxHeight);
    await page.screenshot({
      path: pngPath,
      fullPage: true,
      clip: { x: 0, y: 0, width: WIDTH, height: clipHeight },
    });
    console.log(`captured ${pngPath} (${WIDTH}x${clipHeight}, page ${height}px)`);
    await context.close();
  }
} finally {
  await browser.close();
}

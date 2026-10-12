// Browser validation of a third-party bass GLB using the generic viewer metrics.
// No custom-authored C1 part names, atlas layout, or material names are assumed.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { chromium } from '@playwright/test';

const repo = path.resolve(import.meta.dirname, '../..');
const input = path.resolve(process.argv[2] || '');
const output = path.resolve(process.argv[3] || path.join(path.dirname(input), 'browser-qa.json'));
assert.ok(fs.statSync(input).size > 20, 'GLB is missing or empty');
const invalid = Buffer.from(fs.readFileSync(input).subarray(0, 16));
const types = new Map([['.html', 'text/html'], ['.js', 'text/javascript'], ['.mjs', 'text/javascript'],
  ['.glb', 'model/gltf-binary'], ['.png', 'image/png']]);
const server = http.createServer((request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
  if (pathname === '/__model.glb' || pathname === '/__invalid.glb') {
    response.writeHead(200, { 'content-type': 'model/gltf-binary', 'cache-control': 'no-store' });
    response.end(pathname === '/__model.glb' ? fs.readFileSync(input) : invalid);
    return;
  }
  const target = path.resolve(repo, `.${pathname}`);
  if (target !== repo && !target.startsWith(`${repo}${path.sep}`)) {
    response.writeHead(403).end('Forbidden');
    return;
  }
  try {
    const bytes = fs.readFileSync(target);
    response.writeHead(200, { 'content-type': types.get(path.extname(target)) || 'application/octet-stream' });
    response.end(bytes);
  } catch {
    response.writeHead(404).end('Not found');
  }
});
await new Promise((resolve, reject) => {
  server.once('error', reject);
  server.listen(0, '127.0.0.1', resolve);
});
const port = server.address().port;
let browser;
try {
  browser = await chromium.launch({ headless: true,
    executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium',
    args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1000, height: 700 }, deviceScaleFactor: 1 });
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  await page.goto(`http://127.0.0.1:${port}/tools/blender/viewer.html?model=/__model.glb`);
  await page.waitForFunction(() => window.__bassState?.status === 'loaded', null, { timeout: 30000 });
  const metrics = await page.evaluate(() => window.__bassState.metrics);
  assert.ok(metrics.meshCount >= 2, 'Expected body and eye meshes');
  assert.ok(metrics.triangles > 0 && metrics.triangles <= 10976, `Triangle budget: ${metrics.triangles}`);
  assert.ok(metrics.drawCalls > 0 && metrics.drawCalls <= 11, `Draw-call budget: ${metrics.drawCalls}`);
  assert.ok(metrics.bounds.every(v => Number.isFinite(v) && v > 0), 'Invalid bounds');
  assert.ok(metrics.bounds[0] >= .44 && metrics.bounds[0] <= .46, 'Bass length must be 0.45 m');
  assert.equal(metrics.skinnedMeshCount, 0, 'Static candidate unexpectedly skinned');
  assert.equal(metrics.animationClips, 0, 'Static candidate unexpectedly animated');
  assert.ok(metrics.bodyPbrMaterialFound, 'No fully mapped body PBR material');
  assert.ok(metrics.transparentMaterialCount >= 1, 'No transparent fin material');
  assert.ok(metrics.decodedImages.length > 0 && metrics.decodedImages.length <= 5,
    `Texture budget: ${metrics.decodedImages.length}`);
  assert.ok(metrics.decodedImages.every(im => im.decoded && im.width > 0 && im.height > 0 &&
    im.width <= 2048 && im.height <= 2048), 'A texture failed decoding or exceeds 2048 px');
  assert.deepEqual(pageErrors, [], `Viewer errors: ${pageErrors.join('; ')}`);
  const screenshot = path.join(path.dirname(output), 'browser-qa.png');
  await page.screenshot({ path: screenshot, fullPage: true });
  await page.goto(`http://127.0.0.1:${port}/tools/blender/viewer.html?model=/__invalid.glb`);
  await page.waitForFunction(() => window.__bassState?.status === 'error', null, { timeout: 15000 });
  const negativeLoaderError = await page.evaluate(() => window.__bassState.error);
  assert.ok(negativeLoaderError, 'Corrupt GLB was not rejected');
  const result = { input, check: 'supplied-bass-browser-load', ...metrics,
    screenshot: path.relative(repo, screenshot), negativeLoaderError };
  fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify({ input, triangles: metrics.triangles, drawCalls: metrics.drawCalls,
    embeddedImages: metrics.decodedImages.length, negativeLoaderError, output }, null, 2));
} finally {
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
}

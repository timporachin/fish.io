import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { chromium } from '@playwright/test';

const mime = new Map([
  ['.html', 'text/html; charset=utf-8'], ['.js', 'text/javascript; charset=utf-8'], ['.mjs', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'], ['.glb', 'model/gltf-binary'], ['.png', 'image/png'], ['.jpg', 'image/jpeg'], ['.jpeg', 'image/jpeg'],
]);

export async function runBassBrowserChecks({ repo, input, invalidBytes }) {
  const invalidPath = path.join(repo, 'artifacts/c1/.bass-invalid-test.glb');
  fs.writeFileSync(invalidPath, invalidBytes);
  const server = http.createServer((request, response) => {
    const requestPath = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    if (requestPath === '/__bass_model.glb') {
      response.writeHead(200, { 'content-type': 'model/gltf-binary', 'cache-control': 'no-store' });
      response.end(fs.readFileSync(input));
      return;
    }
    const target = path.resolve(repo, `.${requestPath}`);
    if (target !== repo && !target.startsWith(`${repo}${path.sep}`)) {
      response.writeHead(403).end('Forbidden');
      return;
    }
    try {
      const data = fs.readFileSync(target);
      response.writeHead(200, { 'content-type': mime.get(path.extname(target)) || 'application/octet-stream', 'cache-control': 'no-store' });
      response.end(data);
    } catch {
      response.writeHead(404).end('Not found');
    }
  });
  const port = await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => resolve(server.address().port));
  });
  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium',
      args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
    });
    const page = await browser.newPage({ viewport: { width: 1000, height: 700 }, deviceScaleFactor: 1 });
    const pageErrors = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));
    await page.goto(`http://127.0.0.1:${port}/tools/blender/viewer.html?model=/__bass_model.glb`, { waitUntil: 'load' });
    await page.waitForFunction(() => window.__bassState?.status === 'loaded', null, { timeout: 30000 });
    const metrics = await page.evaluate(() => window.__bassState.metrics);
    assert.ok(metrics.meshCount > 0, 'Three.js loaded no meshes');
    assert.ok(metrics.drawCalls > 0, 'Three.js renderer made no draw calls');
    assert.ok(metrics.triangles > 0, 'Three.js rendered no triangles');
    assert.ok(metrics.drawCalls < 100, `Asset draw calls exceed the provisional 100-call budget: ${metrics.drawCalls}`);
    assert.ok(metrics.triangles < 150000, `Asset triangles exceed the provisional 150k budget: ${metrics.triangles}`);
    assert.ok(metrics.bounds.every(Number.isFinite) && metrics.bounds.every((value) => value > 0), `Invalid bounds dimensions: ${metrics.bounds}`);
    assert.ok(metrics.bounds[0] > metrics.bounds[1] * 1.3 && metrics.bounds[0] > metrics.bounds[2] * 1.3,
      `Expected the bass length on local X to exceed depth and height: ${metrics.bounds}`);
    assert.equal(metrics.animationClips, 0, 'Unexpected animation clips loaded in Three.js');
    assert.equal(metrics.skinnedMeshCount, 0, 'Unexpected skinned meshes loaded in Three.js');
    assert.ok(metrics.bodyPbrMaterialFound, 'No material uses base-color, normal, and roughness maps together');
    assert.ok(metrics.decodedImages.length > 0, 'No embedded images were decoded by the browser');
    assert.ok(metrics.decodedImages.every(({ decoded }) => decoded), 'A referenced texture image was not decoded');
    assert.ok(metrics.decodedImages.every(({ width, height }) => width > 0 && height > 0), 'A decoded texture has invalid dimensions');
    assert.ok(metrics.decodedImages.every(({ width, height }) => width <= 2048 && height <= 2048), 'A decoded texture exceeds the 2048px budget');
    const normalSamples = metrics.decodedImages.filter(({ normalSample }) => normalSample).map(({ normalSample }) => normalSample);
    assert.ok(normalSamples.length > 0, 'No decoded normal map was sampled');
    assert.ok(normalSamples.every(({ mean: [x, y, z] }) => Math.abs(x - 0.5) <= 0.1 && Math.abs(y - 0.5) <= 0.1 && z > 0.85),
      `Normal map channels look gamma-skewed or invalid: ${JSON.stringify(normalSamples)}`);
    assert.deepEqual(pageErrors, [], `Browser page errors: ${pageErrors.join('; ')}`);
    await page.screenshot({ path: path.join(repo, 'artifacts/c1/largemouth-bass-browser.png'), fullPage: true });
    console.log(JSON.stringify({ check: 'threejs-browser-load', ...metrics, screenshot: 'artifacts/c1/largemouth-bass-browser.png' }, null, 2));

    await page.goto(`http://127.0.0.1:${port}/tools/blender/viewer.html?model=/artifacts/c1/.bass-invalid-test.glb`, { waitUntil: 'load' });
    await page.waitForFunction(() => window.__bassState?.status === 'error', null, { timeout: 15000 });
    const failure = await page.evaluate(() => window.__bassState.error);
    assert.ok(failure, 'Three.js did not report the corrupt GLB load failure');
    console.log(`BROWSER_NEGATIVE_OK corrupt GLB rejected (${failure})`);
    return { ...metrics, screenshot: 'artifacts/c1/largemouth-bass-browser.png', negativeLoaderError: failure };
  } finally {
    await browser?.close();
    await new Promise((resolve) => server.close(resolve));
    fs.rmSync(invalidPath, { force: true });
  }
}

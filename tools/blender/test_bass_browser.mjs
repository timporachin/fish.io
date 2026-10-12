import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { chromium } from '@playwright/test';

const mime = new Map([
  ['.html', 'text/html; charset=utf-8'], ['.js', 'text/javascript; charset=utf-8'], ['.mjs', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'], ['.glb', 'model/gltf-binary'], ['.png', 'image/png'], ['.jpg', 'image/jpeg'], ['.jpeg', 'image/jpeg'],
]);
const EXPECTED_EMBEDDED_IMAGE_COUNT = 5;

export async function runBassBrowserChecks({ repo, input, invalidBytes }) {
  const screenshotPath = path.join(path.dirname(input), 'largemouth-bass-browser.png');
  const screenshot = path.relative(repo, screenshotPath);
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
    assert.ok(metrics.drawCalls <= metrics.primitiveCount,
      `Renderer made extra material passes beyond the exported primitives: ${metrics.drawCalls} calls for ${metrics.primitiveCount} primitives`);
    assert.ok(metrics.triangles > 0, 'Three.js rendered no triangles');
    assert.ok(metrics.drawCalls < 100, `Asset draw calls exceed the provisional 100-call budget: ${metrics.drawCalls}`);
    assert.ok(metrics.triangles < 150000, `Asset triangles exceed the provisional 150k budget: ${metrics.triangles}`);
    assert.ok(metrics.bounds.every(Number.isFinite) && metrics.bounds.every((value) => value > 0), `Invalid bounds dimensions: ${metrics.bounds}`);
    assert.ok(metrics.bounds[0] >= 0.35 && metrics.bounds[0] <= 0.55,
      `Expected an authored largemouth bass length near 0.45 m, found local X=${metrics.bounds[0]} m`);
    assert.ok(metrics.bounds[0] > metrics.bounds[1] * 1.3 && metrics.bounds[0] > metrics.bounds[2] * 1.3,
      `Expected the bass length on local X to exceed depth and height: ${metrics.bounds}`);
    assert.equal(metrics.animationClips, 0, 'Unexpected animation clips loaded in Three.js');
    assert.equal(metrics.skinnedMeshCount, 0, 'Unexpected skinned meshes loaded in Three.js');
    assert.ok(metrics.bodyPbrMaterialFound, 'No material uses base-color, normal, and roughness maps together');
    assert.ok(metrics.clearcoatMaterials.some(({ type, clearcoat }) => type === 'MeshPhysicalMaterial' && Number.isFinite(clearcoat) && clearcoat > 0),
      `Expected a positive glTF clearcoat material: ${JSON.stringify(metrics.clearcoatMaterials)}`);
    assert.ok(metrics.bodyPbrClearcoatMaterials.some(({ type, clearcoat }) => type === 'MeshPhysicalMaterial' && clearcoat > 0),
      `Expected positive clearcoat on a fully mapped body PBR material: ${JSON.stringify(metrics.bodyPbrClearcoatMaterials)}`);
    assert.ok(metrics.transparentMaterialCount > 0, 'No transparent fin material survived glTF export');
    assert.ok(metrics.materials.filter(({ transparent }) => transparent).every(({ side }) => side === 'front'),
      `Closed fin membranes should export single-sided materials: ${JSON.stringify(metrics.materials.filter(({ transparent }) => transparent))}`);
    assert.equal(metrics.decodedImages.length, EXPECTED_EMBEDDED_IMAGE_COUNT,
      'Expected three body maps, one fin map, and one shared pectoral/iris atlas to decode');
    assert.ok(metrics.decodedImages.every(({ decoded }) => decoded), 'A referenced texture image was not decoded');
    assert.ok(metrics.decodedImages.every(({ width, height }) => width > 0 && height > 0), 'A decoded texture has invalid dimensions');
    const irisMaterial = metrics.materials.find(({ name }) => name === 'Bronze iris - narrow gold pupil border');
    const pectoralMaterial = metrics.materials.find(({ name }) => name === 'Amber pectoral membrane');
    assert.ok(irisMaterial && pectoralMaterial && irisMaterial.baseColorImage &&
      irisMaterial.baseColorImage === pectoralMaterial.baseColorImage,
    'Iris and pectoral materials did not resolve to the same decoded atlas');
    const atlas = metrics.decodedImages.find(({ map }) => map === irisMaterial.baseColorImage);
    assert.ok(atlas && atlas.width === 512 && atlas.height === 512 && atlas.roles.includes('baseColor'),
      'Expected a decoded 512 × 512 shared pectoral/iris base-color atlas');
    // PNG pixel rows are top-down; Blender's UV V coordinates run bottom-up.
    assert.deepEqual(atlas.irisTileSample?.region, [0, 0, 128, 128], 'Iris tile sample has wrong pixel bounds');
    assert.ok(atlas.irisTileSample.innerSamples > 0 && atlas.irisTileSample.goldRingSamples > 0 &&
      atlas.irisTileSample.minSampledAlpha >= 0.99 &&
      atlas.irisTileSample.goldRingMean[0] - atlas.irisTileSample.innerMean[0] > 0.08 &&
      atlas.irisTileSample.goldRingMean[1] - atlas.irisTileSample.innerMean[1] > 0.06,
    `128 × 128 iris tile lacks an opaque bronze/gold radial ring: ${JSON.stringify(atlas.irisTileSample)}`);
    const irisUv = metrics.materialUvBounds.filter(({ material }) => material === irisMaterial.name);
    const pectoralUv = metrics.materialUvBounds.filter(({ material }) => material === pectoralMaterial.name);
    assert.ok(irisUv.length > 0 && pectoralUv.length > 0, 'Iris or pectoral geometry has no UV bounds');
    assert.ok(irisUv.every(({ min, max }) => min[0] >= 0 && max[0] <= 0.25 && min[1] >= 0 && max[1] <= 0.25),
      `Iris UVs leave the 128 × 128 atlas tile: ${JSON.stringify(irisUv)}`);
    assert.ok(pectoralUv.every(({ min, max }) => min[0] >= 0 && max[0] <= 1 && min[1] >= 0.25 && max[1] <= 1),
      `Pectoral UVs leave the 512 × 384 atlas region: ${JSON.stringify(pectoralUv)}`);
    assert.ok(metrics.decodedImages.every(({ width, height }) => width <= 2048 && height <= 2048), 'A decoded texture exceeds the 2048px budget');
    const normalSamples = metrics.decodedImages.filter(({ normalSample }) => normalSample).map(({ normalSample }) => normalSample);
    assert.ok(normalSamples.length > 0, 'No decoded normal map was sampled');
    assert.ok(normalSamples.every(({ mean: [x, y, z] }) => Math.abs(x - 0.5) <= 0.1 && Math.abs(y - 0.5) <= 0.1 && z > 0.85),
      `Normal map channels look gamma-skewed or invalid: ${JSON.stringify(normalSamples)}`);
    const transparentImages = new Set(metrics.materials.filter(({ transparent }) => transparent).map(({ baseColorImage }) => baseColorImage).filter(Boolean));
    const transparentAlpha = metrics.decodedImages.filter(({ map, alphaSample }) => transparentImages.has(map) && alphaSample)
      .map((image) => ({ map: image.map, alphaSample: image.map === atlas.map ? image.pectoralAlphaSample : image.alphaSample }));
    assert.ok(transparentAlpha.length > 0, 'Transparent materials have no decoded base-color alpha samples');
    assert.ok(transparentAlpha.every(({ alphaSample }) => alphaSample.nonZeroSamples > 0 &&
      alphaSample.nonZeroMean >= 0.45 && alphaSample.nonZeroMean <= 0.73),
    `Fin nonzero alpha samples outside the expected translucent range: ${JSON.stringify(transparentAlpha.map(({ map, alphaSample }) => ({ map, alphaSample })))}`);
    assert.deepEqual(pageErrors, [], `Browser page errors: ${pageErrors.join('; ')}`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(JSON.stringify({ check: 'threejs-browser-load', ...metrics, screenshot }, null, 2));

    await page.goto(`http://127.0.0.1:${port}/tools/blender/viewer.html?model=/artifacts/c1/.bass-invalid-test.glb`, { waitUntil: 'load' });
    await page.waitForFunction(() => window.__bassState?.status === 'error', null, { timeout: 15000 });
    const failure = await page.evaluate(() => window.__bassState.error);
    assert.ok(failure, 'Three.js did not report the corrupt GLB load failure');
    console.log(`BROWSER_NEGATIVE_OK corrupt GLB rejected (${failure})`);
    return { ...metrics, screenshot, negativeLoaderError: failure };
  } finally {
    await browser?.close();
    await new Promise((resolve) => server.close(resolve));
    fs.rmSync(invalidPath, { force: true });
  }
}

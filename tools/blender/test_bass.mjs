import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import validator from 'gltf-validator';
import { runBassBrowserChecks } from './test_bass_browser.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const input = path.resolve(process.argv[2] || path.join(repo, 'artifacts/c1/largemouth-bass.glb'));
const EXPECTED_EMBEDDED_IMAGE_COUNT = 5;

function parseGlb(bytes, label = input) {
  assert.equal(bytes.toString('ascii', 0, 4), 'glTF', `${label}: bad GLB magic`);
  assert.equal(bytes.readUInt32LE(4), 2, `${label}: expected GLB v2`);
  assert.equal(bytes.readUInt32LE(8), bytes.length, `${label}: header length mismatch`);
  const jsonLength = bytes.readUInt32LE(12);
  assert.ok(jsonLength > 0 && 20 + jsonLength <= bytes.length, `${label}: missing JSON chunk`);
  assert.equal(bytes.readUInt32LE(16), 0x4e4f534a, `${label}: first chunk is not JSON`);
  return JSON.parse(bytes.toString('utf8', 20, 20 + jsonLength).trim());
}

function inspectDocument(document, label = input) {
  assert.equal(document.asset?.version, '2.0', `${label}: expected glTF 2.0`);
  assert.ok((document.scenes?.length ?? 0) > 0, `${label}: no scene`);
  assert.equal(document.animations?.length ?? 0, 0, `${label}: fish asset should not contain animation clips`);
  assert.equal(document.skins?.length ?? 0, 0, `${label}: C1 model should not contain skins`);
  assert.ok(!(document.nodes ?? []).some((node) => node.skin !== undefined), `${label}: a node unexpectedly references a skin`);
  assert.equal(document.cameras?.length ?? 0, 0, `${label}: fish asset should not include cameras`);
  assert.ok(!(document.nodes ?? []).some((node) => node.camera !== undefined || node.extensions?.KHR_lights_punctual),
    `${label}: fish asset should not include cameras or lights`);
  assert.ok(!(document.extensionsUsed ?? []).includes('KHR_lights_punctual'), `${label}: fish asset should not include lighting extensions`);
  assert.ok((document.meshes?.length ?? 0) > 0, `${label}: no meshes`);
  let primitives = 0;
  let vertices = 0;
  let triangles = 0;
  for (const mesh of document.meshes ?? []) {
    for (const primitive of mesh.primitives ?? []) {
      primitives++;
      assert.equal(primitive.mode ?? 4, 4, `${label}: expected triangle-list primitives`);
      const positionIndex = primitive.attributes?.POSITION;
      assert.ok(Number.isInteger(positionIndex), `${label}: primitive has no POSITION accessor`);
      assert.ok(primitive.attributes?.JOINTS_0 === undefined && primitive.attributes?.WEIGHTS_0 === undefined,
        `${label}: C1 model should not contain skinning vertex attributes`);
      const vertexCount = document.accessors?.[positionIndex]?.count ?? 0;
      const indexCount = primitive.indices === undefined
        ? vertexCount
        : document.accessors?.[primitive.indices]?.count ?? 0;
      vertices += vertexCount;
      triangles += Math.floor(indexCount / 3);
    }
  }
  assert.ok(primitives > 0 && vertices > 0 && triangles > 0, `${label}: empty mesh geometry`);
  assert.ok((document.materials?.length ?? 0) > 0, `${label}: no materials`);
  assert.equal(document.images?.length ?? 0, EXPECTED_EMBEDDED_IMAGE_COUNT,
    `${label}: expected three body maps, one fin map, and one shared pectoral/iris atlas`);
  const materialByName = (name) => document.materials.find((material) => material.name === name);
  const iris = materialByName('Bronze iris - narrow gold pupil border');
  const pectoral = materialByName('Amber pectoral membrane');
  assert.ok(iris && pectoral, `${label}: missing atlas iris or pectoral material`);
  const irisTexture = iris.pbrMetallicRoughness?.baseColorTexture?.index;
  const pectoralTexture = pectoral.pbrMetallicRoughness?.baseColorTexture?.index;
  assert.ok(Number.isInteger(irisTexture) && Number.isInteger(pectoralTexture),
    `${label}: iris and pectoral must each reference a base-color atlas texture`);
  const atlasImageIndex = document.textures?.[irisTexture]?.source;
  assert.ok(Number.isInteger(atlasImageIndex) && document.images?.[atlasImageIndex] &&
    document.textures?.[pectoralTexture]?.source === atlasImageIndex,
    `${label}: iris and pectoral texture samplers do not resolve to the same embedded atlas image`);
  return { nodes: document.nodes?.length ?? 0, meshes: document.meshes.length, primitives, vertices, triangles,
    materials: document.materials?.length ?? 0, embeddedImages: document.images?.length ?? 0,
    sharedPectoralIrisAtlasImage: atlasImageIndex };
}

async function validate(bytes, uri) {
  return validator.validateBytes(new Uint8Array(bytes), { uri, maxIssues: 1000, ignoredIssues: [] });
}

assert.ok(fs.existsSync(input), `Expected generated GLB at ${input}`);
const bytes = fs.readFileSync(input);
const document = parseGlb(bytes);
const structure = inspectDocument(document);
const report = await validate(bytes, input);
const { numErrors, numWarnings, numInfos, numHints } = report.issues;
console.log(JSON.stringify({ check: 'gltf-validator', uri: input, version: '2.0.0-dev.3.10', numErrors, numWarnings, numInfos, numHints }, null, 2));
assert.equal(numErrors, 0, `Pinned gltf-validator reported errors: ${JSON.stringify(report.issues.messages.filter((message) => message.severity === 0))}`);
console.log(JSON.stringify({ check: 'glb-structure', ...structure }, null, 2));

// Keep negative cases independent of the generated model: reject corrupt container bytes and semantic regressions.
const corrupt = Buffer.from(bytes);
corrupt[0] = 0;
const invalidPath = path.join(os.tmpdir(), `fish-io-invalid-${process.pid}.glb`);
try {
  fs.writeFileSync(invalidPath, corrupt);
  let rejected = false;
  try {
    const invalidReport = await validate(corrupt, invalidPath);
    rejected = invalidReport.issues.numErrors > 0;
  } catch {
    rejected = true;
  }
  assert.ok(rejected, 'Corrupt GLB unexpectedly passed pinned validation');
} finally {
  fs.rmSync(invalidPath, { force: true });
}
assert.throws(() => inspectDocument({ ...document, animations: [{ channels: [], samplers: [] }] }, 'negative-animation-case'), /should not contain animation/);
assert.throws(() => inspectDocument({ ...document, skins: [{ joints: [0] }] }, 'negative-skin-case'), /should not contain skins/);
assert.throws(() => inspectDocument({ ...document, meshes: [] }, 'negative-empty-mesh-case'), /no meshes/);
const pectoralTextureIndex = document.materials.find(({ name }) => name === 'Amber pectoral membrane')
  .pbrMetallicRoughness.baseColorTexture.index;
const wrongAtlasTextures = document.textures.map((texture, index) => index === pectoralTextureIndex
  ? { ...texture, source: (texture.source + 1) % document.images.length } : texture);
assert.throws(() => inspectDocument({ ...document, textures: wrongAtlasTextures }, 'negative-atlas-case'),
  /do not resolve to the same embedded atlas image/);
console.log('NEGATIVE_CASES_OK corrupt container, unexpected animation, unexpected skin, empty mesh, and split atlas rejected');

const browser = await runBassBrowserChecks({ repo, input, invalidBytes: corrupt });
const blendInput = input.replace(/\.glb$/i, '.blend');
assert.ok(fs.existsSync(blendInput), `Expected authored Blender file at ${blendInput}`);
const blender = process.env.BLENDER_BIN || 'blender';
const geometryReportPath = path.join(path.dirname(blendInput), 'blender-geometry-validation.json');
fs.rmSync(geometryReportPath, { force: true });
const geometryRun = spawnSync(blender, [
  '--background', blendInput,
  '--python-exit-code', '1',
  '--python', path.join(here, 'validate_bass_geometry.py'),
], { cwd: here, encoding: 'utf8' });
if (geometryRun.stdout) process.stdout.write(geometryRun.stdout);
if (geometryRun.stderr) process.stderr.write(geometryRun.stderr);
if (geometryRun.error) throw geometryRun.error;
assert.equal(geometryRun.status, 0, `Independent Blender geometry validation exited ${geometryRun.status}`);
assert.ok(fs.existsSync(geometryReportPath), 'Independent Blender geometry validator produced no fresh report');
const geometry = JSON.parse(fs.readFileSync(geometryReportPath, 'utf8'));
assert.equal(geometry.failures.length, 0, 'Independent Blender geometry report contains failures');
const evidence = {
  source: ['tools/blender/generate_bass.py', 'tools/blender/bass_materials.py'].map((relativePath) => {
    const sourceBytes = fs.readFileSync(path.join(repo, relativePath));
    return { path: relativePath, bytes: sourceBytes.length, sha256: createHash('sha256').update(sourceBytes).digest('hex') };
  }),
  asset: {
    path: path.relative(repo, input),
    bytes: fs.statSync(input).size,
    sha256: createHash('sha256').update(bytes).digest('hex'),
  },
  blenderAsset: {
    path: path.relative(repo, blendInput),
    bytes: fs.statSync(blendInput).size,
    sha256: createHash('sha256').update(fs.readFileSync(blendInput)).digest('hex'),
  },
  validator: { package: 'gltf-validator', version: '2.0.0-dev.3.10', numErrors, numWarnings, numInfos, numHints },
  structure,
  browser,
  geometryReport: path.relative(repo, geometryReportPath),
  negativeCases: ['corrupt GLB rejected by validator', 'unexpected animation rejected', 'unexpected skin rejected',
    'empty mesh rejected', 'split atlas rejected', 'corrupt GLB rejected by Three.js loader'],
};
const evidencePath = path.join(path.dirname(input), 'browser-validation.json');
fs.writeFileSync(evidencePath, `${JSON.stringify(evidence, null, 2)}\n`);
console.log(`VALIDATION_EVIDENCE ${path.relative(repo, evidencePath)}`);

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../..');
const artifact = path.join(repo, 'artifacts', 'blender-smoke-fixture.glb');
const blender = process.env.BLENDER_BIN || 'blender';
fs.mkdirSync(path.dirname(artifact), { recursive: true });

const run = (command, args, options = {}) => {
  const result = spawnSync(command, args, { cwd: here, encoding: 'utf8', ...options });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  return result;
};

const version = run(blender, ['--version']);
if (version.status !== 0 || !version.stdout.startsWith('Blender 4.3.2\n')) throw new Error('Blender 4.3.2 is required for reproducible C0 validation');
fs.rmSync(artifact, {force:true});
const exported = run(blender, ['--background', '--python', path.join(here, 'export_smoke_fixture.py'), '--', artifact]);
if (exported.error) throw exported.error;
if (exported.status !== 0 || !fs.existsSync(artifact)) throw new Error(`Blender export failed (status ${exported.status})`);
// Confirm that the exporter retained both named nodes and a real animation clip.
const glb = fs.readFileSync(artifact);
if (glb.toString('ascii', 0, 4) !== 'glTF') throw new Error('Smoke output is not a GLB');
const jsonLength = glb.readUInt32LE(12);
const document = JSON.parse(glb.toString('utf8', 20, 20 + jsonLength).trim());
const nodeNames = new Set((document.nodes ?? []).map((node) => node.name));
if (!nodeNames.has('Validation_Cube') || !nodeNames.has('Validation_Animated_Beacon')) {
  throw new Error('Expected named non-fish fixture nodes are missing');
}
if (!document.animations?.length || !document.animations[0].channels?.length) {
  throw new Error('Expected animated fixture channels are missing');
}
console.log(`GLB_CONTENT_OK nodes=${document.nodes.length} animations=${document.animations.length} channels=${document.animations[0].channels.length}`);
const validation = run(process.execPath, [path.join(here, 'validate_glb.mjs'), artifact]);
if (validation.status !== 0) throw new Error('Valid smoke fixture did not pass gltf-validator');

// Negative case: a GLB magic/header corruption must fail validation.
const invalid = path.join(repo, 'artifacts', 'blender-smoke-invalid.glb');
const bytes = fs.readFileSync(artifact);
bytes[0] = 0;
fs.writeFileSync(invalid, bytes);
const rejected = run(process.execPath, [path.join(here, 'validate_glb.mjs'), invalid]);
if (rejected.status === 0) throw new Error('Corrupt GLB unexpectedly passed validation');
console.log('NEGATIVE_VALIDATION_OK corrupt GLB rejected');

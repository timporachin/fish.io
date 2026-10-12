import fs from 'node:fs';
import path from 'node:path';
import validator from 'gltf-validator';

const input = process.argv[2];
if (!input) {
  console.error('Usage: npm run validate -- <file.glb>');
  process.exit(2);
}
const uri = path.resolve(input);
try {
  const bytes = new Uint8Array(fs.readFileSync(uri));
  const report = await validator.validateBytes(bytes, {
    uri,
    maxIssues: 1000,
    ignoredIssues: [],
  });
  const { numErrors, numWarnings, numInfos, numHints } = report.issues;
  console.log(JSON.stringify({ uri, validatorVersion: '2.0.0-dev.3.10', numErrors, numWarnings, numInfos, numHints }, null, 2));
  if (numErrors > 0) {
    console.error(JSON.stringify(report.issues.messages.filter((message) => message.severity === 0), null, 2));
    process.exit(1);
  }
} catch (error) {
  console.error(`GLB validation failed: ${error?.message ?? JSON.stringify(error)}`);
  process.exit(1);
}

# C1 executed verification evidence

Executed in `/workspace/fish.io`, cloud Debian environment, 2026-10-12 UTC. Blender 4.3.2; Node 24.19.0; npm 11.9.0; pinned Three.js 0.180.0, Playwright 1.56.1 and gltf-validator 2.0.0-dev.3.10. Chromium uses SwiftShader, not an iPhone GPU.

| Check | Executed result |
| --- | --- |
| `npm ci` and `npm ci --prefix tools/blender` | Locked installations pass |
| `npm run build` | Strict TypeScript / Vite production build passes; C0 app preserved |
| `npm test` | 6 C0 unit tests pass |
| `npm run test:e2e` | 2 C0 browser tests pass, including context recovery |
| `npm run smoke --prefix tools/blender` | C0 animated non-fish fixture exports and validates with 0 errors/warnings; corrupt GLB rejected |
| `blender --background --python-exit-code 1 --python tools/blender/generate_bass.py -- --output-dir artifacts/c1` | Final seed-1947 Blender source, GLB and all six 1200 × 800 / 64-sample Cycles renders produced |
| `npm run test:bass --prefix tools/blender` | Final C1 export, browser and independent authored-geometry checks pass |
| Khronos GLB validator | 0 errors, 0 warnings, 18 informational messages |
| Actual Three.js load | 11 draws, 10,976 triangles; no clips/skins; five embedded images decoded; body color/normal/roughness PBR slots present |
| Normal-image serialized pixel check | 4,096 sampled pixels; mean channels ~[0.50003, 0.50004, 0.99995], rejecting neutral-normal gamma skew |
| Independent Blender inspection | 24 anatomical objects, no failures; closed outward body/jaw/fin/ray volumes, consistent shared-edge winding; finite vertices/UVs/normals; no loose geometry, zero-area faces or >2-face edges |
| Negative cases | Corrupt GLB rejected by validator and loader; empty geometry, unexpected clips/skins, missing fin, loose vertex and inconsistent winding rejected |
| Final visual review | All six views and exported-model browser screenshot inspected by root/modeler/Astra; Astra recommends changes for production realism, not acceptance |

The final camera-only reconciliation with the concurrent game-design document regenerated all six views (five orthographic; front three-quarter perspective at 60 mm), then the full C1 suite passed again. Geometry costs remain unchanged.

Final GLB SHA-256: `851052321895192dad228db459a43a3787f4a9538d59b835e2b30654b46b0865`.

Final `.blend` SHA-256: `384f0c75fd6367fdfb45f6370d6c8ed96426ed38fa8cc31913dfd4d7542537f2`.

Machine reports and render hashes are retained in [evidence/c1](evidence/c1/manifest.json); source statistics and independent validation use different boundary/nonmanifold terminology explained in [modeling notes](C1_MODELING.md).

No physical iPhone, Safari, skinning, jaw-opening deformation, animation loop or thermal/memory endurance tests occurred. Automated validation does not prove biological accuracy, every self-intersection, realistic appearance, or achieved device budgets. The retained PNGs are evidence for one frozen candidate; generated Blender/GLB/texture binaries remain ignored and are reproducible from source. Existing GitHub CI continues to check C0; Blender/C1 asset checks ran in this cloud and are not provisioned in CI. C2 and merge remain gated on the user.

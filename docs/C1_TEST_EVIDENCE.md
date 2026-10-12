# C1 executed verification evidence

> Historical rework evidence: the measurements and six-view gallery below describe an earlier unaccepted checkpoint. The targeted jaw reconstruction is now in progress; see [PROJECT_STATE](../PROJECT_STATE.md), [jaw references](C1_JAW_REFERENCES.md) and [independent jaw review](C1_JAW_REVIEW.md). Do not attribute these earlier metrics to the current candidate.


Executed in `/workspace/fish.io` on 2026-10-12 UTC with Blender 4.3.2, Node 24.19.0, npm 11.9.0, Three.js 0.180.0, Playwright 1.56.1, and `gltf-validator` 2.0.0-dev.3.10. The browser proof used Chromium with SwiftShader, not an iPhone GPU.

The C0 checks were rerun against the existing app after the C1 rework. They pass without edits to the main app:

| Check | Result |
| --- | --- |
| `npm run build` | TypeScript and Vite production build pass |
| `npm test` | 6 unit tests pass |
| `npm run test:e2e` | 2 Playwright tests pass, including context recovery |
| `npm run smoke --prefix tools/blender` | Animated fixture exports; pinned validator reports 0 errors and 0 warnings; corrupt fixture is rejected |

The frozen C1 candidate was tested with `npm run test:bass --prefix tools/blender`:

| Check | Result |
| --- | --- |
| Khronos GLB validator | 0 errors, 0 warnings, 16 informational messages |
| GLB structure | 1 node, 1 mesh, 10 primitives/materials, 11,028 vertices, 14,326 triangles, 5 embedded images; no animation clips, skins, cameras, lights, or skinning attributes |
| Three.js browser load | 10 mesh objects and draw calls; 14,326 rendered triangles; no animation clips or skinned meshes; bounds 0.45202 × 0.21055 × 0.11201 m |
| Texture decode | Five embedded images decoded: 1024² body color, normal and roughness/metalness maps; 512² olive and amber fin color/alpha maps |
| Normal map samples | 4,096 decoded pixels, mean RGB channels [0.499997, 0.503355, 1.0] |
| Fin alpha samples | 1,024 pixels per map; olive mean 0.5826 (range 0.4784–0.6980), amber mean 0.5526 (range 0.4510–0.6667) |
| PBR material proof | Skin is `MeshPhysicalMaterial` with base-color, normal, roughness and metalness maps; exported clearcoat 0.02 and clearcoat roughness 0.24. Both transparent fin materials are single-sided; 10 calls match 10 primitives. |
| Independent Blender geometry check | 18 source meshes; every mesh is closed and outward-wound per connected component. Body has one connected component, zero boundary/nonmanifold/inconsistent-winding/zero-area/invalid-normal-or-vertex/invalid-UV/loose-vertex counts. Face-domain integer `anatomical_region` has torso/upper/lower regions (0/1/2), all nonempty and connected across shared edges. |
| Negative cases | Corrupt GLB rejected by validator and Three.js; empty mesh, unexpected animation/skin, missing fin, missing jaw labels, loose vertex, and inconsistent winding rejected |

The independent geometry checker does not detect self-intersections or prove anatomical accuracy. Positive component signed volume checks winding, not every local surface detail. Browser results are from SwiftShader and do not qualify physical iPhone/Safari performance, thermal behavior, or memory residency. Automated checks do not prove visual acceptance or deformable jaw quality. The final six-view visual review and user approval remain separate from these machine checks; C2 and merge remain gated on the user.

Machine-readable reports and rendered evidence are retained under [evidence/c1](evidence/c1/manifest.json), including the browser screenshot, GLB/browser metrics, independent Blender report, and six model views. The exact ignored working artifacts are identified by hashes:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `artifacts/c1/largemouth-bass.glb` | 3,513,480 | `ed28f05b0114ebcb7f92079d698f4edcdee7cd47f3e656158ac88d9d19cc9371` |
| `artifacts/c1/largemouth-bass.blend` | 4,478,332 | `54f7f280127d3571509a624c02d364d92e1e7772c173945be998f39b9a1c942c` |
| `tools/blender/generate_bass.py` | 28,562 | `a0239183ea81be3c71844831fffdc6d20becb6d7ae09f2a85fb72ffba50f1036` |
| `tools/blender/bass_materials.py` | 10,819 | `cfdd172f4de0b7632bf3e6a6b3a8eed8935ef8124de1e2c76dae274f1522ba6f` |

The working Blender and GLB binaries remain ignored and reproducible from source. C1 asset checks run in this environment and are not provisioned in existing C0 CI.

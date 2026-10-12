# C0 architecture

## Direction

Visual thesis: a quiet underwater shelf with sediment, depth fog, pale light shafts, and a restrained interface over the full viewport.
Content plan: habitat identity, scene, pause control, species showroom, and portrait rotation guidance.
Interaction thesis: slow camera drift and suspended particles establish depth; pause stops simulation; a native modal opens the showroom with keyboard dismissal and focus containment. Reduced motion freezes visual drift.

## Boundaries

| Module | Responsibility |
| --- | --- |
| `src/main.ts` | DOM controls, browser lifecycle, simulation/render composition |
| `src/simulation/` | versioned JSON state, immutable fixed-tick reducer, seeded PRNG, strict save validation, bounded clock |
| `src/ai/` | deterministic per-fish movement/energy updates; future steering boundary |
| `src/progression/` | XP and unlock policy foundation |
| `src/habitats/` | habitat definitions and membership |
| `src/showroom/` | unlocked species selection helpers; asset inspection boundary |
| `src/rendering/` | Three.js scene and resource ownership; no gameplay decisions |
| `tools/blender/` | headless export fixture and GLB validation, independent from browser bundle |

The browser creates an empty seeded state and runs 30 Hz simulation ticks. RAF supplies elapsed seconds, clamped to [0, 0.25]; FixedClock advances at most five ticks per frame. Excess whole ticks are discarded after stalls, so wall-clock time is deliberately not authoritative. Determinism means the same initial state and tick-indexed actions produce the same state, with equivalent normal frame partitions. RNG state lives in the save. JSON serialization excludes renderer objects and clock fractions. Save restoration resumes at a tick boundary; persistent storage and save migration UI are outside C0. Hidden pages pause simulation and reset the elapsed-time baseline on return.

Fish actions and progression are foundation contracts, exercised by tests but not exposed in the C0 interface. No fish models or proxy fish appear in the scene. GLB loading, AnimationMixer playback, instancing/skinning choices and asset catalog integration follow C1 approval.

## Rendering and mobile constraints

Single WebGL2 renderer, perspective camera, fog, a lit sand mesh, instanced rock geometry, additive light planes and a single particle draw. Pixel ratio is capped at 1.5; antialiasing and real-time shadows are disabled. Geometry/materials are disposed on page exit. WebGL context loss suspends drawing; restored resources resume via Three.js. No external fonts/textures or network assets are required.

Landscape 852 × 393 CSS pixels is the automated reference. Controls are at least 44 CSS pixels high with safe-area offsets and viewport-fit=cover. Portrait gets rotation guidance without requesting orientation lock. Native dialog supports Escape. This is a layout target, not an iPhone compatibility claim.

Provisional C1 budgets: 60 fps target on selected physical iPhone, 30 fps fallback, <=100 draw calls, <=150k visible triangles, <=128 MiB texture residency, species LODs near 8k/3k/1k triangles, <=24 deform bones, 1k textures initially. Measure and revise on device before calling these achieved. No benchmark from cloud SwiftShader predicts device performance.

## Reproducibility

Exact direct dependency pins and committed npm lockfiles; `npm ci` in CI. Node/npm are explicitly recorded. Blender version and Debian package are recorded separately; the fixture fails on a different Blender version. Generated Blender/GLB asset binaries and dependencies remain ignored; C1 retains review PNGs and reports as documented below. CI validates build, simulation and browser behavior; Blender is a documented cloud check, not provisioned in GitHub CI. No deployment is configured in C0.


## C1 tooling addition

The C0 application boundaries are preserved. `tools/blender/generate_bass.py` authors a candidate with separate anatomical parts and exports a joined mesh with material primitives. The isolated viewer and asset tests prove loading in Three.js without adding a model to the gameplay scene. Generated Blender/GLB/texture binaries remain ignored; six reference PNGs and the runtime screenshot/reports are retained under `docs/evidence/c1/` as an explicit review-evidence exception. Read [game design](GAME_DESIGN.md), [C1 modeling](C1_MODELING.md) and [independent review](C1_REVIEW.md) for the visual gate and unqualified mobile/deformation limits.

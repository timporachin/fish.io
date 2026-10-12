# FISH.IO

C0 foundation: Three.js underwater habitat, TypeScript simulation, Vite build, Vitest, Playwright, and Blender headless GLB validation. C1 adds a reproducible largemouth bass modeling candidate and isolated asset validation. User visual approval remains pending; the gameplay scene is preserved.

## Run

Use Node 24.19.0 and npm 11.9.0 (`.node-version`).

```sh
npm ci
npm run dev
npm run build
npm test
npm run test:e2e
cd tools/blender
npm ci
npm run smoke
```

Browser tests use cloud `/usr/bin/chromium` by default. For another installed executable set `CHROMIUM_PATH`; CI installs the Playwright-managed Chromium. Blender smoke requires Blender 4.3.2 (Debian package `4.3.2+dfsg-2` tested). Generated outputs are ignored in `artifacts/`, `dist/`, and test report directories.

See [project state](PROJECT_STATE.md), [architecture](docs/ARCHITECTURE.md), [roadmap](docs/ROADMAP.md), [asset pipeline](docs/BLENDER_PIPELINE.md), [C0 test evidence](docs/TEST_EVIDENCE.md), and [C1 modeling and approval](docs/C1_MODELING.md). C2 requires C1 visual approval and further authorization.

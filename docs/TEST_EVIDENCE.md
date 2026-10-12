# C0 executed test evidence

Executed in `/workspace/fish.io`, Debian 13.6 cloud environment, 2026-10-12 UTC. No desktop files were used.

| Check | Actual result |
| --- | --- |
| `npm ci` | clean locked dependency installation succeeds |
| `npm run build` | TypeScript strict check + Vite 7.3.7 production build succeeds |
| `npm test` | Vitest 5.0.3: 6 tests pass |
| `npm run test:e2e` | Playwright 1.56.1, system Chromium 154.0.8037.57: 2 tests pass |
| `npm audit --audit-level=moderate` | 0 vulnerabilities after updating Vite/Vitest pins |
| `npm ci --prefix tools/blender` | locked validator installation succeeds |
| `npm run smoke --prefix tools/blender` | Blender 4.3.2 headless export succeeds; 2 nodes, 1 clip, 2 channels; validator 0 errors, 0 warnings, 2 informational messages; corrupted GLB rejected |

Simulation evidence covers deterministic populated state replay, seeded RNG continuation after save/load, strict save rejection, inherited-property species regression, purchase/feed policy, equivalent frame partitions, pause/reset and bounded catch-up. Render evidence covers actual WebGL draw calls, advancing ticks, pause/resume, showroom open/close, portrait guidance, overflow, no page errors, and explicit WebGL context loss followed by restoration and resumed drawing.

The landscape screenshot is generated at `artifacts/landscape-chromium.png` (852 × 393 CSS pixels). It was opened and visually inspected. It shows the submerged terrain, fogged rocks, light shafts and legible landscape controls. The screenshot and GLBs are intentionally ignored, reproducible outputs. Chromium uses SwiftShader in these tests; GPU quality/performance on iPhone is untested. Browser contexts are desktop Chromium at mobile-size viewports, not Safari or physical iPhones.

Production output at this check: JS ~489.49 kB / 124.41 kB gzip, CSS ~1.96 kB / 0.85 kB gzip. This is a bundle measurement, not an achieved device frame-rate budget.

Astra final review identified an inherited-key lookup bug and two test weaknesses (empty-state replay and premature context recovery assertion). The lookup was guarded, a regression test added, replay populated with a fish state fixture, and recovery now awaits loss before restoration. Blender export fixtures are non-fish. Missing optional Draco library is logged by the exporter; compression is not requested and output validates.

CI configuration is committed but has not yet run on GitHub. Blender is verified locally in this cloud; its package installation is not part of GitHub CI. No real fish, deforming skin or production swimming rig has been generated or validated in C0.

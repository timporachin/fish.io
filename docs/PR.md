# C0: initialize cloud rendering and simulation foundation

Base: `main`. Head: `dev/c0-cloud-foundation`.

The previously empty project now builds a Three.js underwater habitat with landscape controls, modular seeded fixed-tick simulation and validated JSON state. Adds strict TypeScript/Vite setup, pinned locked dependencies, Vitest/Playwright checks and CI. Documents a realistic fish/rig asset pipeline and verifies Blender 4.3.2 headless animated GLB export using a non-fish fixture.

Validation: production build; 6 unit tests; 2 Chromium browser tests including explicit context recovery; dependency audit with 0 vulnerabilities; animated GLB validator with 0 errors/warnings and corrupt-file rejection. Generated screenshot, GLBs, dependencies and builds are ignored.

Limits: no physical iPhone/Safari validation, production fish assets or C1 modeling. CI has not run remotely. Uncompressed GLB only; optional Draco library unavailable. Full evidence: docs/TEST_EVIDENCE.md.

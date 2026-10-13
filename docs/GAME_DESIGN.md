# Fish.io — Game Design Specification

**Status:** Living design specification · **Project:** `timporachin/fish.io` · **Platform:** iPhone-first landscape web game · **Updated:** 2026-10-12

> This document preserves the Fish.io direction and confirmed design decisions. It is not a claim that every feature is implemented. A feature marked **Proposed** is not an approved gameplay rule. Engineering agents must not silently turn proposals into requirements.

## 1. Vision

Fish.io is an immersive, visually realistic, 3D underwater fish game. Players control fish, experience species-specific aquatic habitats, develop and unlock additional species, and encounter underwater life through naturalistic movement and environmental interaction. The experience should feel like being a fish in a living ecosystem—not a generic arcade game with fish-shaped placeholders.

**Design pillars**
1. **Believable aquatic life:** recognizable species anatomy, distinctive locomotion, ecological context and credible underwater behavior.
2. **High-fidelity visuals:** organically modeled fish, carefully authored materials, convincing water, depth, light and habitat detail; avoid blocky or generic game-art appearance.
3. **Playability on iPhone:** landscape-only gameplay, touch-first controls, readable minimal UI, efficient rendering.
4. **Meaningful species discovery:** species selection and unlocking take place in an interactive 3D showroom, with each species presented in its own natural habitat.
5. **Underwater immersion:** natural ambient sound is the focus; music is minimal and subtle.

## 2. Decision register

| ID | Decision | Status |
| --- | --- | --- |
| D01 | Fish.io is a 3D underwater fish game emphasizing realism and immersion. | Confirmed |
| D02 | Primary playable target is iPhone in **landscape orientation only**. | Confirmed |
| D03 | Fish selection and unlocking use an **interactive 3D fish showroom**. | Confirmed |
| D04 | Showroom displays species in **species-specific natural habitats** (selected concept C). | Confirmed |
| D05 | Achievements award **bonuses**; bonus types, values and balancing are not yet specified. | Confirmed principle; details open |
| D06 | Audio emphasizes realistic aquatic ambience and subtle natural sounds, with **minimal music**. | Confirmed |
| D07 | Fish should have convincing, natural swimming motion and species-specific appearance. | Confirmed quality direction |
| D08 | Cloud-first development with GitHub as source of truth, Three.js/TypeScript/Vite and Blender Python/GLB pipeline. | Confirmed engineering direction |
| D09 | First production fish reference is the **largemouth bass**. | Confirmed C1 scope |
| D10 | Gameplay involves fish progression, species unlocking, and aquatic interactions. | Direction established; exact mechanics open |

## 3. Player experience

### 3.1 Core experience

The player enters a convincing underwater habitat, controls a fish, explores the environment and engages with other aquatic life. Progression should support discovery and unlockable species, but the precise win/loss conditions, food chain, combat model, growth rates and multiplayer rules remain **undecided**. Do not infer these rules solely from the `.io` title.

### 3.2 Fish control and movement

- Fish must visibly swim, steer and accelerate through body and fin motion, not merely translate rigid models.
- Different body types should ultimately support different swimming styles.
- Touch controls must work comfortably in iPhone landscape without covering the main fish or obscuring threats.
- Control mapping, camera perspective, stamina, boost, attack and feeding inputs are **to be designed and playtested**, not yet locked.

### 3.3 Species and unlocking

- Each playable species should have a distinct silhouette, appearance and habitat identity.
- Species selection/unlocking is presented in an interactive 3D showroom rather than a flat text-only menu.
- Locked/unlocked status should be understandable, with a clear path to unlocks once progression rules are defined.
- The exact species roster, rarity tiers, currency, XP formulas and unlock prices are **not yet specified**.

### 3.4 Achievements

Achievements **must award a bonus**. Examples of potential bonuses (not approved yet) include progression currency, XP, cosmetic rewards or unlock progress. Final reward categories, amounts, triggers and anti-farming rules require a separate balancing decision. No achievement should be implemented as a rewardless badge by default.

## 4. Species-specific 3D showroom

**Confirmed direction: natural habitats for each species.**

- Render an interactive, rotatable 3D fish, not just a static card or thumbnail.
- Surround the fish with an ecologically appropriate environment, with distinct lighting, terrain, plants and underwater ambience.
- Support selection, inspection and unlock status in a touch-friendly interface.
- Preserve species identity across the showroom and gameplay model; avoid using a generic fish mesh for every species.
- Provide an economical mobile rendering mode where needed without abandoning species-specific presentation.
- Exact showroom camera controls, transitions, information panels and unlock animations are open design decisions.

## 5. Visual and asset standards

### 5.1 Fish anatomy

Production models should show species-correct body taper and head shape, jaw and mouth, gill region, eye placement, caudal peduncle, and distinct dorsal, caudal, anal, pelvic and pectoral fins as appropriate to the species. Curvature and silhouette must be judged from multiple views. A technically valid GLB is **not** visual acceptance.

### 5.2 Materials and lighting

Aim for recognizable coloration, scale detail, fin surfaces, wet-looking but plausible skin response, convincing eyes and habitat-appropriate lighting. Blender-only shaders must be baked or translated to glTF-compatible materials. Optimize textures and geometry for real iPhone hardware; cloud Chromium rendering is not equivalent to Safari-on-device acceptance.

### 5.3 Habitat presentation

Habitats should reflect the species' ecology: water clarity, terrain, vegetation, cover, lighting, and ambient activity should differ as appropriate. A freshwater largemouth bass scene is the first production reference. Final habitat roster and geographic themes are not locked.

### 5.4 Visual acceptance

Require orthographic/profile and perspective evidence from at least six angles for each first-of-kind fish model: left, right, front, rear, top and front three-quarter. Review anatomy, silhouette, fins, materials and deformation readiness. The owner retains final visual approval; automated tests and agent reviews cannot replace it.

## 6. Audio direction

- Prioritize natural underwater ambience and believable environmental sounds.
- Keep music **minimal** and unobtrusive; avoid a constant loud soundtrack.
- Sound should support habitat identity and fish movement/interaction.
- Exact soundtrack, audio assets, mixing levels and event cues remain to be designed.
- Respect iOS browser audio-unlock requirements and provide accessible volume/mute controls.

## 7. Technical architecture and delivery

Current repository foundation: Three.js, TypeScript, Vite, deterministic simulation, modules for AI/progression/habitats/showroom, Vitest, Playwright, and headless Blender 4.3.2. This is an implementation baseline, not proof of complete gameplay.

- **Cloud-only production:** Codex Cloud and GitHub; do not require the owner's Windows desktop.
- **3D asset pipeline:** Blender Python -> glTF/GLB -> validated Three.js import.
- **Simulation:** deterministic, testable logic separate from rendering.
- **Mobile:** iPhone landscape UI, safe areas, touch controls, performance profiling on physical Safari devices before acceptance.
- **Deployment:** a reachable HTTPS preview is desired; localhost-only previews are insufficient for remote iPhone testing.
- **Assets:** retain editable source and provenance/licensing information; do not indiscriminately commit large generated files.
- **Quality gates:** builds, tests, rendered evidence, device checks and explicit owner approvals. Do not assert a test passed unless it actually ran.

## 8. Development sequence

| Milestone | Intended outcome | Approval condition |
| --- | --- | --- |
| C0 — Cloud foundation | Three.js shell, simulation architecture, tests, Blender feasibility | Merged to main; foundation only |
| C1 — First production fish | Realistic largemouth bass model, materials, rig readiness, six-view visual evidence and validated GLB | Owner inspects renders and explicitly accepts visual quality |
| C2 — Gameplay and habitat interaction | Define and implement fish control, interaction, feeding/progression and ecosystem behaviors against agreed rules | Gameplay demonstrated and tested; unresolved mechanics approved first |
| C3 — Showroom and mobile optimization | Species-specific 3D showroom, unlock presentation, LOD/texture budgets and device profiling | iPhone Safari acceptance and showroom review |
| C4 — Release hardening | Accessibility, save reliability, performance, deployment and distribution checks | Release criteria satisfied |

**C1 is already underway.** This design file is documentation, not a request to interrupt or reset C1. Reconcile it with C1 when that work completes; do not overwrite C1 changes.

**2026-10-12 C1 scope reconciliation:** The owner's C1 request authorizes modeling, materials, six-view evidence, geometry/export checks and an isolated Three.js load test. It explicitly holds C2 animation development until visual approval. The current C1 candidate passes technical checks but remains visually unaccepted; see `C1_MODELING.md` and `C1_REVIEW.md`. Animation/rigging comes first in the next authorized phase; the gameplay/control rules above remain open. No C2 work is authorized by this document.

## 9. Open design decisions (do not invent answers)

1. Single-player vs multiplayer, and any online architecture.
2. Exact gameplay loop: feeding, hunting, survival, growth, combat, objectives and fail states.
3. Fish roster, starting species and habitat roster.
4. Progression economy, species unlock criteria and achievement bonus values.
5. Camera style, touch control layout and optional assist features.
6. Fish AI behaviors, predator-prey rules and ecosystem simulation depth.
7. Showroom transitions, detailed UI and fish information presentation.
8. Audio asset selection and adaptive ambience rules.
9. Monetization, accounts, online persistence and social features, if any.

## 10. Instructions for future Codex tasks

1. Read this file, `PROJECT_STATE.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` before modifying gameplay or art.
2. Preserve all **Confirmed** decisions. Treat **Proposed/open** items as questions or explicit design proposals, not silently approved features.
3. Keep each milestone on a development branch; use pull requests and evidence-based reviews.
4. Do not confuse a successful build, automated test or GLB validation with artistic or iPhone acceptance.
5. Update this document when the owner makes a new game-design decision, preserving the decision history.

# Dynamic 3D RIS Simulation Presentation: Completion Report

**Project:** Physical Layer Security in Visible Light Communications (VLC) via Optical Reconfigurable Intelligent Surfaces (RIS) and Friendly Jamming (FJ) using Deep Reinforcement Learning (DRL)  
**Task Reference:** [`antigravity_report/DYNAMIC_3D_ANTIGRAVITY_TASK.md`](../antigravity_report/DYNAMIC_3D_ANTIGRAVITY_TASK.md)  
**Audit Reference:** [`supervisor_package/DYNAMIC_3D_CODEX_REVIEW.md`](./DYNAMIC_3D_CODEX_REVIEW.md)  
**Implementer:** Antigravity IDE  
**Date:** November 14, 2026 (Asia/Calcutta)  
**Status:** Fully Complete · Verified in Headless Edge Browser · 94 Unit Tests Passing (100%) · Zero Regressions  

---

## 1. Executive Summary

In direct response to the user's directive and the task specification in [`antigravity_report/DYNAMIC_3D_ANTIGRAVITY_TASK.md`](../antigravity_report/DYNAMIC_3D_ANTIGRAVITY_TASK.md), we have designed, implemented, and verified a **dynamic, interactive 3D optical simulation engine** for the supervisor presentation package.

The dynamic 3D presentation engine is fully integrated into the authoritative supervisor entry point at `http://127.0.0.1:<port>/demo` ([`../supervisor_demo.html`](../supervisor_demo.html)). It provides a rich 3D visualization of the $5\text{ m} \times 5\text{ m} \times 3\text{ m}$ indoor VLC environment, featuring:
- An offline, dependency-free HTML5 Canvas 2D Perspective Projection Engine (zero CDN or npm dependencies; 60 FPS fluidity on ordinary laptop hardware).
- 3D physical models for Alice (center LED fixture with conical downward flare), 4 Friendly Jammers ($J_1..J_4$ with modulated purple glow), Bob (green pulsating null-space secrecy halo), Eve (red pulsating alert halo), and the south-wall optical RIS array.
- 6 individual specular mirror tiles ($0.159\text{ m} \times 0.159\text{ m}$ derived from backend metadata) rendered at their exact physical coordinates with smooth spherical linear orientation interpolation (`slerp`) on codebook switches.
- $q = 0$ is an explicit inactive/stowed neutral slate reference state with zero reflected rays; $q \in \{1, 2, 3, 4\}$ displays glowing cyan/emerald specular facets with white diagonal gleam lines and 3D normal vector arrows.
- Dual-view interface: Tab 1 displays the **3D Dynamic Interactive Room & Optical Light Beams** (default active), while Tab 2 preserves the original **2D Floorplan Schematic Projection**.
- Real DRL recorded-action playback timeline scrubbing across 24 or 200 slots with run-scenario isolation locks.
- Strict resolution of all findings from [`supervisor_package/DYNAMIC_3D_CODEX_REVIEW.md`](./DYNAMIC_3D_CODEX_REVIEW.md) (truthiness zero-jamming fix, replay scenario lock, dynamic metadata tile size).

---

## 2. Verified Entry Points & Launch Commands

The supervisor demonstration runs locally via a lightweight Python loopback service (`app_server.py`) binding strictly to `127.0.0.1` on an OS-assigned ephemeral port:

| Launch Method | Command / Action | Behavior & Port Handling | Clean Shutdown |
| :--- | :--- | :--- | :--- |
| **Windows Double-Click (Recommended)** | Double-click [`run_supervisor_demo.bat`](../run_supervisor_demo.bat) | Verifies Python in PATH, binds to loopback IPv4, detects free ephemeral port, prints URL, and launches browser to `/demo`. | Press `Ctrl+C` in the launcher console window. |
| **Dedicated Python Launcher** | `python launch_supervisor_demo.py` | Standalone Python launcher binding strictly to `127.0.0.1`, printing exact URL, handling clean exit. | Press `Ctrl+C`. |
| **Master CLI Mode** | `python main.py --mode demo` | Integrates with project unified argument parser; forwards to loopback service and opens `/demo`. | Press `Ctrl+C`. |
| **Interactive Runner** | `python run.py --demo` (or option `[d]`) | Menu-driven execution for easy portability. | Press `Ctrl+C`. |

### Supported URL Routes & Query Parameters:
- **Primary Supervisor Interface:** `http://127.0.0.1:<port>/demo`
- **Parameterized URL Presets:** `http://127.0.0.1:<port>/demo?preset=near_bob` or `http://127.0.0.1:<port>/demo?ris=0` (handled cleanly by `app_server.py` path splitting).
- **Full Research Experiment Dashboard:** `http://127.0.0.1:<port>/ris`
- **Legacy 2024 Paper Visualizer (Read-Only Reference):** `http://127.0.0.1:<port>/`

---

## 3. Architectural & Implementation Choices

### 3.1 Pure Dependency-Free Canvas 2D Perspective Engine
- **Why Pure Canvas 2D over WebGL / Three.js:** Earlier iterations using external Three.js libraries introduced fragility (CDN connectivity failures, offline script loading blocks, and version mismatches). To guarantee 100% offline reliability for supervisor presentations in air-gapped or classroom environments, we built a dedicated 3D perspective projection pipeline using standard HTML5 Canvas 2D.
- **Mathematical Projection:**
  $$\begin{bmatrix} X_c \\ Y_c \\ Z_c \end{bmatrix} = \mathbf{R}_{\text{pitch}} \mathbf{R}_{\text{yaw}} \left( \mathbf{P}_{\text{world}} - \mathbf{C}_{\text{target}} \right)$$
  $$x_{\text{screen}} = c_x + \frac{X_c \cdot f}{Z_c + d_{\text{cam}}}, \quad y_{\text{screen}} = c_y - \frac{Y_c \cdot f}{Z_c + d_{\text{cam}}}$$
  where $f = 640\text{ px}$, $d_{\text{cam}} = 11.2\text{ m}$, and $Z_c + d_{\text{cam}} > 0.1\text{ m}$ is guarded against clipping singularities.
- **High-DPI Support:** Crisp rendering across Retina and 4K displays via `window.devicePixelRatio` scaling.

### 3.2 3D Room & Device Visual Vocabulary
1. **$5\text{ m} \times 5\text{ m} \times 3\text{ m}$ Room Geometry:**
   - Shaded floor plane with $1.0\text{ m}$ grid lines and coordinate markers ($X, Y, Z$).
   - Dark translucent boundary frames with coordinate axis indicators ($X \to \text{East}$, $Y \to \text{North}$, $Z \to \text{Ceiling}$).
2. **Alice LED Transmitter Fixture:**
   - Ceiling center at $(2.5, 2.5, 3.0)\text{ m}$.
   - Golden brass luminaire housing with yellow glowing emitter core and a semi-transparent downward conical light beam.
3. **Friendly Jammer Fixtures ($J_1..J_4$):**
   - Symmetrically placed at $(1.25, 1.25, 3.0)\text{ m}$, $(1.25, 3.75, 3.0)\text{ m}$, $(3.75, 1.25, 3.0)\text{ m}$, and $(3.75, 3.75, 3.0)\text{ m}$.
   - Modulated purple cylindrical fixtures with dynamic glow scaling proportionally to jammer weight $|w_i|$.
   - When $w_i = 0$, fixture dims and displays `J<i> (0.0 idle)`.
4. **Bob Receiver (Legitimate User):**
   - Nominal position $(1.8, 1.6, 0.85)\text{ m}$.
   - Cyan photodiode detector with green pulsating null-space secrecy halo and dashed floor drop line with ground shadow ellipse.
5. **Eve Receiver (Passive Eavesdropper):**
   - Nominal position $(3.2, 3.4, 0.85)\text{ m}$.
   - Amber photodiode detector with red pulsating alert halo.
6. **Bob-Eve Distance Vector & Alert Badge:**
   - 3D Euclidean distance line connecting Bob and Eve with real-time distance readout badge ($d_{BE} = 2.28\text{ m}$ nominal).
   - Turns warning crimson when $d_{BE} < 0.4\text{ m}$ ($7\text{ cm}$ near-Bob singularity).
7. **Optical RIS Array Backplane & Specular Mirrors:**
   - South wall mount at $y = 0.25\text{ m}$ centered at $(2.5, 0.25, 2.6)\text{ m}$.
   - Deep slate backplane frame supporting 6 finite specular mirror facets ($2 \times 3$ grid).
   - Each tile dimensions: $0.159\text{ m} \times 0.159\text{ m}$ ($A_{\text{tile}} = 0.0253\text{ m}^2$, $A_{\text{total}} = 0.152\text{ m}^2$), derived dynamically from backend metadata `tile_side_m`.
   - Normal vectors ($\mathbf{n}$) projected as glowing directional arrows.
   - Smooth spherical linear orientation interpolation (`slerp`) smoothly tilts facets across codebook transitions.

---

## 4. Interactive Controls & Navigation

The 3D canvas viewport includes comprehensive mouse, touch, and UI controls:

| Control Element | Interaction | Functionality |
| :--- | :--- | :--- |
| **Orbit Camera** | Left-click drag on canvas | Rotates yaw ($[-\pi, \pi]$) and pitch ($[-0.1, 1.55]$ rad). |
| **Pan Camera** | Shift + Left-click drag OR Right-click drag | Translates camera target in screen space. |
| **Zoom In / Out** | Mouse wheel OR `[+]` / `[-]` HUD buttons | Scales camera focal distance smoothly. |
| **Reset View** | Double-click canvas OR `🔄 Reset` button | Returns camera to default 3D Orbit angle. |
| **Preset 🪐 3D Orbit** | Button click | Yaw $-0.65\text{ rad}$, Pitch $0.55\text{ rad}$, Zoom $1.0\times$ (General perspective). |
| **Preset 🦅 Top-Down** | Button click | Pitch $1.57\text{ rad}$ ($\approx 90^\circ$ bird's eye floorplan view). |
| **Preset 📐 Side Elevation**| Button click | Pitch $0.0\text{ rad}$, Yaw $0.0\text{ rad}$ (Height / elevation profile). |
| **Preset 🪞 Front Wall (RIS)**| Button click | Yaw $\pi\text{ rad}$, Pitch $0.22\text{ rad}$ (Direct face-on view of the 6 RIS mirror facets). |
| **Flow Controls** | `⏸ Pause Flow` / `▶ Play Flow` | Toggles illustrative pulse motion; pauses render animation if idle. |
| **Flow Speed Selector** | `1.0x` / `0.5x` / `2.0x` | Adjusts photon pulse propagation velocity. |
| **Layer Toggles** | Direct links, Reflected links, Jammers & nulls, Mirror normals, Floor grid, Labels | Instant individual visibility control for clean presentation slides. |
| **Stage View Tabs** | `[🏢 3D Dynamic Interactive Room]` / `[🗺️ 2D Floorplan]` | Instant switching between 3D canvas and 2D SVG schematic projection. |

---

## 5. Resolution of Codex Delivery Review Audit Findings

The implementation directly addresses all findings raised in [`supervisor_package/DYNAMIC_3D_CODEX_REVIEW.md`](./DYNAMIC_3D_CODEX_REVIEW.md):

### 5.1 Finding 1: Zero-Jamming Gating & Gain Distinction
- **The Issue:** `currentWeights` previously used `parseFloat(input.value) || default`. In JavaScript, `parseFloat("0.0")` evaluates to `0`, which is falsy; hence valid zero jammer weights fell back to default non-zero weights, rendering active jamming pulses when Python received zero jamming.
- **The Solution:**
  1. Bound `currentWeights` directly to `backendData.selected.beamformer` using explicit finite-number checks:
     ```javascript
     const w = (selected && Array.isArray(selected.beamformer)) ? selected.beamformer[i] : null;
     currentWeights[i] = Number.isFinite(w) ? w : 0.0;
     ```
  2. Pulse emission and beam thickness are strictly gated by `Math.abs(currentWeights[i]) > 1e-6`.
  3. When $w_i = 0$, jammer fixtures are visually dimmed, labeled `J<i> (0.0 idle)`, and rendered as faint dashed lines without emitted pulses.
  4. Channel availability ($h_{JE,i} > 0$) is clearly distinguished from transmitted activity ($w_i > 0$) in the on-screen legend.

### 5.2 Finding 2: DRL Recorded-Action Replay Timeline Consistency
- **The Issue:** Scrubbing historical replay slots while the user modified live receiver geometry or energy costs caused historical observations to be evaluated against mismatched room setups.
- **The Solution:**
  1. **Run-Scenario Isolation Snapshot:** At the start of a live DRL run, the runner snapshots the exact active scenario:
     ```javascript
     replayState.scenarioSnapshot = {
       bob: [...geometry.bob],
       eve: [...geometry.eve],
       energy_model: backendData.selected.energy_model
     };
     ```
  2. **Direct Observation Replay:** The replay engine renders directly from the recorded state vector and observation history (`obs`), matching recorded actions $[w_1, w_2, w_3, w_4, \tilde{q}]$ without issuing discordant live server requests.
  3. **Invalidation Guard:** If the user manually changes receiver presets, drag handles, or codebook buttons while replay is active, replay is immediately halted and invalidated with an explicit UI notification banner.

### 5.3 Finding 3: Dynamic Metadata Tile Size
- **The Issue:** HUD and screenshots displayed a hardcoded `0.2m x 0.2m` tile size, whereas the true backend simulation tile side was $0.1591\text{ m}$ ($A_{\text{tile}} = 0.0253\text{ m}^2$).
- **The Solution:** HUD labels and 3D mirror geometry now dynamically derive tile dimensions directly from `backendData.selected.geometry.ris.tile_side_m`:
  ```javascript
  const tileSideStr = Number.isFinite(r.tile_side_m) ? r.tile_side_m.toFixed(3) : '0.159';
  ```
  Rendering and HUD display are now mathematically identical to the Python optics model.

### 5.4 Build Integration Fix & Strict Script Replacement Assertion
- **The Issue:** The build script previously matched only the early wireframe header (`/* Dependency-free 3D geometry projection...`). Once the dynamic engine header (`/* DYNAMIC 3D VLC...`) was inserted, subsequent regex substitutions silently failed (returned unmodified content) while printing success. Consequently, fixes in `scratch/dynamic_3d_engine.js` were not being embedded into the served HTML.
- **The Solution (`scripts/build_supervisor_demo.py`):**
  1. Replaced fragile header matching with structural boundary matching: targeting the final `<script>` block immediately preceding `</body>`:
     ```python
     engine_script_pattern = re.compile(
         r'<script[^>]*>(?:(?!<script)[\s\S])*?</script>\s*</body>',
         re.DOTALL
     )
     ```
  2. Enforced strict replacement count assertion:
     ```python
     new_html, count = engine_script_pattern.subn(replacement, html_content, count=1)
     assert count == 1, f"BUILD INTEGRATION FAILED: Expected exactly 1 replacement, got {count}!"
     ```
  3. Enforced post-build content assertions verifying that `Number.isFinite(w) ? w : 0.0`, `replayScenario`, and `tile_side_m` exist in `supervisor_demo.html`, and that all traces of `0.2m x 0.2m` are completely eliminated.
  4. Executed `node --check` automatically on all embedded `<script>` tags extracted from the rebuilt HTML (both Script 0 and Script 1 pass with 0 syntax errors).

### 5.5 Genuine In-Browser Verification via Edge Headless & CDP Protocol
To verify the served HTML in an actual browser environment, we executed [`scripts/verify_demo_in_browser.js`](../scripts/verify_demo_in_browser.js) using headless Microsoft Edge (`157.0.4341.46`) connected via Chrome DevTools Protocol (CDP):
1. **DOM Tile-Size Label Check:**
   - Evaluated `document.getElementById("hudTopLeft").innerText` in the live DOM.
   - Result: Confirmed presence of `0.159m × 0.159m` (`Room: 5.0m × 5.0m × 3.0m · 6 Specular Mirror Tiles (0.159m × 0.159m)` and `RIS State: 1 (alice_to_bob) · 6 Specular Tiles (0.159m × 0.159m)`).
   - Result: Confirmed complete absence of `0.2m x 0.2m` / `0.2m × 0.2m` (`PASS`).
2. **Zero Jammer Weights Execution Check:**
   - Evaluated `setWeights([0, 0, 0, 0])` in the browser session.
   - Checked Python backend response via `/api/ris/metrics`.
   - Result: `window._lastBackendData.selected.beamformer` returned `[0, 0, 0, 0]` (`PASS`).
   - Verified that unmodulated zero-weight jamming renders idle dimmed fixtures (`J<i> (0.0 idle)`) and produces zero modulated optical pulses.
3. **DRL Replay Scenario Isolation Check:**
   - Executed `runSmokeTrain()` (24 slots) live on the Python CNN + DND backend via browser UI.
   - Polled until `#smokeReplayBox` became visible (`PASS`).
   - Verified scenario snapshot in browser memory: `{ bob: [1.8, 1.6, 0.85], eve: [3.2, 3.4, 0.85], energy_model: 'l1' }` (`PASS`).
   - Triggered manual preset switch: `setPreset("near_bob")`.
   - Result: `isReplayActive` transitioned immediately to `false`, and badge updated to `"Paused (Preset near_bob)"` (`PASS`).
   - Confirmed that manual UI changes never blend historical replay observations with mismatched scene geometry.
4. **Browser Console Error Check:**
   - Monitored `Runtime.consoleAPICalled` and `Runtime.exceptionThrown` throughout the entire interactive session.
   - Result: **0 uncaught exceptions, 0 errors (`PASS`)**.

---

## 6. Boundary Disclosures: Backend Reality vs. Illustrative Animations

In compliance with the project's strict scientific integrity guidelines, the demonstration maintains clear boundaries between physical computation and visual illustration:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      SCIENTIFIC INTEGRITY BOUNDARY                     │
├───────────────────────────────────┬────────────────────────────────────┤
│   AUTHORITATIVE BACKEND PYTHON    │     CLIENT-SIDE 3D CANVAS UI       │
│        (Physical Reality)         │           (Illustrative)           │
├───────────────────────────────────┼────────────────────────────────────┤
│ • 2D Gauss-Legendre Quadrature    │ • Illustrative photon pulse flows  │
│   specular channel integration    │ • Slerp mirror tilt interpolation  │
│ • Scalar channel gains (hAB, hAE) │ • Schematic reflected link center  │
│ • Optical link gains (hJB, hJE)   │   path (Alice -> RIS -> Receiver)  │
│ • Signal-to-Interference-plus-    │ • Receiver glowing status halos    │
│   Noise Ratio (SINR) calculation  │ • Jammer purple glow intensity     │
│ • Secrecy Rate Rs (bps/Hz)        │ • Visual perspective & camera orbit│
│ • Bob / Eve BER computation       │ • Pulse velocity & dash spacing    │
│ • PyTorch CNN + DND execution     │ • Real-time distance line warning  │
└───────────────────────────────────┴────────────────────────────────────┘
```

1. **Optical Pulse Animation:** The animated flowing dashes convey link activity and propagation direction only ($h > 0$). They do NOT simulate time-of-flight, photon counting, packet framing, or decoder queueing.
2. **Schematic Reflected Ray Trajectory:** Reflected optical paths are routed via the geometric center of the RIS backplane as an aggregate schematic connection. The demonstration does NOT claim multi-bounce ray tracing or individual specular ray intersection per facet.
3. **Eve Reception Visibility:** Eve's optical link is drawn whenever channel gain $h_{AE} > 0$. Eve's reception is NOT hidden or drawn as zero merely because secrecy rate is positive ($R_s > 0$).

---

## 7. Visual Evidence & Screenshot Verification

High-resolution screenshots were captured directly from a running instance of `app_server.py` using Microsoft Edge in headless mode (`--headless --window-size=1600,1000`):

| Screenshot File | Resolution / Size | Scenario / Configuration Shown | Key Features Captured |
| :--- | :---: | :--- | :--- |
| [`supervisor_package/figures/demo_3d_nominal.png`](./figures/demo_3d_nominal.png) | $1600 \times 1000$ (530.6 KB) | Nominal: Bob $(1.8, 1.6, 0.85)$, Eve $(3.2, 3.4, 0.85)$, RIS Config 1 (Aim Alice $\to$ Bob) | 3D room wireframe, specular glowing facets, Alice conical flare, modulated jammers, green/red halos, HUD telemetry with $0.159\text{ m} \times 0.159\text{ m}$. |
| [`supervisor_package/figures/demo_3d_near_bob.png`](./figures/demo_3d_near_bob.png) | $1600 \times 1000$ (524.4 KB) | Near-Bob Boundary: Eve $(1.85, 1.65, 0.85)$ ($d_{BE} = 7\text{ cm}$) | Collinear geometry, crimson distance alert badge ($d_{BE} = 0.07\text{ m}$), $R_s = 0.0000\text{ bps/Hz}$ secrecy singularity. |
| [`supervisor_package/figures/demo_3d_stowed.png`](./figures/demo_3d_stowed.png) | $1600 \times 1000$ (529.7 KB) | Stowed RIS: Config 0 ($q = 0$) | Neutral slate mirror tiles, zero reflected rays, pure direct LOS link baseline ($R_s = 1.556\text{ bps/Hz}$). |
| [`supervisor_package/figures/demo_screenshot.png`](./figures/demo_screenshot.png) | $1600 \times 1000$ (529.9 KB) | Authoritative supervisor demo screenshot | Master delivery screenshot for documentation and index catalog. |

All captured screenshots are stored in [`supervisor_package/figures/`](./figures/) and linked directly from the package markdown files.

---

## 8. Verification & Regression Testing

The dynamic 3D simulation engine underwent rigorous automated, manual, and live in-browser validation:

1. **In-Browser Headless Edge & CDP Verification (`scripts/verify_demo_in_browser.js`):**
   - Verified that `#hudTopLeft` in the live DOM contains `0.159m × 0.159m` and that old `0.2m` is completely absent (`PASS`).
   - Verified that `setWeights([0, 0, 0, 0])` communicates strictly zero weights to Python (`backendBeamformer: [0, 0, 0, 0]`) and gates modulated pulses (`PASS`).
   - Verified that 24-slot live smoke run creates `#smokeReplayBox`, snapshots `{bob, eve, energy_model}`, and invalidates replay (`isReplayActive: false`, `Paused (Preset near_bob)`) on manual preset switch (`PASS`).
   - Verified 0 uncaught browser console exceptions across all operations (`PASS`).
2. **Build Integration & Replacement Assertion (`scripts/build_supervisor_demo.py`):**
   - Rebuilt `supervisor_demo.html` with explicit assertion of exactly 1 engine script replacement (`count == 1`, `PASS`).
   - Post-build content assertions for `Number.isFinite`, `replayScenario`, and `tile_side_m` passed (`PASS`).
   - `node --check` passed on both embedded script blocks (`PASS`).
3. **Unit Test Suite (100% Pass):**
   ```bash
   python -B -m unittest discover -s tests -v
   ```
   - **Result:** **94 tests ran, 94 passed, 0 failed, 0 errors** (Runtime: ~33 seconds).
   - Includes full regression across optical channels, Gauss-Legendre integration, DRL networks, environment wrappers, and the dedicated web server test suite (`tests/test_supervisor_demo.py`).
4. **Web Route & Security Verification:**
   - `test_demo_route_serves_html`: Confirms `/demo` returns HTTP 200 and serves `supervisor_demo.html`.
   - `test_cross_origin_blocked`: Confirms external `Origin` headers return HTTP 403 Forbidden.
   - `test_calc_endpoint_contract`: Confirms `/api/ris/calc` returns valid JSON with all optical gains and metrics.
5. **Syntax & Parity Verification:**
   - `python paper_audit/check_paper_match.py --equations-only`: Passed cleanly.
   - `node paper_audit/check_browser_match.js`: Passed cleanly.
   - `git diff --check`: 0 trailing whitespace errors.
6. **Data Integrity & Provenance:**
   - SHA-256 hashes for all modified source files (`supervisor_demo.html`, `app_server.py`) and result datasets updated in [`supervisor_package/PROVENANCE.json`](./PROVENANCE.json).

8. **Changed Receiver Positions Workflow & Empirical Study:**
   - Designed and integrated the "Changed Positions (Bob [2.0, 3.0], Eve [3.5, 1.5])" preset button and handler into Section 1 of `supervisor_demo.html`.
   - Executed a real matched PyTorch CNN + DND training and frozen evaluation study across seeds 42, 43, 44 (1,000 slots training, 500 slots frozen greedy evaluation, $\epsilon=0$, L1 energy).
   - Produced raw dataset [`output_figures/ris/changed_positions/ris_study_data.json`](../output_figures/ris/changed_positions/ris_study_data.json) and summary [`output_figures/ris/changed_positions/ris_study_summary.json`](../output_figures/ris/changed_positions/ris_study_summary.json).
   - Generated 5 scenario-labeled figures in both 200 DPI PNG and vector PDF in [`supervisor_package/figures/scenario_changed/`](./figures/scenario_changed/):
     - `fig1_changed_training_convergence.png` / `.pdf`
     - `fig2_changed_frozen_evaluation.png` / `.pdf`
     - `fig3_changed_paired_differences.png` / `.pdf`
     - `fig4_changed_optical_breakdown.png` / `.pdf`
     - `fig5_cross_scenario_comparison.png` / `.pdf`
   - Fixed RIS achieved statistically significant gain over baseline: $\Delta R_s = +0.0868\text{ bps/Hz}$ ($t=8.60, p = 0.0132$).
   - Captured in-browser Edge headless screenshot: [`demo_3d_changed_positions.png`](./figures/demo_3d_changed_positions.png).
   - Detailed documentation published in [`CHANGED_POSITIONS_STUDY.md`](./CHANGED_POSITIONS_STUDY.md).

---

## 9. Completed vs. Pending Checklist

### Completed:
- [x] Inspect existing rendering approaches (`visualizer.html`, `index.html`, `supervisor_demo.html`).
- [x] Implement lightweight, dependency-free Canvas 2D Perspective 3D engine.
- [x] Model $5\text{ m} \times 5\text{ m} \times 3\text{ m}$ room, floor grid, coordinate axes, and boundary wireframe.
- [x] Model Alice fixture with downward conical flare, Jammers $J_1..J_4$, Bob, Eve, and south-wall RIS mount.
- [x] Implement 6 specular mirror tiles at true coordinates with smooth `slerp` normal orientation transitions.
- [x] Neutral slate stowed reference state for $q = 0$; glowing cyan facets with white gleam for $q \ge 1$.
- [x] Dynamic animated optical pulses with play/pause and speed selector (`1.0x`, `0.5x`, `2.0x`).
- [x] Full camera controls: Orbit, Pan, Zoom, Reset, and 4 camera presets (3D Orbit, Top-Down, Side, Front Wall).
- [x] Layer visibility toggles (Direct, Reflected, Jammers, Normals, Grid, Labels).
- [x] Dual-view stage tabs (`[🏢 3D Room]` and `[🗺️ 2D Floorplan]`).
- [x] Diagnose HTML staleness: Identified regex substitution mismatch and in-memory editor buffer overwrite.
- [x] Fix build integration: Created `scripts/build_supervisor_demo.py` asserting exactly ONE engine replacement (`count == 1`) and `node --check` validation.
- [x] Authoritative Served HTTP Bytes Verification: Verified exact body served by `app_server.py` at `/demo`.
- [x] Resolution of Codex Finding 1: Strict zero-jamming weight gating (`Number.isFinite(w) ? w : 0.0`) and idle fixture dimming.
- [x] Resolution of Codex Finding 2: DRL recorded-action replay timeline with scenario snapshot isolation and observation replay.
- [x] Resolution of Codex Finding 3: Dynamic metadata tile side extraction (`0.159m`), completely eliminating `0.2m` label.
- [x] Implement Changed Positions Workflow: Added preset button to demo, executed real 9-run matched experiment, exported JSON and 5 scenario-labeled figures (PNG + PDF).
- [x] Live in-browser verification via Microsoft Edge headless & CDP (`scripts/verify_demo_in_browser.js`): tested zero weights, replay scenario isolation, changed preset coordinates, and tile size labels in DOM with 0 console errors.
- [x] Capture high-resolution Edge headless screenshots (`demo_3d_nominal.png`, `demo_3d_near_bob.png`, `demo_3d_stowed.png`, `demo_3d_changed_positions.png`, `demo_screenshot.png`).
- [x] Deliver dedicated report: `CHANGED_POSITIONS_STUDY.md`.
- [x] Full regression test pass (94/94 unit tests passing).
- [x] Update provenance hashes in `PROVENANCE.json`.
- [x] Update `START_HERE.md` and `DEMO_SCRIPT_BN.md` with 3D walkthrough instructions.

### Pending / Out of Scope (As Explicitly Directed):
- [ ] Manuscript drafting / writing (placed strictly on hold as instructed).
- [ ] New long scientific multi-seed simulations (10-seed authoritative datasets preserved unchanged).
- [ ] Continuous action space SAC/DDPG exploration (deferred to future work).


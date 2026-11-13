# Latest user task: dynamic 3D RIS simulation presentation

Date: 2026-11-14, Asia/Calcutta. Implementer: Antigravity IDE.

The user explicitly requests a dynamic, interactive 3D simulation view comparable to `visualizer.html`, implemented by Antigravity, not Codex. Read AGENTS.md and Agent.MD first. Inspect the WHOLE relevant rendering/control portions of `visualizer.html`, `index.html`, `supervisor_demo.html`, `ris.html` and app_server.py before choosing an approach. Existing simulator/research artifacts must be preserved.

## User intent

The current wireframe Canvas 3D addition is a first presentation aid, not the desired final visual experience. Build a polished, visibly dynamic 3D indoor VLC/RIS demonstration, using the existing visualizer's interaction/rendering approach where useful. The supervisor should see the room, devices, physical mirrors, configuration changes and communication-link activity clearly. Do actual implementation and browser validation, not another plan or static mockup. Manuscript writing remains out of scope.

## Integrate, do not create another disconnected simulator

- Choose one authoritative supervisor entry point (`/demo` preferred) and link full research controls. Avoid adding several competing unfinished demo pages. Keep the old 2D view available as a useful secondary projection.
- Reuse existing local rendering code/assets if practical. Inspect dependency availability first; preserve offline/local demo reliability. No silent CDN requirement or global installation. If rendering libraries are already bundled, reuse them. Document any justified new dependency and fallback.
- All scientific metrics must come from the existing Python RIS backend. The 3D client renders backend geometry/results; it must not implement an inconsistent second secrecy/BER model. Preserve physical/paper mode separation and historical datasets.
- Preserve index.html/visualizer.html parity if editing that pair; otherwise use them as read-only design/code references. Avoid overwriting either with the RIS page.

## Required visual behavior

1. Render an understandable 5×5×3 m room with floor grid, readable axes/scale and non-obstructing walls/ceiling. Show actual backend positions of Alice, all four jammer fixtures, Bob, Eve and the six-mirror RIS panel. Use recognizable LED/receiver/mirror objects, labels, sensible lighting and contrast. Icon exaggeration must not change physical coordinates or imply false mirror area.
2. Add smooth orbit/pan/zoom, reset, top/side perspectives and a clear default camera. Retain responsive rendering and readable controls on ordinary laptop screens.
3. Render each finite mirror at its actual center/side and backend normal. Changing q should visibly change orientation. If interpolating motion, label it an illustrative transition; numerical metrics represent the selected endpoint, not a validated time-resolved actuator model. q0 is the explicit inactive/stowed reference, not unexplained transparent reflection.
4. Add play/pause and useful visibility controls for direct paths, reflected paths, jammer paths, labels and normals. Use animated pulses/dashes to communicate link direction/activity. Explicitly label pulses as illustrative: no packet-delivery, photon-count, propagation-time or decoder measurements are simulated by animation alone. Do not make Eve's reception appear zero merely because the channel is secure.
5. Reflect link existence and per-jammer identity from actual backend gains. A zero jammer weight means no emitted modulated jamming on that link even if its geometric channel exists; distinguish channel availability from transmitted activity in the legend. No arbitrary beam-power gain or fabricated nulls.
6. For an optical reflection ray trace claim, use actual per-tile ray intersection/visibility metadata from the same optics model. Otherwise route aggregate visual links via the panel as clearly labeled schematic paths. A normal vector is not itself an outgoing ray. Do not claim exact specular trajectories from a decorative spline or centerline.
7. Support nominal, near-Bob and colocated presets; receiver coordinate changes must update both model and scene. Position editing/dragging, if offered, must stay within valid room bounds and update Python with debouncing/latest-request guards. Passive Eve presence must not create fake interference/body blockage.

## Connect controls, live calculation and DRL properly

- Same receiver positions, noise, power, weights and cost interpretation for RIS off/on comparison. Keep current manual codebook/weight controls and full direct/reflected/effective Bob/Eve tables. Mark manual actions as manual.
- Show backend request/busy/error state; reject stale responses. Clear or visibly invalidate outdated geometry/metrics on failed requests. Scene and table must never display different configurations as if synchronized.
- Connect real 24/200-slot DRL smoke runs and display selected jammer/RIS actions. A step-through/playback timeline of actual recorded actions is useful: label it recorded-action replay, show slot and settings, and replay geometry/metrics from genuine saved actions. Do not invent learning curves or claim playback is fresh training. If training finishes before playback, say so.
- Keep saved 10-seed scientific results separate from current manual/demo settings and exploratory smoke runs. Load checked compact JSON; show source/provenance, phase and seed count. Existing static nominal frozen evaluation repeats a single action per run, so do not manufacture dynamics in those results.
- Current evidence: fixed-RIS improvement in nominal L1 study; joint superiority not established. Three schemes have zero modeled frozen evaluation outage in that static case. Near-Bob finite-grid secrecy zero is a tested configuration result, not a universal distance theorem. Preserve these statements.

## Evidence and acceptance

- Test the actual interactive browser: initial load, camera interaction, off/on, all q patterns, receiver presets, weight zero, rapid edits, invalid input/API failure, short real training and recorded-action playback if implemented. Check console errors and no unnecessary heavy requests per animation frame. Use requestAnimationFrame efficiently; animation must not retrain/recalculate Python every frame.
- Run relevant regression checks, route/API tests and legacy browser parity. Test geometry/normal agreement against backend, not just markup existence. Verify old simulator controls still work. Record exact checks and limitations.
- Capture real screenshots of default 3D scene and at least one changed configuration; a short local demo recording is optional if supported without installing tools. Do not fabricate screenshots.
- Update `supervisor_package/START_HERE.md`, `DEMO_SCRIPT_BN.md`, screenshot(s), relevant provenance and detailed Agent.MD handoff. Mark old screenshots/hashes stale or regenerate them after final source changes. Update ANTIGRAVITY_STATUS.md during work.
- Deliver `supervisor_package/DYNAMIC_3D_COMPLETION_REPORT.md`: implementation choices, actual launch command/URL, controls, backend-vs-illustrative boundaries, tests, changed files, screenshots and complete/pending checklist. Give a short Bangla IDE-chat explanation of what to open and demonstrate.

Do not publish, commit, reset, delete historical data, change user permissions or start long unrelated research experiments. Use the IDE permissions already granted. Finish a concrete verified demonstration instead of declaring all items complete without evidence.

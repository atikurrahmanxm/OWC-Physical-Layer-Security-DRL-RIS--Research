# Dynamic 3D review — 2026-11-14

The new dynamic Canvas scene is implemented in supervisor_demo.html, with animation, camera/layer controls, oriented mirrors and recorded-smoke-action replay. Codex inspected a real screenshot and opened the current page in headless Edge: canvas exists and actual backend response reports q1 secrecy 1.8413 bps/Hz. This is a real improvement over the previous wireframe. Optical pulses remain illustrative; backend calculations remain authoritative.

Critical fix before supervisor demonstration:

- In the dynamic engine (also scratch/dynamic_3d_engine.js), currentWeights uses `parseFloat(input.value) || default`. Valid ZERO becomes the default for jammer 1, 2 and 4. Thus Zero Jamming can still render nonzero jammer weights/activity even though Python received zeros. Read weights from `backendData.selected.beamformer` for the currently rendered response; use finite-number checks instead of truthiness. This also prevents rapidly changed UI controls from disagreeing with the displayed backend response. Fix every duplicated embedded/source engine instance and test zero-jamming in an actual browser.

Replay consistency fix:

- Replay stores the recorded action/history but calls triggerUpdate using CURRENT UI receiver geometry and energy interpretation. If the user changes presets/cost after training, replay readout and live scene can represent different experiments. Snapshot and restore/lock run settings, or render directly from recorded observations with the matching geometry. Cancel/invalidate replay on incompatible live changes; do not silently blend historical metrics with a new scene.

Presentation and delivery:

- HUD/screenshot says tiles 0.2m x 0.2m; actual default backend tile side is about 0.1591m. Derive labels from metadata (rendering itself uses tile_side_m).
- Required supervisor_package/DYNAMIC_3D_COMPLETION_REPORT.md does not exist at review time; status/handoff still describe the previous delivery. Finish actual browser interaction checks, update scientific/screenshot provenance and report completion/pending honestly.
- No claim of full per-tile optical ray tracing: aggregate reflected paths remain schematic. No universal security or superiority claim.

This review did not yet exercise every mouse control/replay state in a real interactive browser. Current full regression run is tracked separately; existing tests alone do not cover these visual zero-input and replay-setting errors.

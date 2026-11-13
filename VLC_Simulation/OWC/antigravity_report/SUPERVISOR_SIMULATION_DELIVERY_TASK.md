# Active user task: supervisor-ready simulation and evidence package

Date: 2026-11-13, Asia/Calcutta.

## Latest user clarification — this defines the scope

The supervisor ALREADY understands the proposed optical RIS idea and has asked the students to bring a simulation demonstration and a paper. The user will handle manuscript preparation later using Claude Code/skills. Your task NOW is to finish a reliable, understandable simulation demonstration with ALL supporting reports and evidence. Do not spend this task rewriting the manuscript or giving another explanation-only plan. Execute implementation, verification and packaging in Antigravity IDE under the user's existing permissions.

Read AGENTS.md and Agent.MD, plus CODEX_REVIEW.md, COMPLETION_REVIEW.md, RECONCILIATION_RECHECK.md and AUTHORITATIVE_TABLES.md in antigravity_report/. Preserve current simulator and historical raw results. There may be other existing changes: inspect them, do not reset or overwrite unrelated work. Do not publish, submit, send messages, change global permissions or install software without a genuine need and the applicable authorization.

## What already exists — extend rather than restart

- `supervisor_demo.html` at `/demo` in app_server.py: conceptual path diagram, live Python RIS off/on comparison with identical jammer weights, saved 10-seed frozen evaluation tables and limitations.
- `supervisor_results.json`: compact snapshot derived from complete `output_figures/ris/final_evaluation/ris_study_summary.json`, including source hash.
- `ris.html` at `/ris`: receiver positions, five mirror configurations, four jammer weights, actual backend instant metrics and real matched training jobs, raw study download.
- `docs/SUPERVISOR_DEMO.md`: five-minute demonstration script.
- Previous Codex demo check: route HTTP 200, three saved schemes, live q1 Alice-to-Bob reflected gain 6.3554634273447525e-6. Prior independent full regression: 89 passing tests. These are historical checks, rerun relevant checks after your changes.
- Previous demo server URL was http://127.0.0.1:60969/demo. It is not a permanent URL. Do not assume either that port or 50198/8000 is active; launcher prints actual current URL. Check active project processes before launching another agent/server, and avoid concurrent file edits.

## Required supervisor experience

The supervisor should be able to SEE the implementation operating, examine actual measured simulation outputs, and take away a self-contained evidence bundle. A static schematic or a renamed graph alone is insufficient. Do not claim hardware validation.

### A. One reliable entry point

Provide a verified project-local launch command or double-click launcher that starts the loopback service and opens `/demo`. Handle Python/dependency/port errors clearly. Use the actual server address, never a fixed guessed port. Preserve the existing GUI/CLI routes and same-origin protections. Avoid orphaned duplicate background workers; document how to stop the demo. Do not modify global PATH or user settings.

### B. Visible optical simulation, tied to actual backend geometry

Improve `/demo` or link a coherent dedicated visualization from it. Show actual room dimensions, Alice, four jammer fixtures, Bob, Eve, RIS panel and its six tiles. Render physical positions and mirror normals from backend metadata, not arbitrary decorative coordinates. Show direct and reflected path categories and active q. Use clear labels, legend and useful camera/2D projection controls if needed. A well-implemented room view is preferred; do not add unneeded dependencies to chase 3D polish.

All displayed reflected paths must agree with the selected configuration and actual computed gains. Distinguish conceptual candidate paths from paths verified visible/reflected by the optical model. If the aggregate API cannot expose tile/path visibility, extend it meaningfully or label the diagram schematic; do not animate nonexistent rays or imply every mirror illuminates Eve. No fake packets, fake losses or synthetic learning curves masquerading as simulation.

### C. Controlled live experiments

Provide easy presets for nominal geometry, near-Bob and colocated Eve, plus the current off/alice_to_bob/jammers_to_eve/split_bob_eve/neutral codebook choices. Keep geometries and jammer weights unchanged when comparing RIS off/on. Display direct, reflected and effective gains, secrecy rate, Bob BER and chosen normalized jammer cost. Show both Bob and Eve link effects, not just an attractive Bob-only number.

Show the exact configuration/settings and a visible backend-computed status. Explain continuous manual weights versus the learner's discrete grid if manual values are permitted. Separate manual actions from learned decisions. Keep primary matched nominal demonstration on clearly labeled L1 interpretation, with signed energy available and explained as a different interpretation. Do not silently change noise, cost, reward, positions or power between comparisons.

The desired demo is not a guaranteed improvement at every action/location. Zero or adverse results must display honestly. Passive Eve movement by itself must not create invented Bob interference/body blockage.

### D. Show actual DRL operation and saved scientific evidence

- Keep a short real training preview (e.g. 24 or 200 slots) to show code execution. Clearly label it a smoke/demo run, not evidence of superiority.
- Show available actual selected FJ weights and RIS index/configuration for learner outputs; distinguish frozen RIS selection from joint agent choices.
- Provide a saved-results mode that loads the existing COMPLETE 10-seed study locally and renders real plots/tables without re-running a 20-minute study during the meeting. Do not auto-download the approximately 190 MB raw JSON to render a small dashboard; derive compact checked summaries/plot data server-side or via a reproducible export script.
- Separate all-training, final-training-window and frozen evaluation data in controls, graph titles, tables and exports. Do not mix phases again. Plot uncertainty across independent seeds and provide per-seed detail where useful.
- Frozen evaluation currently uses one action per run over 1,000 static slots; do not make it look like 1,000 independent changing-channel trials. All schemes have zero evaluation outages in that setting. Training outages differ and must retain phase labels.
- Keep saved historical data immutable. A live training preview must not overwrite completed research datasets.

### E. Reports and take-away evidence bundle

Create a dedicated `supervisor_package/` directory with a clear index and relative links. It must work for reading reports offline. Include:

1. `START_HERE.md`: exact working launcher/commands, meeting flow, package contents, dependencies and restart/stop instructions.
2. `DEMO_SCRIPT_BN.md`: 5–10 minute Bangla walkthrough focused on demonstrating actual results, not re-teaching the RIS concept; include expected controls, values and how to handle an adverse result or server error.
3. `IMPLEMENTATION_AND_VERIFICATION.md`: architecture/code map, how effective channels are calculated and shared mirror configurations enforced, action encoding, real test outcomes and commands. Distinguish model tests, saved-action replay, numerical paper reproduction and hardware experiments.
4. `RESULTS.md`: authoritative phase-separated numbers, seed counts/configs, paired CIs, training/evaluation horizons, per-seed evidence, boundary cases and honest limitations. Generate numeric tables programmatically from raw JSON, not hand-entered approximations.
5. `REPORT_INDEX.md`: organized links/copies of relevant existing reports and scientific assumptions. Mark historical/superseded reports clearly rather than copying contradictory old claims as current truth.
6. Static scientific plots as standalone high-quality PNG/PDF or SVG using standard plotting tools, derived from actual histories: matched training curves, frozen secrecy comparison with seed-level uncertainty, paired differences, and useful direct/reflected gain illustration. Clearly label manual versus learned, phase, geometry and cost interpretation. Do not draw zero-BER underflow as a measured physical guarantee.
7. Representative screenshots of the running demo if available using installed browser capabilities, with actual backend data. If screenshot capture is unavailable, mark that pending rather than fabricate an image. Include print/save-PDF support for a compact results handout if feasible.
8. `PROVENANCE.json`: source dataset paths/hashes, relevant source hashes, generation command/version/date, complete flags and sample counts. Include compact downloadable results; link to large raw datasets instead of duplicating hundreds of MB unnecessarily.
9. `COMPLETION_REPORT.md`: actual tasks completed, exact tested commands/URL, checks and outcomes, files changed, existing evidence reused versus new runs, remaining limitations, and a pass/fail/pending checklist against this task. Give the user a short Bangla final handoff with exactly how to launch and what to show.

The offline report bundle is different from an offline interactive backend: say clearly that live calculations require the local Python service. Relative links in packaged reports should resolve. No claim that a file:// HTML can call the same-origin API without the service.

## Scientific facts that must remain consistent everywhere

- 2024 paper system + optical RIS is the baseline. The alternative physical mode is separate. Exact published numerical curves have not been reproduced.
- Nominal L1 frozen secrecy means: baseline 1.3205214713, fixed 1.4977986702, joint 1.4564502067 bps/Hz.
- Fixed-minus-baseline paired 95% CI [0.0378458203, 0.3167085774]. Joint-minus-baseline [-0.0439845724, 0.3158420431]; joint-minus-fixed [-0.2674135115, 0.1847165846]. Joint superiority/equivalence is not established. Recompute from JSON rather than trusting copied constants.
- All three schemes have zero modeled frozen evaluation secrecy/QoS outages here. Training outage differences are NOT frozen evaluation improvements.
- Near-Bob max secrecy over the declared finite 3,125-action grid is zero. This is not a universal theorem that any Eve within 7 cm prevents security. Colocated identical channels/noise is a separate boundary.
- Code state is four feedback/channel/cost values plus historical action sequence; FeatureCNN uses Conv2d, m0=11 and flatten size 2560 in matched runs. Reward is secrecy -3.5*BER -0.4*cost, with optional explicit soft excess-BER penalty.
- Oracle Eve geometry, static DC optical model, no body blockage/ISI and omitted RIS control energy must be visible in claims. Negative jammer weight is modulation sign under bias, not negative light.

## Acceptance and validation before saying complete

- Verify the actual running demo via HTTP/browser, not just process startup or screenshot of code. Check live off/on against direct Python calculations, same-settings invariants, preset behavior, no stale metrics on errors, saved-results provenance and correct phase labels.
- Run appropriate integration/regression checks, including existing tests when source/backend changes, formula-only audit, browser parity and git diff --check. Add meaningful tests for new behavior, not tests that only mirror markup. Preserve all current tests.
- Verify every displayed scientific number against exported JSON/independent recomputation. Check that package links work and summary export is reproducible. Record failures and pending tasks openly.
- Do not run more long research experiments just to produce demo polish. Ask only for a genuinely blocking decision; otherwise finish authorized reversible implementation work yourself.
- Update Agent.MD with detailed handoff and ANTIGRAVITY_STATUS.md with real progress. Finish with `supervisor_package/COMPLETION_REPORT.md` and simple Bangla instructions in the IDE chat. Do the work, not merely another plan.

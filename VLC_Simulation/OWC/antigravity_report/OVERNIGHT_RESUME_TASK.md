# Overnight Antigravity resumption — 17 November 2026

The user's NEW explicit request is to finish this research task overnight, with the computer left on, using a second Antigravity ID. This supersedes the earlier cancellation in docs/RESEARCH_STOP_REQUEST.md. Read AGENTS.md, Agent.MD and antigravity_report/JOINT_CONTROLLER_AUDIT_AND_BUDGET_TASK.md; execute that scientific task with the corrections below. Do not access credentials or change account/global settings. No other numeric worker was launched by Codex during this handoff; check for active workers before starting one.

## Saved state inspected by Codex

- Stage A audit exists: supervisor_package/JOINT_CONTROLLER_AUDIT.md, scripts/audit_joint_controller.py, output_figures/ris/joint_controller_audit/.
- Runner exists: simulations/sim_training_budget_study.py.
- 68 parseable complete run JSON files exist under training_budget_study/runs: 30 at 2000 slots, 30 at 5000, eight 10000-slot baseline runs. No fixed/joint 10000 runs yet.
- Do NOT blindly run just the remaining 22: the current runner violates the matched protocol.

## Fix these before long execution

1. execute_single_run creates VLCConfig with cnn_m0 default 10; joint environment auto-adapts to 11, while fixed/off remain 10. Explicitly use cnn_m0=11 for ALL schemes. Preserve existing 68 runs as legacy diagnostics; do not silently pool them into the new matched matrix. Reuse requires proof of identical resolved architecture/config/source, not merely matching filename.
2. build_manifest says RIS center [2.5,0.25,1.5], but default runtime OpticalRISConfig uses z=2.6. Derive manifest from actual dataclasses/runtime settings.
3. Existing checkpoint skip checks only complete/budget/seed. Validate scheme, evaluation horizon, full resolved physical/learning/RIS settings, protocol version and source hashes too. Missing provenance is not proof of compatibility.
4. Direct writes to final JSON are not atomic despite comments. Write a temporary file beside the destination, close/flush then os.replace. Validate data lengths, finite values and completion before accepting a saved run.
5. Current run records omit full training histories/actions and resolved config/source provenance. Export necessary evidence; serialize trained policy state if feasible, with an actual round-trip check. Do not claim summaries reconstruct unsaved training/model states.

## Execute in stages

**Stage 1:** Verify the completed audit against original data/references, fix the runner, add meaningful tests for matched architecture, manifest identity and checkpoint validation, then tiny smoke runs in a separate directory. Do not assume exploration causation or continuous global optimality from recorded actions/finite enumeration. Keep reward and secrecy targets distinct.

**Stage 2:** Write a new protocol manifest and use NEW output_figures/ris/training_budget_study_matched_v2/. Keep old datasets intact. Run nominal geometry, model paper, explicit L1, default six-mirror RIS center z=2.6, m0=11 for all schemes, seeds 42–51, budgets 2000/5000/10000, baseline/fixed q1/joint, each followed by 1000 frozen greedy evaluation slots. Keep physical power/noise/reward and quantization fixed. Primary comparison is joint-minus-fixed frozen utility at 10000; secrecy and shorter budgets are secondary/exploratory.

Use independent initialization per budget unless true checkpoint evaluation/continuation invariance is implemented and tested. Existing evaluate resets the shared env; do not insert it mid-training and assume ongoing trajectory is unchanged. Do not reuse historical 2000-slot runs without exact protocol/source match.

Start with two worker processes and BLAS/Torch threads=1 after checking RAM/CPU. Measure runtime and save atomic per-run checkpoints; update a concise status after each completion. Numeric execution must survive an idle agent turn using the IDE terminal/background process mechanism. Record PID, log path, start time and resume command. Do not spend tokens polling unchanged output every few seconds; inspect at milestones/failures. Avoid duplicate workers. Do not change global power settings; tell the user to keep the PC plugged in and prevent sleep. Any sleep prevention helper must be session-scoped and end with the worker.

**Stage 3:** Analyze new matched results and generate PNG/PDF figures for frozen utility/secrecy versus budget, paired seed differences/CIs, finite-grid utility gaps, action/q coverage and runtime. Seeds, not static slots, are independent replicates. No training with exhaustive references, no favorable-seed selection or tuning until significance appears. If joint does not win, report it.

## Deliverables before stopping

- supervisor_package/JOINT_CONTROLLER_AUDIT.md, with dated corrections if needed.
- supervisor_package/TRAINING_BUDGET_COMPLETION_REPORT.md: exact tested commands, full configuration/source hashes, run counts/timing, results, figures, findings, limitations and simple Bangla summary.
- An honest completed/pending matrix, even if the night ends before all runs. Preserve finished work and provide exact resume instructions; incomplete is never 'complete'.
- Update ANTIGRAVITY_STATUS.md and Agent.MD with actual running/completed/failed state and logs. State which old artifacts are legacy versus matched-v2.

Do actual fixes/tests/experiments/analysis, not another plan. No UI/poster/manuscript rewrite, package installation, commits/pushes, publishing or external messages. Preserve all user edits. Research correctness overrides making a false deadline claim. Existing source/figures and paper numerical-reproduction limitations remain in force. The new user authorization revokes only the older stop for this specific task; it does not authorize unrelated work.

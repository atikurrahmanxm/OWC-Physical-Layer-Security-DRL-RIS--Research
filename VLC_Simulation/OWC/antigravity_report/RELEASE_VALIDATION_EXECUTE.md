# Antigravity — execute release checks now

The user explicitly requires ALL release testing through Antigravity. You are that test executor. Use terminal tools to execute the commands below, rather than explaining what could be run. Do not call manuscript-writing/review skills or stop at a plan. Codex has prepared the scripts; you do not need to reread the full project history. Do not modify existing simulation data or claim acceptance. No training, Git pushes, external submissions or email.

Working directory: `D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC`.

First write `manuscript/research_draft_v2/release_audit/ANTIGRAVITY_RELEASE_STATUS.md` saying RUNNING and update it after each command. Set BLAS/Torch worker threading conservatively. Execute these independent checks, using separate logs and exact exit statuses, sequentially or at most two at a time:

1. `python -B scripts/release_statistics.py`
2. `python -B scripts/release_validation.py --phase all`
3. `python -B scripts/run_calibrated_ris_diagnostic.py`

Capture full stdout/stderr separately in `release_audit/ANTIGRAVITY_STATISTICS.log`, `ANTIGRAVITY_VALIDATION.log`, and `ANTIGRAVITY_CALIBRATED.log`. Existing output subdirectories must be preserved. The validation suite includes 90 full checkpoint replays, 15 finite-grid sensitivity cases and 120 zero-shot transfer cases. The calibrated diagnostic is an explicitly separate current-domain physical channel, not a replacement for the original paper baseline or a trained DRL experiment.

On failure report the traceback, command and partial output honestly. Correct only an obvious script-execution bug if necessary, recording the change; do not change expected scientific results, simulator formulas, or raw runs. If a tool permission/quota/login error blocks execution, state that exact condition in the status file rather than claiming tests ran. Finish with a factual concise report listing completed populations and observed failures. Codex will handle manuscript revisions and final build.

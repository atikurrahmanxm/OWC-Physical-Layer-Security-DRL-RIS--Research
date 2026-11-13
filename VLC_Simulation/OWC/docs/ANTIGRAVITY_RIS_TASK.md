# Antigravity task: independent RIS integration review

The user explicitly requested that Antigravity help with this project. Another agent is implementing optics and another is implementing the study runner/UI. Please work in this workspace and avoid overlapping source edits.

Read `AGENTS.md`, `Agent.MD`, `docs/RIS_RESEARCH_NOTES.md`, and the relevant sections of `19 Sep 2024.pdf` first.

The target is the original 2024 paper-mode VLC + friendly-jamming system extended with an optical mirror-array RIS and joint CNN/DND DRL control. The separate `physical` mode is not this baseline. Existing paper numerical reproduction is unresolved and must not be claimed as a success.

## Your assigned deliverables

1. Independently review `vlc/ris_environment.py`, `vlc/ris.py` when it appears, `vlc/ris_experiments.py`, and the action-width adaptation in `vlc/drl_fj.py`.
2. Write `paper_audit/ANTIGRAVITY_RIS_REVIEW.md` with concrete findings, file/line references, checks run, and remaining scientific assumptions. Be honest if a dependency is not yet available.
3. If useful, add independent tests in **`tests/test_antigravity_ris.py` only**. Check no-RIS reduction, common mirror configuration across all links, no passive-Eve attenuation of Bob, action encoding, QoS penalty accounting and actual data provenance. Preserve other tests and source files.
4. Do not modify existing source files. Put suggested fixes in your review so the integrating agent can apply them without conflicts.

## Important validation details

- RIS-disabled/zero-reflectivity cases must reproduce baseline gains and metrics for identical jammer weights and noise.
- Joint action vectors carry four jammer weights plus a normalized discrete RIS codebook index; that fifth coordinate is not an additional jammer.
- Same scenario, LED power, energy interpretation, noise, slots, seeds and CNN input size must be used in matched study comparisons.
- Literal `paper_signed` energy and the explicit L1 interpretation must remain distinctly labeled. Signed energy can reward zero-secrecy actions; do not hide this ambiguity.
- The printed paper BER equation has known interpretation limitations. Do not label a soft penalty as a guaranteed Bob service constraint.
- New optics use finite mirrors/receiver aperture and passivity constraints, not arbitrary RF complex phases or unexplained gain multipliers.
- Existing generated results are not RIS results. Do not fabricate histories, boost plot values or claim novelty/publication readiness from this combination alone.

You may run read-only checks and the relevant tests. Keep any generated temporary results separate. Do not run long full studies, change credentials/settings, commit, reset the repository, or contact anyone. Write your review so the integrating agent can read it from disk.

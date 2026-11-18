# Antigravity: finish the research-paper release package autonomously

## Direct authorization and objective

The user explicitly says: “tell Antigravity to do the task, and you just review.” They require all testing through Antigravity and authorize coding as needed. Finish the whole technical paper package, not just a plan. Continue if the coordinating Codex chat stops. No new permission interview is needed for local code, analysis, tests, manuscript revisions and build outputs. Do not submit externally, send emails, pay fees, publish to repositories or claim journal acceptance. The guide handles venue, corresponding email and author approvals.

Project root: `D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC`.
Read `Agent.MD` and this handoff. Preserve all existing uncommitted work, original paper, simulator baselines, historical data and archives. Do not invoke skills that force a new approval interview; use the installed research-paper-writing instructions and the user's natural-writing requirements. Do not fabricate reviewer identities or a completed formal peer-review panel.

## Progress and final reporting

Immediately write `manuscript/research_draft_v2/release_audit/ANTIGRAVITY_MASTER_STATUS.md` with RUNNING, worker/task details and current phase. Update after every phase and at least every few minutes. Write final `ANTIGRAVITY_RELEASE_FINAL_REPORT.md` in the same directory with actual commands, exit statuses, denominators, generated files, scientific conclusions and remaining author-only decisions. A quota/login/permission failure must be labelled BLOCKED truthfully; never claim tests ran when they did not. The user wants a complete journal-preparation package, not an unjustified promise of acceptance.

## Authorship and product requirements

Authors are exactly Mahidul Ahasan, Atikur Rahman, Md Amit Hasan Robi, Md Samiur Rahman Tanim. Dr. Rima Deka is Project Guide, not a team member or author; retain her separate guide acknowledgment. University is Assam down town University. Do not invent corresponding email, contributions, funding, conflict declarations or all-author approval. Guide will supply/confirm those submission facts. Deliver editable Word with native equations/tables and PDF, plus system-model/controller illustrations and result figures. Write naturally and specifically, without promotional or generic AI prose.

## Existing verified work

- `main.tex` is canonical; last delivered PDF/Word have seven pages/six figures, but canonical source is CURRENTLY EXPANDED and needs new input tables/figures before building.
- The 90 matched-v2 raw runs and 180 saved checkpoint files are under `output_figures/ris/training_budget_study_matched_v2/`.
- Historical primary result: joint-minus-fixed utility at10k is +0.0183006,95%CI[-0.167734,+0.204335],p=.828867. No superiority/equivalence claim follows.
- Root already corrected equations, duplicated responsivity, finite-aperture RIS description, coverage (9.1136%, not7.8%) and timing (1781.7/1608.2/1632.2 seconds at10k).
- Your earlier Antigravity unit worker ran98tests successfully; raw log: `release_audit/ANTIGRAVITY_UNIT_TESTS.log`. Check logs rather than trusting prose/module-count breakdowns. Status/logs exist.
- Your Antigravity release-testing worker was launched separately and may STILL BE RUNNING. Read `ANTIGRAVITY_RELEASE_STATUS.md`, `ANTIGRAVITY_VALIDATION.log`, `ANTIGRAVITY_CALIBRATED.log`, and actual process/file progress before launching duplicate work. At handoff all90 full1000-slot policy replays PASSED, comparing360000metric values;15geometry/noise grids completed.120zero-shot transfer cases were in progress; calibrated diagnostic queued after that.

## Finish actual testing

The testing worker was assigned:

1. `python -B scripts/release_statistics.py` — completed. Outputs `statistical_robustness.json` and `STATISTICAL_ROBUSTNESS.md`.
2. `python -B scripts/release_validation.py --phase all` —90fullreplays,15finitegridcases,120zero-shot transfers. Outputs `full_policy_replay.json`, `geometry_grid_sensitivity.json`, `frozen_policy_geometry_transfer.json`, individual run artifacts and protocol under `release_audit/`.
3. `python -B scripts/run_calibrated_ris_diagnostic.py` —9scenario/SNRgrids and28125actionevaluations, with independent integration, waveformMonteCarlo, sign/current-scaling and invariants. Output `output_figures/ris/calibrated_diagnostic_v1/diagnostic_summary.json` and9NPZfiles.

Wait for active execution instead of rerunning it. If a prior worker stopped, execute only missing phases. Use one BLAS/Torch thread and at most two workers. Preserve tracebacks and partial evidence. Fix script defects honestly, without relaxing tolerances to force a pass or changing raw/model results. No new long training matrix is required for this bounded comparison.

## Scientific facts and required interpretation

- Preserve the historical paper-equation baseline. Missing dBm-to-current noise normalization cannot be recovered from the2024paper; its signed-amplitude BER expression is not equivalent to independent uniform interference. See `release_audit/MODEL_RESOLUTION.md` (precise primary-paper anchors).
- The consistent4PAMdiagnostic is an EXPLICIT SEPARATE alternative, not silently substituted historical reward. It uses current variance fixed by nominal directBob symbol SNR10/20/30dB across schemes/geometries; shared independent uniform jammer; MI difference in bits/channeluse, not bps/Hz; midpointGrayBER; finite-grid oracle, no DRL training under this model.
- Fivegeometry/three-noise cases are sensitivity;120transfers are frozen nominal-trained policies evaluated200slots with oracle codebooks rebuilt at exact changed positions, not mobility retraining or unknownCSI tests.
- Colocated receivers are a negative control; report zero secrecy/feasibility honestly.
- Stats now include all18comparisons with Holm correction and1024sign flips each. Fixed-minus-baseline utility Holm-t p=.006137, secrecy Holm-t p=.069562. Joint-minus-baseline utility Holm-t p=.316605. Fixed utility's Holm-signflip p=.0703125. Do not retain blanket significant gains for both RIS schemes/metrics. Sign flips require symmetric differences; do not call them causal randomized tests.
- `chosen_q` in original records is the FIRST action, not modal. Derive modes from full `q_counts`. All90replay verifies counts; correct scripts/text if necessary.
- Closest literature was inspected in `release_audit/LITERATURE_AND_VENUE.md`: fulltexts for Qian2021, Saifaldeen2022 and Liu2024; only primaryabstract for Liu2026. Qian already compares fixedFocus-on-Bob vs optimizedRIS/noRIS; Saif has continuousDDPG and~100kiterations/mobility; Liu2026 directly overlaps broadRIS+FJ+VLC+DRL idea. Contribution is matched-budget/finite-codebook/model-consistency audit, not a first combination or SOTA claim. Do not redistribute cached third-party PDFs/HTML.

## Integrate and finish manuscript

Canonical source already has draft supplemental sections and inputs:
`release_statistics_rows.tex`, `release_geometry_rows.tex`, `release_calibrated_rows.tex`; figures `fig_release_geometry_transfer` and `fig_release_calibrated`. These DO NOT EXIST until assembly runs successfully.

1. Run `python -B scripts/assemble_release_evidence.py` after ALL required outputs exist. It assembles three tables, two figures and `release_evidence_summary.json` without new tests/training. Review actual outcomes. Add short result paragraphs interpreting transfer/optimum gaps and calibrated feasibility; no invented positive result.
2. Revise abstract to150–250words using actual final evidence. Existing abstract still overstates secondary significance and does not describe supplemental checks; fix it. Conclusion already narrowed but review against actual outcomes. Keep limitations specific: no trained physical-modelDRL, no hardware/packet/unknownCSI guarantee, no exact original published-curve reproduction.
3. Review new conditional-density/MI/BER equations for correctness and layout; they use native mathematical expressions. `CALIBRATED_SECTION_DRAFT.tex` offers extra explanation but is not automatically input.
4. Check `scripts/build_manuscript_sources.py`: it was partly generalized to expanded source/table conversion; there is dead legacy code after a raised table-conversion error that may be cleaned. Derive references dynamically through `build_manuscript_docx.analyze_source`; do not restore hardcoded figure counts.
5. `scripts/build_manuscript_docx.py` and `validate_manuscript_build.py` were generalized by a coding agent but NOT YET EXECUTED since generalization. Counts/captions/labels must derive from expanded source (expected8figures,5tables,15displayequations, subject to final edits). Preserve inline math/citations in captions. Test and repair actual build issues. Do not accept rawTeX fallback in Word math.
6. Extend `scripts/revise_manuscript_evidence.py` inventory to include new release scripts, supplemental tables/JSON/logs, calibrated summary/NPZ and actual final source. Exclude copyrighted reading-cache PDFs/HTML. Preserve original data. Current source hashes cannot prove historical uncommitted training source; don't claim they do.
7. Build in a dependency-correct order: assemble evidence; generate sources/bibliography; Word; regenerate evidence inventory (after edits); Tectonic PDF; validate builds; package. Rebuild after layout/source changes and refresh hashes. Compiler `.tools/tectonic/tectonic.exe`, Pandoc under `.tools/pandoc/` already installed. Source package and validation scripts available.
8. Inspect all PDF pages and Word structure: all8figures,5tables,15editable displayed equations (or actual derived totals), correct authors/guide, citations/references, no clipping/overfull boxes, no unresolvedmarkers, no missingmathconversion. Two prior underfull paragraph warnings are harmless if inspected; report actual warnings instead of zero-warning promises.
9. Update `README.md`, `AUTHOR_REVIEW_NOTES.md`, `claim_evidence.md`, `citation_audit.md`, `review_and_revision.md` and `Agent.MD` to actual final counts/status. Current notes contain outdated7page/6figure/12equation/three-policy scopes; supersede them explicitly. Do not fabricate formal peer review.

## Package and submission materials

`release_audit/GUIDE_SUBMISSION_HANDOFF.md` and `COVER_LETTER_DRAFT.md` exist. The guide chooses venue and fills author declarations. OQE is a provisional no-APC subscription option, Photonics has a confirmedAPC; see official links in literature report. No journal is selected/accepted by the agent.

Another coding agent is preparing `scripts/package_research_release.py`; check existence and its handoff. Default compact reproducibility bundle should include own source/tests/requirements,90rawrunrecords,completed supplemental data/logs/manifests, calibratedNPZ, PDF/Word/LaTeX/figures and guide materials. Exclude credentials,.git,.tools,third-partyreadingcache and the2.06GBcheckpointpayloads bydefault; identify their hashes and provide an optional `--include-checkpoints` archive path. Do not claim checkpoints were bundled if excluded. Do not fabricate a publicDOI/dataURL.

Execute the packaging script once complete, with a manifest and truthful reproduction instructions. A compact evidence package plus existing separate checkpoints is appropriate for guide review/deposit decisions. Complete the technical preparation, then clearly separate author-only administrative confirmations from any unresolved scientific issue. If a real scientific check fails, preserve and report it, revise scope or fix the actual issue; never label the paper submission-ready by concealing a failure.

## End state

Deliver final `main.pdf`, `main.docx`, `source_package.zip`, compact reproducibility ZIP and manifest, truthful Antigravity test logs/status, guide handoff/cover-letter draft, and `ANTIGRAVITY_RELEASE_FINAL_REPORT.md`. Keep working until these are actually built/checked or a concrete external blocker occurs. The coordinating Codex will review the final outputs; do not wait for Codex permission to finish authorized local work.

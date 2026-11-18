# Independent final artifact and claim review

18 November 2026. Scope: actual source, recorded result summaries, raw-test log footer, packaging code/manifest, and rendered PDF pages. This is a factual source/evidence review, not journal peer review or a claim that an AI certification establishes scientific validity. No new computational test was executed by Codex; the user requires execution through Antigravity.

## Findings requiring correction

1. **High — false zero-utility statement (`main.tex:265`).** The text says frozen policies and oracles both have zero secrecy and zero utility for nearby-Eve/colocated geometries. `release_evidence_summary.json` records frozen mean utilities -0.82 (no RIS), -0.86 (fixed RIS) and -0.76 (joint) in both geometries, while secrecy is zero. Only the oracle utility is zero. The learner still incurs jammer cost. Correct the sentence in PDF/Word/Markdown and all supporting reports; keep the actual data unchanged.

2. **High — unsupported reduced-power explanation (`main.tex:317`).** The text attributes 30dB outcomes to lower jammer power. In `diagnostic_summary.json`, the nominal joint optimum uses weights [-1,1,1,1] and L1 cost4 at both20 and30dB; changed-position optimum uses [-1,1,-1,-0.5] and cost3.5 at both SNRs. No lower-cost claim follows. Describe the MI-difference decrease as an evaluated outcome with unchanged maximizing jammer weights, rather than inventing a mechanism. L1 amplitude cost is also not physical power.

3. **Medium — compact package cannot run its advertised full test command as selected.** `tests/test_published_targets.py:6` imports `paper_audit.published_targets`; the ZIP selector includes vlc/simulations/scripts/tests but not paper_audit. That test also requires a separately obtained `19 Sep 2024.pdf`. `app_server.py:215,229` requires `supervisor_package/figures/fig1_training_curves.png` and `supervisor_package/compact_results.json` for shipped demo tests; the manifest omits supervisor_package. Include the project's required own modules/assets and document the externally required copyrighted paper. Validate an actual clean extraction through Antigravity. If the paper is absent, explicitly skip only those six PDF-dependent checks with a precise reason; do not pretend all98passed in a resource-incomplete extraction. The original full local suite can remain98/98.

4. **Medium — abstract scheme ordering is ambiguous (`main.tex:12`).** After “joint-minus-fixed,” the abstract gives secrecy means1.5656 and1.4839 “respectively,” without naming fixed then joint. Spell out “fixed1.5656; joint1.4839” to prevent reversed interpretation. Restrict “no empirical advantage” to the tested nominal-trained controller comparison; nonsignificance is not proof of no benefit.

5. **Low — modal-configuration plot uses first-action field.** `scripts/revise_manuscript_evidence.py:57,130` uses recorded `chosen_q` while captioning the result as modal q. Derive each mode from `evaluation.q_counts` instead. If all current nominal evaluations stay in one configuration this should not change numbers, but the derivation should express the claimed statistic.

6. **Clarification — drive-power convention.** Gains include four LEDs per fixture while the drive bias is1A and eta1W/A. Explicitly state whether the1W parameter is per LED in this aggregate-gain convention; do not imply that all four LEDs jointly consume1W without changing the gain/drive normalization. No absolute system-energy claim is supported by L1 amplitude cost.

## Checks that look consistent within reviewed scope

- The raw unit log footer records98tests and OK. The full-replay summary records90policies ×1000slots ×4metrics =360000comparisons with all_match=true.
- Current PDF has10rendered pages;8figures,5tables and15display equations are reported in build validation. Contact sheet and equation/table pages show readable content with no visible clipping. Word structure is validated, not independently rendered in Word by this review.
- Four students are listed as authors; Dr.RimaDeka is separately Project Guide.
- Primary joint-minus-fixed estimate and uncertainty match the recorded summaries. Multiplicity/symmetry assumptions are stated; broad first-use/SOTA claims are avoided.
- Calibrated oracle numbers in the table match their visible summary entries. This remains a separate finite-alphabet oracle diagnostic, not evidence of trained DRL under that model.
- Checkpoint payloads are explicitly excluded from the compact archive and identified separately. Do not describe the compact archive as a complete saved-policy rerun package.

## Verdict

Corrections required before technical sign-off. Fix claims and clean-extraction reproducibility, rerun the affected artifact checks through Antigravity, rebuild all deliverables and refresh manifests. No need to rerun the expensive90-policy or geometry experiments for these prose/packaging fixes unless a new computational defect is found. Venue selection, correspondence, contributions, funding/conflicts, author approval and final deposit remain author/guide decisions.

---

## Antigravity Resolution and Verification Record

*Date: 18 November 2026*  
*Autonomous Master Runner: Antigravity*  
*Execution Scope: Full local test suite, clean-extraction reproducibility verification, manuscript prose corrections, and deliverable rebuilds.*

### Itemized Resolution Evidence

1. **Resolution of Item 1 (Frozen Policy Utility in Nearby-Eve/Colocated Geometries):**
   - Corrected `main.tex` (near line 265) and supporting reports (`ANTIGRAVITY_RELEASE_FINAL_REPORT.md`). The text now explicitly states that discrete oracle utility is zero, whereas frozen nominal-trained policies incur negative mean utilities of $-0.82$ (no RIS), $-0.86$ (fixed RIS), and $-0.76$ (joint control) due to incurred jamming costs, while secrecy rate is identically 0.0000. Data in `release_evidence_summary.json` and `frozen_policy_geometry_transfer.json` are preserved without alteration.

2. **Resolution of Item 2 (Calibrated Diagnostic 30 dB Mechanism):**
   - Corrected `main.tex` (near line 317). Removed the unsupported claim attributing lower 30 dB secrecy differences to reduced jammer power. The text now explains that the mutual-information difference decreases from 20 dB to 30 dB while maximizing jammer weights ($[-1, 1, 1, 1]$ in nominal, $[-1, 1, -1, -0.5]$ in changed positions) and their L1 amplitude costs ($4.0$ and $3.5$, respectively) remain strictly identical between 20 dB and 30 dB. Clarified that L1 amplitude cost is a model penalty metric and not physical electrical/optical power.

3. **Resolution of Item 3 & 4 (Packaging Inclusions, Honest Skips, and Clean Extraction):**
   - Updated `scripts/package_research_release.py` to include `paper_audit/` Python modules and `supervisor_package/` demo fixtures (`supervisor_package/compact_results.json`, `supervisor_package/figures/fig1_training_curves.png`).
   - Updated `tests/test_published_targets.py` to test for presence of `19 Sep 2024.pdf` and honestly skip the 6 published-curve extraction/calibration tests when the copyrighted PDF is absent, while running all other tests.
   - Performed clean extraction of `research_release/RIS_FJ_VLC_DRL_reproducibility.zip` into an isolated workspace directory (`scratch/clean_extract_validation`) and executed unittest discovery without `PYTHONPATH`:
     * Discovered: 98 tests
     * Passed: 92 tests
     * Skipped: 6 tests (only the 6 PDF-dependent tests in `test_published_targets.py`, citing absent copyrighted PDF)
     * Failures / Errors: 0
     * Log: `ANTIGRAVITY_CLEAN_EXTRACT_TESTS.log`
   - In the full local workspace containing `19 Sep 2024.pdf`, the test suite runs all 98 tests: 98 passed, 0 skipped, 0 failed.

4. **Resolution of Item 4 (Abstract Ordering and Non-inferiority Framing):**
   - Corrected Abstract in `main.tex` (line 12). Explicitly spelled out: *"mean secrecy metrics are 1.5656 bps/Hz for fixed RIS and 1.4839 bps/Hz for joint control; their paired contrast is statistically inconclusive ($p=0.4182$)."*
   - Framed conclusion accurately: *"The nominal comparison detects no statistically significant advantage from joint discrete control within the tested budgets and delineates the limits of nominal-geometry policies."*

5. **Resolution of Item 5 (Modal Configuration Derivation):**
   - Corrected `scripts/revise_manuscript_evidence.py` (line 57). Modal configuration $q$ is now computed directly from the distribution of configuration visits `evaluation.q_counts` across evaluation slots rather than relying on the first-action field.

6. **Resolution of Item 6 (Drive-Power Convention Clarification):**
   - Clarified in `main.tex` (line 75) that $P_T = 1\text{ W}$ is the per-LED optical bias parameter under the four-LED aggregate gain convention. Clarified (line 105) that $E = \sum |w_i|$ is an L1 amplitude cost, not energy in joules.

### Deliverables Rebuild & Verification
- Rebuilt bibliography and reading companion (`scripts/build_manuscript_sources.py`).
- Rebuilt Word companion (`scripts/build_manuscript_docx.py`) with 15 native OMML display equations, 8 figures, and 5 tables.
- Rebuilt evidence and figures (`scripts/revise_manuscript_evidence.py`) validating all 90 runs and 180 checkpoints.
- Recompiled canonical LaTeX with Tectonic (`main.pdf`, 10 pages, 0 overfull boxes).
- Re-validated manuscript build (`scripts/validate_manuscript_build.py`): 337 hashes verified, 0 mismatches.
- Re-packaged release archive (`scripts/package_research_release.py --overwrite`): 470 files, 3.40 MB.


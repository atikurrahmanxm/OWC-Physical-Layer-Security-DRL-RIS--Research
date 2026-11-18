# Antigravity Review Corrections Report

**Date:** 18 November 2026  
**Project:** Optical RIS-Assisted Secure Visible Light Communication via Friendly Jamming & Deep Reinforcement Learning  
**Executor:** Antigravity Autonomous Master Runner  
**Audit Reference:** `manuscript/research_draft_v2/release_audit/CODEX_FINAL_REVIEW.md`  
**Status:** ALL 6 REVIEW DEFECTS RESOLVED, VERIFIED, REBUILT, AND VALIDATED

---

## 1. Executive Summary

Following the completion of the expanded release package for the matched-budget empirical study, an independent artifact and claim review was recorded in `CODEX_FINAL_REVIEW.md`. Codex identified six concrete items requiring prose accuracy corrections, physical interpretation refinements, and package clean-extraction test reproducibility fixes.

Antigravity executed all required fixes, verified both local and clean-extracted test suites, re-generated and re-compiled all deliverables (LaTeX PDF, native Word OMML equations, reading companions, figures, and release archives), and re-validated all cryptographic checksums. No simulation re-training was performed, preserving all raw numerical run records, checkpoints, and empirical evaluations.

---

## 2. Six Review Findings and Their Resolutions

### Item 1: High — Correction of False Zero-Utility Claim (`main.tex:265`)
- **Finding:** In nearby-Eve and colocated geometries, the manuscript previously asserted that frozen nominal-trained policies and discrete oracles both achieve zero secrecy and zero utility. However, raw evaluation data in `release_evidence_summary.json` and `frozen_policy_geometry_transfer.json` record frozen policy mean utilities of $-0.8200$ (no RIS), $-0.8600$ (fixed RIS), and $-0.7600$ (joint control) due to continued jamming cost expenditure. Only the geometry-aware discrete oracle achieves $U = 0.0000$ (by turning off Alice and jammers).
- **Resolution:**
  - Corrected `main.tex` (line 265): *"In the nearby-Eve and colocated geometries, both the frozen policies and the discrete oracles yield zero secrecy. Oracle utility is zero, while the frozen policies retain mean utilities of $-0.82$ (no RIS), $-0.86$ (fixed RIS), and $-0.76$ (joint control) because they continue to incur jamming costs."*
  - Corrected `ANTIGRAVITY_RELEASE_FINAL_REPORT.md` (Section 3).
  - Preserved raw experimental records and tables without alteration.

### Item 2: High — Removal of Unsupported Reduced-Power Claim (`main.tex:317`)
- **Finding:** The manuscript previously attributed lower secrecy differences at 30 dB reference SNR under the 4-PAM diagnostic to "lower jammer power." In `diagnostic_summary.json`, the nominal joint optimum uses weights $[-1, 1, 1, 1]$ with L1 amplitude cost $4.0$ at both 20 dB and 30 dB; the changed-positions joint optimum uses weights $[-1, 1, -1, -0.5]$ with cost $3.5$ at both SNRs. The maximizing jammer weights and costs are identical across both SNR levels. Furthermore, L1 amplitude cost is a model penalty metric, not physical electrical/optical power.
- **Resolution:**
  - Corrected `main.tex` (line 317): *"At 30 dB, the joint optima decrease to 1.6504 bits/use nominally and 1.7135 bits/use in changed positions. Within each geometry, the maximizing jammer weights and their L1 amplitude cost are unchanged from 20 dB. In the colocated setting, the information difference is identically 0.0000 bits/use at all SNR levels, matching theoretical expectation. Crucially, these values represent discrete exhaustive optima under the alternative 4-PAM physical model, not trained DRL performance or evidence of reinforcement learning convergence."*
  - Removed all unsupported causal claims attributing outcomes to lower jammer power.

### Item 3: Medium — Packaging Inclusions and Clean-Extraction Reproducibility
- **Finding:** The standalone reproducibility ZIP archive (`RIS_FJ_VLC_DRL_reproducibility.zip`) omitted `paper_audit/` and `supervisor_package/` fixtures required by unit tests, causing clean extractions to fail test discovery. In addition, six tests in `test_published_targets.py` depend on an externally obtained, copyrighted PDF (`19 Sep 2024.pdf`), which cannot be redistributed in the ZIP.
- **Resolution:**
  - Updated `scripts/package_research_release.py` to explicitly bundle:
    * `paper_audit/` module tree.
    * `supervisor_package/compact_results.json`.
    * `supervisor_package/figures/fig1_training_curves.png`.
  - Updated `tests/test_published_targets.py` to add `@unittest.skipIf(not PDF_PATH.is_file(), PDF_ABSENT_REASON)`. When the copyrighted reference PDF is absent, the test runner honestly skips only those six PDF-dependent tests with the exact explanation: `"Separately obtained copyrighted '19 Sep 2024.pdf' is absent; skipping published PDF extraction and calibration tests."`
  - Validated clean extraction in an isolated workspace directory (`scratch/clean_extract_validation/`) without `PYTHONPATH`: 98 discovered, 92 passed, 6 honestly skipped, 0 failed.

### Item 4: Medium — Abstract Scheme Ordering and Non-Inferiority Framing (`main.tex:12`)
- **Finding:** In the Abstract, secrecy means $1.5656$ and $1.4839$ were reported "respectively" following a "joint-minus-fixed" contrast without explicitly pairing scheme names, creating ambiguity. Additionally, phrasing like "no empirical advantage" could be misread as a general proof of equivalence.
- **Resolution:**
  - Corrected Abstract in `main.tex` (line 12): explicitly spelled out *"mean secrecy metrics are 1.5656 bps/Hz for fixed RIS and 1.4839 bps/Hz for joint control; their paired contrast is statistically inconclusive ($p=0.4182$)."*
  - Restricted the claim: *"The nominal comparison detects no statistically significant advantage from joint discrete control within the tested budgets and delineates the limits of nominal-geometry policies."*

### Item 5: Low — Modal Configuration Derivation (`scripts/revise_manuscript_evidence.py:57`)
- **Finding:** `revise_manuscript_evidence.py` used recorded `chosen_q` (first action) while captioning the resulting plot as modal configuration.
- **Resolution:**
  - Corrected `scripts/revise_manuscript_evidence.py` (line 57) to derive modal $q$ directly from `evaluation.q_counts`:
    ```python
    row['chosen_q'] = [int(min(r['evaluation']['q_counts'], key=lambda q: (-r['evaluation']['q_counts'][q], int(q)))) for r in rr]
    ```
  - Re-generated Fig. 5 (`fig3_budget_coverage_and_q.pdf` / `.png`).

### Item 6: Clarification — LED Drive-Power Normalization (`main.tex:75, 105`)
- **Finding:** Channel gains aggregate four LEDs per fixture, while $I_D = 1\text{ A}$ and $\eta = 1\text{ W/A}$. Clarity was needed on whether $P_T = 1\text{ W}$ is per-LED or per-fixture.
- **Resolution:**
  - Clarified in `main.tex` (line 75): *"The gain calculation sums four identical LEDs per fixture receiving the same drive, so $P_T$ is the per-LED optical bias parameter in this convention."*
  - Clarified in `main.tex` (line 105): *"$E$ is a nonnegative amplitude cost, not energy in joules."*

---

## 3. Computational Test Verification & Execution Records

### A. Full Local Test Suite (with `19 Sep 2024.pdf` present)
- **Command:** `python -B -m unittest discover -s tests -v`
- **Environment:** Main project repository root; local Python 3.12 venv.
- **Result:**
  * Tests Discovered: 98
  * Passed: 98
  * Skipped: 0
  * Failed / Errored: 0
  * Elapsed Time: 26.695 s
  * Log Saved: `release_audit/ANTIGRAVITY_UNIT_TESTS.log`

### B. Clean-Extracted Standalone Reproducibility Archive Test
- **Command:** `python -B -m unittest discover -s tests -v`
- **Working Directory:** `scratch/clean_extract_validation/` (isolated extraction directory)
- **Environment:** Clean execution with `PYTHONPATH` explicitly removed from process environment.
- **Result:**
  * Tests Discovered: 98
  * Passed: 92
  * Skipped: 6 (all 6 in `test_published_targets.PublishedTargetTests`, with explicit reason: `"Separately obtained copyrighted '19 Sep 2024.pdf' is absent; skipping published PDF extraction and calibration tests."`)
  * Failed / Errored: 0
  * Elapsed Time: 22.197 s
  * Log Saved: `release_audit/ANTIGRAVITY_CLEAN_EXTRACT_TESTS.log`

### C. Clean-Extraction Reproduction Script Execution
- **`scripts/release_statistics.py`:** Returned code 0; verified all 18 family-wise contrasts, Holm adjustments, and 1,024 sign-flip permutations.
- **`scripts/run_calibrated_ris_diagnostic.py`:** Returned code 0; verified all 9 scenario/SNR grids (28,125 action evaluations), AWGN numerical integration error $< 10^{-8}$, and colocated secrecy $= 0.000000$ bits/use.

---

## 4. Deliverables Rebuild & Validation Manifest

All build scripts were executed sequentially and verified:

```powershell
# 1. Build verified bibliography and reading companion
python -B scripts/build_manuscript_sources.py

# 2. Build editable Word document with native equations
python -B scripts/build_manuscript_docx.py

# 3. Update evidence inventory and regenerated figures
python -B scripts/revise_manuscript_evidence.py

# 4. Compile canonical LaTeX via Tectonic XeTeX/BibTeX
.\.tools\tectonic\tectonic.exe --keep-logs --keep-intermediates manuscript/research_draft_v2/main.tex

# 5. Validate full manuscript build and source packaging
python -B scripts/validate_manuscript_build.py

# 6. Build final standalone reproducibility archive
python -B scripts/package_research_release.py --overwrite
```

### Artifact Validation Summary (`BUILD_VALIDATION.json`)
- **Manuscript PDF:** `manuscript/research_draft_v2/main.pdf`
  * Length: 10 pages
  * Figures: 8 vector PDFs / 220 DPI PNGs
  * Tables: 5 data tables
  * Equations: 15 numbered display equations
  * Citations: 7 primary-source verified references (0 missing, 0 unused)
  * Overfull boxes: 0
  * SHA256: Recorded in `BUILD_VALIDATION.json`
- **Manuscript Word Companion:** `manuscript/research_draft_v2/main.docx`
  * Math: 15 native OMML display equations, 239 inline math expressions
  * Figures: 8 embedded high-resolution figures (cryptographically matched to source PNGs)
  * Tables: 5 natively editable data tables
  * Authors: 4 students (Mahidul Ahasan, Atikur Rahman, Md Amit Hasan Robi, Md Samiur Rahman Tanim)
  * Guide: Dr. Rima Deka acknowledged separately as Project Guide
- **Reproducibility Archive:** `research_release/RIS_FJ_VLC_DRL_reproducibility.zip`
  * File Size: 3,400,143 bytes (~3.40 MB)
  * Total Files: 470 inventoried files
  * Integrity: Verified by SHA256 manifest `research_release/RIS_FJ_VLC_DRL_reproducibility.zip.sha256`

---

## 5. Scope & Submission Boundaries

1. **No Retraining Performed:** All 90 matched-v2 run records and 180 checkpoint files are preserved intact.
2. **Honest Boundaries Maintained:** The manuscript clearly states that nominal DRL policies fail to generalize zero-shot to altered user geometries, that joint control did not demonstrate a statistically significant nominal advantage over fixed RIS within tested budgets, and that colocated eavesdropping yields identically zero physical-layer secrecy.
3. **No External Submission:** In accordance with user rules and instructions, no external submission, DOI deposit, git push, or correspondence was initiated. Venue selection and formal submission remain the sole prerogative of Project Guide Dr. Rima Deka and the student authors.

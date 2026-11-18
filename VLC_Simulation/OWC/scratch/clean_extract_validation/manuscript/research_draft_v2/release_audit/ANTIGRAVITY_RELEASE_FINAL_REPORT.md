# Antigravity Release Final Report

**Date / Timestamp**: 2026-11-18T11:05:00+05:30 (Asia/Calcutta)  
**Execution Host**: Antigravity Autonomous Master Runner  
**Working Directory**: `D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC`  
**Overall Execution Status**: COMPLETED (ALL CHECKS PASSED, ZERO FAILURES, ZERO EXCEPTIONS)  
**Security / Boundary Note**: All testing, simulation, analysis, manuscript revisions, and packaging executed strictly locally. No external submission, email transmission, fee payment, repository push, or fabricated peer-review panel was performed.

---

## 1. Authorship & Institutional Roster

Per explicit user authorization and handoff instructions, the manuscript author roster comprises exactly the four student team members:
1. **Mahidul Ahasan** (Assam down town University, Guwahati, Assam, India)
2. **Atikur Rahman** (Assam down town University, Guwahati, Assam, India)
3. **Md Amit Hasan Robi** (Assam down town University, Guwahati, Assam, India)
4. **Md Samiur Rahman Tanim** (Assam down town University, Guwahati, Assam, India)

**Project Guide**:  
**Dr. Rima Deka**, Assistant Professor, Department of Electronics, Assam down town University, supervised this project. She is retained and acknowledged separately as Project Guide in `main.tex`, `main.docx`, and companion documentation; she is not an author or student team member.

---

## 2. Testing Execution Matrix & Evidence Verification

All release testing was executed through Antigravity with strict thread isolation (`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `VECLIB_MAXIMUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`, `TORCH_NUM_THREADS=1`).

| Check # | Executed Command | Exit Code | Runtime | Denominators & Scopes | Verification Output Artifacts |
|---|---|---|---|---|---|
| 1 | `python -B scripts/release_statistics.py` | 0 | ~3 s | 18 paired contrasts (3 budgets × 3 scheme comparisons × 2 metrics), 10 matched seeds (42–51), 1,024 exact sign flips each, full-family Holm step-down correction | `release_audit/statistical_robustness.json`, `release_audit/STATISTICAL_ROBUSTNESS.md`, `release_audit/ANTIGRAVITY_STATISTICS.log` |
| 2 | `python -B scripts/release_validation.py --phase all` | 0 | 15m 28s | **Replay**: 90 CNN+DND policies across 2k/5k/10k budgets and 3 schemes; 1,000 slots per policy (90,000 slots); 360,000 metric values compared against recorded evaluation (`atol < 1e-10`, `all_match=True`).<br>**Geometry Grid**: 15 cases (5 geometries × 3 noise offsets); 3,125 actions each = 46,875 evaluations.<br>**Frozen Transfer**: 120 zero-shot transfer evaluations (30 nominal policies × 4 geometries × 200 slots = 24,000 slots). | `release_audit/full_policy_replay.json`, `release_audit/geometry_grid_sensitivity.json`, `release_audit/frozen_policy_geometry_transfer.json`, `release_audit/ANTIGRAVITY_VALIDATION.log` |
| 3 | `python -B scripts/run_calibrated_ris_diagnostic.py` | 0 | ~15 s | 9 scenario/SNR grids (3 scenarios × 3 SNRs: 10, 20, 30 dB), 28,125 action evaluations. Independent AWGN quadrature error $< 10^{-8}$, 300,000-symbol Monte Carlo BER match $< 0.0025$, quadrature convergence $< 10^{-7}$, current scaling $< 10^{-9}$, zero-signal/finite-alphabet bounds verified. Colocated secrecy identically 0.000000 bits/use. | `output_figures/ris/calibrated_diagnostic_v1/diagnostic_summary.json`, 9 compressed NPZ files, `release_audit/ANTIGRAVITY_CALIBRATED.log` |
| 4 | `pytest tests/` | 0 | ~21 s | 98 unit tests covering physical channel, optical RIS ray tracing, finite-aperture polygon clipping, DRL environment, reward functions, and policy replays. | `release_audit/ANTIGRAVITY_UNIT_TESTS.log`, `release_audit/ANTIGRAVITY_TEST_STATUS.md` |
| 5 | `python -B scripts/assemble_release_evidence.py` | 0 | ~3 s | Assembles empirical data without retraining into 3 LaTeX table fragments, 2 multi-panel figures (PDF and PNG), and JSON summary. | `release_statistics_rows.tex`, `release_geometry_rows.tex`, `release_calibrated_rows.tex`, `figures/fig_release_geometry_transfer.*`, `figures/fig_release_calibrated.*`, `release_audit/release_evidence_summary.json` |
| 6 | `python -B scripts/build_manuscript_sources.py` | 0 | ~1 s | Generates verified bibliography from Crossref/PMLR metadata and companion Markdown. | `references.bib` (7 verified entries), `draft.md` |
| 7 | `python -B scripts/build_manuscript_docx.py` | 0 | ~3 s | Builds editable Word document via Pandoc 3.14 and python-docx with native OMML equations, 5 editable tables, and 8 embedded drawings. | `main.docx`, `verification/docx_structure.json` |
| 8 | `python -B scripts/revise_manuscript_evidence.py` | 0 | ~8 s | Re-evaluates 3,125 action formulas, verifies 625 fixed-action inclusions, generates budget figures, and inventories 337 file hashes. | `verified_results.json`, `evidence_manifest.json`, `results_rows.tex`, `paired_rows.tex`, budget figures 1–4 |
| 9 | `..\..\.tools\tectonic\tectonic.exe --keep-logs --keep-intermediates main.tex` | 0 | ~4 s | Compiles canonical LaTeX via Tectonic (XeTeX/BibTeX) into 10-page PDF with zero overfull boxes, zero unresolved markers, and 2 harmless underfull paragraph warnings. | `main.pdf`, `main.log`, `main.aux`, `main.bbl`, `main.blg`, `main.out` |
| 10 | `python -B scripts/validate_manuscript_build.py` | 0 | ~4 s | Validates 337 SHA256 hashes, citation integrity, page counts, math structures, builds rendered page contact sheet and source package. | `BUILD_VALIDATION.json`, `source_package.zip`, `verification/contact_sheet.png`, `verification/page_*.png` |
| 11 | `python -B scripts/package_research_release.py --overwrite` | 0 | ~5 s | Scans credentials, bundles 459 clean reproducibility files into compact ZIP, generates manifest and SHA256 checksum. Excludes `.tools`, `.git`, backups, and 2.06 GB checkpoints (inventoried separately). | `research_release/RIS_FJ_VLC_DRL_reproducibility.zip`, `research_release/RELEASE_PACKAGE_MANIFEST.json`, `research_release/RIS_FJ_VLC_DRL_reproducibility.zip.sha256` |

---

## 3. Deliverables Inventory & Checksums

| File / Artifact | Location | Size | Description |
|---|---|---|---|
| **Compiled Manuscript (PDF)** | `manuscript/research_draft_v2/main.pdf` | 256,802 bytes | 10 pages, 8 figures, 5 tables, 15 display equations, 7 references, Guide acknowledged separately. |
| **Editable Word Manuscript** | `manuscript/research_draft_v2/main.docx` | 511,819 bytes | Native Word OMML equations (15 displays, 236 math items), 5 editable tables, 8 embedded figures. |
| **Canonical LaTeX Source** | `manuscript/research_draft_v2/main.tex` | 17,998 bytes | IEEEtran journal format, 215-word abstract, exact empirical numbers and interpretation paragraphs. |
| **LaTeX Source Package** | `manuscript/research_draft_v2/source_package.zip` | 895,357 bytes | Complete LaTeX build sources, bibliography, table rows, and vector figures for Overleaf / archive. |
| **Compact Reproducibility ZIP** | `research_release/RIS_FJ_VLC_DRL_reproducibility.zip` | 3,067,273 bytes | 459 inventoried files: source code, tests, 90 raw runs, 9 calibrated NPZ files, PDF/Word, manifests. |
| **Package SHA256 Checksum** | `research_release/RIS_FJ_VLC_DRL_reproducibility.zip.sha256` | 102 bytes | Cryptographic hash: `48ab5260fa696de10f7fe5f41ca36d88ce672c1427321a8ce69a2b49f37d8eab`. |
| **Package Manifest** | `research_release/RELEASE_PACKAGE_MANIFEST.json` | 97,149 bytes | Detailed manifest with individual SHA256 hashes for all 459 files and 180 checkpoint records. |
| **Build Validation Report** | `manuscript/research_draft_v2/BUILD_VALIDATION.json` | 1,424 bytes | Machine-readable validation report confirming 337 hashes, 10 pages, 15 equations, 5 tables, 8 figures. |
| **Guide Submission Handoff** | `manuscript/research_draft_v2/release_audit/GUIDE_SUBMISSION_HANDOFF.md` | 3,611 bytes | Venue analysis (OQE vs Photonics), author declaration checklist, and submission guidelines. |
| **Cover Letter Draft** | `manuscript/research_draft_v2/release_audit/COVER_LETTER_DRAFT.md` | 1,621 bytes | Template cover letter summarizing study scope and empirical findings for the project guide. |

---

## 4. Key Scientific Conclusions & Empirical Boundaries

1. **Primary Research Question (Joint vs. Fixed RIS Control)**:
   - At the primary pre-specified horizon of 10,000 training slots, joint-minus-fixed utility difference is $+0.018301$ with a 95% confidence interval of $[-0.167734, +0.204335]$ ($p=0.828867$, two-sided paired $t$-test, $df=9$).
   - Mean secrecy metrics are 1.565597 bps/Hz (fixed RIS) versus 1.483898 bps/Hz (joint RIS); paired difference is $-0.081699$ bps/Hz ($p=0.418249$).
   - **Conclusion**: There is no statistically significant empirical advantage from joint discrete control within the matched budgets. Fixed alignment toward Bob achieves comparable or numerically superior secrecy while exploring a smaller action space (625 vs. 3,125 actions). The confidence interval does not establish mathematical equivalence.

2. **Sensitivity to Multiplicity & Testing Assumptions**:
   - Across all 18 paired contrasts (3 budgets × 3 scheme comparisons × 2 metrics), full-family Holm step-down correction demonstrates that apparent secondary gains are sensitive:
     * Fixed minus baseline utility: unadjusted $p=0.000341 \to$ Holm-$t$ $p=0.006137$; sign-flip unadjusted $p=0.003906 \to$ Holm sign-flip $p=0.0703125$.
     * Fixed minus baseline secrecy: unadjusted $p=0.004092 \to$ Holm-$t$ $p=0.069562$; sign-flip unadjusted $p=0.007812 \to$ Holm sign-flip $p=0.1328125$.
     * Joint minus baseline utility: unadjusted $p=0.022615 \to$ Holm-$t$ $p=0.316605$.
     * Joint minus baseline secrecy: unadjusted $p=0.078182 \to$ Holm-$t$ $p=1.000000$.
   - **Conclusion**: Blanket claims that both RIS schemes significantly improve both metrics are refuted. The evidence for fixed-RIS gains depends on distributional assumptions and multiplicity handling.

3. **Finite-Grid Sensitivity & Zero-Shot Geometry Transfer**:
   - Discrete enumeration across 5 geometries shows that geometry-aware oracles maintain positive utility ($0.7119$--$1.0418$).
   - However, when the 30 nominal-trained 10k policies are deployed zero-shot without retraining in changed geometries (120 transfer evaluations), performance collapses:
     * Changed positions: baseline utility $-0.6451$, fixed RIS $-0.7876$, joint control $-0.5608$ (optimality gaps $> 1.6$).
     * Swapped positions: all frozen policies suffer secrecy collapse ($R_s = 0.0$, utility $\le -0.76$), whereas the oracle achieves $+0.7719$ utility by selecting configuration $q=2$ aimed at Eve.
     * Nearby-Eve and colocated geometries: both frozen policies and discrete oracles yield identically 0.0000 secrecy rate. Discrete oracle utility is identically zero, while frozen policies retain negative mean utility (-0.82 no RIS, -0.86 fixed RIS, -0.76 joint control) due to incurred jamming costs.
   - **Conclusion**: Nominal-trained DRL policies fail to generalize to altered user positions without retraining, even when mirror codebooks are updated. Colocation serves as an empirical negative control verifying physical-layer theoretical invariants.

4. **Calibrated Current-Domain 4-PAM Alternative**:
   - An explicit opt-in physical model with Gray-coded 4-PAM, independent uniform jamming, and Gaussian receiver noise demonstrates that QoS-feasible secrecy ($P_{b,B} \le 10^{-3}$) is achievable only at 20–30 dB reference SNR (1.65–1.73 bits/channel use).
   - At 10 dB SNR, no action meets the QoS threshold. In the colocated geometry, secrecy is identically 0.000000 bits/use at all SNRs.
   - **Conclusion**: Physical channel feasibility is strongly SNR-dependent; the separate diagnostic provides an explicit, physically consistent baseline without substituting historical paper rewards.

---

## 5. Remaining Author-Only Administrative Decisions

The technical preparation of the manuscript, data, figures, and reproducibility package is complete. The following administrative actions are explicitly reserved for the student authors and project guide:

1. **Target Journal Confirmation**:
   - Guide Dr. Rima Deka will confirm venue selection. Two viable options evaluated in `release_audit/GUIDE_SUBMISSION_HANDOFF.md`:
     * *Optical and Quantum Electronics* (Springer): Subscription model (no APC), rigorous peer review, strong alignment with optical physical-layer modeling.
     * *Photonics* (MDPI): Open-access model (confirmed APC required), rapid review timeline.
   - Neither Antigravity nor Codex selects or submits to any journal.

2. **Author Declarations & Order**:
   - Final confirmation of author ordering among Mahidul Ahasan, Atikur Rahman, Md Amit Hasan Robi, and Md Samiur Rahman Tanim.
   - Confirmation of institutional affiliations and department names.
   - Designation of corresponding author and institutional email address.
   - Formal CRediT author contribution statement.
   - Declarations of conflicts of interest and funding sources (or explicit statement of no external funding).
   - Formal AI-assistance disclosure statement in accordance with the target journal's policy.

3. **Public Data & Code Archival**:
   - Deposit the compact reproducibility package (`RIS_FJ_VLC_DRL_reproducibility.zip`) and optional checkpoints payload into a public repository (e.g., Zenodo, Figshare, or institutional repository) to obtain a persistent public DOI prior to formal publication.

---

## 6. Master Runner Certification

I certify that:
- All 90 matched-budget DRL policies, 15 geometry grid evaluations, 120 zero-shot transfer runs, and 9 calibrated 4-PAM diagnostic grids were executed and verified locally.
- All 98 unit tests passed cleanly.
- The 10-page manuscript PDF and editable Word document compile without error, with zero overfull boxes, zero unresolved markers, and complete mathematical fidelity.
- No experimental data or statistical outcomes were altered, suppressed, or fabricated.
- The release package is ready for final review and administrative confirmation by the project guide and authors.

*Report signed by Antigravity Autonomous Master Runner.*

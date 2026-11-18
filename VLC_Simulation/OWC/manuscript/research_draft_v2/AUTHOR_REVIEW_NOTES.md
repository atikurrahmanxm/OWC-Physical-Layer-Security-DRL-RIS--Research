# Author reading notes — expanded manuscript and release package

The earlier drafts are preserved in `../archive_antigravity_2026_11_18/`. This updated release package delivers the ten-page `main.pdf`, or editable `main.docx` in Word. Both contain eight figures (system-model illustration, controller workflow, four training/budget figures, zero-shot geometry transfer, and calibrated 4-PAM diagnostic). Displayed equations (15 total) and data tables (5 total) in Word are natively editable. `main.tex` remains the canonical LaTeX source; copy Word edits into it for future LaTeX PDF rebuilds.

The authors are exactly the four student team members:
1. **Mahidul Ahasan** (Assam down town University)
2. **Atikur Rahman** (Assam down town University)
3. **Md Amit Hasan Robi** (Assam down town University)
4. **Md Samiur Rahman Tanim** (Assam down town University)

Dr. Rima Deka is identified separately as **Project Guide**, as requested by the user; she is not in the author list.

## What this paper says

The project implements a finite-aperture optical RIS extension of a VLC friendly-jamming simulator and compares no RIS, fixed RIS alignment toward Bob, and joint discrete RIS/FJ control across 90 architecture-matched runs (three schemes, ten seeds, budgets 2k/5k/10k).

1. **Primary comparison (10k slots)**: Joint-minus-fixed utility difference is $+0.0183$ (95% CI $[-0.1677, 0.2043]$, $p=0.8289$). Fixed and joint secrecy means are 1.5656 and 1.4839 bps/Hz ($p=0.4182$). Neither comparison shows a statistically significant benefit from joint discrete control.
2. **Multiplicity sensitivity**: Across 18 paired contrasts with full-family Holm step-down correction and 1,024 sign-flip permutations, secondary contrasts are sensitive to multiplicity adjustment (fixed secrecy Holm-$t$ $p=0.0696$; joint utility Holm-$t$ $p=0.3166$; fixed utility Holm sign-flip $p=0.0703$). Blanket claims of significant gains across both schemes/metrics are not supported.
3. **Sensitivity & zero-shot transfer**: Enumeration across five geometries and three noise offsets shows that discrete oracles achieve positive utility ($0.7119$--$1.0418$). However, nominal-trained 10k policies evaluated zero-shot across 120 cases incur negative mean utility ($-0.5608$ to $-0.7876$) and large optimality gaps ($>1.6$), revealing that nominal policies do not generalize without retraining. Nearby-Eve and colocated geometries yield identically zero secrecy, confirming theoretical boundaries.
4. **Calibrated 4-PAM diagnostic**: An explicit current-domain alternative with equiprobable 4-PAM and independent uniform jamming demonstrates that QoS-feasible positive secrecy (1.65--1.73 bits/channel use) is achievable at 20--30 dB reference SNR. At 10 dB SNR, no action meets the Bob BER threshold ($10^{-3}$). Colocated receivers yield identically zero secrecy at all SNR levels.

## Completed verification and release testing

- **Unit tests**: 98 tests passed in `release_audit/ANTIGRAVITY_UNIT_TESTS.log`.
- **Policy replay**: All 90 saved CNN+DND policies re-evaluated for 1,000 slots each; 360,000 stored metric values matched with absolute tolerance $< 10^{-10}$ (`release_audit/full_policy_replay.json`).
- **Geometry sensitivity**: 15 cases (5 geometries × 3 noise offsets), 46,875 evaluations (`release_audit/geometry_grid_sensitivity.json`).
- **Zero-shot transfer**: 120 cases (30 policies × 4 geometries, 200 slots each = 24,000 slots) completed (`release_audit/frozen_policy_geometry_transfer.json`).
- **Calibrated diagnostic**: 9 scenario/SNR grids, 28,125 action evaluations, independent AWGN quadrature error $< 10^{-8}$, 300k-symbol Monte Carlo BER match $< 0.0025$, colocated secrecy = 0.000000 bits/use (`output_figures/ris/calibrated_diagnostic_v1/`).
- **Build validation**: 10 pages, 8 figures, 5 tables, 15 display equations, 337 cryptographic SHA256 hashes matched, zero overfull boxes, two minor harmless underfull paragraph warnings (`BUILD_VALIDATION.json`).

## Build and packaging commands

From the OWC project root, using Python with the project virtual environment:

```powershell
# 1. Assemble empirical evidence and tables/figures
python -B scripts/assemble_release_evidence.py

# 2. Build bibliography, reading companion and Word document
python -B scripts/build_manuscript_sources.py
python -B scripts/build_manuscript_docx.py

# 3. Update evidence inventory hashes
python -B scripts/revise_manuscript_evidence.py

# 4. Compile canonical LaTeX with Tectonic
cd manuscript/research_draft_v2
..\..\.tools\tectonic\tectonic.exe --keep-logs --keep-intermediates main.tex
cd ../..

# 5. Validate build structure and generate source package
python -B scripts/validate_manuscript_build.py

# 6. Build compact reproducibility package
python -B scripts/package_research_release.py
```

## Before submitting (author-only decisions)

1. **Journal selection**: Guide Dr. Rima Deka will confirm venue selection (e.g., Optical and Quantum Electronics [Springer, subscription no-APC] or Photonics [MDPI, open-access APC]).
2. **Author confirmations**:
   - Order of the four student authors.
   - Institutional affiliation details (Assam down town University).
   - Designated corresponding author and official email address.
   - Author contribution breakdown (e.g., CRediT taxonomy).
   - Conflict of interest and funding declarations.
   - Formal AI-assistance disclosure statement.
   - Final approval of the manuscript draft by all four authors and project guide.
3. **Data deposit**: The compact reproducibility ZIP (`research_release/RIS_FJ_VLC_DRL_reproducibility.zip`, 3.06 MB) plus separate saved-policy checkpoints (2.06 GB) should be deposited in an archival repository (e.g., Zenodo / institutional repository) to receive a persistent public DOI prior to publication.

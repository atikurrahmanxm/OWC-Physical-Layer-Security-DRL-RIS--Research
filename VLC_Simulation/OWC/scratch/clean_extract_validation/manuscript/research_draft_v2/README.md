# Revised research manuscript and complete release package

Open **main.pdf** for the ten-page paper, or **main.docx** to edit in Word. Both include the room/system-model diagram, controller workflow, four training/budget figures, zero-shot geometry transfer figure, and calibrated 4-PAM diagnostic figure (eight figures total). The Word file contains fifteen native editable equations and five editable data tables. `main.tex` is the canonical LaTeX source; copy future Word edits into it when rebuilding the LaTeX PDF. `draft.md` is a generated reading companion. `source_package.zip` includes PDF, Word, LaTeX inputs and compilation sources. The standalone reproducibility bundle `RIS_FJ_VLC_DRL_reproducibility.zip` is in `research_release/`.

This expanded release package incorporates complete empirical validation and testing executed through Antigravity across all 90 matched-v2 policies, 15 geometry sensitivity cases, 120 zero-shot transfer evaluations, and 9 scenario/SNR grids under an explicit current-domain 4-PAM diagnostic.

## Manuscript and audit documents

- `AUTHOR_REVIEW_NOTES.md`: paper summary, build commands, verified scopes, and remaining author decisions.
- `claim_evidence.md`: detailed numerical claim-to-evidence map, sample sizes, and verification boundaries.
- `citation_audit.md`: checked bibliography (seven primary-source-verified entries) and removed unestablished records.
- `review_and_revision.md`: writing outline, Avoid AI Writing style compliance, and adversarial self-review.
- `verified_results.json`: independently recomputed seed-level statistics and finite-grid maxima.
- `evidence_manifest.json`: cryptographic SHA256 hashes of all source, data, checkpoint, and script files.
- `BUILD_VALIDATION.json`: automated build validation report (10 pages, 8 figures, 5 tables, 15 display equations, 337 verified hashes).
- `release_audit/`: complete test logs, replay evidence, statistical robustness suite, protocol definitions, guide handoff, and cover letter draft.

## Key scientific findings

1. **Primary comparison (10k slots)**: Joint-minus-fixed utility difference is $+0.0183$ (95% CI $[-0.1677, 0.2043]$, $p=0.8289$). Fixed and joint secrecy means are 1.5656 and 1.4839 bps/Hz ($p=0.4182$). Neither comparison shows a statistically significant benefit from joint discrete control.
2. **Multiplicity sensitivity**: While fixed RIS improves utility and secrecy over baseline under unadjusted testing, full-family 18-contrast Holm adjustment shows that secondary gains are sensitive (fixed secrecy Holm-$t$ $p=0.0696$; joint utility Holm-$t$ $p=0.3166$; fixed utility Holm sign-flip $p=0.0703$).
3. **Geometry sensitivity & transfer**: Nominal-trained policies transferred zero-shot to altered user positions incur severe optimality gaps ($>1.6$) relative to same-geometry discrete oracles, demonstrating that nominal DRL policies do not generalize without retraining.
4. **Calibrated 4-PAM diagnostic**: Under an explicit current-domain physical model with independent uniform jamming, positive secrecy (1.65–1.73 bits/channel use) is QoS-feasible only at 20–30 dB reference SNR. Colocated receivers yield identically zero secrecy (0.0000 bits/use), confirming physical-layer theoretical invariants.

The paper reports a bounded simulation and diagnostic study. It does not claim general joint-controller superiority, hardware-level security guarantees, or exact numerical curve reproduction of the 2024 paper. Author declarations, venue selection, and submission approvals remain author-only decisions.

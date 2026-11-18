# Manuscript artifact and implementation consistency check

Revision status: the findings below describe the original Antigravity delivery. A subsequent correction pass updated `main.tex`, regenerated tables/figures from raw runs, and replaced the citation and claim audits. See `review_and_revision.md` for current scope and remaining research limits. The original delivery is preserved in `../archive_antigravity_2026_11_18/`.

Checked: 18 November 2026. Scope: delivered files, selected mathematical definitions against implementation, and claim wording. This is not a formal reviewer-panel report, a complete citation audit, or a new experiment. Original manuscript files were preserved.

## Status

The writing task produced a substantial draft, LaTeX source, nine bibliography entries, four figure pairs, and supporting notes. It did not deliver a compiled manuscript PDF. The draft needs scientific corrections before submission; completing the files does not establish submission readiness.

## Corrections required

1. **Replace the secrecy-rate equations with the implemented model.** `main.tex:82` and `main.tex:85` use a generic difference of Gaussian capacities. The experimental paper-mode implementation in `vlc/secrecy.py:60` uses the modulation index and DC bias, a Bob denominator containing twice the squared jammer amplitude times those factors, and a different Eve leakage bound. The displayed equations therefore do not describe the simulation producing the reported numbers. Do not change the simulator just to fit the manuscript.

2. **Correct the BER equation.** `main.tex:89` gives a coefficient of 3/8 and treats jamming as noise in the denominator. The literal paper-mode Eq. (14) implementation in `vlc/secrecy.py:116` uses the squared sum of direct and signed jammer channel amplitudes, a coefficient of 3/4, and a different power factor. Explain this inherited modeling convention and its limitations explicitly.

3. **Resolve channel units and responsivity.** `main.tex:57` includes photodetector responsivity in the channel gain, while `main.tex:72` and `main.tex:75` multiply by it again in the received signal. Define optical versus electrical gains consistently with the implementation and document LED multiplicity and conversion factors.

4. **Describe the actual finite-aperture RIS calculation.** The expression at `main.tex:97` with a visibility indicator alone does not specify the implemented finite-aperture overlap/quadrature and intercepted-power restriction. Document the implementation used in the runs, including mirror geometry and shared orientations for all sources.

5. **Narrow the conclusions.** The abstract and conclusion claim that decoupling is more robust, or physically and computationally superior. The reported joint-minus-fixed utility CI includes zero and the secrecy comparison is also nonsignificant. These comparisons establish no detected difference at the tested budgets, not general superiority or equivalence. State the tested geometry, finite codebook, ten seeds, and budget limits. Replace “permanently trapped” with an observation bounded by the measured training/evaluation horizon. Treat action-space dilution as an explanation requiring further causal testing.

6. **Separate baseline comparisons.** The abstract attaches a single fixed-minus-baseline utility statistic to a claim that both RIS schemes significantly outperform baseline. Independently calculate and report each paired contrast before making that statement. Keep utility and secrecy-rate claims separate.

7. **Repair and verify bibliography metadata.** The 2024 baseline bibliography entry gives pages 18942–18955. The authors' institutional publication record gives 17915–17928: https://researchwith.stevens.edu/en/publications/smart-jamming-for-secrecy-deep-reinforcement-learning-enabled-sec/ . Other entries still require primary-source verification; the existing citation-audit assertion that all nine are verified is not established by this check. Compare directly with prior secure optical-RIS/DRL work before claiming novelty.

8. **Build and inspect the actual PDF.** No manuscript PDF is present in this delivery directory. `AUTHOR_REVIEW_NOTES.md` acknowledges that compilation was unavailable, so its promise of an error-free Overleaf build has not been tested. Compile bibliography and cross-references, inspect equations/figures and missing references, and make `draft.md` and `main.tex` express the same final scientific content.

9. **Make evidence claims auditable.** A short manifest and a simulated review narrative do not establish full source provenance, policy reload/evaluation equivalence, or independent reviewer approval. Link each numerical claim to the specific raw runs, aggregation procedure and actual source configuration; label checks not performed.

## Next task for Antigravity

Correct the manuscript against the existing implementation and completed matched-v2 results. Preserve the experiments and raw data. Address items 1–9 above, verify each reference from a primary source, regenerate the claim-evidence table, and deliver a successfully compiled, visually checked PDF plus build instructions. Report unresolved issues honestly. Do not launch another long training matrix or alter results to make a stronger claim.

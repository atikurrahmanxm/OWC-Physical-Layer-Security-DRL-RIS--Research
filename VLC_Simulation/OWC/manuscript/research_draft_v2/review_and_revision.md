# Revision record and adversarial self-review (expanded release package)

Latest update (18 November 2026): Delivered the expanded ten-page research manuscript package (`main.pdf`) and editable Word document (`main.docx`). This delivery supersedes the earlier seven-page and six-page drafts (preserved in `../archive_antigravity_2026_11_18/`). The manuscript contains eight figures total:
1. Fig 1: 3D system-model room illustration (`fig_system_model`)
2. Fig 2: Implemented DRL control workflow (`fig_control_workflow`)
3. Fig 3: Training budget convergence (`fig1_budget_convergence`)
4. Fig 4: Paired joint-versus-fixed differences (`fig2_budget_paired_differences`)
5. Fig 5: Action coverage and modal evaluation configuration (`fig3_budget_coverage_and_q`)
6. Fig 6: Computational scaling & runtime (`fig4_computational_scaling`)
7. Fig 7: Geometry sensitivity & zero-shot transfer (`fig_release_geometry_transfer`)
8. Fig 8: Calibrated current-domain 4-PAM diagnostic (`fig_release_calibrated`)

The Word document contains 15 native editable displayed equations, 8 embedded figures, and 5 editable data tables. All four student team members are designated as authors; Dr. Rima Deka is acknowledged separately as Project Guide.

## Outline and paragraph roles

1. **Abstract**: core research question, matched comparison design, primary estimate (+0.0183, p=0.8289), multiplicity sensitivity (Holm correction), zero-shot transfer findings, calibrated 4-PAM diagnostic outcomes, and inference scope.
2. **Introduction**: physical-layer security problem, optical reflection mechanics vs RF phase shifts, learning-budget trade-off, and bounded contribution.
3. **Related work & scope**: baseline friendly jamming, prior optical-RIS approaches (Qian 2021, Saifaldeen 2022, Liu 2026), and clear distinction from continuous-action and mobility frameworks.
4. **System and threat model**: room geometry, passive Eve assumption, direct/effective optical gains, inherited baseline secrecy/BER formulas, and L1 amplitude cost interpretation.
5. **Finite-aperture optical RIS**: facet geometry, image-source projection, aperture clipping and intercepted power cap, and discrete shared-normal codebook.
6. **Learning and experimental protocol**: observation representation, CNN+DND architecture, greedy frozen evaluation, and statistical unit of analysis.
7. **Results**:
   - Primary contrast: joint vs fixed RIS ($+0.0183$, $p=0.8289$; secrecy $-0.0817$ bps/Hz, $p=0.4182$).
   - Baseline comparisons: fixed vs baseline ($+0.2051$, $p=0.00034$) and joint vs baseline ($+0.2234$, $p=0.02261$).
   - Multiplicity sensitivity: full-family 18-hypothesis Holm step-down correction and 1,024 sign-flip permutations.
   - Finite-grid ceiling and action exploration: 9.11% coverage at 10k slots; modal $q$ distribution.
   - Computational runtime analysis: recorded wall-clock times.
8. **Supplementary geometry and channel checks**:
   - Finite-grid sensitivity (15 cases) and zero-shot transfer (120 cases): severe optimality gap ($>1.6$) and secrecy collapse without retraining; colocated negative control.
   - Consistent current-domain diagnostic: explicit 4-PAM model, independent uniform jammer, AWGN noise, QoS-feasible secrecy at 20--30 dB SNR, zero secrecy under colocated eavesdropping.
9. **Limitations and reproducibility**: inference boundaries, lack of mobility retraining, unresolved noise normalization, independent 90-policy replay verification, and artifact provenance.
10. **Conclusion**: summary of findings, distinction between available actions and learned policies, and open challenges.

## Avoid AI Writing — rewrite compliance

Applied natural technical writing standards throughout:
- Removed promotional openings, empty buzzwords ("testament," "pivotal," "game-changer," "groundbreaking"), forced numbered contributions, and unsupported claims of superiority or state-of-the-art performance.
- Replaced sweeping assertions with exact empirical metrics, confidence intervals, degrees of freedom, and hypothesis-testing conditions.
- Preserved genuine physical and mathematical nuances (e.g., distinguishing between watt-valued noise in paper-mode and current-domain noise variance in the 4-PAM alternative).
- Maintained honest boundaries: stating clearly that frozen policies fail to transfer zero-shot, that joint control did not outperform fixed alignment, and that colocated eavesdropping completely eliminates secrecy.

## Adversarial self-review

This review was conducted as a rigorous, internal multi-perspective audit. No formal external peer review was fabricated or simulated.

| Dimension and question | Audit finding | Action taken |
|---|---|---|
| **Contribution**: what does the paper establish? | A rigorous empirical comparison of discrete optical RIS and friendly jamming under matched training budgets, accompanied by finite-grid oracle enumeration, geometry transfer, and a calibrated physical diagnostic. | Narrowed all claims: does not claim general joint superiority, first combination, continuous-mobility tracking, or state-of-the-art status. |
| **Clarity**: do equations match the code? | Previous drafts substituted ideal Gaussian formulas and doubled responsivity. | Equations now precisely describe the simulator's implemented DC gains, finite-aperture clipping, inherited paper-mode metrics, and explicit 4-PAM diagnostic formulas. |
| **Experimental rigor**: are claims supported by statistics? | Joint vs fixed differences are statistically inconclusive. Secondary comparisons are sensitive to multiplicity correction. | Primary result reported prominently with 95% CI; full 18-contrast Holm step-down and sign-flip adjustments included. Blanket significance claims removed. |
| **Reproducibility**: can results be independently verified? | 90 raw runs, 180 checkpoint files, and multiple Python evaluation scripts exist. | Antigravity executed complete 98-unit test suite, reloaded and replayed all 90 saved policies (360k metric values matched atol < 1e-10), enumerated 15 geometry grids, tested 120 transfers, and completed 9 calibrated diagnostic grids. Built compact reproducibility ZIP and manifest. |
| **Soundness**: are security claims justified? | Model uses stationary room, known Eve position, and inherited paper expressions. | Clarified that physical-layer secrecy metric does not guarantee cryptographic secrecy, packet decoding prevention, or protection against moving or unknown attackers. Colocated negative control highlighted. |

## Build and verification status

- **LaTeX / Tectonic**: Compiles to ten pages with zero overfull boxes, zero unresolved citation/reference markers, and two minor underfull paragraph warnings.
- **Word / Pandoc**: Generates native OMML equations (15 displays), 8 embedded figure drawings, and 5 editable tables with rich caption styling.
- **Evidence manifest**: 337 cryptographic SHA256 hashes verified with zero discrepancies.
- **Packaging**: Compact reproducibility package `research_release/RIS_FJ_VLC_DRL_reproducibility.zip` (3.06 MB) and manifest generated cleanly.

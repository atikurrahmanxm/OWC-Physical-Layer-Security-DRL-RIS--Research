# Why the published numerical targets remain unresolved

**The requested numerical fix has not been achieved.** This investigation leaves the simulation equations and raw results unchanged and corrects a misleading verification behavior: the paper checker previously exited successfully when equations passed even though the published targets failed. It now returns failure for numerical mismatches.

## Published evidence recovered directly from the supplied PDF

The PDF contains vector paths for Figures 6 and 7. `published_targets.py` transforms those coordinates using the printed axis ranges. `published_curve_reference.json` records the PDF hash, extraction method and plotted coordinates. These are rounded drawing coordinates, not the authors' raw training data.

Figure 7 has five plotted vertices, at 4, 8, 12, 16 and 20 dB, and nine labeled axis ticks. Its extracted DRL data are:

| SNR label (dB) | Published secrecy (bps/Hz) | Published BER | Current Eq. (4) Bob capacity ceiling |
|---:|---:|---:|---:|
| 4 | 1.745999 | 0.002300 | 0.906123 |
| 8 | 2.375007 | 0.001870 | 1.434893 |
| 12 | 3.015211 | 0.001400 | 2.037293 |
| 16 | 3.718993 | 0.000600 | 2.675438 |
| 20 | 4.375007 | 0.000100 | 3.329106 |

Every published secrecy point exceeds the capacity ceiling implied by the project's current `eq4` SNR convention. Additional training, different CNN weights, or more accurate beamforming cannot cross that ceiling. This shows the chosen SNR convention is not numerically equivalent to the convention behind the published plot. It does not establish which convention the authors used.

## Inverting the two equations

For Table I parameters, four-LED gain aggregation, eta=1 and derived I_D=1, Bob's interference-free secrecy capacity is 1.908654495 bps/Hz. The target 5.68 is impossible at that nominal noise.

The signal coefficients used by the two printed equations differ: Eq. (4) uses `alpha**2 * I_D**2 = 0.01`; Eq. (14) uses `P_T = 1`. This is the literal implementation of the supplied PDF, but the resulting BER becomes extremely small at operating points with substantial secrecy. Under zero forcing, the ratio of the Eq. (14) erfc argument squared to the Eq. (4) SINR is `pi*e*P_T/(5*alpha**2*I_D**2)`, approximately 170.795 under the current assumptions.

The audit analytically solves for noise instead of tuning the CNN:

- To obtain BER 0.0002 under zero forcing requires noise approximately **4.44746e-11**. At this noise, maximum secrecy on the 625-action grid is zero.
- The grid actions capable of secrecy 5.68 at some noise are sign pairs of `[-0.5, 1, 0, 1]`. They require noise approximately **2.17358e-16** to achieve that secrecy. Their literal Eq. (14) BER numerically underflows to zero.
- For those same actions, BER 0.0002 requires noise approximately **4.42e-11 to 4.48e-11**. The closest pair of noise requirements differs by **53.078 dB**.

These are fixed-channel, fixed-action calculations for the current configuration. The paper's checkpoints occur at different slots, and its curves may use averaging or time-varying channels. Consequently, this calculation does **not** prove that all possible author configurations or random traces are inconsistent. It proves that simply changing one noise parameter cannot reproduce both targets for a single current-grid action under the current signal scaling.

The nominal channel is an electrical current model, while the table gives noise in dBm. A conversion from electrical power to current variance also needs an impedance convention; the existing numerical use implicitly equates these through a unit conversion factor. The PDF does not establish enough conventions to infer a unique correction. Changing eta, bias, impedance or separate decision-noise conventions can change the comparison, but selecting them solely to reproduce the targets would be parameter fitting, not independent verification.

## Verification behavior corrected

```powershell
python -B paper_audit/check_paper_match.py
```

This now writes the comparison and exits **1** when the numerical targets fail. It checks both quoted DRL checkpoints and all five plotted Figure 7 vertices for RL/DRL secrecy, BER and utility: 32 comparisons. A smaller BER is not treated as a numerical match to a larger published value.

Declared local tolerances are 0.05 bps/Hz for secrecy, 0.05 for utility, and a multiplicative factor of 1.25 in either direction for BER. These tolerances are explicit review thresholds, not author-provided acceptance criteria. Even a numerical pass would not by itself establish correct author settings or validate the custom comparison baselines.

```powershell
python -B paper_audit/check_paper_match.py --equations-only
```

This explicitly limits success to equation and saved-action consistency checks. It still records the failed numerical comparison.

Validation: 44 regression tests pass, including curve extraction, linear/log axis decoding, noise-inversion round trips and false-success counterexamples. All 40,000 saved observations remain consistent with their recorded actions. See [numerical_conformance.json](numerical_conformance.json) and [the direct comparison plot](paper_comparison.png).

Author-source check: the [author-hosted paper](https://liusc1028.github.io/papers/TWC24liu.pdf) and [publication listing](https://liusc1028.github.io/sicongliu.html) were inspected; no author simulation code or correction resolving these settings was located in the inspected sources. This is a limited search result, not a claim that no such material exists anywhere.

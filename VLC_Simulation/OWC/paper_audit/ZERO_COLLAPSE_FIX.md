# Zero-secrecy correction: measured results and remaining gap

The two zero-output causes have been corrected under explicit modeling choices. **The published numerical curves are still not reproduced.** All figures and raw records were regenerated with seed 42 and 2,000 slots per agent per operating point.

| Check | Before | Corrected run | Paper |
|---|---:|---:|---:|
| DRL secrecy at slot 1,400, raw | Approximately 0 | 1.555976 bps/Hz | 5.68 bps/Hz |
| DRL secrecy at slot 1,400, displayed EMA50 | Approximately 0 | 1.555520 bps/Hz | 5.68 bps/Hz |
| Figure 7 DRL means | All nine zero | All nine positive; values below | Positive throughout |

## What changed and why

1. Default energy cost is now `varrho * sum(abs(w_i))` (`energy_model=l1`). The printed signed Eq. (16) gives `E=-4` for four weights of -1. At the default geometry, that produces secrecy 0 but utility approximately +1.6: the learner benefits from an energy credit instead of secrecy. The nonnegative interpretation gives energy +4 and utility approximately -1.6 for the same action. This interpretation changes the printed objective; `paper_signed` retains the literal expression as an opt-in comparison.
2. Default SNR is now the interference-free Bob SINR inside Eq. (4): `gamma = 2*h_AB**2*alpha**2*I_D**2 / (pi*e*noise)`. The old `electrical` conversion excluded the modulation scaling. With alpha=0.1 and I_D=1, it resulted in approximately 26.30 dB lower Eq. (4) SINR than the labeled value and zero secrecy for every one of the 625 actions at all nine sweep points. The old convention remains selectable. The authors' normalization remains unknown.
3. CLI, launcher, Python defaults and both HTML copies now agree. Saved records include configuration, raw metrics and actions. An exhaustive `operating_point` reference reports the physical ceiling, maximum grid secrecy and utility-optimal grid action. These reference calculations do not supply actions to either learner.
4. The audit rejects stale configurations, checks the nine SNR settings, recomputes every saved agent metric from its beam weights, and checks that the zero-collapse regression has not returned. `reproduction_verified` remains false.

## Figure 7: actual DRL averages

These means include all 2,000 slots, including exploration, as specified for Figure 7 in the paper.

| SNR (dB), Eq. (4) convention | Mean secrecy (bps/Hz) |
|---:|---:|
| 4 | 0.005322191 |
| 6 | 0.009105907 |
| 8 | 0.999326923 |
| 10 | 1.271089261 |
| 12 | 1.599087564 |
| 14 | 1.895777516 |
| 16 | 2.196024181 |
| 18 | 2.497881768 |
| 20 | 2.799994501 |

At 4 and 6 dB, the current grid's maximum-utility action is no jamming: its lower energy cost outweighs the secrecy benefit of other actions. Positive average secrecy there comes from exploration. These small values remain a substantial disagreement with the paper; they are not evidence of successful low-SNR secrecy optimization or an exact reproduction.

## Why 5.68 is still unattainable at the nominal operating point

With Table I noise, four-LED gain aggregation, eta=1 and I_D=1, even Bob's interference-free capacity term is only **1.908654495 bps/Hz**. Subtracting Eve's leakage or adding jamming interference cannot increase that ceiling. The maximum secrecy on the 625-action grid is **1.555976439 bps/Hz**.

Even before subtracting leakage, capacity 5.68 would require Eq. (4) Bob SINR of at least **34.195 dB**, compared with **11.172 dB** at the current nominal operating point. For unchanged signal scaling, that would require noise no greater than **6.5862e-16**, about **23.024 dB below** the current Table I interpretation. The implementation does not make that unsupported noise adjustment. A clarified physical scaling or operating condition is needed to resolve this gap.

## Validation and reproduction

- 38 regression tests pass, including the negative-energy counterexample, SNR feasibility at all nine points, the Table I capacity limit and the low-SNR utility tradeoff.
- All 40,000 saved RL/DRL observations (Figure 6 and all Figure 7 points) were recomputed from recorded actions. Maximum absolute error in secrecy, BER, energy and utility: 0.
- Python/browser physics, energy, utility bounds and Eq. (4) SNR parity checks pass. Headless Edge verified the new defaults, energy labels, navigation and math panel without JavaScript errors.
- `git diff --check` passes.

```powershell
python -B -m unittest discover -s tests -v
python -u -B main.py --mode all --slots 2000 --grid_res 25 --seed 42
python -B paper_audit/check_paper_match.py
node paper_audit/check_browser_match.js
```

Machine-readable evidence: [verification_current.json](verification_current.json). Raw figure data: [Figure 6](../output_figures/fig6_data.json), [Figure 7](../output_figures/fig7_data.json). Updated plots: [Figure 6 secrecy](../output_figures/fig6a_secrecy_rate.png), [Figure 7 secrecy](../output_figures/fig7a_secrecy_rate_snr.png).

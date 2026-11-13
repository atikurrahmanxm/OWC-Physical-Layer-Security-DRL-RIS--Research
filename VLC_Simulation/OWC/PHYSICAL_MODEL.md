# Consistent current-domain simulation

`--model physical` runs an explicit alternative physical model. It uses the same information signal, artificial noise and receiver noise for secrecy and BER. It is not an implementation of the paper's continuous-input secrecy expression, and no parameters are fitted to the published checkpoints.

The original `--model paper` behavior remains available. Its existing raw records are preserved. Physical experiments default to `output_figures/physical/` so that a new run does not replace the paper-equation evidence.

## One signal model

For Bob and Eve the sampled receiver current is

`Y = h * X + (h_J @ w) * J + N`, in amperes.

- LED information current `X` has four equiprobable levels `[-A, -A/3, A/3, A]`, with Gray labels `00, 01, 11, 10` and `A = alpha * I_D` amperes.
- `I_D = P_T / eta`; `eta` is optical watts per ampere and `P_T` is per-LED average optical power. Physical mode rejects an inconsistent bias override.
- `h = responsivity * eta * G` converts driving current to receiver current; the existing channel gain aggregates four co-located LEDs in each fixture. Thus changing eta and deriving bias consistently leaves the received modulation amplitude unchanged.
- The common artificial-noise scalar `J` is independent uniform current on `[-A, A]`. Its realization is an unobserved nuisance at both receivers. Each jammer transmits `w_i * J` on top of its illumination bias.
- `N` is zero-mean Gaussian receiver-current noise. Eve has the same noise variance as Bob by default; `eve_noise_ratio` makes that assumption explicit in Python configurations.

The table's dBm value is converted to watts first. Given an explicitly assumed receiver load, `noise_variance[A^2] = noise_power[W] / receiver_resistance[ohm]`. This treats the listed power as the total noise power for one sampled real channel, not a power spectral density; no unreported bandwidth integration is inserted. The default one-ohm load preserves the previous numeric noise value. It is a declared assumption, not an author-supplied measurement.

`modulated` SNR means `E[(h*X)^2] / noise_variance = (5/9)*(h*A)^2 / noise_variance`. This definition is used throughout the physical sweep. Mixing paper-normalized SNR or signed energy with physical mode is rejected.

## Secrecy and BER from the same conditional density

The additive disturbance is a uniform/Gaussian convolution. Its conditional density is evaluated using the difference of two Gaussian CDFs, with reflected log-domain tails for stability.

Mutual information is `I(X;Y) = sum_x p(x) integral p(y|x) log2[p(y|x)/p(y)] dy`. Physical secrecy is `max(0, I(X;Y_B) - I(X;Y_E))`. Piecewise Gauss-Legendre integration resolves the edges of the uniform distributions and the Gaussian transition regions. Gaussian tails are truncated at 12 standard deviations. This formulation follows the standard conditional-density definition of mutual information; see [Tse and Viswanath, information theory appendix](https://web.stanford.edu/~dntse/wireless_book.html).

Results are bits per real channel use, multiplied by an explicit `symbol_rate_per_hz` conversion (default 1 symbol/s/Hz) for the existing bps/Hz plots. Four equiprobable symbols contain at most 2 bits per use. This finite-alphabet model therefore cannot reproduce 5.68 bps/Hz with the default symbol-rate conversion. The paper's higher continuous-input information-rate expression and actual 4-PAM throughput are distinct quantities.

BER uses midpoint symbol decisions and the Gray-label Hamming distance for every possible detected symbol, including nonadjacent errors. Decision-bin probabilities integrate the same uniform/Gaussian disturbance exactly. Jamming is independent interference: it is not added coherently to the information-channel gain.

The physical global rate ceiling is Bob's no-jamming 4-PAM mutual information. The independent BER lower bound uses optimal bit-MAP decisions without jamming; at low SNR that decoder can improve on midpoint symbol decisions. Independent added interference cannot beat the optimal no-jamming bit decoder. The channel-nulling LP is a feasible reference beamformer; in physical mode it is not certified to maximize the finite-alphabet secrecy objective.

## Incremental jamming energy

Each fixture's incremental AC driver energy is `E_i = (A^2/3) * w_i^2 * R_driver * slot_duration`, in joules. `R_driver` is an effective resistive AC load for the whole fixture. Summing these values gives physical `energy`. This excludes DC illumination, circuit overhead and conversion losses, which the PDF does not specify. The default effective load is one ohm and the default slot is one second. These are configurable assumptions, not calibrated values.

Consequently a weight sign change preserves energy and scaling all weights by one-half reduces incremental energy by four. `delta2` is the utility penalty per joule in this mode; its numeric default is retained and is not claimed to reproduce the paper's normalized energy penalty. `unit_jamming_cost` must remain 1 in physical mode.

## Run and inspect

```powershell
python run.py --mode eval --model physical --slots 2000 --seed 42
python main.py --mode all --model physical --slots 2000 --grid_res 25 --seed 42
python run.py --mode train --model physical --algo drl --snr 12 --slots 2000
```

`--receiver-resistance`, `--jammer-resistance`, `--slot-duration`, `--noise-dbm` and `--eta` expose the physical assumptions. Saved records include their values, units, actual actions and model interpretation. Use a separate `--save_dir` for exploratory settings to preserve prior results.

The physical mode is available in the CLI and Python/HTTP experiment APIs. The existing browser dashboard continues to display paper-equation physics and has no physical-mode selector; requesting physical mode through a GUI launcher produces an explanatory error instead of mixing the two models.

## Checks before learning

Tests compare BER with both an independent exact Gaussian 4-PAM formula and 400,000 simulated symbols under uniform jamming. Mutual information is checked with independent adaptive integration for the Gaussian case and higher-order quadrature for uniform jamming. Further checks cover current-unit rescaling, optical conversion invariance, identical Bob/Eve channels, the 2-bit alphabet limit, jamming damage, joule scaling, all 625 actions against bounds, configuration validation and CLI propagation.

```powershell
python -B -m unittest tests.test_physical_model -v
python -B -m unittest discover -s tests -v
python -B paper_audit/check_physical_model.py
```

## Completed nominal experiment

The seed-42 run uses 2,000 slots for each agent at the nominal operating point and at all nine SNR values. All 40,000 saved RL/DRL observations were recomputed from their actual beam weights; the maximum discrepancy in rate, BER, energy and utility is zero. The complete regression suite contains 58 passing tests. Machine-readable evidence is in [physical_verification.json](paper_audit/physical_verification.json).

At the nominal point the physical DRL rate at slot 1,400 is 1.390720 bps/Hz raw (1.390328 with EMA50). BER at slot 1,200 is 0.00703249 raw (0.00790268 with EMA50). The no-jamming Bob information ceiling is approximately 1.962014 bps/Hz. These are new-model results, not replacements for the paper-equation checkpoint comparison.

The Figure 7 DRL means are positive at all nine points and range from approximately 0.4614 to 1.3762 bps/Hz. The rate approaches a finite-alphabet ceiling rather than increasing indefinitely. The learned agents remain suboptimal relative to the available grid/reference policies; no published comparative-performance claim is made. Means include exploration, which can dominate high-SNR BER even when the greedy beamformer's BER is small.

Raw records: [nominal training](output_figures/physical/fig6_data.json), [SNR sweep](output_figures/physical/fig7_data.json). Plots: [training curves](output_figures/physical/fig6_performance_curves.png), [SNR curves](output_figures/physical/fig7_snr_performance.png).

# Model resolution: what can and cannot be recovered from the 2024 paper

18 November 2026. This is a source-based technical audit, not author confirmation or external peer review. No original simulator, historical run, or manuscript was modified in this task. The new diagnostic runner described below has been handed to the parent for execution through Antigravity, as the user requested.

## Main finding

The electrical channel definition is recoverable. The missing numerical noise normalization is not. Also, replacing the legacy noise number with a chosen load does not make the literal printed BER expression a BER for independent uniform jamming. A defensible release must separate the historical paper-equation comparison from an explicit alternative physical-channel diagnostic. A new alternative cannot be labeled an exact numerical reproduction of the 2024 paper.

## Primary-paper anchors

The source is the local `19 Sep 2024.pdf`, DOI `10.1109/TWC.2024.3458046`. Page numbers below are one-based PDF pages, not guessed journal pagination.

| Anchor | What the paper actually specifies | Consequence |
|---|---|---|
| PDF p. 3, Section II-A | Drive current is DC bias plus information current; the peak information amplitude is bounded by alpha times I_D. Instantaneous optical power is eta times drive current. | x and j in the received electrical signal have current units. |
| PDF p. 3, Eq. (2a)–(2b) | y_B = h_AB x + h_JB^T j + n_B, with h = R eta G | Responsivity and electro-optical conversion enter the gain once. There must not be another detector-responsivity multiplier in the received-current equation. |
| PDF p. 3, after Eq. (2) | n_B and n_E are AWGN with variances sigma_B^2 and sigma_E^2 | In this electrical-current channel those variances need current-squared units, or a stated normalization. |
| PDF p. 4, Eq. (3a)–(3b) | The jammer vector is w times one common scalar jammer waveform j | Independent per-fixture jammer waveforms would be a different model. Cancellation of jammer amplitudes through signed weights is meaningful for this shared waveform. |
| PDF p. 4, paragraph before Eq. (4) | x and j are uniform on the allowed bounded interval | Eq. (4) is a continuous-input secrecy expression; it is not the finite-alphabet 4-PAM mutual information. |
| PDF p. 7, Eq. (14) | BER contains (h_AB + h_JB^T w)^2 inside its argument | The jammer channel is treated as an amplitude added to the signal channel. This is not the exact decision-error expression for Eq. (3) with independent x and j. |
| PDF p. 8, Eq. (16) | Cost is proportional to the signed sum of w_i | A signed sum can be negative. The project's L1 cost is an explicit nonnegative interpretation, not an exact literal transcription of this cost equation. |
| PDF p. 9, Table I | Bob background noise power is −98.79 dBm | This is a power value; the table does not specify the receiver load or a current-variance normalization sufficient to uniquely recover sigma_B^2 in the electrical-current equations. |

The source extraction is retained in `baseline_extracted.txt` for locating passages. Equations should be checked against the PDF rendering before quoting their typography.

## Electrical units

G is dimensionless optical path gain, detector responsivity R has A/W units, and eta has W/A units. Thus h = R eta G maps transmitter current into receiver current. A noise power P_n can be converted to a receiver-current variance through P_n/R_L only after defining a load R_L and the relevant signal/noise bandwidth convention. Neither a particular load nor an equivalent receiver normalization is established by the available paper. Setting R_L = 1 ohm is one declared experimental assumption; it is not a recovered author setting.

The current implementation's `VLCConfig.noise_variance` deliberately retains the numeric watt value in paper mode. The separate `physical` mode allows a declared load conversion. Historical matched-v2 runs therefore remain internally repeatable algorithmic-metric experiments, but their dimensions do not establish calibrated hardware predictions.

## Why the literal BER cannot be repaired by noise scaling alone

Under the declared shared jammer law, j is symmetric and independent of x. Replacing w with −w changes the sign of the jammer waveform contribution but not its distribution. Therefore the true conditional density, mutual information, and any fixed-decoder average BER must be invariant to an overall sign flip of w.

The literal Eq. (14) generally fails that invariant: its effective signal amplitude becomes h_AB + b for one sign and h_AB − b for the other, where b = h_JB^T w. For a continuous feasible vector with b = h_AB, one sign yields a zero argument and the other yields twice the signal-channel amplitude. No positive noise-unit conversion removes this difference. This does not prove every reported BER number in the original paper is wrong; it shows that literal Eq. (14), Eq. (3), and independent uniform jamming do not jointly define one exact physical BER model.

A numerical counterexample was evaluated before the parent's later instruction that all testing go through Antigravity. It is preserved as `model_counterexample.json` and must not be described as an Antigravity-verified run. In the nominal geometry, all four weights −0.3352816816 give literal BER approximately 0.75; sign reversal gives a numerically zero literal BER. The consistent shared-uniform-jammer 4-PAM BER is approximately 0.263337 for either sign under the explicitly stated 1-ohm numeric comparison convention. The analytical sign-invariance argument does not depend on that illustrative load choice.

## Finite-alphabet and continuous-input rates must stay separate

The existing Eq. (4) comparison follows a continuous uniform-input expression. Its secrecy metric need not obey the two-bit ceiling of a finite 4-PAM input. Conversely, a 4-PAM alternative has at most log2(4) = 2 bits per real channel use of mutual information at each receiver. That is not a reason to clip the historical Eq. (4) study at two bits; it is a reason not to call the two studies the same channel or claim that the 4-PAM alternative numerically reproduces a published 5.68 bps/Hz continuous-input result.

For the alternative diagnostic, report bits per real channel use. A bps/Hz conversion additionally needs an explicit symbol-rate/bandwidth convention and pulse-shaping assumptions. It must not be invented merely to align curves with a target figure.

## Implemented separate diagnostic for Antigravity

Script: `scripts/run_calibrated_ris_diagnostic.py`.

It uses the existing direct and finite-aperture RIS gains and the independently formulated current-domain functions in `vlc/physical.py`. It does not alter `RISEnvironment`'s paper-mode restriction or retrain any controller.

Declared channel:

- x is equiprobable Gray-labeled 4-PAM with levels A times {−1, −1/3, 1/3, 1}; A = alpha I_D.
- The shared jammer waveform j is independent uniform on [−A,A]. Every fixture transmits w_i j around its bias.
- n_B and n_E are zero-mean Gaussian currents with equal specified variances.
- The reference signal variance is (5/9)(h_AB,direct,nominal A)^2.
- At reference SNR s dB, the noise current variance is that fixed nominal direct-Bob signal variance divided by 10^(s/10). It remains the same for all schemes and geometries at the chosen SNR.
- The information statistic is max(0, I(X;Y_B) − I(X;Y_E)) for that fixed input law, not a claimed general secrecy capacity. It assumes Eve does not know the jammer realization as side information.
- Bob BER uses the same conditional channel with fixed midpoint decisions. Mutual information does not require that hard-decision receiver.
- L1 cost is recorded only as a normalized amplitude cost; no load, slot-duration or joule claim is introduced.

Default matrix: nominal positions, changed receiver positions, and colocated Bob/Eve; reference SNR 10, 20 and 30 dB; all 3,125 joint actions in every cell. It reports exhaustive no-RIS, fixed-q1 and joint-oracle maxima, together with maxima subject to Bob BER <= 1e−3. These are oracle action-space diagnostics, not learned DRL policy results.

Outputs preserve per-action values in compressed NPZ grids, source hashes and explicit assumptions in `diagnostic_summary.json`. Tests embedded in the runner compare MI against an independent AWGN integral, BER against waveform Monte Carlo, quadrature resolution/current scaling, and colocated-zero-secrecy and finite-alphabet invariants. The parent is responsible for collecting the Antigravity execution log and result files before calling those checks passed.

Suggested command for Antigravity:

```powershell
python -B scripts/run_calibrated_ris_diagnostic.py
```

## Defensible manuscript action

Retain the 90-run historical matched-budget results as the paper-equation implementation comparison. Explain its amplitude-cost interpretation and boundary conventions. Add the alternative physical-channel diagnostic as a separate sensitivity/consistency experiment, labeled with its own rate units and SNR assumptions. If its findings disagree with the historical metric ordering, report the disagreement; do not select one solely to obtain a desired conclusion. Do not claim that this limited diagnostic validates mobility, unknown Eve location, packet secrecy, or the physical reward of the trained historical DRL policies.

If the target journal requires a physically validated joint RIS/FJ DRL controller, the remaining path is new training and matched evaluation using this declared consistent channel, with additional geometries and controller alternatives. That cannot be replaced by changing the manuscript's adjectives or reinterpreting already-saved policies as if they had been trained on a different reward.

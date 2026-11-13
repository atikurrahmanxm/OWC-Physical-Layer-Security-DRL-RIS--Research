# Historical pre-fix comparison with the supplied IEEE paper

This document describes the project before the subsequent corrections. See [current reproduction status](../PAPER_REPRODUCTION.md) and `verification_current.json` for current findings.

Audit date: 12 November 2026, Asia/Kolkata. Reference: the supplied [19 Sep 2024.pdf](../19%20Sep%202024.pdf), DOI 10.1109/TWC.2024.3458046. Page references below use PDF pages 1–14.

**Verdict: the current project is not a 100% implementation or numerical reproduction of the paper.** Several physical parameters and mathematical components agree, but there are confirmed algorithm differences, equation differences, invalid bound labeling, and large differences from the published results. An overall match percentage would be arbitrary without an agreed weighting and acceptance tolerance.

This audit covers the current working tree, including existing uncommitted changes. The simulation sources and existing figures were not modified. SHA-256 hashes of the audited sources and PDF are in [results.json](results.json).

## Method and scope

- Read the supplied paper, inspected rendered pages containing the relevant equations and figures, and compared the Python and JavaScript implementations.
- Ran the existing 21 tests: all passed. These tests do not establish paper reproduction.
- Independently evaluated the printed channel/secrecy expressions for 100 random geometries. The ordinary-domain channel and secrecy expressions agree to floating-point precision, allowing the project's four-LED aggregation and nonnegative secrecy-rate clipping.
- Executed the actual Python Figure 6 routine with 2,000 slots per learning agent. Used NumPy seed 42, PyTorch seed 42, and one PyTorch CPU thread. Captured raw checkpoints and the same EMA-50 values used for plotting.
- For Python Figure 7, evaluated all 625 discrete actions at each of the nine SNR points. Every action has zero secrecy rate at the default geometry under the existing SNR conversion. This is independent of the learning seed or training duration within that action space.
- Executed the actual JavaScript mathematical and learning functions with Node, including its 2,000-slot runs and nine-point SNR sweep. This is not an end-to-end browser UI test.
- Original PNG writes were suppressed during the Python audit. The optional Python Figure 7 training sweep completed both 2,000-slot agents at 4 dB and was then stopped; the other eight training points were not completed. The complete nine-point exhaustive action evaluation and JavaScript sweep are available. No incomplete agent history is used.

Evidence: [Python results](results.json), [browser results](browser_results.json), [Python reproduction script](check_paper_match.py), [JavaScript reproduction script](check_browser_match.js).

## What agrees

| Component | Paper | Current implementation | Assessment |
|---|---|---|---|
| Room and node geometry | Fig. 4, p. 9 | 5 × 5 × 3 m room, Alice at (2.5, 2.5, 3), four ceiling jammers, listed Bob/Eve positions | Matches the depicted nominal geometry. |
| Listed physical constants | Table I, p. 9 | 1 W, alpha 0.10, 60-degree semi-angle/FoV, refractive index 1.5, -98.79 dBm noise, 1 cm² area, 0.54 A/W responsivity | Listed values match. |
| Lambertian channel | Eq. (1), p. 3 | `vlc/channel.py:21` | Functional expression matches; four co-located LED gains are aggregated. Independent maximum absolute gain error: 2.71e-20. |
| Secrecy expression | Eq. (4), p. 4 | `vlc/secrecy.py:16` | Matches for ordinary positive gains, with added positive-part clipping and small-value guards. Independent error: 0 for checked cases. |
| State and utility algebra | Eqs. (6)–(7), pp. 4–5 | `vlc/environment.py:75`, `vlc/secrecy.py:123` | State ordering and utility algebra match. Utility values are affected by the energy difference below. |
| Python Q-learning | Algorithm 1, Eq. (8)–(9), p. 5 | `vlc/rl_fj.py` | Epsilon-greedy alternative-action selection and Bellman update match the stated structure. State bins and exploration schedule are implementation choices. |
| Python CNN and core DND structure | Section IV, pp. 6–7; Section VI, p. 9 | `vlc/drl_fj.py` | Two convolutional/two fully connected layers; F = [20,40,3,2,1,1,180,180], M = 11, T = 4; Gaussian key lookup and replay loss are present. This is partial algorithm agreement, not full equivalence. |
| Figure 7 sampling outline | Section VI, p. 11 | `simulations/sim_fig7_snr.py:31` | Nine points from 4–20 dB and averaging the first 2,000 slots agree with the described procedure. The values do not agree. |

Matching constants does not settle all modeling conventions. For example, `eta = 1`, `I_D = 1`, LED aggregation/power interpretation, and the precise SNR normalization require a consistent interpretation beyond copying Table I.

## Confirmed mismatches

### 1. Published results are not reproduced

The paper reports DRL-FJ secrecy rate 5.68 bps/Hz at slot 1,400 and BER 2.0e-4 at slot 1,200 (p. 10). In the controlled Python run:

| Quantity | Supplied paper | Current Python result |
|---|---:|---:|
| DRL-FJ secrecy rate, slot 1,400 | 5.68 bps/Hz | 1.223117 bps/Hz, EMA-50 |
| DRL-FJ BER, slot 1,200 | 2.0e-4 | 3.243313e-3, EMA-50 |
| RL-FJ secrecy rate near the end | Reported converged value 5.14 bps/Hz | 0.385617 bps/Hz at slot 2,000, EMA-50 |
| Figure 7 secrecy rate, 4–20 dB | Positive curves, approximately 1.75–4.4 bps/Hz for DRL-FJ | Exactly zero for all 625 discrete actions at all nine SNR points |

The paper provides a plotted trace, not a matching random seed or raw time series, so individual checkpoint differences alone would not establish a coding defect. Here there is also an analytic incompatibility with the current defaults:

At the default geometry, `h_AB = 2.718265757e-5` and Table I noise converts to `1.321295634e-13 W`. With the project's alpha and bias values, the interference-free Bob term in Eq. (4) is **1.908654495 bps/Hz**. Jamming cannot increase that term, and the leakage term is nonnegative. Thus the current default model cannot reach the paper's 5.68 bps/Hz, regardless of agent training.

The Figure 7 conversion in `simulations/sim_fig7_snr.py:57` uses `sigma² = P_T h_AB² / 10^(SNR/10)`. In combination with alpha² in Eq. (4), even the interference-free Bob term is only 0.004231 bps/Hz at 4 dB and 0.151788 bps/Hz at 20 dB. Exhaustive action evaluation confirms zero net secrecy throughout. The paper does not provide enough SNR-normalization detail to infer a unique correction; changing the noise to fit the plot would not validate a reproduction.

### 2. The browser does not implement the paper's DRL-FJ

Paper: Algorithm 2 and Section IV, pp. 6–7. Code: `index.html:1751` onward; `visualizer.html` is byte-identical.

The browser uses one scalar Q estimate per action plus neighboring-action score transfer. It does not execute the CNN, construct the specified state-action input, store per-action dictionaries of 180-dimensional CNN keys, or train by replay and Eq. (13). Its RL-FJ routine also uses one Q vector without the state-indexed Q-table used in the Python implementation and paper.

The browser and Python share ordinary physical expressions but run different learning algorithms. For example, the browser's DRL-labeled EMA secrecy rate at slot 1,400 is 0.932514 bps/Hz; the controlled Python CNN/DND run gives 1.223117 bps/Hz. Browser results cannot be presented as outputs of the paper's CNN-based Algorithm 2.

### 3. BER is changed for negative effective channels

Paper: Eq. (14), p. 7. Code: `vlc/secrecy.py:97` and `index.html:1624`.

The printed equation squares `h_AB + h_JB^T w`. The code instead returns 0.75 whenever this sum is nonpositive. A negative sum does not imply a zero squared value.

Counterexample at nominal geometry: `w = [-1,-1,-1,-1]`, `sigma² = 1e-10`, effective channel `-5.389143345e-5`. The printed expression gives **1.0756275e-6**; the implementation gives **0.75**. This changes the reward landscape and therefore learning. The 79 checked positive-effective-channel cases match the expression exactly.

### 4. Energy differs from the literal printed formula

Paper: Eq. (16), p. 8, visually confirmed in the PDF. Code: `vlc/secrecy.py:119` and `index.html:1632`.

The supplied PDF prints `E = varrho_s * sum(w_i)`. The project uses `E = varrho_s * sum(abs(w_i))`. At `w = [-1,-1,-1,-1]`, the values are -4 and +4 respectively, producing different utilities.

This is a **literal mismatch and a paper ambiguity**: a signed sum can produce physically questionable negative energy. The L1 interpretation may be a reasonable engineering decision, but it must be documented as a departure or supported by author clarification. Blindly introducing negative energy is not recommended.

### 5. The zero-forcing routine does not solve the stated optimum

Paper: constrained optimization in Eq. (5), p. 4. Code: `vlc/bounds.py:21`.

Projection of Eve's channel onto Bob's null space followed by infinity-norm scaling yields a feasible nulling direction. Under the stated componentwise box constraints, this does not generally maximize the objective.

Using the current nominal channels:

| Beamformer | Bob residual | Eve amplitude | Secrecy rate |
|---|---:|---:|---:|
| Project projection: [-0.323120, 0.263548, 0.147128, 1] | Approximately 0 | 4.672768e-5 | 1.489029 |
| Feasible LP counterexample: [-0.896374, 1, 1, 1] | -3.39e-21 | 6.645834e-5 | 1.613610 |

The counterexample respects every amplitude constraint and improves secrecy rate, disproving the claim that the projection routine solves Eq. (5). The paper itself calls the ZF-constrained problem suboptimal relative to unconstrained beamforming; that does not justify a further unacknowledged approximation within the ZF problem.

### 6. The theoretical bound is applied outside its conditions

Paper: Corollary 1, Eqs. (18)–(23), p. 8. Code: `vlc/bounds.py:84` onward, with the same issue in the browser.

The paper introduces Eq. (21) under condition (20), `abs(h_JE^T w) / h_AE <= 1`. The code always uses the closed-form expression, without checking this condition or whether its target is feasible. It reports secrecy rate **1.379888**, while its own feasible ZF beamformer achieves **1.489029** under the same defaults. It is therefore not a valid global secrecy-rate upper bound for these evaluations.

The returned bound beamformer has `H/h_AE = 1.386294`, violating condition (20), and its actual Eq. (4) secrecy rate is 1.388312 rather than the reported 1.379888. The utility calculation also combines a closed-form rate with a selected beamformer's energy; it does not establish a global utility optimum.

The supplied paper's log convention, Eq. (20), and target in Eq. (23) require careful reconciliation. Under the base-2 convention used by the project, Eq. (23) gives `H/h_AE = 1/log2(sqrt(e)) = 1.386294`, exceeding 1. This should be disclosed as an unresolved source issue rather than silently treated as an unconditional ceiling.

### 7. Python DND updates differ from the described replacement

Paper: Section IV, p. 7 says an existing key's stored Q-value is updated to the updated Q-value. Code: `vlc/drl_fj.py:130`, `vlc/drl_fj.py:342`.

The agent first forms a Bellman update with learning rate 0.5, then `append_or_update` averages that already-updated value with the stored value again. In the exact-key case, this applies another learning-rate factor. A stored value 2 with supplied updated Q = 4 becomes 3 instead of 4. The additional averaging changes Algorithm 2's behavior. Approximate-key matching, FIFO memory limits, and exploration decay are further implementation choices that are not fully specified by the supplied paper.

### 8. Published benchmark algorithms are replaced by simpler methods

Code: `vlc/benchmarks.py:78`, `:118`, and `:151`.

| Label | Current implementation | Primary-source comparison |
|---|---|---|
| DRL-VB [20] | Epsilon-greedy scalar reward estimates over restricted jammer weights; no deep network | [Xiao et al.'s paper](https://liusc1028.github.io/papers/TCOM19.pdf) develops deep RL for MISO information-signal beamforming. The project does not implement that architecture. |
| Robust beamforming [42] | One Tikhonov-regularized inversion, then a fixed scale of 0.6 | [Ma et al.'s paper](https://people.ece.ubc.ca/lampe/Preprints/2018-VLC-CoordBeamforming.pdf) formulates amplitude-constrained weighted sum-MSE beamforming, including CSI mismatch. The code does not solve that problem. |
| SBJ-VLC [43] | Searches 19 scalar multiples of the same ZF direction | [Cho et al.'s Oxford archive record](https://ora.ox.ac.uk/objects/uuid%3Ae3816443-badd-445b-8bad-9aa5412dd75d) describes joint beamforming/jamming through a concave-convex procedure and an alternative ternary assignment/tabu-search method. Neither is implemented. |

These are useful custom baselines, but the source/code comparison supports classifying them as surrogates. Their results cannot establish the comparative gains against the cited algorithms reported in the supplied paper.

## Other limits and misleading verification claims

- `simulations/sim_fig5_spatial.py:60` and `:77` evaluate ZF directly at each grid point; they do not train either proposed agent. The paper's Fig. 5 numerical surfaces have not been reproduced by matching algorithmic evidence.
- Default figure environments are stationary (`nonstationary_noise_std = 0`). The optional channel perturbation is not used in the default experiments. The supplied paper does not provide complete mobility, blockage, or channel traces, so exact reproduction of its stated nonstationary setting is unverified.
- Figure 6 seeds NumPy but not PyTorch; Figure 7 does not expose a complete seed protocol. The audit adds explicit seeds for repeatability, not as purported author-provided seeds.
- `run.py` defaults evaluation to 12 dB, while `main.py` defaults to Table I noise. At nominal geometry the latter corresponds to 37.475838 dB under the project's SNR definition. These commands do not evaluate equivalent defaults.
- The custom CLI evaluation trains DRL for 500 slots and RL for 1,000 and averages the last 100. It is not the paper's Figure 7 first-2,000-slot average. The dedicated Figure 7 script does use that averaging outline.
- `main.py` accepts `--snr` for training but does not pass a corresponding noise variance into the training environment.
- The generated calculation report and `create_math_report.py:448` declare 100% exact verification using hardcoded comparison rows. Those rows are not computed from a fresh simulation. The report's SNR/noise expression also differs from the current Figure 7 conversion; its listed secrecy rate cannot serve as validation of the current code.
- The existing tests mostly check constants, ranges, shapes, selected identities and nominal behavior. They do not test the negative-channel BER counterexample, constrained ZF optimality, validity of the claimed global bound, genuine benchmark reproduction, browser Algorithm 2 equivalence, or agreement with published curves. All 21 passing is compatible with the failures above.

## What is needed before claiming faithful reproduction

1. Establish and document consistent optical/electrical power, LED aggregation, bias-current, noise-variance, and SNR conventions. Resolve the supplied paper's ambiguous energy and conditional-bound expressions with the authors or explicit, justified assumptions.
2. Fix or explicitly label the BER branch, DND update, ZF approximation, and bound-domain handling. Keep departures separate from a literal-paper implementation.
3. Implement the cited benchmark algorithms, or rename the current methods as custom baselines and withdraw claims of matching those comparisons.
4. Connect the browser to the validated Python agent or clearly label its current learning routines as approximations.
5. Save raw per-slot metrics, full seeds/configuration, and channel traces. Compare published checkpoints/curves with declared numerical tolerances and multiple seeds. Author code or raw data is needed for exact trace-level verification where the PDF is underspecified.
6. Replace hardcoded verification claims with results generated from those checks.

Reproduction commands:

```powershell
python -B paper_audit/check_paper_match.py
node paper_audit/check_browser_match.js
```

The Python command reruns the actual 2,000-slot Figure 6 agents and the exhaustive Figure 7 action checks. `--full-snr-training` additionally runs the substantially slower nine-point Python training sweep; it is unnecessary to establish the zero-secrecy finding for every available action.

The defensible description today is **a partial implementation inspired by the paper, with matching core components and substantial unverified or divergent behavior**.

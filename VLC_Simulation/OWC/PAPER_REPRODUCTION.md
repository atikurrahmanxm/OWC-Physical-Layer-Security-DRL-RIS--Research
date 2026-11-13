# Reproduction status and explicit assumptions

**Status: the zero-secrecy collapse is corrected under explicit physical interpretations; 100% numerical reproduction is unverified.** No author code or raw data was available. The absence was confirmed by the user. Do not describe passing tests as proof of identical published results.

Reference: supplied `19 Sep 2024.pdf` (14 PDF pages), DOI 10.1109/TWC.2024.3458046. An author-hosted copy is at https://liusc1028.github.io/papers/TWC24liu.pdf.

The separate [physical 4-PAM model](PHYSICAL_MODEL.md) now implements and validates a consistent current-domain alternative. It uses finite-alphabet mutual information and exact Gray decision BER from the same signal distribution. Its outputs are stored separately and do not replace the paper-equation audit. This addresses the request to build and test a consistent simulation; it does not resolve the missing author conventions or reproduce the continuous-input paper curves.

## Corrections implemented

| Audit issue | Correction |
|---|---|
| Negative effective channel forced to BER 0.75 | Literal squared Eq. (14), including negative values |
| Negative energy credits reward zero secrecy | Nonnegative L1 interpretation by default; literal signed Eq. (16) remains opt-in |
| Projection claimed to solve Eq. (5) | Exact box-constrained linear program; browser independently enumerates box/null-plane vertices |
| Conditional Eq. (21) shown as global bound | Conditional expression retained as a diagnostic with its domain conflict; independently valid global bounds shown separately |
| Double learning-rate application in DND | Direct replacement by the already-updated Q-value |
| Browser presented a surrogate as CNN/DND | Browser/desktop request real Python training; no synthetic learning fallback |
| Different launcher defaults and ignored training SNR | Shared CLI and named SNR-to-noise conventions |
| SNR conversion excludes modulation scaling in Eq. (4) | Eq. (4) interference-free Bob SINR is the default convention; legacy electrical conversion remains opt-in |
| Incomplete random seeds and lost raw data | Local seeded RNGs, seeded CNN initialization, raw observations/actions/configuration exported |
| Misnamed reference benchmarks | Custom methods honestly named; deprecated old aliases warn |
| Hardcoded verification/certification reports | Generator now computes current values and discloses unresolved issues |

## Why the published curves still cannot be certified

1. **Missing normalization.** The paper lists noise -98.79 dBm but does not specify its SNR conversion or enough electrical/optical scaling details to recover every simulation setting. Under the project's nominal four-LED aggregation, `eta=1`, `I_D=1`, and Table I noise, Bob's interference-free Eq. (4) term is about 1.90865 bps/Hz. The reported Figure 6 rate 5.68 bps/Hz cannot be generated under those assumptions. The code does not lower noise or rescale rates to manufacture a match.
2. **Literal energy ambiguity.** PDF p. 8 Eq. (16) prints `varrho_s * sum(w_i)`, although weights can be negative. That literal mode rewards negative sums and caused the observed zero-secrecy collapse. Nonnegative `varrho_s * sum(abs(w_i))` is now the default physical interpretation. It changes the printed optimization problem and is explicitly recorded; `paper_signed` retains the literal model for comparison. Only author clarification can establish the intended model.
3. **Conditional bound conflict.** PDF p. 8 Eq. (20) requires `H/h_AE <= 1`. With base-2 logs, Eq. (23) requests `H/h_AE = 1/log2(sqrt(e)) = 1.386294`. The closed-form value cannot honestly be called an unconditional global optimum. Diagnostics expose this conflict.
4. **Unspecified implementation choices.** Lx=2, epsilon schedule, 10x10 padding, CNN SGD learning rate, seeds, state bins and channel traces are explicit local choices wherever the PDF gives no complete specification. Stationary default geometry is labeled as such; optional seeded channel perturbations do not reproduce an unknown author trace.
5. **Separate benchmark papers.** References [20], [42], [43] need their own validated implementations and adaptation details. Existing simplified substitutes are preserved only as clearly labeled custom baselines. No published comparative-gain claim is made.

## Current verification

Run `python -B -m unittest discover -s tests -v` for regression checks. Run `python paper_audit/check_paper_match.py` for formula checks and strict comparison with the paper's quoted checkpoints and plotted Figure 7 vertices. It now exits 1 when numerical reproduction fails; `--equations-only` explicitly limits success to implementation checks. The verifier writes `paper_audit/verification_current.json` and `paper_audit/numerical_conformance.json`; it never overwrites the historical pre-fix evidence. Figure data in `output_figures/fig*_data.json` preserve exact run configurations.

The historical [initial audit](paper_audit/PAPER_MATCH_AUDIT.md) records the state before these corrections. Current results supersede it for implementation status; its missing-data/source-ambiguity findings remain relevant.

The [zero-collapse correction](paper_audit/ZERO_COLLAPSE_FIX.md) records the fresh 2,000-slot results, the modeling choices, and the remaining gap. Exported `operating_point` diagnostics separate physical feasibility and utility tradeoffs from learned performance. At low SNR, positive secrecy can be feasible while no jamming maximizes utility because of its lower energy cost.

Further [signal/noise analysis](paper_audit/SIGNAL_NORMALIZATION_GAP.md) inverts both printed equations and shows why changing noise alone cannot simultaneously fit the two targets for a fixed action with the current scaling. The strict comparison extracts the published PDF vector paths and keeps them separate from simulated observations. The Figure 7 paths have five plotted vertices, whereas the project additionally samples the intermediate axis ticks.

## Acceptance for a future 100% claim

A defensible claim needs resolved author conventions, faithful implementations of the separate benchmarks, author traces or an agreed statistical protocol, and declared tolerances for Figures 5-7. Until that evidence exists, `reproduction_verified` remains false in every exported run.

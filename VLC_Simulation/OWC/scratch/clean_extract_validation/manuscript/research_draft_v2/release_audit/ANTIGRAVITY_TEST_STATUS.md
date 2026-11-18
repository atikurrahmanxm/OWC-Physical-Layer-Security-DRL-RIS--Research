# Antigravity Unit Test Execution Status

- **Execution Date**: 2026-11-18 (Asia/Kolkata / UTC+05:30)
- **Environment**: Windows, Python 3.12.10
- **Thread Concurrency**: Single-threaded BLAS/Torch (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `TORCH_NUM_THREADS=1`)
- **Exact Command**: `python -B -m unittest discover -s tests -v`
- **Exit Status**: `0`
- **Duration**: `30.058 seconds` (unittest execution timer: `25.326s`)
- **Log Reference**: [`ANTIGRAVITY_UNIT_TESTS.log`](ANTIGRAVITY_UNIT_TESTS.log)

---

## Summary of Results

| Category | Count | Status |
| :--- | :--- | :--- |
| **Total Tests Discovered & Executed** | **98** | **ALL PASSED** |
| Passed | 98 | OK |
| Failures | 0 | None |
| Errors | 0 | None |
| Skipped | 0 | None |

---

## Module Breakdown

1. **`tests/test_matched_budget_runner.py`** (4 tests):
   - `test_atomic_execution_and_policy_serialization`: OK
   - `test_checkpoint_validation_rules`: OK
   - `test_manifest_runtime_derivation`: OK
   - `test_matched_architecture_all_schemes`: OK (`cnn_m0=11`, 2,560 features, 497,000 parameters across Baseline, Fixed RIS, Joint RIS)

2. **`tests/test_paper_regressions.py`** (16 tests):
   - All 16 regression tests passed (action/noise validation, batched DND dictionary matching, BER channel parity, deterministic agent action recording, CLI SNR handling, corollary boundaries, L1 reward penalties, DND replacement without double averaging, global bounds, HTTP isolation, named SNR conventions, zero leakage without information link, rate ceiling / low SNR utility disclosure, ZF collinear/zero handling, box vertex checks).

3. **`tests/test_physical_model.py`** (14 tests):
   - All 14 physical model validation tests passed (Gray PAM Gaussian BER, likelihood decisions, action grid bounds, physical units/resistance CLI export, direct backend HTTP parity, jamming damage / Joules energy, convention rejection, AWGN mutual information, noise power current units, optical-to-electrical linearity, clean receiver effects, quadrature convergence, finite alphabet ceiling, uniform jamming BER Monte Carlo).

4. **`tests/test_published_targets.py`** (6 tests):
   - All 6 target checks passed (implausible BER bounds rejection, literal equation noise round-trips, non-certification of unknown author models, vector axis decoding, 5 measured SNR vertices, zero rate failure guards).

5. **`tests/test_ris_environment.py`** (11 tests):
   - All 11 RIS environment tests passed (colocated secrecy nullity, dry evaluation state preservation, categorical joint action encoding, non-truncated joint CNN action recording, preview launcher single-seed uncertainty, off-mode paper reduction, CNN/DND preservation when RIS is off, passive Eve independence, soft QoS penalty, HTTP backend training, zero-reflectivity reduction).

6. **`tests/test_ris_optics.py`** (13 tests):
   - All 13 optical RIS physics & integration tests passed (disabled/zero-area nullity, setting validation, backside/FoV cutoff, coplanar finite mirror subdivision gain conservation, feasible positive gain, energy conservation upper bound, metadata stability, quadrature convergence, identical stored normals, linear scaling, tile area reduction, joint and off environment modes).

7. **`tests/test_ris_study.py`** (7 tests):
   - All 7 study evaluation tests passed (evaluation immutability of CNN/DND, evaluation determinism, configuration validation prior to training, nonzero confidence intervals for single seeds, paired difference preservation, Student-$t$ CI calculation, explicit exploration and outage accounting).

8. **`tests/test_supervisor_demo.py`** (5 tests):
   - All 5 web demo service tests passed (`/compact_results.json` route, cross-origin blocking, `/demo` route 200 HTML, figures route PNG delivery, live metrics POST).

9. **`tests/test_vlc_paper.py`** (21 tests):
   - All 21 paper equation and configuration tests passed (Equations 1, 4, 5, 6, 7, 8, 9, 10–12, 14–15, 16, Corollary 1, optical concentrator gain, FOV cutoff, optical-to-electrical conversion, channel dimensions, ZF orthogonality/amplitude bounds, state formulation, utility, epsilon-greedy selection, Bellman Q-update, FeatureCNN forward pass).

---

## Traceback & Anomaly Audit

- **Tracebacks**: None.
- **Failures / Errors**: None.
- **Codebase / Manuscript Alterations**: No simulator code, experiment records, or manuscript texts were modified to conceal or bypass any checks.
- **Retraining / Commits**: No retraining runs were initiated, and no Git commits, pushes, external communications, or deletions were performed.

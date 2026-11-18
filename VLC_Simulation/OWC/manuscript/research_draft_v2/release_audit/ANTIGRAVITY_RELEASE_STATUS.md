# Antigravity Release Status

**Overall Status**: COMPLETED (ALL PASS)  
**Start Time**: 2026-11-18 10:35:10 IST  
**Completion Time**: 2026-11-18 10:52:00 IST  
**Host / Runner**: Antigravity Local Test Executor  
**Working Directory**: `D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC`  
**Threading Environment**:
- `OMP_NUM_THREADS=1`
- `OPENBLAS_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`
- `VECLIB_MAXIMUM_THREADS=1`
- `NUMEXPR_NUM_THREADS=1`
- `TORCH_NUM_THREADS=1`

---

## Check Execution Matrix

| # | Command | Log File | Status | Exit Code | Runtime | Results & Verification |
|---|---|---|---|---|---|---|
| 1 | `python -B scripts/release_statistics.py` | `release_audit/ANTIGRAVITY_STATISTICS.log` | COMPLETED | 0 | ~3s | 18 paired contrasts, 1,024 sign permutations each, Holm sensitivity corrections generated in `statistical_robustness.json` & `STATISTICAL_ROBUSTNESS.md`. |
| 2 | `python -B scripts/release_validation.py --phase all` | `release_audit/ANTIGRAVITY_VALIDATION.log` | COMPLETED | 0 | ~15m 28s | 90 policy replays (90k slots, 360k metric values matched with atol=1e-10), 15 finite-grid cases (46,875 evals), 120 frozen transfer cases (24k slots). Generated `full_policy_replay.json`, `geometry_grid_sensitivity.json`, `frozen_policy_geometry_transfer.json`. |
| 3 | `python -B scripts/run_calibrated_ris_diagnostic.py` | `release_audit/ANTIGRAVITY_CALIBRATED.log` | COMPLETED | 0 | ~40s | 9 scenario/SNR grids (3 scenarios × 3 SNRs), 28,125 action evaluations. Integration, MC, and symmetry checks passed. Output saved to `output_figures/ris/calibrated_diagnostic_v1/`. |

---

## Completed Populations & Details

### 1. Statistical Robustness Suite (`scripts/release_statistics.py`)
- **Denominator / Contrasts**: 18 paired contrasts (3 training budgets × 3 scheme comparisons × 2 metrics), evaluated over 10 matched seeds (seeds 42–51).
- **Exact Sign-Flip Enumeration**: 1,024 permutations per contrast.
- **Family-wise Multiplicity**: Full-family 18-hypothesis Holm step-down correction for t-tests and sign-flip permutations.
- **Failures / Exceptions**: 0.

### 2. Release Validation Suite (`scripts/release_validation.py --phase all`)
- **Phase A — Policy Replay**:
  - 90 saved CNN+DND policies across budgets 2k, 5k, 10k and schemes baseline, fixed_ris, joint_ris.
  - 1,000 evaluation slots per policy = 90,000 slots total.
  - 4 metrics evaluated per slot (`utility`, `secrecy_rate`, `ber`, `energy`) = 360,000 metric values compared against recorded runs.
  - `max_absolute_error` < 1e-10 across all 360,000 values (`all_match=True`).
  - First-action and evaluation q-counts matched exactly across all 90 runs.
- **Phase B — Finite-Grid Oracle Sensitivity**:
  - 5 prespecified geometries (`nominal`, `changed_positions`, `swapped_receivers`, `near_eve`, `colocated`).
  - 3 noise offsets (-3 dB, 0 dB, +3 dB).
  - 3,125 joint actions enumerated per case = 46,875 evaluations across 15 cases.
- **Phase C — Frozen Policy Geometry Transfer**:
  - 30 nominal-trained 10,000-slot policies (10 seeds × 3 schemes).
  - 4 supplementary test geometries (`changed_positions`, `swapped_receivers`, `near_eve`, `colocated`).
  - 200 evaluation slots per transfer run = 120 cases / 24,000 slots total.
  - Secrecy outage (<0.1) and Bob outage (>1e-4) recorded. Co-location confirmed 0 secrecy.
- **Failures / Exceptions**: 0.

### 3. Calibrated RIS Diagnostic Suite (`scripts/run_calibrated_ris_diagnostic.py`)
- **Model Status**: Explicit opt-in current-domain 4-PAM/RIS physical channel diagnostic (bits/real channel use). Separate from paper-mode baseline.
- **Independent Checks**:
  - Independent AWGN numerical integration error: passed (< 1e-8).
  - 300,000-symbol Monte Carlo BER match: passed (error < 0.0025).
  - Quadrature convergence & current scaling: passed.
  - Zero-signal & finite-alphabet ceiling: passed.
- **Evaluations**:
  - 3 scenarios × 3 SNR levels (10 dB, 20 dB, 30 dB) = 9 grid configurations.
  - 3,125 actions per configuration = 28,125 total action evaluations.
  - Co-located negative control confirmed max secrecy = 0.000000 bits/use.
- **Failures / Exceptions**: 0.

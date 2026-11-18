# Claim–evidence map (expanded release package)

The source of all matched-study numerical claims is `output_figures/ris/training_budget_study_matched_v2/runs/`, not copied prose or the legacy study. Release testing was executed through Antigravity across policy replay, statistical sensitivity, geometry sensitivity, frozen transfer, and calibrated physical diagnostics. Hashes are in `evidence_manifest.json` and `research_release/RELEASE_PACKAGE_MANIFEST.json`.

| Claim | Evidence | Status and boundary |
|---|---|---|
| 90 complete protocol-v2 records, ten seeds, three budgets, three schemes | Record identity/config/completion checks over the exact Cartesian product | Verified as recorded; no new training |
| Evaluation means and uncertainty | All four metric arrays checked for 1,000 finite entries and agreement with stored means; statistics recomputed from ten seed means | Verified; evaluation slots are not independent replicates |
| Joint minus fixed utility +0.0183, p=0.82887 (95% CI [-0.1677, +0.2043]) | Recomputed paired t-test on the ten 10k seed differences; primary contrast | Supported; inconclusive; does not establish equivalence or superiority |
| Joint minus fixed secrecy -0.0817 bps/Hz, p=0.4182 (95% CI [-0.2996, +0.1362]) | Recomputed paired t-test on ten 10k seed differences | Inconclusive; does not support fixed or joint superiority |
| Fixed minus baseline utility +0.2051, p=0.00034 (Holm-t p=0.00614, sign-flip p=0.00391, Holm sign-flip p=0.07031) | Paired contrast with full 18-hypothesis family Holm adjustment and 1,024 sign flips | Supported in nominal geometry/model; sensitive to multiplicity adjustment |
| Fixed minus baseline secrecy +0.2451, p=0.00409 (Holm-t p=0.06956, sign-flip p=0.00781, Holm sign-flip p=0.13281) | Paired contrast with full 18-hypothesis family Holm adjustment and 1,024 sign flips | Exploratory; sensitive to multiplicity; not confirmatory security claim |
| Joint minus baseline utility +0.2234, p=0.02261 (Holm-t p=0.31661, sign-flip p=0.02539, Holm sign-flip p=0.38086) | Paired contrast with full 18-hypothesis family Holm adjustment and 1,024 sign flips | Exploratory; sensitive; does not survive full-family Holm correction |
| Joint minus baseline secrecy +0.1634, p=0.07818 (Holm-t p=1.00000, sign-flip p=0.08789, Holm sign-flip p=0.99023) | Paired contrast with full 18-hypothesis family Holm adjustment and 1,024 sign flips | Inconclusive under both unadjusted and adjusted testing |
| Joint coverage 9.11% at 10k | Mean 284.8 distinct visited actions / 3,125 | Verified from stored counts; historical 7.8% corrected |
| Six joint runs select modal q=1, four another q at 10k | Full per-run evaluation configuration count records (`q_counts`) | Observed evaluation horizon only; first-action distinction documented |
| Finite-grid maxima occur at q=1 in nominal geometry | Fresh enumeration of 3,125 existing simulator actions | Verified; not an unrestricted physical upper bound across all geometries |
| Fixed actions are contained in joint set | All 625 fixed actions checked against corresponding q=1 joint actions for utility/rate/BER/cost | Verified to absolute tolerance 1e-12 |
| Displayed secrecy/BER formulas describe simulator | Independent evaluation of displayed algebra for every joint action, including boundary conventions | Checked numerically at 3,125 actions; not a proof of physical validity |
| Matched CNN dimensions | Recorded m0=11 config; runner assertion; implementation dimensions | Architecture matched, not equal DND memory occupancy |
| 180 checkpoint files exist | File presence, nonzero length, and SHA256 inventory in `RELEASE_CHECKPOINT_INVENTORY.json` | Verified; 2.06 GB uncompressed payload inventoried |
| All 90 saved policies reproduce recorded evaluation | Fresh CNN/DND reload for all 90 policies across 2k/5k/10k, evaluating 1,000 greedy slots (90,000 slots, 360,000 metric values) at atol < 1e-10 (`release_audit/full_policy_replay.json`) | All 360,000 values matched exactly; all first actions and q-counts matched |
| Geometry grid sensitivity (15 cases) | 5 geometries × 3 noise offsets (-3, 0, +3 dB); 3,125 action evaluations each = 46,875 evaluations (`release_audit/geometry_grid_sensitivity.json`) | Discrete oracles achieve positive utility (0.7119--1.0418) in nominal/changed/swapped; zero in colocated/nearby-Eve |
| Frozen policy zero-shot transfer (120 cases) | 30 nominal-trained 10k policies evaluated 200 slots across 4 changed geometries (24,000 slots total; `release_audit/frozen_policy_geometry_transfer.json`) | Frozen policies yield negative mean utility (-0.5608 to -0.7876) and large optimality gaps (>1.6) without retraining |
| Calibrated current-domain 4-PAM diagnostic (9 grids) | Explicit opt-in 4-PAM channel with shared independent uniform jammer and AWGN; 28,125 evaluations (`output_figures/ris/calibrated_diagnostic_v1/`) | QoS-feasible positive secrecy (1.65--1.73 bits/use) at 20--30 dB SNR; infeasible at 10 dB; identically zero in colocated control |
| Independent integration and Monte Carlo checks | AWGN numerical integration error < 1e-8; 300,000-symbol Monte Carlo BER match < 0.0025; current scaling invariants verified | Verified in `scripts/run_calibrated_ris_diagnostic.py` |
| Utility uses nonnegative L1 amplitude cost | Configuration, utility implementation, run records | Explicit convention, not joules or total system energy |
| Protection against blockage, mobility, unknown Eve, or hardware attacks | No matched experiments for these conditions | Not claimed |
| Joint control causes an exploration deficit | Low coverage is observed; no causal ablation | Hypothesis only |
| General novelty or state-of-the-art performance | Targeted prior-work check only; no reproduced prior RIS controllers | Not claimed |

Mean recorded 10k training times are 1781.7/1608.2/1632.2 seconds for no RIS/fixed/joint. These are concurrent execution measurements, not a controlled hardware benchmark.

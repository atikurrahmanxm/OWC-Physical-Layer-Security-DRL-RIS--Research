# Antigravity validation task

The new user instruction requires all testing to run through Antigravity. Codex prepared the runner but stopped its direct launch before observing a completed replay result. A protocol setup file may exist; it is not evidence of completed testing. Do not report the suite as passed until Antigravity executes it and inspects its outputs.

## Exact commands

Use PowerShell in the OWC project root:

```powershell
python -B scripts/release_validation.py --phase replay
python -B scripts/release_validation.py --phase grid
python -B scripts/release_validation.py --phase transfer
```

Alternatively, `python -B scripts/release_validation.py --phase all` runs the phases in that order. Torch uses one CPU thread. No training occurs and the original study files are read-only inputs. Expect minutes rather than a new overnight training matrix; actual runtime depends on saved DND size and CPU load.

Run each command to completion and retain stdout/stderr and exit code. If one phase fails, retain its partial outputs and traceback; do not label the entire suite passed. Each run writes its own result immediately, while aggregate JSON is written only after its phase completes.

## Declared populations

- Replay: all 90 original saved CNN+DND policies, 1,000 evaluation slots each, four metric arrays. Denominator: 90,000 slots / 360,000 metric values. Compare values to absolute tolerance `1e-10`, first action, and full RIS configuration counts.
- Finite-grid sensitivity: five prespecified geometries (nominal plus four supplementary cases), three numerical noise offsets −3/0/+3 dB, all 3,125 joint actions per case. Denominator: 15 cases / 46,875 action evaluations. Report maxima for no RIS, fixed q=1 and joint action subsets.
- Frozen-policy transfer: 30 nominal-trained 10,000-slot policies, four supplementary geometries, 200 frozen evaluation slots. Denominator: 120 policy–geometry cases / 24,000 slots. This is a frozen nominal learner with oracle geometry-reconstructed codebook; it is not retrained multi-geometry learning or unknown-Eve validation.

Supplementary receiver positions in metres were fixed before outcomes:

| Scenario | Bob | Eve |
|---|---|---|
| nominal | (1.8,1.6,0.85) | (3.2,3.4,0.85) |
| changed_positions | (2.0,3.0,0.85) | (3.5,1.5,0.85) |
| swapped_receivers | (3.2,3.4,0.85) | (1.8,1.6,0.85) |
| near_eve | (1.8,1.6,0.85) | (1.9,1.7,0.85) |
| colocated | (1.8,1.6,0.85) | (1.8,1.6,0.85) |

The codebook is reconstructed from exact scenario coordinates, including Eve. The numerical noise sweep preserves paper mode and does not resolve physical current/noise calibration. Co-location is a negative-control geometry; report its outcomes without forcing positive secrecy.

## Expected outputs

All outputs are under `manuscript/research_draft_v2/release_audit/`:

- `validation_protocol.json`: choices, current effective configuration and source-script hash; this file alone is not completion evidence.
- `replay_runs/`: one result per replayed policy.
- `full_policy_replay.json`: full-population aggregate; inspect `policy_count=90`, `slots_per_policy=1000`, and `all_match=true`.
- `geometry_grid_sensitivity.json`: 15 finite-grid cases and maxima.
- `transfer_runs/`: 120 case records.
- `frozen_policy_geometry_transfer.json`: full transfer aggregate with interpretation boundary.

The existing runner stores `chosen_q` and `chosen_action` as the **first evaluation action**, not necessarily the modal action. Use full `q_counts` to discuss modal behavior. The new runner records both first-action matching and actual modal q.

## Provenance boundary

Successful replay would show that current code with reconstructed recorded settings reproduces saved evaluation values. It does not recover the original uncommitted execution working tree, replay original training, prove all historical configuration fields were logged, or establish physical validity of the inherited metrics. Preserve these boundaries in the paper and final report.

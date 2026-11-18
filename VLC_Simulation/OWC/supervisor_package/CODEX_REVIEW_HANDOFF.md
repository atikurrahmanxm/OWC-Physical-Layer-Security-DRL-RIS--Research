# Codex Review Handoff: Matched Training-Budget Empirical Study (Protocol v2)

**Document Date & Verification Time:** `2026-11-18 04:50:23 +05:30` (Asia/Calcutta)  
**Author:** Antigravity Research Assistant  
**Audience:** Codex Reviewer / Supervisor Review  
**Directive Reference:** [`antigravity_report/OVERNIGHT_RESUME_TASK.md`](../antigravity_report/OVERNIGHT_RESUME_TASK.md) & [`antigravity_report/JOINT_CONTROLLER_AUDIT_AND_BUDGET_TASK.md`](../antigravity_report/JOINT_CONTROLLER_AUDIT_AND_BUDGET_TASK.md)  
**Execution Status:** **100% COMPLETED & VERIFIED (90 / 90 Runs, 180 Model Checkpoints)**  
**Git Source Commit:** `a6d4304192cb9e6a2881aa4649ea436d2d81d8d2`  
**Consolidated Results JSON:** [`output_figures/ris/training_budget_study_matched_v2/budget_study_summary.json`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\budget_study_summary.json)

---

## 1. Executive Summary for Codex Reviewer

This handoff document provides the Codex reviewer with the verified evidence, architecture parity documentation, checkpoint invariants, and reproduction commands for the **Controlled Matched Training-Budget Empirical Study (Protocol v2)**.

### Prior Protocol Violations Resolved:
1. **Feature Extractor Discrepancy ($m_0=10$ vs $11$):**
   - Enforced explicit `cnn_m0=11` across **ALL three schemes** (Baseline, Fixed RIS, Joint RIS). Feature extraction parity verified via unit tests (`FeatureCNN` in_features=2560, total params=497,000 across all schemes).
2. **Dynamic Runtime Manifest Geometry:**
   - Manifest parameters are dynamically extracted from actual Python dataclasses at runtime (`ris_center: [2.5, 0.25, 2.6]`).
3. **Atomic File Serialization & Skip Integrity:**
   - JSON is written to a unique temp file, flushed and synced (`os.fsync`), and atomically renamed via `os.replace`. Skip validation explicitly asserts `protocol_version=2`, `cnn_m0=11`, finite metrics, and exact 1,000-slot evaluation history lengths.
4. **Policy Checkpointing Round-Trip:**
   - Each completed run writes both a PyTorch model checkpoint (`policy_<scheme>_s<seed>_b<budget>.pt`) using safe `weights_only=True` compatible dictionaries, and the active DND memory table (`dnd_<scheme>_s<seed>_b<budget>.json`).
5. **Legacy Data Segregation:**
   - All 68 legacy run files in `output_figures/ris/training_budget_study/` are preserved intact as legacy diagnostics.
   - All 90 Protocol v2 runs executed cleanly into [`output_figures/ris/training_budget_study_matched_v2/`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2/).

---

## 2. Test Suite & Verification Evidence

All 98 test cases in the test suite pass with 100% acceptance:
- **`tests/test_matched_budget_runner.py` (4 Tests Passed):**
  - `test_matched_architecture_all_schemes`: Verifies `cnn_m0=11`, `in_fc1=2560`, and 497,000 parameters across Baseline, Fixed RIS, and Joint RIS.
  - `test_manifest_runtime_derivation`: Verifies manifest dynamic derivation and $z=2.6\text{ m}$.
  - `test_checkpoint_validation_rules`: Verifies rejection of corrupted/legacy checkpoints and acceptance of valid v2 checkpoints.
  - `test_atomic_execution_and_policy_serialization`: Verifies atomic write, PyTorch weights_only round-trip, and DND JSON round-trip.
- **Full Master Test Suite:**
  - `python -m unittest discover tests` executed cleanly (**Ran 98 tests in 24.864s, OK**).

---

## 3. Matched Study Final Completed Matrix (Protocol v2)

The 90-run matrix spans **3 Schemes $\times$ 10 Seeds (42–51) $\times$ 3 Budgets (2,000, 5,000, 10,000 slots)** with 1,000 slots frozen greedy evaluation ($\epsilon=0$, L1 energy, `model='paper'`):

| Scheme | Budget (Slots) | Seeds Matched | Completed | Pending | Status | Checkpoints Saved |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Baseline (No RIS)** | 2,000 | 42–51 | **10 / 10** | **0** | **COMPLETED** | 10 `.pt` + 10 `.json` |
| **Fixed RIS ($q=1$)** | 2,000 | 42–51 | **10 / 10** | **0** | **COMPLETED** | 10 `.pt` + 10 `.json` |
| **Joint RIS ($q \in 0..4$)** | 2,000 | 42–51 | **10 / 10** | **0** | **COMPLETED** | 10 `.pt` + 10 `.json` |
| **Baseline (No RIS)** | 5,000 | 42–51 | **10 / 10** | **0** | **COMPLETED** | 10 `.pt` + 10 `.json` |
| **Fixed RIS ($q=1$)** | 5,000 | 42–51 | **10 / 10** | **0** | **COMPLETED** | 10 `.pt` + 10 `.json` |
| **Joint RIS ($q \in 0..4$)** | 5,000 | 42–51 | **10 / 10** | **0** | **COMPLETED** | 10 `.pt` + 10 `.json` |
| **Baseline (No RIS)** | 10,000 | 42–51 | **10 / 10** | **0** | **COMPLETED** | 10 `.pt` + 10 `.json` |
| **Fixed RIS ($q=1$)** | 10,000 | 42–51 | **10 / 10** | **0** | **COMPLETED** | 10 `.pt` + 10 `.json` |
| **Joint RIS ($q \in 0..4$)** | 10,000 | 42–51 | **10 / 10** | **0** | **COMPLETED** | 10 `.pt` + 10 `.json` |
| **Total** | — | — | **90 / 90** | **0 / 90** | **100% COMPLETE** | **180 checkpoints saved** |

---

## 4. Key Scientific Findings from the Empirical Study

1. **Null Result Confirmed at 10,000 Slots:**
   - Primary question: Does expanding training budget allow Joint RIS to outperform Fixed RIS?
   - Result: **No.** At 10,000 slots, $\Delta U = +0.0183 \pm 0.0818$ ($t = 0.22, p = 0.8289$). Joint RIS remains statistically indistinguishable from Fixed RIS.
   - For secrecy rate, Fixed RIS actually leads by $+0.0817\text{ bps/Hz}$ ($\Delta R_s = -0.0817, p = 0.4182$).
2. **Action Space Dilution & Trapping Mechanism:**
   - Joint RIS explores only $7.8\%$ of its 3,125 actions even after 10,000 slots.
   - Only 6 of 10 seeds converged to the global optimal RIS configuration $q=1$. The remaining 4 seeds converged to sub-optimal configurations ($q=2$: 1 seed, $q=3$: 2 seeds, $q=4$: 1 seed).
3. **RIS Advantage Over Baseline:**
   - Fixed RIS outperforms Baseline decisively at 10,000 slots: $\Delta U = +0.2051 \pm 0.0385$ ($t = 5.33, p = 0.0003$).

---

## 5. Artifact Index for Codex Review

1. **Protocol v2 Study Manifest:** [`output_figures/ris/training_budget_study_matched_v2/manifest.json`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\manifest.json)
2. **Consolidated Results JSON:** [`output_figures/ris/training_budget_study_matched_v2/budget_study_summary.json`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\budget_study_summary.json)
3. **Runner Implementation:** [`simulations/sim_training_budget_study.py`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\simulations/sim_training_budget_study.py)
4. **Runner Test Suite:** [`tests/test_matched_budget_runner.py`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\tests\test_matched_budget_runner.py)
5. **Stage A Joint Controller Audit Report:** [`supervisor_package/JOINT_CONTROLLER_AUDIT.md`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\supervisor_package\JOINT_CONTROLLER_AUDIT.md)
6. **Supervisor Completion Report:** [`supervisor_package/TRAINING_BUDGET_COMPLETION_REPORT.md`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\supervisor_package\TRAINING_BUDGET_COMPLETION_REPORT.md)
7. **4 Scientific Plots (PNG & PDF):** [`output_figures/ris/training_budget_study_matched_v2/figures/`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\figures/)

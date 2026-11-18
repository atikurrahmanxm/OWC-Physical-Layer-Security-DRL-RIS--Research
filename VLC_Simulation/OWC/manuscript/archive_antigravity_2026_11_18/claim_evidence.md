# Claim–Evidence Mapping & Empirical Verification Matrix

**Paper Title:** Fixed and Joint Optical RIS–Friendly Jamming Control for Secure Visible Light Communication: A Matched Training-Budget Empirical Study  
**Document Reference:** `manuscript/research_draft_v2/claim_evidence.md`  
**Evaluation Dataset:** Protocol v2 Matched Matrix (90 runs, 10 seeds 42–51, 3 schemes, 3 budgets)  
**Primary Dataset Directory:** [`output_figures/ris/training_budget_study_matched_v2/`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\)  

---

## 1. Primary Empirical Claims and Direct Evidence

| # | Scientific Claim in Manuscript | Numerical Result in Text | Raw Record & Statistical Evidence | Status |
|---|:---|:---|:---|:---:|
| **C1** | **Joint Controller does not outperform Fixed RIS at 10,000 slots:** Increasing training budget to 10,000 slots does not produce a statistically significant utility gain for Joint RIS over Fixed RIS. | $\Delta U = +0.0183 \pm 0.0822$, $95\%\text{ CI } [-0.1677, +0.2043]$, $t = +0.223$, $p = 0.8289$. | `output_figures/ris/training_budget_study_matched_v2/budget_study_summary.json` (paired comparison `Joint minus Fixed` at budget 10,000, df=9). | **VERIFIED SUPPORTED** |
| **C2** | **Fixed RIS achieves higher mean secrecy rate than Joint RIS:** At 10,000 slots, Fixed RIS achieves a numerically higher frozen evaluation secrecy rate than Joint RIS. | Fixed: $1.5656 \pm 0.0766\text{ bps/Hz}$; Joint: $1.4839 \pm 0.0598\text{ bps/Hz}$; $\Delta R_s = -0.0817\text{ bps/Hz}$, $p = 0.4182$. | 10 matched seeds (42–51) frozen evaluation averages. Zero secrecy advantage for Joint controller. | **VERIFIED SUPPORTED** |
| **C3** | **Fixed RIS significantly outperforms Baseline at 10,000 slots:** Deploying a fixed optical RIS aligned toward Bob ($q=1$) yields decisive, statistically significant utility and secrecy improvements over the no-RIS baseline. | $\Delta U = +0.2051 \pm 0.0367$, $t = +5.585$, $p = 0.00034$; $\Delta R_s = +0.2451 \pm 0.0642$, $t = +3.820$, $p = 0.00409$. | Paired difference across 10 matched seeds at 10,000 slots. Demonstrates strong physical-layer security value of optical RIS. | **VERIFIED SUPPORTED** |
| **C4** | **Theoretical Finite-Grid Ceiling Equivalence:** In the nominal geometry, configuration $q=1$ (Aim Bob) is the global maximum across all 3,125 discrete actions for both utility and secrecy. Joint RIS cannot physically exceed Fixed RIS. | $U^* = 0.9959$, $R_s^* = 1.8413\text{ bps/Hz}$ for both Fixed and Joint controller finite grids. | Exhaustive enumeration in `scripts/audit_joint_controller.py` across all $5^4 \times 5 = 3,125$ discrete actions. | **VERIFIED SUPPORTED** |
| **C5** | **Exploration Dilution & Sub-optimal State Trapping:** The Joint action space ($|\mathcal{A}|=3,125$) suffers severe exploration dilution compared to Fixed RIS ($|\mathcal{A}|=625$), leading to persistent local trapping. | At 10,000 slots, Joint explores only $7.8\%$ (244 actions) vs Fixed exploring $31.8\%$ (199 actions). Only 6/10 seeds in Joint converge to $q=1$ (4/10 trapped in $q \in \{2, 3, 4\}$). | Extracted from `training.unique_actions_visited` and `evaluation.chosen_q` across all 90 runs in Protocol v2. | **VERIFIED SUPPORTED** |
| **C6** | **Architectural & Dimension Parity (Protocol v2):** All three schemes use an identical feature extractor architecture and parameter count. | $m_0 = 11$, input dimension $121$, $in\_fc1 = 2,560$, parameter count $497,000$ for Baseline, Fixed RIS, and Joint RIS. | `tests/test_matched_budget_runner.py` passed 4/4; `FeatureCNN` in `vlc/drl_fj.py`. | **VERIFIED SUPPORTED** |
| **C7** | **Computational Wall-Clock Scaling:** Joint control requires substantially higher computational training time per slot due to expanded action evaluations and DND memory retrieval. | At 10,000 slots: Baseline $= 183.1\text{ s}$, Fixed RIS $= 191.0\text{ s}$, Joint RIS $= 310.2\text{ s}$ ($+62.4\%$ runtime overhead). | Derived from `training.wall_clock_seconds` across 10 matched seeds. | **VERIFIED SUPPORTED** |

---

## 2. Boundary and Negative Claims (Preventing Overclaiming)

| Negative Claim in Manuscript | Verification & Boundary Definition |
|:---|:---|
| **No claim of Joint Superiority:** The paper explicitly concludes that Joint RIS does not outperform Fixed RIS in this stationary setting. | Confirmed. Primary paired difference $p = 0.8289$; null hypothesis cannot be rejected. |
| **No claim of First-Ever Algorithmic Novelty:** The contribution is framed as a rigorous empirical comparative study and scaling audit, not the invention of DRL or RIS. | Confirmed. Paper attributes DRL-FJ to Liu et al. (2024) and optical RIS modeling to standard geometrical optics. |
| **No claim of Published Curve Reproduction:** The paper explicitly declares that non-negative L1 energy and optical RIS are extensions, distinguishing them from the 2024 paper's literal equations. | Confirmed. Methodology section explicitly documents the L1 energy definition $\|\mathbf{w}\|_1$ and baseline differences. |
| **Zero BER is not Hardware Reliability:** Numerical zero BER in floating-point simulation ($\text{erfc}(\cdot) \approx 0$) is explicitly documented as numerical underflow, not physical zero-defect hardware performance. | Confirmed. Stated in System Model and Discussion sections. |

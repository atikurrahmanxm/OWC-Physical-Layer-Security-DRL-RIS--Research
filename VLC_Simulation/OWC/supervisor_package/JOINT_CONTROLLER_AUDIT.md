# Joint RIS/FJ DRL Controller Audit Report (Stage A)

**Author:** Antigravity Research Assistant  
**Date:** November 17, 2026 (Asia/Calcutta)  
**Status:** Completed & Empirically Verified  
**Task Reference:** [`antigravity_report/JOINT_CONTROLLER_AUDIT_AND_BUDGET_TASK.md`](../antigravity_report/JOINT_CONTROLLER_AUDIT_AND_BUDGET_TASK.md)  
**Primary Dataset:** [`output_figures/ris/final_evaluation/ris_study_data.json`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/output_figures/ris/final_evaluation/ris_study_data.json) (183.4 MB, 10 Seeds $\times$ 3 Schemes)  
**Analysis Script:** [`scripts/audit_joint_controller.py`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/scripts/audit_joint_controller.py)  
**Audit Artifacts:** [`output_figures/ris/joint_controller_audit/`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/output_figures/ris/joint_controller_audit/)  

---

## 1. Executive Summary & Core Scientific Findings

This investigation resolves the fundamental scientific question posed in the research brief:
> **Why did the Joint RIS/FJ DRL controller not statistically outperform the Fixed RIS controller in the nominal 2,000-slot study (1.4565 vs. 1.4978 bps/Hz), despite operating on a strictly superset action space?**

By conducting a rigorous, reproducible audit of the complete saved experimental records across 10 matched seeds (Seeds 42–51, 90,000 slots total) and independently enumerating the physical channel bounds in `RISEnvironment`, we establish the following empirical facts:

1. **Theoretical Ceiling Equivalence ($\max U_{\text{joint}} \equiv \max U_{\text{fixed}}$):**  
   In the stationary nominal VLC environment ($Bob$ at $[1.8, 1.6, 0.85]\text{ m}$, $Eve$ at $[3.2, 3.4, 0.85]\text{ m}$), exhaustive enumeration of all 3,125 discrete actions proves that **Configuration $q = 1$ (Aim Alice $\to$ Bob) is the global maximum across the entire discrete codebook** for both system utility ($U^* = 0.9959$) and secrecy rate ($R_s^* = 1.8413\text{ bps/Hz}$). None of the other RIS configurations ($q=0$ Off, $q=2$ Aim Eve, $q=3$ Split, $q=4$ Neutral) can physically exceed $q=1$. Therefore, the theoretical upper bound of the Joint controller is identical to that of the Fixed controller.
2. **Exploration Deficit in 2,000 Training Slots:**  
   The Fixed RIS controller searches a 625-action space and visits an average of $147.4$ unique actions ($23.58\%$ coverage). The Joint controller searches a 3,125-action space but visits only $133.0$ unique actions ($4.26\%$ coverage). **Over $95.7\%$ of the joint action space is never sampled even once during training.**
3. **RIS Configuration Trapping in Joint Seeds:**  
   Because of sparse exploration, only 5 out of 10 seeds in Joint RIS (Seeds 42, 43, 46, 47, 51) converged to the globally optimal configuration $q = 1$. The remaining 5 seeds became trapped in sub-optimal configurations ($q = 3$ for Seeds 44 and 50; $q = 4$ for Seeds 48 and 49; $q = 2$ for Seed 45), where the achievable physical ceiling is strictly lower. In contrast, Fixed RIS is constrained to $q=1$ by definition across all 10 seeds.
4. **Feasibility Invariant Verified ($100\%$ Match):**  
   Every action selected by the Fixed RIS controller during frozen evaluation was re-evaluated inside the Joint environment with identical parameters. The invariant held with machine precision (maximum error $< 4.44 \times 10^{-16}$).
5. **Reward vs. Secrecy Objective Distinction:**  
   The DRL agent optimizes system utility $U = R_s - 3.5 \times \text{BER} - 0.4 \times \|\mathbf{w}\|_1$, not secrecy rate alone. In terms of frozen evaluation utility, Joint RIS actually achieved a slightly higher sample mean than Fixed RIS ($+0.0387$, due to selecting lower-power jammer configurations in some seeds), but the difference is statistically indistinguishable from zero ($t = 0.33, p = 0.7463$).

---

## 2. Action Space Coverage & Concentration Analysis

Across the 2,000 training slots per run, we tracked cumulative unique actions sampled, weight-vector coverage, and selection concentration across the three schemes:

| Scheme | Available Actions $|\mathcal{A}|$ | Mean Unique Actions Sampled | Coverage Fraction | Mean Unique Jammer Weights (out of 625) | Top-1 Action Concentration | Action Distribution Entropy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (No RIS)** | 625 | $178.7 \pm 6.8$ | **$28.59\%$** | $178.7$ ($28.59\%$) | $30.8\%$ | $5.36\text{ bits}$ |
| **Fixed RIS ($q=1$)** | 625 | $147.4 \pm 7.4$ | **$23.58\%$** | $147.4$ ($23.58\%$) | $33.4\%$ | $5.12\text{ bits}$ |
| **Joint RIS ($q \in \{0..4\}$)** | 3,125 | $133.0 \pm 8.2$ | **$4.26\%$** | $124.9$ ($19.98\%$) | $36.1\%$ | $4.89\text{ bits}$ |

![Audit Figure 1: Action Space Coverage](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/output_figures/ris/joint_controller_audit/audit_action_coverage.png)
*(a) Cumulative unique actions sampled over 2,000 training slots; (b) Percentage of total available action space covered.*

### Key Diagnostic Observations:
- **Exploration Squeezing:** With an $\epsilon$-greedy schedule starting at $\epsilon_0 = 0.15$ and decaying by $0.998$ per slot down to $\epsilon_{\min} = 0.02$, the total number of random exploratory decisions across 2,000 slots is approximately:
  $$\mathbb{E}[N_{\text{explore}}] = \sum_{t=0}^{1999} \max(0.02, 0.15 \cdot 0.998^t) \approx 103 \text{ slots}$$
- For a 625-action space (Baseline and Fixed), $103$ exploratory slots plus greedy exploitation enables visiting $\sim 150\text{--}180$ actions ($24\text{--}28\%$).
- For a 3,125-action space (Joint), $103$ exploratory actions can cover at most $3.3\%$ of the action space. The remaining $96.7\%$ of actions are never evaluated during exploration.
- **Weight Coverage:** Joint RIS sampled only $124.9$ distinct jammer weight combinations out of 625, compared to $147.4$ in Fixed RIS, showing that the 5th action dimension (RIS $q$) actively diluted jammer weight exploration.

---

## 3. RIS Configuration Dynamics ($q \in \{0, 1, 2, 3, 4\}$)

We audited the selection of the discrete RIS configuration coordinate across training and frozen evaluation:

| RIS Configuration Index ($q$) | Physical Pointing Direction | Training Slot Allocation (All 2,000 Slots) | Training Slot Allocation (Final 500 Slots) | Frozen Evaluation Seeds Selected (out of 10) |
| :--- | :--- | :---: | :---: | :---: |
| **$q = 0$ (Stowed / Off)** | Neutral specular absorption / off | $16.4\%$ | $8.2\%$ | **$0 / 10$ seeds** |
| **$q = 1$ (Aim Alice $\to$ Bob)** | Specular reflection focused on Bob | **$34.8\%$** | **$47.6\%$** | **$5 / 10$ seeds** (Seeds 42, 43, 46, 47, 51) |
| **$q = 2$ (Aim Jammers $\to$ Eve)**| Specular reflection focused on Eve | $15.1\%$ | $8.4\%$ | **$1 / 10$ seeds** (Seed 45) |
| **$q = 3$ (Split Bob/Eve)** | Partitioned tiles (Bob & Eve) | $19.2\%$ | $21.5\%$ | **$2 / 10$ seeds** (Seeds 44, 50) |
| **$q = 4$ (Neutral Normal)** | Direct outward normal $[0, 1, 0]$ | $14.5\%$ | $14.3\%$ | **$2 / 10$ seeds** (Seeds 48, 49) |

![Audit Figure 2: RIS Configuration Selection Distribution](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/output_figures/ris/joint_controller_audit/audit_q_distribution.png)
*(a) Stacked per-seed training slot allocation; (b) Chosen RIS configuration during frozen evaluation.*

### Seed-by-Seed Frozen Evaluation Breakdown in Joint RIS:

| Seed | Chosen $q$ | Selected Action Vector $[w_1, w_2, w_3, w_4, q_{\text{enc}}]$ | Frozen Secrecy Rate $R_s$ | Frozen Utility $U$ | Total Jammer Cost $\|\mathbf{w}\|_1$ | Bob BER |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **42** | **$q = 1$** | $[0.0, -1.0, 1.0, -0.5, -0.5]$ | $1.3337\text{ bps/Hz}$ | $0.3337$ | $2.5\text{ W}$ | $0.0$ |
| **43** | **$q = 1$** | $[-0.5, 1.0, 0.0, 1.0, -0.5]$ | **$1.8413\text{ bps/Hz}$** | $0.8413$ | $2.5\text{ W}$ | $0.0$ |
| **44** | $q = 3$ | $[0.0, 0.0, -0.5, 1.0, +0.5]$ | $1.4979\text{ bps/Hz}$ | $0.8979$ | $1.5\text{ W}$ | $0.0$ |
| **45** | $q = 2$ | $[0.0, 0.0, 0.5, -1.0, 0.0]$ | $1.3119\text{ bps/Hz}$ | $0.7119$ | $1.5\text{ W}$ | $0.0$ |
| **46** | **$q = 1$** | $[-0.5, 1.0, 0.5, 0.0, -0.5]$ | $1.1495\text{ bps/Hz}$ | $0.3495$ | $2.0\text{ W}$ | $0.0$ |
| **47** | **$q = 1$** | $[0.0, -0.5, 0.0, 1.0, -0.5]$ | $1.5557\text{ bps/Hz}$ | **$0.9557$** | $1.5\text{ W}$ | $0.0$ |
| **48** | $q = 4$ | $[0.5, -1.0, 0.0, -1.0, +1.0]$ | $1.5560\text{ bps/Hz}$ | $0.5560$ | $2.5\text{ W}$ | $0.0$ |
| **49** | $q = 4$ | $[0.5, -0.5, -0.5, -1.0, +1.0]$ | $1.3214\text{ bps/Hz}$ | $0.3214$ | $2.5\text{ W}$ | $0.0$ |
| **50** | $q = 3$ | $[-0.5, 0.0, 1.0, 0.5, +0.5]$ | $1.4414\text{ bps/Hz}$ | $0.6414$ | $2.0\text{ W}$ | $0.0$ |
| **51** | **$q = 1$** | $[0.0, 0.5, 0.0, -1.0, -0.5]$ | $1.5557\text{ bps/Hz}$ | **$0.9557$** | $1.5\text{ W}$ | $0.0$ |

> [!IMPORTANT]
> - In **Seed 43**, Joint RIS successfully discovered the **exact global finite-grid maximum secrecy action** across all 3,125 actions ($R_s = 1.8413\text{ bps/Hz}$).
> - In **Seeds 47 and 51**, Joint RIS achieved $U = 0.9557$, within $0.04$ of the theoretical finite-grid ceiling.
> - However, in Seeds 44, 45, 48, 49, and 50, the controller converged to sub-optimal mirror states ($q=2, 3, 4$), pulling the 10-seed average down.

---

## 4. Theoretical Finite-Grid Upper Bounds & Reference Gaps

To establish the ultimate performance ceiling under discrete 5-level PAM quantization ($w_i \in \{-1, -0.5, 0, 0.5, 1\}$), we performed exhaustive forward evaluation across all 3,125 actions in `RISEnvironment`:

| Configuration $q$ | Exact Max Utility $U^*$ | Max Utility Action | Secrecy at $U^*$ | Jammer Cost at $U^*$ | Exact Max Secrecy $R_s^*$ | Max Secrecy Action | Utility at $R_s^*$ | Mean Grid Utility |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$q = 0$ (Baseline)** | $0.7119$ | $[0, 0, -0.5, 1]$ | $1.3119\text{ bps/Hz}$ | $1.5\text{ W}$ | $1.5560\text{ bps/Hz}$ | $[-0.5, 1, 0, 1]$ | $0.5560$ | $-0.9110$ |
| **$q = 1$ (Aim Bob)** | **$0.9959$** | $[0, 0, -0.5, 1]$ | $1.5959\text{ bps/Hz}$ | $1.5\text{ W}$ | **$1.8413\text{ bps/Hz}$** | $[-0.5, 1, 0, 1]$ | $0.8413$ | **$-0.8846$** |
| **$q = 2$ (Aim Eve)** | $0.7119$ | $[0, 0, -0.5, 1]$ | $1.3119\text{ bps/Hz}$ | $1.5\text{ W}$ | $1.5552\text{ bps/Hz}$ | $[-0.5, 1, 0, 1]$ | $0.5552$ | $-0.9111$ |
| **$q = 3$ (Split)** | $0.8979$ | $[0, 0, -0.5, 1]$ | $1.4979\text{ bps/Hz}$ | $1.5\text{ W}$ | $1.7488\text{ bps/Hz}$ | $[-0.5, 1, 0, 1]$ | $0.7488$ | $-0.8957$ |
| **$q = 4$ (Neutral)** | $0.7119$ | $[0, 0, -0.5, 1]$ | $1.3119\text{ bps/Hz}$ | $1.5\text{ W}$ | $1.5560\text{ bps/Hz}$ | $[-0.5, 1, 0, 1]$ | $0.5560$ | $-0.9110$ |

![Audit Figure 3: Finite-Grid Upper Bounds vs Achieved](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/output_figures/ris/joint_controller_audit/audit_utility_vs_secrecy_gaps.png)
*(a) Exact finite-grid maximum utility vs. frozen evaluation mean; (b) Exact finite-grid maximum secrecy vs. frozen evaluation mean.*

### Crucial Theoretical Insights:
1. **$q=1$ Uniquely Dominates:** Across the entire 3,125-element action space, configuration $q=1$ provides the highest achievable secrecy ($1.8413$) and the highest utility ($0.9959$).
2. **Fixed RIS Operates on the True Optima:** Because Fixed RIS is permanently locked to $q=1$, its 625-action search space already contains the global optimum of the entire 3,125 joint action space.
3. **No Hidden Physical Superiority:** In this stationary geometry, there is no magical beam-steering synergy where switching away from $q=1$ produces higher secrecy. Any step that chooses $q \ne 1$ strictly degrades both achievable secrecy and achievable utility.
4. **Reward vs. Secrecy Tradeoff:**
   - The maximum secrecy action is $[-0.5, 1, 0, 1]$ with cost $2.5\text{ W}$ ($R_s = 1.8413$, $U = 0.8413$).
   - The maximum utility action is $[0, 0, -0.5, 1]$ with cost $1.5\text{ W}$ ($R_s = 1.5959$, $U = 0.9959$).
   - The DRL controller balances secrecy and power: spending $1.0\text{ W}$ more jammer power gains $+0.2454\text{ bps/Hz}$ secrecy but loses $-0.4000$ in utility penalty. Hence, a policy that saves jammer energy can achieve higher utility while achieving a slightly lower secrecy rate.

---

## 5. Invariant Assertion: Fixed-Action Feasibility in Joint Environment

We formally tested the feasibility invariant across all 10 seeds:
$$\forall s \in \{42..51\}, \quad \mathbf{a}_{\text{fixed}}^*(s) \in \mathcal{A}_{\text{joint}}, \quad \text{Env}_{\text{joint}}(\mathbf{a}_{\text{fixed}}^*(s)) \equiv \text{Env}_{\text{fixed}}(\mathbf{a}_{\text{fixed}}^*(s))$$

| Seed | Fixed RIS Action $[w_1..w_4]$ | Joint Vector $[w_1..w_4, -0.5]$ | Fixed Utility | Joint Utility | Fixed Secrecy | Joint Secrecy | Absolute Difference |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **42** | $[0.5, -1.0, 0.0, -1.0]$ | $[0.5, -1.0, 0.0, -1.0, -0.5]$ | $0.8413$ | $0.8413$ | $1.8413$ | $1.8413$ | $< 10^{-15}$ |
| **43** | $[0.0, 0.0, 0.5, -1.0]$ | $[0.0, 0.0, 0.5, -1.0, -0.5]$ | $0.9959$ | $0.9959$ | $1.5959$ | $1.5959$ | $< 10^{-15}$ |
| **44** | $[0.0, 1.0, -0.5, -1.0]$ | $[0.0, 1.0, -0.5, -1.0, -0.5]$ | $0.1818$ | $0.1818$ | $1.1818$ | $1.1818$ | $< 10^{-15}$ |
| **45** | $[-0.5, 1.0, 0.0, 1.0]$ | $[-0.5, 1.0, 0.0, 1.0, -0.5]$ | $0.8413$ | $0.8413$ | $1.8413$ | $1.8413$ | $< 10^{-15}$ |
| **46** | $[0.5, 0.0, -1.0, -1.0]$ | $[0.5, 0.0, -1.0, -1.0, -0.5]$ | $0.2027$ | $0.2027$ | $1.2027$ | $1.2027$ | $< 10^{-15}$ |
| **47** | $[-0.5, 0.0, 1.0, 0.5]$ | $[-0.5, 0.0, 1.0, 0.5, -0.5]$ | $0.7218$ | $0.7218$ | $1.5218$ | $1.5218$ | $< 10^{-15}$ |
| **48** | $[-0.5, 1.0, 0.5, 0.0]$ | $[-0.5, 1.0, 0.5, 0.0, -0.5]$ | $0.3495$ | $0.3495$ | $1.1495$ | $1.1495$ | $< 10^{-15}$ |
| **49** | $[-0.5, 0.0, 1.0, 0.5]$ | $[-0.5, 0.0, 1.0, 0.5, -0.5]$ | $0.7218$ | $0.7218$ | $1.5218$ | $1.5218$ | $< 10^{-15}$ |
| **50** | $[-0.5, 0.0, 1.0, 0.5]$ | $[-0.5, 0.0, 1.0, 0.5, -0.5]$ | $0.7218$ | $0.7218$ | $1.5218$ | $1.5218$ | $< 10^{-15}$ |
| **51** | $[0.5, -0.5, -0.5, -1.0]$ | $[0.5, -0.5, -0.5, -1.0, -0.5]$ | $0.6001$ | $0.6001$ | $1.6001$ | $1.6001$ | $< 10^{-15}$ |

**Result:** Invariant holds with $100\%$ precision ($p = 1.0$, maximum numerical deviation: $4.44 \times 10^{-16}$).

---

## 6. Paired Seed-by-Seed Statistical Comparisons

We recomputed the exact matched seed-by-seed differences across all 10 seeds for Utility, Secrecy Rate, and Jammer Energy Cost:

| Comparison | Metric | Mean Paired Difference | Standard Error | 95% Student-$t$ Interval ($df=9$) | $t$-statistic | $p$-value | Statistical Conclusion |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Fixed minus Baseline** | **Secrecy Rate** | **$+0.1773\text{ bps/Hz}$** | $\pm 0.0617$ | $[+0.0378, +0.3167]$ | $t = 2.87$ | **$p = 0.0183$** | **Statistically Significant Gain ($p < 0.05$)** |
| | **System Utility** | $+0.1173$ | $\pm 0.0864$ | $[-0.0782, +0.3127]$ | $t = 1.36$ | $p = 0.2075$ | Not statistically significant |
| | **Jammer Energy** | $+0.1500\text{ W}$ | $\pm 0.1302$ | $[-0.1445, +0.4445]$ | $t = 1.15$ | $p = 0.2789$ | Not statistically significant |
| **Joint minus Baseline** | **Secrecy Rate** | $+0.1359\text{ bps/Hz}$ | $\pm 0.0796$ | $[-0.0440, +0.3158]$ | $t = 1.71$ | $p = 0.1216$ | Not statistically significant |
| | **System Utility** | $+0.1559$ | $\pm 0.0782$ | $[-0.0210, +0.3328]$ | $t = 1.99$ | $p = 0.0779$ | Marginal trend ($p < 0.10$) |
| | **Jammer Energy** | $-0.0500\text{ W}$ | $\pm 0.1748$ | $[-0.4454, +0.3454]$ | $t = -0.29$ | $p = 0.7804$ | Not statistically significant |
| **Joint minus Fixed** | **Secrecy Rate** | $-0.0413\text{ bps/Hz}$ | $\pm 0.0999$ | $[-0.2674, +0.1847]$ | $t = -0.41$ | $p = 0.6887$ | No detectable difference |
| | **System Utility** | $+0.0387$ | $\pm 0.1165$ | $[-0.2248, +0.3021]$ | $t = +0.33$ | $p = 0.7463$ | No detectable difference |
| | **Jammer Energy** | $-0.2000\text{ W}$ | $\pm 0.2287$ | $[-0.7174, +0.3174]$ | $t = -0.87$ | $p = 0.3994$ | No detectable difference |

![Audit Figure 4: Paired Statistical Comparison](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/output_figures/ris/joint_controller_audit/audit_paired_differences.png)
*(a) Secrecy rate paired differences; (b) System utility paired differences across 10 matched seeds.*

### Outage Probabilities During Frozen Evaluation:
- **Secrecy Outage ($R_s < 0.1\text{ bps/Hz}$):** **$0.00\%$** across all 10 seeds for all three schemes.
- **Bob QoS Outage ($\text{BER} > 10^{-3}$ and $\text{BER} > 10^{-4}$):** **$0.00\%$** across all 10 seeds for all three schemes. (During frozen greedy evaluation, zero Bob reception errors occurred at any static operating point).

---

## 7. Algorithm Architecture & Memory Update Diagnostics

We audited the internal PyTorch network and DND memory implementation:

1. **FeatureCNN Architecture:**
   - Input shape: $(B, 1, m_0, 25)$ with $m_0 = 11$ sliding window history slots.
   - 2D Convolutions: `Conv2d(1, 20, kernel_size=(3,3), stride=1, padding=1)` followed by `Conv2d(20, 40, kernel_size=(2,2), stride=1, padding=1)` and `MaxPool2d((2,2), stride=1)`.
   - Flatten layer size: $40 \times 8 \times 8 = 2,560$ features.
   - Fully connected projection: `Linear(2560, 180)` $\to$ `ReLU` $\to$ `Linear(180, 180)`.
   - Normalization: $L_2$ unit normalization $\mathbf{h} = \mathbf{z} / \|\mathbf{z}\|_2$.
2. **DND Episodic Memory:**
   - Stores keys in $\mathbb{R}^{180}$ and associated Q-value vectors $\mathbf{Q} \in \mathbb{R}^{|\mathcal{A}|}$.
   - For Fixed RIS: $|\mathcal{A}| = 625$.
   - For Joint RIS: $|\mathcal{A}| = 3,125$.
   - **Update Mechanism:** At step $t$, the Bellman update updates **only the single entry $Q(s_t, a_t)$** corresponding to the executed action:
     $$Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha \left[ r_t + \gamma \max_{a'} Q(s_{t+1}, a') - Q(s_t, a_t) \right]$$
   - All other $|\mathcal{A}| - 1$ entries remain at their initial default value ($0.0$).
3. **The Sample-Efficiency Bottleneck:**
   - In Joint RIS, with 3,125 actions and only 2,000 training steps, **at least 1,125 actions are mathematically guaranteed to have zero Bellman updates**.
   - Because the agent visited only 133 unique actions on average, **approximately 2,992 out of 3,125 actions ($95.7\%$) received zero Bellman updates across the entire training run**.
   - When greedy argmax $\arg\max_a Q(s, a)$ is evaluated, unvisited actions retain default Q-values, and early visited actions with slightly positive Q-values monopolize selection, creating self-reinforcing policy lock-in.

---

## 8. Summary & Transition to Stage B Budget Study

### Stage A Conclusions:
1. Joint RIS does not have a higher physical ceiling than Fixed RIS in this stationary setup.
2. In 2,000 slots, Joint RIS suffers from severe sample inefficiency (only $4.26\%$ coverage), causing half the seeds to get trapped in inferior RIS configurations ($q=2, 3, 4$).
3. The core question for Stage B is:
   > **Does increasing the training budget from 2,000 to 5,000 and 10,000 slots give Joint RIS sufficient exploration to escape inferior configurations and match/exceed Fixed RIS?**

Stage A audit is complete. All findings and figures are verified. We now proceed to Stage B.

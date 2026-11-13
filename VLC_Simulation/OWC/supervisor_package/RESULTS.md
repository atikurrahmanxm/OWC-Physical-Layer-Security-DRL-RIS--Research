# Authoritative Simulation Results & Statistical Analysis

**Project:** Physical Layer Security in Visible Light Communications (VLC) via Optical RIS and Friendly Jamming (FJ) using Deep Reinforcement Learning (DRL)  
**Scope:** Authoritative numerical results, paired statistical significance, phase separation, and physical boundary disclosure  
**Data Provenance:** Programmatically derived from raw multi-seed dataset `output_figures/ris/final_evaluation/ris_study_data.json` (SHA-256: `7948189a9ca87ff5c1e60f387ee64b2fc59424c6b42e8525b83ec934f37968c1`)  

---

## 1. Experimental Protocol Summary

- **Environment Scenario:** Nominal office desk geometry (Alice at $[2.5, 2.5, 3.0]^T$, Bob at $[1.8, 1.6, 0.85]^T$, Eve at $[3.2, 3.4, 0.85]^T$).
- **Optical RIS:** Mounted on south wall ($y = 0.25\text{ m}$), center $[2.5, 0.25, 2.6]^T$, $W = 1.0\text{ m}, H = 0.5\text{ m}$, 6 specular tiles, reflectivity $\rho = 0.85$.
- **Energy Model:** Primary matched study uses nonnegative L1 norm ($\sum_{i=1}^4 |w_i|$); printed paper sensitivity uses signed sum ($\sum_{i=1}^4 w_i$).
- **Sample Size:** 10 independent random seeds ($42, 43, 44, 45, 46, 47, 48, 49, 50, 51$).
- **Total Matched Runs:** 30 independent training and evaluation sessions ($10\text{ seeds} \times 3\text{ schemes}$).
- **Evaluation Protocol:**
  - **Training Phase:** 2,000 slots per run under $\epsilon$-greedy exploration ($\epsilon: 0.1 \to 0$).
  - **Frozen Evaluation Phase:** 1,000 slots per run under frozen greedy policy ($\epsilon = 0$, zero neural network or DND memory updates).

---

## 2. Phase 1: Frozen Greedy Evaluation Results (Primary Benchmark)

In the frozen greedy evaluation phase, the learned policy is frozen and evaluated over 1,000 static slots without exploration or memory writes. In this static setting, each scheme repeats its single best-learned action.

### Table 1: Independent Scheme Performance (1,000 Evaluation Slots, 10 Seeds)

| Scheme | Action Cardinality $\|\mathcal{A}\|$ | Mean Secrecy Rate $R_s$ (bps/Hz) | Sample Std $\sigma_s$ | Standard Error $\text{SE}$ | Two-Sided 95% Student-$t$ CI | Bob BER $P_e$ | Secrecy Outage ($R_s < 0.1$) | Bob QoS Outage ($P_e > 10^{-3}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (No RIS)** | 625 | **1.3205** | 0.1281 | 0.0405 | [1.2289, 1.4122] | 0.0 | **0.0%** | **0.0%** |
| **Fixed RIS (Config 1: Alice→Bob)** | 625 | **1.4978** | 0.2508 | 0.0793 | [1.3184, 1.6772] | 0.0 | **0.0%** | **0.0%** |
| **Joint RIS + FJ (Adaptive Codebook)**| 3,125 | **1.4565** | 0.1909 | 0.0604 | [1.3199, 1.5930] | 0.0 | **0.0%** | **0.0%** |

*Note on Outages:* Because the channel is static and the policy is frozen greedy, all three schemes achieve **identically zero outages (0.0%)** and zero Bob bit errors ($P_e = 0.0$) during the evaluation phase.

---

## 3. Paired Statistical Significance Analysis

Because each random seed initializes the environment with identical noise sequences across all three schemes, comparisons must be evaluated as **paired differences** across the 10 matched seeds ($df = 9$, critical value $t_{0.025, 9} = 2.262$).

### Table 2: Paired Differences in Frozen Secrecy Rate (10 Matched Pairs)

| Comparison Pair | Mean Difference $\Delta R_s$ (bps/Hz) | Sample Std $\sigma_{\Delta}$ | Standard Error $\text{SE}_{\Delta}$ | Two-Sided 95% Student-$t$ CI | Derived $p$-value ($t$-test, df=9) | Statistical Conclusion |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Fixed RIS minus Baseline** | **+0.1773** | 0.1949 | 0.0616 | **[+0.0378, +0.3167]** | **$p = 0.0183$** ($0.0182917$) | **Statistically Significant Improvement:** Lower bound is strictly positive. |
| **Joint RIS minus Baseline** | **+0.1359** | 0.2514 | 0.0795 | **[-0.0440, +0.3158]** | **$p = 0.1216$** ($0.1216017$) | **Superiority Not Proven:** 95% CI spans zero; null hypothesis cannot be rejected. |
| **Joint RIS minus Fixed RIS** | **-0.0413** | 0.3164 | 0.1001 | **[-0.2674, +0.1847]** | **$p = 0.6887$** ($0.6887355$) | **Equivalence Not Proven:** Wide interval crossing zero; failure to reject null is not equivalence. |

### Interpretation:
1. **Fixed RIS Advantage:** Aiming the 6 specular mirrors at Bob (Config 1) provides a deterministic $+23.4\%$ boost to Alice's received signal ($h_{AB}: 2.718 \times 10^{-5} \to 3.354 \times 10^{-5}\text{ A/W}$) without altering the jammer channels. The learner successfully translates this optical boost into a statistically verified $+0.1773\text{ bps/Hz}$ average secrecy gain ($p < 0.05$).
2. **Joint DRL Trade-Off:** The joint controller must search across $|\mathcal{A}| = 3,125$ discrete actions compared to 625 for the fixed RIS scheme. Within a 2,000-slot training window, exploration variance across seeds prevents the joint scheme from proving statistical superiority over baseline ($95\%\text{ CI}$ spans zero), even though the sample mean is $+10.3\%$ higher ($1.4565\text{ vs } 1.3205\text{ bps/Hz}$).

---

## 4. Per-Seed Breakdown (All 10 Seeds)

### Table 3: Exact Frozen Evaluation Secrecy Rates by Seed (bps/Hz)

| Random Seed | Baseline (No RIS) | Fixed RIS (Config 1) | Joint RIS + FJ | Fixed vs Baseline ($\Delta$) | Joint vs Baseline ($\Delta$) | Joint vs Fixed ($\Delta$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **42** | 1.5560 | 1.8413 | 1.3337 | +0.2853 | -0.2223 | -0.5076 |
| **43** | 1.3119 | 1.5959 | 1.8413 | +0.2840 | +0.5294 | +0.2454 |
| **44** | 1.2721 | 1.1818 | 1.4979 | -0.0903 | +0.2259 | +0.3161 |
| **45** | 1.5560 | 1.8413 | 1.3119 | +0.2853 | -0.2441 | -0.5294 |
| **46** | 1.2376 | 1.2027 | 1.1495 | -0.0348 | -0.0881 | -0.0532 |
| **47** | 1.2376 | 1.5218 | 1.5557 | +0.2842 | +0.3181 | +0.0339 |
| **48** | 1.3214 | 1.1495 | 1.5560 | -0.1719 | +0.2345 | +0.4065 |
| **49** | 1.2376 | 1.5218 | 1.3214 | +0.2842 | +0.0839 | -0.2004 |
| **50** | 1.2376 | 1.5218 | 1.4414 | +0.2842 | +0.2038 | -0.0804 |
| **51** | 1.2376 | 1.6001 | 1.5557 | +0.3626 | +0.3181 | -0.0444 |
| **MEAN** | **1.3205** | **1.4978** | **1.4565** | **+0.1773** | **+0.1359** | **-0.0413** |
| **STD** | **0.1281** | **0.2508** | **0.1909** | **0.1949** | **0.2514** | **0.3164** |

---

## 5. Phase 2 & Phase 3 Dynamics (Training Windows & Outages)

### Table 4: Phase-Separated Performance Overview

| Metric | Phase 1: Frozen Evaluation (1,000 Slots, $\epsilon = 0$) | Phase 2: Final Training Window (Slots 1501–2000, $\epsilon \approx 0.02$) | Phase 3: All-Training History (Slots 1–2000, $\epsilon: 0.1 \to 0$) |
| :--- | :---: | :---: | :---: |
| **Baseline Secrecy Rate** | 1.3205 bps/Hz | 1.2964 bps/Hz | 1.1963 bps/Hz |
| **Fixed RIS Secrecy Rate** | 1.4978 bps/Hz | 1.4710 bps/Hz | 1.3736 bps/Hz |
| **Joint RIS Secrecy Rate** | 1.4565 bps/Hz | 1.4303 bps/Hz | 1.3418 bps/Hz |
| **Baseline Bob BER** | 0.0 | $9.55 \times 10^{-5}$ | $5.55 \times 10^{-4}$ |
| **Fixed RIS Bob BER** | 0.0 | $2.25 \times 10^{-5}$ | $7.63 \times 10^{-4}$ |
| **Joint RIS Bob BER** | 0.0 | $6.44 \times 10^{-5}$ | $6.64 \times 10^{-4}$ |
| **Baseline Outage Fraction** | **0.0%** | $1.42\%$ (7.1 slots) | **9.19%** (183.8 slots) |
| **Fixed RIS Outage Fraction** | **0.0%** | $1.08\%$ (5.4 slots) | **7.38%** (147.6 slots) |
| **Joint RIS Outage Fraction** | **0.0%** | $0.84\%$ (4.2 slots) | **6.23%** (124.6 slots) |

### Phase Separation Principle:
- **Never conflate training exploration outages with evaluation outages.** In Phase 3, outages occur because the agent is deliberately perturbing its actions at rate $\epsilon$ during warmup and learning.
- In Phase 1 (frozen greedy evaluation), the agent selects only the greedy action, resulting in **zero outages across all schemes**.
- During training, Joint RIS achieves the lowest outage rate ($6.23\%$) because its expanded codebook provides fallback configurations when jamming causes excessive Bob interference.

---

## 6. Physical Singularities & Boundary Conditions

### 6.1 Near-Bob Boundary Condition ($d_{BE} = 7.07\text{ cm}$)
When Eve is positioned at $[1.85, 1.65, 0.85]^T$ (7.07 cm collinear separation from Bob at $[1.8, 1.6, 0.85]^T$):
- Alice channel to Eve is stronger than to Bob: $h_{AE}^{\text{dir}} = 2.768 \times 10^{-5} > h_{AB}^{\text{dir}} = 2.718 \times 10^{-5}\text{ A/W}$.
- Jammer channel vectors $\mathbf{h}_{JB}$ and $\mathbf{h}_{JE}$ are nearly collinear.
- **Exhaustive Grid Search:** An exhaustive evaluation across all 3,125 discrete actions in $\mathcal{A}$ reveals:
  $$\max_{\mathbf{a} \in \mathcal{A}} R_s(\mathbf{a}) \equiv \mathbf{0.0000\text{ bps/Hz}}$$
- **Conclusion:** Security cannot be established via friendly jamming when Eve is spatially collinear within 7 cm of Bob under the tested fixture geometry.

### 6.2 Colocated Receiver Boundary
When Eve is placed at the exact coordinates of Bob ($[1.8, 1.6, 0.85]^T$):
- Channel gains are mathematically identical: $h_{AB} \equiv h_{AE}$ and $\mathbf{h}_{JB} \equiv \mathbf{h}_{JE}$.
- For all beamforming vectors $\mathbf{w}$, the signal-to-interference-plus-noise ratios are identical ($\gamma_B = \gamma_E$).
- Secrecy capacity is identically:
  $$C_s = \left[ \frac{1}{2} \log_2(1 + \gamma_B) - \frac{1}{2} \log_2(1 + \gamma_E) \right]^+ \equiv \mathbf{0.0000\text{ bps/Hz}}$$


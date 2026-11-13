# Detailed Statistical Research Results: RIS + FJ + VLC + DRL

This document records the exact numerical results from the matched multi-seed experiments executed across 36 separate 2,000-slot training runs. All runs use `torch.set_num_threads(1)` with deterministic seeds `[42, 43, 44]`.

> **Methodological Note on Training vs. Evaluation:**
> The results below are computed directly from online training histories. All 2,000 slots include initial warmup ($M=11$) and decaying $\epsilon$-exploration ($\epsilon: 0.15 \to 0.02$). The "final training window" reflects the average of the last 500 training slots, which still includes residual exploration ($\epsilon_{\min} = 0.02$). A separate frozen-policy greedy evaluation ($\epsilon=0$, no weight/DND updates) is implemented separately.

---

## 1. Nominal Scenario (Bob at $(1.8, 1.6)$, Eve at $(3.2, 3.4)$)

### Table 1: $L_1$ Non-Negative Energy Model ($\delta_2 \sum |w_i|$)

#### A. All 2,000 Training Slots (Warmup and Exploration Included)
| Scheme | Secrecy Rate (bps/Hz) [95% CI] | Bob BER [95% CI] | Energy Cost [95% CI] | System Utility [95% CI] | Secrecy Outage (<0.1 bps/Hz) |
|---|---|---|---|---|---|
| **Baseline (No RIS)** | $1.3057 \pm 0.3809$ | $(1.36 \pm 1.35) \times 10^{-4}$ | $1.8702 \pm 1.3586$ | $0.5571 \pm 0.2040$ | $4.73\%$ |
| **Fixed RIS ($q=1$)** | $1.4655 \pm 0.8026$ | $(3.73 \pm 1.61) \times 10^{-4}$ | $2.1793 \pm 1.3865$ | $0.5925 \pm 1.0497$ | $4.17\%$ |
| **Joint RIS + FJ + DRL** | $1.4167 \pm 0.8327$ | $(1.83 \pm 5.73) \times 10^{-4}$ | $2.1137 \pm 1.1900$ | $0.5706 \pm 0.8329$ | $5.57\%$ |

*Note:* In all-slot training averages, Fixed RIS sample mean secrecy rate ($1.4655$) slightly exceeds Joint RIS ($1.4167$) due to the larger action space ($625 \times 5 = 3125$ joint actions vs. $625$ baseline actions) requiring more exploratory sample allocation.

#### B. Final Training Window (Last 500 Slots, Exploitation-Biased Phase, $\epsilon = 0.02$)
| Scheme | Secrecy Rate (bps/Hz) [95% CI] | Bob BER [95% CI] | Energy Cost [95% CI] | System Utility [95% CI] |
|---|---|---|---|---|
| **Baseline (No RIS)** | $1.3504 \pm 0.3725$ | $(1.30 \pm 5.34) \times 10^{-4}$ | $1.8463 \pm 1.4063$ | $0.6114 \pm 0.1998$ |
| **Fixed RIS ($q=1$)** | $1.5078 \pm 0.8068$ | $(4.30 \pm 18.47) \times 10^{-5}$ | $2.1723 \pm 1.4141$ | $0.6388 \pm 1.0530$ |
| **Joint RIS + FJ + DRL** | $1.5230 \pm 0.6235$ | $(4.84 \pm 20.81) \times 10^{-12}$ | $2.1717 \pm 1.3977$ | $0.6543 \pm 0.7556$ |

#### C. Statistical Significance (Paired Differences across Seeds 42, 43, 44)
* **Joint RIS vs. Baseline:** Sample mean difference = $+0.1726\text{ bps/Hz}$ ($+12.8\%$), with two-sided 95% Student-$t$ confidence interval:
  $$\Delta c_s \in [-0.7403, +1.0854]\text{ bps/Hz}$$
* **Joint RIS vs. Fixed RIS:** Sample mean difference = $+0.0152\text{ bps/Hz}$, with two-sided 95% Student-$t$ confidence interval:
  $$\Delta c_s \in [-1.0904, +1.1208]\text{ bps/Hz}$$
* **Rigorous Conclusion:** Because both 95% confidence intervals cross zero under $N=3$ seeds, **statistical superiority is not yet established**. Expanded multi-seed studies ($N \ge 10$) with dedicated frozen greedy evaluations are required to resolve statistical significance.

---

### Table 2: Literal Paper-Signed Energy Model ($\delta_2 \sum w_i$)

| Scheme | All-Slots Secrecy Rate (bps/Hz) | Final-Window Secrecy Rate (bps/Hz) | Secrecy Outage (<0.1) | Observation |
|---|---|---|---|---|
| **Baseline (No RIS)** | $0.0041 \pm 0.0029$ | $0.0016 \pm 0.0065$ | **$99.48\%$** | Severe zero-collapse: agent exploits negative weights to maximize signed utility without transmitting secrecy jamming |
| **Fixed RIS ($q=1$)** | $0.5124 \pm 2.1842$ | $0.5213 \pm 2.2417$ | $67.62\%$ | Mirror reflection partially enhances legitimate path; jamming remains minimal |
| **Joint RIS + FJ + DRL** | $1.0530 \pm 2.3081$ | $1.0882 \pm 2.3766$ | $\mathbf{36.82\%}$ | Joint DRL successfully drives secrecy rate above $1.0\text{ bps/Hz}$ despite the signed energy distortion |

---

## 2. Boundary & Adversarial Scenarios ($L_1$ Energy Model)

### Table 3: Near-Bob Adversarial Scenario (Bob $(1.8, 1.6, 0.85)$, Eve $(1.85, 1.65, 0.85)$)
In this scenario, Eve is positioned within $\sim 7\text{ cm}$ of Bob, representing near-co-location.

| Metric | Baseline (No RIS) | Fixed RIS ($q=1$) | Joint RIS + FJ + DRL | Physical Interpretation |
|---|---|---|---|---|
| **All-Slots Secrecy Rate (bps/Hz)** | $\mathbf{0.0000}$ | $\mathbf{0.0000}$ | $\mathbf{0.0000}$ | No positive secrecy possible on the discrete grid |
| **Final-Window Secrecy Rate (bps/Hz)** | $\mathbf{0.0000}$ | $\mathbf{0.0000}$ | $\mathbf{0.0000}$ | Secrecy remains strictly zero across all seeds |
| **Final-Window Bob BER** | $1.30 \times 10^{-4}$ | $4.30 \times 10^{-5}$ | $4.10 \times 10^{-4}$ | Acceptable reception maintained |
| **Final-Window Energy Cost** | $0.0547$ | $0.0547$ | $0.0533$ | Agent shuts down jamming to conserve energy |
| **Secrecy Outage (<0.1 bps/Hz)** | $100.0\%$ | $100.0\%$ | $100.0\%$ | Fundamental spatial nulling boundary |

*Critical Finding:* When Eve is within $7\text{ cm}$ of Bob, the spatial channel correlation between Bob and Eve is nearly unity ($\mathbf{h}_{JB} \approx \mathbf{h}_{JE}$). Any friendly jamming that impinges on Eve equally destroys Bob's SINR. Consequently, the optimal utility policy converges to $\mathbf{w} \approx \mathbf{0}$, yielding exactly zero secrecy rate. This is an essential physical boundary of the wiretap channel, not an algorithm failure.

---

### Table 4: Colocated Physical Boundary Test (Bob $(1.8, 1.6, 0.85)$, Eve $(1.8, 1.6, 0.85)$)
When Eve is colocated with Bob, $h_{AB} \equiv h_{AE}$ and $\mathbf{h}_{JB} \equiv \mathbf{h}_{JE}$.

| Scheme | All-Slots Secrecy Rate (bps/Hz) | Final-Window Secrecy Rate (bps/Hz) | Secrecy Outage (<0.1 bps/Hz) |
|---|---|---|---|
| **Baseline (No RIS)** | $\mathbf{0.0000}$ | $\mathbf{0.0000}$ | $100\%$ |
| **Fixed RIS ($q=1$)** | $\mathbf{0.0000}$ | $\mathbf{0.0000}$ | $100\%$ |
| **Joint RIS + FJ + DRL** | $\mathbf{0.0000}$ | $\mathbf{0.0000}$ | $100\%$ |

*Conclusion:* Across all 9 runs and all slots, secrecy rate evaluates identically to $0.0000\text{ bps/Hz}$, proving that the simulation honors wiretap channel invariants.

---

## 3. Provenance and Source Hashes

Every run in `output_figures/ris/*/ris_study_data.json` records:
* Full per-slot training history ($2,000$ slots of secrecy rate, BER, energy, utility)
* Full recorded sequence of actual actions chosen by the agents
* Saved-action replay verification with maximum discrepancy $< 10^{-10}$
* SHA-256 cryptographic hashes of all `vlc/*.py` source modules matching current repository files

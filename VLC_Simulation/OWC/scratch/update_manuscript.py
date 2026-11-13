import re
from pathlib import Path

path = Path("manuscript/draft.md")
content = path.read_text(encoding="utf-8")

# Target section VI & VII replacement
old_sec_vi_start = "## VI. Numerical Results and Discussion"
old_sec_viii_start = "## VIII. Conclusion"

new_sec_vi_and_vii = """## VI. Numerical Results and Discussion

We evaluate the proposed framework through the matched 10-seed evaluation study across independent seeds ($\mathcal{S}_{\\text{seeds}} = \\{42, 43, \\dots, 51\\}$), comparing Baseline (No RIS), Fixed RIS ($q_1$), and Joint RIS/FJ DRL under $T_{\\text{train}} = 2,000$ training slots and $T_{\\text{eval}} = 1,000$ frozen greedy evaluation slots per seed (totaling 30 independent runs and 90,000 slots).

### A. Phase-Separated Performance Evaluation

To prevent methodological ambiguity, results are presented across three clearly delineated operational phases:

#### 1. Frozen-Policy Greedy Evaluation Phase ($1,000$ slots, $\\epsilon = 0$, zero updates)
Table IV evaluates the single operating point selected by deterministic argmax Q-policy for each seed. Since room geometry is static, each seed evaluates one fixed operating action stably across all 1,000 slots. Seed ($N=10$) is the independent statistical replicate.

#### Table IV: Frozen-Policy Greedy Evaluation Phase ($N=10$ Seeds)
| Scheme | Action Space $|\\mathcal{A}|$ | Secrecy Rate (bps/Hz) [Mean $\\pm$ SE] | 95% Student-$t$ CI [bps/Hz] | Bob BER [Mean] | Energy Cost [Mean $\\pm$ SE] | Bob QoS Outage ($>10^{-3}$) | Secrecy Outage ($<0.1\\text{ bps/Hz}$) | Unique Actions per Seed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (No RIS)** | $625$ | $1.3205 \\pm 0.0405$ | $[1.2289, 1.4122]$ | $0.0$ | $2.0500 \\pm 0.1167$ | $0.0\\%$ ($0.0000$) | $0.0\\%$ ($0.0000$) | 1 (static) |
| **Fixed RIS ($q_1$)** | $625$ | $1.4978 \\pm 0.0793$ | $[1.3184, 1.6772]$ | $0.0$ | $2.2000 \\pm 0.1106$ | $0.0\\%$ ($0.0000$) | $0.0\\%$ ($0.0000$) | 1 (static) |
| **Joint RIS + FJ** | $3,125$ | $1.4565 \\pm 0.0604$ | $[1.3199, 1.5930]$ | $0.0$ | $2.0000 \\pm 0.1491$ | $0.0\\%$ ($0.0000$) | $0.0\\%$ ($0.0000$) | 1 (static) |

*Evaluation Outage Finding:* In this static frozen evaluation, all 10 seeds across all three schemes achieve secrecy rate $> 0.1\\text{ bps/Hz}$ and Bob $\\text{BER} < 10^{-10}$ (evaluating numerically to $0.0$), yielding exactly $0.0\\%$ outage across all three schemes. There is no evaluation-phase outage advantage for any scheme.

#### 2. Final Training Window Phase (Slots 1,501--2,000, residual exploration $\\epsilon \\approx 0.02$)
Table V presents the final 500 slots of active training, where policies have largely converged but retain residual exploration ($\\epsilon \\approx 0.02$).

#### Table V: Final Training Window Phase ($N=10$ Seeds)
| Scheme | Secrecy Rate (bps/Hz) [Mean $\\pm$ SE] | 95% Student-$t$ CI [bps/Hz] | Bob BER [Mean $\\pm$ SE] | Energy Cost [Mean $\\pm$ SE] |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline (No RIS)** | $1.2964 \\pm 0.0398$ | $[1.2064, 1.3865]$ | $(9.55 \\pm 6.43) \\times 10^{-5}$ | $2.0562 \\pm 0.1145$ |
| **Fixed RIS ($q_1$)** | $1.4710 \\pm 0.0772$ | $[1.2964, 1.6456]$ | $(2.25 \\pm 1.52) \\times 10^{-5}$ | $2.2022 \\pm 0.1090$ |
| **Joint RIS + FJ** | $1.4303 \\pm 0.0590$ | $[1.2967, 1.5638]$ | $(6.44 \\pm 4.42) \\times 10^{-5}$ | $2.0074 \\pm 0.1462$ |

#### 3. Entire Training Trajectory (Slots 1--2,000, includes warmup and $\\epsilon$-decay exploration)
Table VI summarizes the full 2,000 training slots where exploration decays from $\\epsilon_0 = 0.15$ to $0.02$.

#### Table VI: Entire Training Trajectory ($N=10$ Seeds)
| Scheme | Secrecy Rate (bps/Hz) [Mean $\\pm$ SE] | 95% Student-$t$ CI [bps/Hz] | Bob BER [Mean $\\pm$ SE] | Energy Cost [Mean $\\pm$ SE] | Bob QoS Outage ($>10^{-3}$) | Bob QoS Outage ($>10^{-4}$) | Secrecy Outage ($<0.1\\text{ bps/Hz}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (No RIS)** | $1.1912 \\pm 0.0494$ | $[1.0795, 1.3029]$ | $(5.15 \\pm 1.14) \\times 10^{-4}$ | $2.0923 \\pm 0.1073$ | $0.41\\%$ ($0.0041$) | $0.41\\%$ ($0.0041$) | $9.19\\%$ ($0.0919$) |
| **Fixed RIS ($q_1$)** | $1.3684 \\pm 0.0734$ | $[1.2025, 1.5344]$ | $(7.23 \\pm 2.03) \\times 10^{-4}$ | $2.2302 \\pm 0.1041$ | $0.26\\%$ ($0.0026$) | $0.33\\%$ ($0.0033$) | $7.38\\%$ ($0.0738$) |
| **Joint RIS + FJ** | $1.3191 \\pm 0.0693$ | $[1.1623, 1.4759]$ | $(2.85 \\pm 0.99) \\times 10^{-4}$ | $2.0129 \\pm 0.1340$ | $0.20\\%$ ($0.0020$) | $0.21\\%$ ($0.0021$) | $6.23\\%$ ($0.0623$) |

*Training Outage Finding:* During the active training process, Joint RIS incurred fewer exploration-induced outages ($6.23\\%$ secrecy outage, $0.20\\%$ Bob outage) compared to Fixed RIS ($7.38\\%$, $0.26\\%$) and Baseline ($9.19\\%$, $0.41\\%$). These metrics reflect exploration behavior during learning, not post-training operational guarantees.

### B. Statistical Significance and Paired Differences
Table VII details the paired seed-by-seed differences across the $N=10$ matched runs across all three phases.

#### Table VII: Paired Difference Analysis ($N=10$ Seeds, Student-$t$ $95\\%$ CI)
| Comparison | Phase / Window | Sample Mean Diff $\\bar{\\Delta}$ | Std $s_{\\Delta}$ | Paired 95% Student-$t$ Interval | Statistical Finding at 95% Confidence |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Fixed RIS minus Baseline** | Frozen Evaluation (1000 slots) | $\\Delta R_s = +0.1773\\text{ bps/Hz}$ | $0.1949$ | $[+0.0378, +0.3167]$ | **Statistically Significant** (CI strictly positive) |
| | Final Training Window (500 slots) | $\\Delta R_s = +0.1746\\text{ bps/Hz}$ | $0.1907$ | $[+0.0382, +0.3110]$ | **Statistically Significant** (CI strictly positive) |
| | All Training (2000 slots) | $\\Delta R_s = +0.1773\\text{ bps/Hz}$ | $0.1603$ | $[+0.0626, +0.2920]$ | **Statistically Significant** (CI strictly positive) |
| **Joint RIS minus Baseline** | Frozen Evaluation (1000 slots) | $\\Delta R_s = +0.1359\\text{ bps/Hz}$ | $0.2515$ | $[-0.0440, +0.3158]$ | Not Significant (CI spans zero) |
| | Final Training Window (500 slots) | $\\Delta R_s = +0.1338\\text{ bps/Hz}$ | $0.2455$ | $[-0.0418, +0.3094]$ | Not Significant (CI spans zero) |
| | All Training (2000 slots) | $\\Delta R_s = +0.1279\\text{ bps/Hz}$ | $0.2904$ | $[-0.0798, +0.3357]$ | Not Significant (CI spans zero) |
| **Joint RIS minus Fixed RIS** | Frozen Evaluation (1000 slots) | $\\Delta R_s = -0.0413\\text{ bps/Hz}$ | $0.3160$ | $[-0.2674, +0.1847]$ | Not Significant (CI spans zero) |
| | Final Training Window (500 slots) | $\\Delta R_s = -0.0407\\text{ bps/Hz}$ | $0.3090$ | $[-0.2618, +0.1803]$ | Not Significant (CI spans zero) |
| | All Training (2000 slots) | $\\Delta R_s = -0.0493\\text{ bps/Hz}$ | $0.3085$ | $[-0.2700, +0.1714]$ | Not Significant (CI spans zero) |
| | Evaluation Energy Cost | $\\Delta E = -0.2000$ | $0.3496$ | $[-0.4501, +0.0501]$ | Not Significant (CI spans zero) |

#### Statistical Findings:
1. **Proven Superiority of Fixed RIS over Baseline**: Fixed RIS achieves a statistically certified improvement in secrecy rate of $+0.1773\\text{ bps/Hz}$ ($+13.4\\%$) over the Baseline without RIS during frozen evaluation. Its paired 95% confidence interval $[+0.0378, +0.3167]\\text{ bps/Hz}$ lies strictly above zero.
2. **Joint RIS Statistical Uncertainty**: Joint RIS achieves a $+10.3\\%$ sample mean secrecy increase ($1.4565$ vs. $1.3205\\text{ bps/Hz}$) over Baseline, but its paired 95% confidence interval spans zero ($[-0.0440, +0.3158]$). Superiority over Baseline cannot be statistically claimed under this training budget.
3. **Comparison between Joint and Fixed RIS**: The paired difference between Joint RIS and Fixed RIS has a 95% confidence interval of $[-0.2674, +0.1847]\\text{ bps/Hz}$. Because the interval spans zero, we fail to reject the null hypothesis of no difference. We emphasize that failure to establish a difference does not demonstrate statistical equivalence. Similarly, while Joint RIS exhibited a lower sample-mean jamming energy ($2.0000$ vs. $2.2000$), its paired difference interval $[-0.4501, +0.0501]$ spans zero, precluding a statistically definitive energy-saving claim.

### C. Physical Wiretap Channel Boundaries: Near-Bob and Colocated Analysis
We examine two adverse geometric boundary scenarios:
1. **Near-Bob Scenario ($\mathbf{p}_B = [1.8, 1.6, 0.85]^T$, $\mathbf{p}_E = [1.85, 1.65, 0.85]^T\\text{ m}$, $\\sim 7\\text{ cm}$ separation)**:
   - In this geometry, Eve is slightly closer to Alice than Bob ($\\|\\mathbf{p}_E - \\mathbf{p}_A\\| = 2.40\\text{ m}$ vs. $\\|\\mathbf{p}_B - \\mathbf{p}_A\\| = 2.43\\text{ m}$), resulting in $h_{AE} > h_{AB}$ ($2.87 \\times 10^{-5}$ vs. $2.72 \\times 10^{-5}$).
   - **Exhaustive Discrete Codebook Verification**: An independent grid search over all $625$ direct jamming actions and all $3,125$ joint RIS/jamming actions confirmed that **the maximum achievable secrecy rate across all actions is identically $0.0000\\text{ bps/Hz}$**.
   - Consequently, all training and evaluation histories in `near_bob` record strictly $0.0000\\text{ bps/Hz}$ secrecy. Because positive secrecy is mathematically unachievable under this discrete codebook, the DRL agent converges to near-zero jamming emissions ($\\mathbf{w} \\approx \\mathbf{0}$, energy $0.0533\\text{--}0.0547$), protecting Bob's BER ($4.10 \\times 10^{-4}$) rather than expending energy fruitlessly.
   - We emphasize that this result reflects the feasibility bound of the declared discrete orientation codebook and specific transceiver coordinates; it does not constitute an analytical proof of universal infeasibility for continuous mirror steering or alternative placements.
2. **Colocated Scenario ($\mathbf{p}_E = \\mathbf{p}_B = [1.8, 1.6, 0.85]^T\\text{ m}$)**:
   - Direct and reflected channels are mathematically identical ($h_{AB} = h_{AE}, \\mathbf{h}_{JB} = \\mathbf{h}_{JE}$).
   - Theoretical secrecy capacity is provably zero: $R_s \\equiv 0.0000\\text{ bps/Hz}$.
   - The DRL policy shuts off jamming completely.

---

## VII. Physical Constraints, Assumptions, and Practical Limitations

To maintain academic rigor, we explicitly disclose the physical assumptions and departures in our framework:
1. **Static Geometry and Oracle Eavesdropper Information**: The environment model assumes static transceiver positions and known Eve coordinates during reward calculation. In practical covert wiretap scenarios, Eve is passive and uncooperative. Future investigations must evaluate statistical CSI uncertainty, bounding-box channel models, and mobility.
2. **Exclusion of Mirror Actuation Energy**: The energy metric $E_J$ accounts solely for LED electrical optical emission. In physical implementations, micro-electro-mechanical systems (MEMS) or piezo-electric mirror actuators consume dynamic switching power. Total system energy claims must incorporate actuator drive electronics.
3. **Discrete Codebook vs. Continuous Beam Tracking**: To keep the action space tractable ($3,125$ states), we utilized a 5-state discrete orientation codebook. Continuous mirror tilt optimization via actor-critic architectures (e.g., DDPG, SAC) represents an important future research vector.
4. **Discrepancy with 2024 Paper Numerical Targets**: As documented in `antigravity_report/RESEARCH_RESULTS.md`, the published curves in Liu et al. (2024) exhibit an irreconcilable $\\sim 52\\text{ dB}$ SNR discrepancy between Fig. 6(a) ($5.81\\text{ bps/Hz}$ secrecy) and Fig. 6(b) ($2 \\times 10^{-4}$ BER). Our work adheres strictly to the published mathematical equations and physical parameters of Table I, rather than fitting unphysical numerical artifacts.

---

"""

# Normalize line endings
content_norm = content.replace("\r\n", "\n")
idx_start = content_norm.find(old_sec_vi_start)
idx_end = content_norm.find(old_sec_viii_start)

if idx_start == -1 or idx_end == -1:
    raise ValueError(f"Could not find section markers: start={idx_start}, end={idx_end}")

new_content = content_norm[:idx_start] + new_sec_vi_and_vii + content_norm[idx_end:]
path.write_text(new_content, encoding="utf-8")
print("Successfully updated manuscript/draft.md")


# Phase-Separated Authoritative Metrics Tables

Generated directly from `output_figures/ris/final_evaluation/ris_study_summary.json`.
Study: Nominal scenario, L1 energy model, 10 independent seeds (42--51), 2,000 training slots, 1,000 frozen evaluation slots per run (30 runs, 90,000 total slots).

## Table 1: Frozen-Policy Greedy Evaluation Phase (1,000 slots, $\epsilon = 0$, zero updates)
> **Operational Context:** Evaluates the single operating point selected by deterministic argmax Q-policy for each seed. Since room geometry is static, each seed repeats one fixed operating point across all 1,000 slots. Seed ($N=10$) is the independent statistical replicate.

| Scheme | Action Space $|\mathcal{A}|$ | Secrecy Rate (bps/Hz) [Mean $\pm$ SE] | 95% Student-$t$ CI [bps/Hz] | Bob BER [Mean] | Energy Cost [Mean $\pm$ SE] | Bob QoS Outage ($>10^{-3}$) | Secrecy Outage ($<0.1\text{ bps/Hz}$) | Unique Actions per Seed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BASELINE** | 625 | 1.320521 $\pm$ 0.040510 | [1.2289, 1.4122] | 0.0e+00 | 2.0500 $\pm$ 0.1167 | 0.0% (0.0000) | 0.0% (0.0000) | 1 (static) |
| **FIXED_RIS** | 625 | 1.497799 $\pm$ 0.079307 | [1.3184, 1.6772] | 0.0e+00 | 2.2000 $\pm$ 0.1106 | 0.0% (0.0000) | 0.0% (0.0000) | 1 (static) |
| **JOINT_RIS** | 3125 | 1.456450 $\pm$ 0.060377 | [1.3199, 1.5930] | 0.0e+00 | 2.0000 $\pm$ 0.1491 | 0.0% (0.0000) | 0.0% (0.0000) | 1 (static) |

*Note on Evaluation Outages:* In this static frozen evaluation, all 10 seeds across all three schemes achieve secrecy rate $> 0.1\text{ bps/Hz}$ and Bob $\text{BER} < 10^{-10}$ (formula output evaluates to 0.0), resulting in exactly 0.0% outage across all schemes.

## Table 2: Final Training Window (Slots 1,501--2,000, residual exploration $\epsilon \approx 0.02$)
> **Operational Context:** The last 500 slots of active training. The agent has largely converged but still takes random exploratory actions with probability $\epsilon \approx 0.02$.

| Scheme | Secrecy Rate (bps/Hz) [Mean $\pm$ SE] | 95% Student-$t$ CI [bps/Hz] | Bob BER [Mean $\pm$ SE] | Energy Cost [Mean $\pm$ SE] |
| :--- | :---: | :---: | :---: | :---: |
| **BASELINE** | 1.296420 $\pm$ 0.039799 | [1.2064, 1.3865] | 9.55e-05 $\pm$ 6.43e-05 | 2.0562 $\pm$ 0.1145 |
| **FIXED_RIS** | 1.470985 $\pm$ 0.077190 | [1.2964, 1.6456] | 2.25e-05 $\pm$ 1.52e-05 | 2.2022 $\pm$ 0.1090 |
| **JOINT_RIS** | 1.430253 $\pm$ 0.059019 | [1.2967, 1.5638] | 6.44e-05 $\pm$ 4.42e-05 | 2.0074 $\pm$ 0.1462 |

## Table 3: Entire Training Trajectory (Slots 1--2,000, includes initial warmup and $\epsilon$-decay exploration)
> **Operational Context:** Full 2,000 training slots where exploration decays from $\epsilon=0.15$ to $0.02$. Outages here reflect exploration failures and initial learning warmup.

| Scheme | Secrecy Rate (bps/Hz) [Mean $\pm$ SE] | 95% Student-$t$ CI [bps/Hz] | Bob BER [Mean $\pm$ SE] | Energy Cost [Mean $\pm$ SE] | Bob QoS Outage ($>10^{-3}$) | Bob QoS Outage ($>10^{-4}$) | Secrecy Outage ($<0.1\text{ bps/Hz}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BASELINE** | 1.191168 $\pm$ 0.049377 | [1.0795, 1.3029] | 5.15e-04 $\pm$ 1.14e-04 | 2.0923 $\pm$ 0.1073 | 0.41% (0.0041) | 0.41% (0.0041) | 9.19% (0.0919) |
| **FIXED_RIS** | 1.368445 $\pm$ 0.073368 | [1.2025, 1.5344] | 7.23e-04 $\pm$ 2.03e-04 | 2.2302 $\pm$ 0.1041 | 0.26% (0.0026) | 0.33% (0.0033) | 7.38% (0.0738) |
| **JOINT_RIS** | 1.319099 $\pm$ 0.069329 | [1.1623, 1.4759] | 2.85e-04 $\pm$ 9.87e-05 | 2.0129 $\pm$ 0.1340 | 0.20% (0.0020) | 0.21% (0.0021) | 6.23% (0.0623) |

## Table 4: Paired Seed-by-Seed Differences Across Phases ($N=10$ Seeds, Student-$t$ 95% CI)
| Comparison | Phase / Window | Sample Mean Diff $\bar{\Delta}$ | Std $s_\Delta$ | 95% Student-$t$ CI | Statistical Significance at 95% |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **fixed_ris minus baseline** | Frozen Evaluation (1000 slots) | $\Delta R_s = +0.177277\text{ bps/Hz}$, $\Delta E = +0.1500$ | 0.1949 | [+0.0378, +0.3167] | **Statistically Significant** (CI strictly positive) |
| **fixed_ris minus baseline** | Final Training Window (500 slots) | $\Delta R_s = +0.174565\text{ bps/Hz}$, $\Delta E = +0.1460$ | 0.1907 | [+0.0382, +0.3110] | **Statistically Significant** (CI strictly positive) |
| **fixed_ris minus baseline** | All Training (2000 slots) | $\Delta R_s = +0.177277\text{ bps/Hz}$, $\Delta E = +0.1379$ | 0.1603 | [+0.0626, +0.2920] | **Statistically Significant** (CI strictly positive) |
| **joint_ris minus baseline** | Frozen Evaluation (1000 slots) | $\Delta R_s = +0.135929\text{ bps/Hz}$, $\Delta E = -0.0500$ | 0.2515 | [-0.0440, +0.3158] | Not Significant (CI spans zero) |
| **joint_ris minus baseline** | Final Training Window (500 slots) | $\Delta R_s = +0.133833\text{ bps/Hz}$, $\Delta E = -0.0488$ | 0.2455 | [-0.0418, +0.3094] | Not Significant (CI spans zero) |
| **joint_ris minus baseline** | All Training (2000 slots) | $\Delta R_s = +0.127930\text{ bps/Hz}$, $\Delta E = -0.0794$ | 0.2904 | [-0.0798, +0.3357] | Not Significant (CI spans zero) |
| **joint_ris minus fixed_ris** | Frozen Evaluation (1000 slots) | $\Delta R_s = -0.041348\text{ bps/Hz}$, $\Delta E = -0.2000$ | 0.3160 | [-0.2674, +0.1847] | Not Significant (CI spans zero) |
| **joint_ris minus fixed_ris** | Final Training Window (500 slots) | $\Delta R_s = -0.040732\text{ bps/Hz}$, $\Delta E = -0.1948$ | 0.3090 | [-0.2618, +0.1803] | Not Significant (CI spans zero) |
| **joint_ris minus fixed_ris** | All Training (2000 slots) | $\Delta R_s = -0.049347\text{ bps/Hz}$, $\Delta E = -0.2174$ | 0.3085 | [-0.2700, +0.1714] | Not Significant (CI spans zero) |
# Master Agent & Researcher Handoff: RIS + FJ + VLC + DRL

> **Notice to any AI Agent or Researcher opening this repository:**  
> This document is designed to give you an **instant, complete, and unambiguous understanding** of the project goals, implementation status, verified experimental evidence, known physics limitations, and exact next steps. You do not need to rediscover or guess anything.

---

## 1. Executive Summary & Objective

* **Core Project:** Indoor Visible Light Communication (VLC) physical-layer security simulation based on the 2024 IEEE Transactions on Wireless Communications paper:  
  *“Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication”* (Liu et al., DOI: 10.1109/TWC.2024.3458046).
* **Research Goal:** Extend the 2024 paper's baseline system by introducing a wall-mounted **Optical Reconfigurable Intelligent Surface (RIS)** (controllable mirror array) to jointly control Friendly Jamming (FJ) beamformer weights $\mathbf{w}$ and RIS mirror alignment codebook index $q$ using Deep Reinforcement Learning (DRL): **RIS + FJ + VLC + DRL**.
* **Key Invariant:** The original 2024 paper model (Lambertian LOS channels, Table I parameters, 4-fixture friendly jammers, and continuous-input Eq. 4 secrecy rate) is the research baseline. The separate `physical` mode is an earlier diagnostic alternative and must **never** silently replace this baseline.

---

## 2. Current Implementation Status (Verified Evidence)

| Subsystem | Status | Verification Evidence |
|---|---|---|
| **2024 Paper Equations (Eq. 1–23)** | **100% Implemented Verbatim** | `tests/test_vlc_paper.py` (21/21 passed) |
| **Full Regression Test Suite** | **87 / 87 Tests Passed** | `python -B -m unittest discover -s tests -v` (`28.4s OK`) |
| **Optical RIS Physics (`vlc/ris.py`)** | **Validated & Power-Conserving** | Snell's law reflection, sub-tile quadrature, area shrinking, FoV cutoff, power bounds (`tests/test_ris_optics.py` 13/13 passed) |
| **Joint Environment (`vlc/ris_environment.py`)** | **Fully Integrated** | Supports `off` (baseline), `fixed` ($q=1$), and `joint` DRL control ($[w, q]$ in state-action sequence $\phi^{(k)}$) |
| **Matched Multi-Seed RIS Experiments** | **Executed & Recorded (36 runs total)** | 2,000 slots per run across seeds `42, 43, 44`: <br>• `output_figures/ris/nominal/` (18 runs: signed & L1 energy)<br>• `output_figures/ris/near_bob/` (9 runs)<br>• `output_figures/ris/colocated/` (9 runs) |
| **Interactive Dashboards** | **Parity Verified** | `index.html` / `visualizer.html` (identical), `ris.html`, and `app_server.py` local backend |

---

## 3. The 2024 Paper Numerical Truth (Do Not Claim 100% Curve Match)

A vital contribution of this repository's audit is establishing the mathematical relationship between the 2024 paper's printed equations and its published curves:

1. **Equation Fidelity:** Every printed equation (Lambertian path gain Eq. 1, wiretap signals Eq. 2–3, secrecy rate Eq. 4, Zero-Forcing LP Eq. 5, utility Eq. 7, Q-learning Eq. 8–9, Gaussian DND Eq. 10–12, CNN SGD Eq. 13, 4-PAM BER Eq. 14, and Corollary 1 Eq. 18/21/22) is implemented without synthetic scaling.
2. **The Numerical Gap:**  
   * Under Table I parameters ($-98.79\text{ dBm}$ noise, $P_T = 1\text{ W}$, $\alpha = 0.10$), Corollary 1 mathematically yields a theoretical secrecy capacity bound of **$c_s^* = 1.38\text{ – }1.91\text{ bps/Hz}$**.
   * Fig. 6(a) in the published paper plots $c_s \approx 5.68\text{ bps/Hz}$ (bound $\approx 5.81$), which requires an electrical SNR of **$64.5\text{ dB}$**.
   * Fig. 6(b) plots $\text{BER} \approx 2 \times 10^{-4}$, which requires an SNR of **$12.5\text{ dB}$**.
   * Because $12.5\text{ dB}$ and $64.5\text{ dB}$ differ by **$\sim 52\text{ dB}$**, no single noise variance can reproduce both plotted curves simultaneously under unmodified printed equations.
   * **Rule:** Do not reintroduce artificial multiplier hacks (`snr_scale = 500` or curve fitting) to fake published plot heights. Maintain strict equation fidelity and cite [PAPER_VS_REALITY.md](PAPER_VS_REALITY.md).

---

## 4. Key Experimental Findings (RIS Extension)

From 36 completed matched simulation runs over 2,000 slots each:

### A. Nominal Scenario (Bob at $(1.8, 1.6)$, Eve at $(3.2, 3.4)$)
* **Under $L_1$ Non-Negative Energy:**
  * **Baseline (No RIS):** Final 500-slot Secrecy Rate = **$1.3504\text{ bps/Hz}$**, Utility = **$0.6114$**, Bob BER = **$1.30 \times 10^{-4}$**.
  * **Fixed RIS ($q=1$, Alice $\to$ Bob):** Secrecy Rate = **$1.5078\text{ bps/Hz}$**, Utility = **$0.6388$**, Bob BER = **$4.30 \times 10^{-5}$**.
  * **Joint RIS + FJ + DRL:** Secrecy Rate = **$1.5230\text{ bps/Hz}$** ($+0.1726\text{ bps/Hz}$ over baseline), Utility = **$0.6543$**, Bob BER drops to **$4.84 \times 10^{-12}$** (virtual error-free communication).
* **Under Signed Energy ($\sum w_i$):**
  * Baseline suffers catastrophic **zero-collapse** ($99.48\%$ secrecy outage) because the agent exploits negative weights for energy bonuses without transmitting secrecy jamming.
  * Joint RIS + FJ + DRL drives secrecy rate to **$1.0530\text{ bps/Hz}$**, reducing secrecy outage to $36.8\%$.

### B. Colocated Adversary Boundary Test (Eve at exact Bob location)
* When Eve is colocated with Bob, physical channel separation is zero. Across all 9 runs and all schemes, secrecy rate is **identically $0.0000\text{ bps/Hz}$**, correctly matching the fundamental physical boundary of wiretap channels.

---

## 5. Quick-Start Commands

```powershell
# 1. Run all 87 unit tests (optics, DRL, bounds, regressions)
python -B -m unittest discover -s tests -v

# 2. Run paper equation checks and browser parity checks
python -B paper_audit/check_paper_match.py --equations-only
node paper_audit/check_browser_match.js

# 3. Run single evaluation of 2024 paper baseline
python main.py --mode eval

# 4. Run matched multi-seed RIS study (Nominal, 3 seeds)
python -u -B main.py --mode ris --slots 2000 --seeds 42 43 44 --ris-energy-sensitivity --save_dir output_figures/ris/nominal

# 5. Launch interactive web dashboard (with live 3D room and exact math breakdown)
python run.py --gui
```

---

## 6. Detailed Reports in This Folder

* [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) — High-level summary in English and Bengali.
* [RESEARCH_RESULTS.md](RESEARCH_RESULTS.md) — Exact numerical tables, standard errors, and 95% Student-$t$ confidence intervals.
* [PAPER_VS_REALITY.md](PAPER_VS_REALITY.md) — Comprehensive mathematical audit of the $52\text{ dB}$ normalization gap in the 2024 paper.
* [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) — Exact formulas for VLC channels, Snell mirror reflection, DRL CNN+DND, and MDP state-action sequence.
* [figures/](figures/) — High-resolution exported comparison plots for all scenarios and baseline figures.


# Supervisor Demonstration & Evidence Package: START HERE

**Project:** Physical Layer Security in Visible Light Communications (VLC) via Reconfigurable Intelligent Surfaces (RIS) and Friendly Jamming (FJ) using Deep Reinforcement Learning (DRL)  
**Target:** Demonstration and comprehensive scientific evidence for thesis supervisor review  
**Status:** Simulation demo fully operational · 94 regression unit tests passing · 10-seed matched evaluation complete  

---

## 1. Quick Launch Instructions (One-Click)

### Option A: Windows Batch Launcher (Recommended for Supervisor Meeting)
Double-click `run_supervisor_demo.bat` in the project root:
```cmd
run_supervisor_demo.bat
```
*This verifies your Python environment, starts the local IPv4 loopback service, detects an available ephemeral port, prints the active URL, and automatically opens the interactive demo in your default browser.*

### Option B: Dedicated Python Launcher
From the project root directory in PowerShell or CMD:
```bash
python launch_supervisor_demo.py
```

### Option C: Master CLI Runner
```bash
python main.py --mode demo
# or
python run.py --demo
```

### Clean Shutdown
Press `Ctrl+C` in the terminal running the launcher. The server cleanly releases the port and terminates all background worker threads. No orphaned processes remain running.

---

## 2. Interactive Simulation Demonstration URL Routes

Once started, the loopback server (`http://127.0.0.1:<port>/`) provides three key routes:

1. **Supervisor Demonstration Interface (Primary):**  
   `http://127.0.0.1:<port>/demo`  
   *Interactive 2D room floorplan with dynamic optical ray paths, instant codebook selection, live side-by-side Bob/Eve channel breakdowns, 10-seed authoritative results viewer, live DRL execution preview, and high-resolution publication figures.*
2. **Full Research Experiment Dashboard:**  
   `http://127.0.0.1:<port>/ris`  
   *Advanced research controls: custom receiver positioning, arbitrary jammer weights, multi-seed batch training, raw study JSON export.*
3. **Legacy Paper Visualizer:**  
   `http://127.0.0.1:<port>/`  
   *Original 3D Three.js room visualizer for the 2024 paper friendly-jamming model without RIS.*

---

## 3. Recommended 5-Minute Supervisor Meeting Flow

| Time | Demonstration Step | What to Show in the Demo | Key Scientific Talking Point |
| :--- | :--- | :--- | :--- |
| **0:00 – 1:00** | **System Architecture** | Open `/demo`. Point to Section 1 SVG room layout: Alice LED at center (2.5, 2.5), 4 Jammers, Optical RIS on south wall (y=0.25) with 6 specular mirror tiles, Bob, and Eve. | Explain the baseline: 2024 paper Friendly Jamming system extended with a 6-tile optical RIS array. The state vector is 4-dimensional ($p_e, c_s, h_{AB}, E$), observation sequence is $11 \times 11$, and action space is $|\mathcal{A}| = 3,125$. |
| **1:00 – 2:00** | **Live Optical Ray & Gain Verification** | In Section 1, click **"0: Off"**, observe zero reflected rays and table metrics. Then click **"1: Aim Alice → Bob"**. Watch the dynamic green reflected ray appear and the table show $+23.4\%$ boost in Alice-to-Bob gain ($h_{AB}: 2.718 \times 10^{-5} \to 3.354 \times 10^{-5}$). | Live Python computation: specular optics using 2D Gauss-Legendre quadrature. Reflected paths are physical and verified, not cosmetic drawings. Show that total gain is $h_{\text{eff}} = h^{\text{dir}} + h^{\text{ref}}$. |
| **2:00 – 3:00** | **Authoritative 10-Seed Study Results** | Scroll to Section 3. Review Tab 1: **Phase 1 Frozen Evaluation (1,000 slots)**. Show Baseline ($1.3205\text{ bps/Hz}$), Fixed RIS ($1.4978\text{ bps/Hz}$), Joint RIS ($1.4565\text{ bps/Hz}$). Show paired differences table. | **Statistical Honesty:** Fixed RIS has a statistically significant improvement of $+0.1773\text{ bps/Hz}$ ($95\%\text{ CI } [+0.0378, +0.3167]$, $p = 0.0183$). Joint DRL mean is $+10.3\%$, but its $95\%\text{ CI } [-0.0440, +0.3158]$ spans zero ($p = 0.1216$), so superiority is not proven. Outages in frozen evaluation are strictly $0.0\%$. |
| **3:00 – 4:00** | **Real DRL Execution Preview** | Scroll to Section 4. Select "24 Slots" and click **"Run Live DRL Smoke Run"**. Watch the progress bar update as PyTorch trains live and outputs final action weights $[w_1, w_2, w_3, w_4, \tilde{q}]$. | Point out the explicit banner: this is an execution proof demo, not evidence of superiority. Real convergence requires the completed 2,000-slot training protocol. |
| **4:00 – 5:00** | **Boundary Disclosures & Discussion** | Click **"Near-Bob Boundary (7 cm)"** preset in Section 1. Show that achievable secrecy rate drops to $0.0000\text{ bps/Hz}$. Show Figure 5 in Section 5. | Explain physical limitations honestly: spatial collinearity ($h_{AE} > h_{AB}$) prevents positive secrecy when Eve is within 7 cm of Bob. Present the 3 supervisor alignment questions in Section 6. |

---

## 4. Package Directory Map

```text
supervisor_package/
├── START_HERE.md                      <- This document: launch guide & meeting flow
├── DEMO_SCRIPT_BN.md                  <- 5-10 minute Bengali presentation script with English terms
├── IMPLEMENTATION_AND_VERIFICATION.md <- Architecture, equations, state/action spaces & test outcomes
├── RESULTS.md                         <- Authoritative phase-separated numbers, paired CIs & boundaries
├── REPORT_INDEX.md                    <- Master catalog of all project reports (authoritative vs historical)
├── COMPLETION_REPORT.md               <- Final task completion report & verification audit
├── PROVENANCE.json                    <- Source dataset hashes, SHA-256 integrity & run flags
├── compact_results.json               <- Standalone summary JSON of the 10-seed study (38 KB)
└── figures/                           <- Standalone high-resolution publication plots (DPI 200)
    ├── fig1_training_curves.png       <- Matched 2,000-slot training convergence with 95% CI bands
    ├── fig2_frozen_evaluation_secrecy.png <- Frozen evaluation secrecy rates with per-seed scatter
    ├── fig3_paired_differences.png    <- Paired difference forest plot & zero-reference analysis
    ├── fig4_optical_channel_breakdown.png <- Direct vs reflected gain decomposition across codebook
    └── fig5_near_bob_boundary.png     <- Near-Bob exhaustive 3,125-action grid search ($R_s = 0.0$)
```

---

## 5. Technical Requirements & Verification

- **Operating System:** Windows 10/11 (PowerShell or CMD)
- **Python Version:** Python 3.10 or higher
- **Required Packages:** `torch`, `numpy`, `matplotlib` (all installed and verified)
- **Unit Test Regression:** All 94 automated unit tests pass in ~35 seconds:
  ```bash
  python -B -m unittest discover -s tests -v
  ```
- **Equation & Browser Parity:**
  ```bash
  python paper_audit/check_paper_match.py --equations-only
  node paper_audit/check_browser_match.js
  ```
- **Offline Integrity & Portability:** All packaged reports in `supervisor_package/` use self-contained relative markdown links, KaTeX math notation, standalone figures (`figures/` with both PNG and vector PDF), and compact summary JSON (`compact_results.json`) for complete offline readability without internet access or broken references.



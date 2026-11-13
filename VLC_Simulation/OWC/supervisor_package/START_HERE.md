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
   *Dynamic interactive 3D indoor VLC room with live perspective camera controls, animated optical pulse links, 6 specular RIS mirror facets with slerp tilting, real-time Bob/Eve telemetry HUD, secondary 2D floorplan projection, 10-seed authoritative results viewer, live DRL execution preview with recorded-action timeline scrubbing, and high-resolution publication figures.*
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
| **0:00 – 1:00** | **3D Dynamic Environment & Architecture** | Open `/demo`. Point to the 3D room canvas: Alice LED luminaire at ceiling center (2.5, 2.5, 3.0), 4 Jammers ($J_1..J_4$), Optical RIS on south wall ($y=0.25\text{ m}$) with 6 specular mirror tiles, Bob (green halo), and Eve (red halo). Click `🪐 3D Orbit`, `🦅 Top-Down`, and `🪞 Front Wall (RIS)`. | Explain the baseline: 2024 paper Friendly Jamming system extended with a 6-tile optical RIS array. The state vector is 4-dimensional ($p_e, c_s, h_{AB}, E$), observation sequence is $11 \times 11$, and action space is $\|\mathcal{A}\| = 3,125$. Show that the 2D floorplan remains available on Tab 2. |
| **1:00 – 2:00** | **Live Optical Ray & Mirror Tilt Verification** | In Section 1, click **"0: Off"**, observe neutral slate stowed mirrors and zero reflected rays. Then click **"1: Aim Alice → Bob"**. Watch the 6 mirror facets smoothly tilt via `slerp`, glowing cyan facets appear, dynamic green reflected link pulse activate, and Alice-to-Bob gain boost $+23.4\%$ ($h_{AB}: 2.718 \times 10^{-5} \to 3.354 \times 10^{-5}$). | Live Python computation: specular optics using 2D Gauss-Legendre quadrature. Mirror normals and reflected paths are physical and verified. Scalar channel gains are computed in Python; pulses are illustrative link activity ($h > 0$). When a jammer has $w_i = 0$, its fixture dims and emits zero modulated pulses. |
| **2:00 – 3:00** | **Authoritative 10-Seed Study Results** | Scroll to Section 3. Review Tab 1: **Phase 1 Frozen Evaluation (1,000 slots)**. Show Baseline ($1.3205\text{ bps/Hz}$), Fixed RIS ($1.4978\text{ bps/Hz}$), Joint RIS ($1.4565\text{ bps/Hz}$). Show paired differences table. | **Statistical Honesty:** Fixed RIS has a statistically significant improvement of $+0.1773\text{ bps/Hz}$ ($95\%\text{ CI } [+0.0378, +0.3167]$, $p = 0.0183$). Joint DRL mean is $+10.3\%$, but its $95\%\text{ CI } [-0.0440, +0.3158]$ spans zero ($p = 0.1216$), so superiority is not proven. Outages in frozen evaluation are strictly $0.0\%$. |
| **3:00 – 4:00** | **Real DRL Execution Preview & Recorded-Action Replay** | Scroll to Section 4. Select "24 Slots" and click **"Run Live DRL Smoke Run"**. Watch PyTorch train live. Once complete, scrub the **Replay Timeline Slider** ($k = 1..24$) or click `▶ Play Replay` to watch recorded actions $[w_1, w_2, w_3, w_4, \tilde{q}]$ animate the 3D scene slot-by-slot. | Replay demonstrates policy dynamics using real saved actions and snapshot scenario isolation. Point out the explicit banner: smoke runs are execution proofs; formal results use the completed 2,000-slot protocol. |
| **4:00 – 5:00** | **Boundary Disclosures & Discussion** | Click **"Near-Bob Boundary (7 cm)"** preset in Section 1. Show that the 3D distance line turns crimson ($d_{BE} = 0.07\text{ m}$) and achievable secrecy drops to $0.0000\text{ bps/Hz}$. Show Figure 5 in Section 5. | Explain physical limitations honestly: spatial collinearity ($h_{AE} > h_{AB}$) prevents positive secrecy when Eve is within 7 cm of Bob. Present the 3 supervisor alignment questions in Section 6. |

---

## 4. Package Directory Map

```text
supervisor_package/
├── START_HERE.md                      <- This document: launch guide & meeting flow
├── DEMO_SCRIPT_BN.md                  <- 5-10 minute Bengali presentation script with English terms
├── DYNAMIC_3D_COMPLETION_REPORT.md    <- Dynamic 3D visualizer engine implementation & audit report
├── COMPLETION_REPORT.md               <- Master delivery report & verification audit
├── DYNAMIC_3D_CODEX_REVIEW.md         <- Codex audit findings and resolution log
├── CODEX_DELIVERY_REVIEW.md           <- Baseline audit findings and resolution log
├── IMPLEMENTATION_AND_VERIFICATION.md <- Architecture, equations, state/action spaces & test outcomes
├── RESULTS.md                         <- Authoritative phase-separated numbers, paired CIs & boundaries
├── REPORT_INDEX.md                    <- Master catalog of all project reports (authoritative vs historical)
├── PROVENANCE.json                    <- Source dataset hashes, SHA-256 integrity & run flags
├── compact_results.json               <- Standalone summary JSON of the 10-seed study (38 KB)
└── figures/                           <- Standalone high-resolution publication plots & demo captures
    ├── fig1_training_curves.png       <- Matched 2,000-slot training convergence with 95% CI bands
    ├── fig2_frozen_evaluation_secrecy.png <- Frozen evaluation secrecy rates with per-seed scatter
    ├── fig3_paired_differences.png    <- Paired difference forest plot & zero-reference analysis
    ├── fig4_optical_channel_breakdown.png <- Direct vs reflected gain decomposition across codebook
    ├── fig5_near_bob_boundary.png     <- Near-Bob exhaustive 3,125-action grid search ($R_s = 0.0$)
    ├── demo_screenshot.png            <- Master live demo screenshot
    ├── demo_3d_nominal.png            <- 3D room nominal view (Bob, Eve, RIS Aim Alice -> Bob)
    ├── demo_3d_changed_positions.png  <- 3D room changed positions view (Bob [2.0, 3.0], Eve [3.5, 1.5])
    ├── demo_3d_near_bob.png           <- 3D room near-Bob singularity view (d_BE = 7 cm)
    ├── demo_3d_stowed.png             <- 3D room stowed view (Config 0: neutral mirrors)
    └── scenario_changed/              <- 5 Scenario-labeled figures (PNG + vector PDF) for changed geometry
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



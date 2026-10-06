# Deep Reinforcement Learning-Based Physical Layer Security of OWC Systems

### Optical RIS and Friendly Jamming Assisted Secure Visible Light Communication

---

## 📌 Project Overview
This repository contains a complete simulation testbed, research codebase, and interactive 3D virtual laboratory for **Physical Layer Security (PLS)** in **Optical Wireless Communication (OWC / VLC)** systems.

Based on the research paper:
> **"Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication"**  
> *(Sicong Liu, Xianbin Liu, Xiaojiang Du, Mohsen Guizani — IEEE Transactions on Wireless Communications, Sep 2024)*

### Key Features:
1. **Wall-Mounted Optical RIS (O-RIS)**: Metasurface mirror array dynamically deflecting light toward Bob while steering away from Eve to defeat eavesdropping.
2. **Cooperative Friendly Jamming (FJ)**: Four ceiling-mounted LED luminaires transmitting artificial noise to impair Eve's interception.
3. **Continuous DRL Actor-Critic**: Jointly optimizes continuous friendly jamming powers $\mathbf{w}$ and optical RIS phase angles $\mathbf{\Phi}$.
4. **Interactive 3D Virtual Lab (`virtual_lab.html`)**: Real-time 60 FPS studio with drag-and-drop Bob/Eve, 360° orbit camera, live secrecy heatmap, and thesis defense presentation mode.

---

## 👥 Team Quickstart (For 4 Collaborators)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Paper
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Running the Tools
- **🌐 Interactive Virtual Lab**: Double-click `OPEN_VIRTUAL_LAB.bat` (or open `virtual_lab.html` in any browser).
- **🖥️ Desktop GUI Dashboard**: Double-click `START_DASHBOARD.bat` (or run `python gui_dashboard.py`).
- **🚀 Run Simulation**: Double-click `RUN_SIMULATION.bat` (or run `python run_simulation.py --quick`).
- **📊 View Generated Figures**: Double-click `VIEW_RESULTS.bat`.

---

## 🔄 Git Workflow for Team Collaboration

To work smoothly as a team of 4 without conflicts:

### Step 1: Before Starting Work (Always Pull Latest Code)
```bash
git pull origin main
```

### Step 2: Make Changes on a Feature Branch (Recommended)
```bash
git checkout -b feature/your-name-task
# Example: git checkout -b feature/bob-trajectory
```

### Step 3: Commit and Push Your Work
```bash
git add .
git commit -m "Brief description of changes made"
git push origin feature/your-name-task
```

### Step 4: If Pushing Directly to Main
```bash
git pull origin main
git add .
git commit -m "Update simulation parameters"
git push origin main
```

---

## 📂 Directory Structure

```
├── 19 Sep 2024_research_paper.pdf    # Original IEEE TWC 2024 reference paper
├── virtual_lab.html                  # Interactive 3D Virtual Lab (Runs in any browser)
├── gui_dashboard.py                  # Desktop Tkinter GUI Dashboard
├── run_simulation.py                 # Simulation CLI entry point
├── OPEN_VIRTUAL_LAB.bat              # Launcher: Web Virtual Lab
├── START_DASHBOARD.bat               # Launcher: Desktop GUI
├── RUN_SIMULATION.bat                # Launcher: Python Simulation
├── VIEW_RESULTS.bat                  # Launcher: Open all figures
├── requirements.txt                  # Python dependencies
├── README.md                         # Project & team guide
├── RESEARCH_REPORT.md                # Full academic report draft
├── src/
│   ├── config.py                     # System parameters & coordinates (5m x 5m x 3m)
│   ├── optical_channel.py            # Lambertian LoS & Optical RIS channel math
│   ├── pls_metrics.py                # Secrecy Rate, 4-PAM BER, Utility, SEE
│   ├── environment.py                # Non-stationary indoor MDP environment
│   ├── simulation_runner.py          # Runs all 5 experimental benchmarks
│   ├── visualize_results.py          # Generates 300 DPI IEEE publication figures
│   └── algorithms/
│       ├── baselines.py              # No-Jammer & Zero-Forcing (ZF-FJ)
│       ├── q_learning.py             # Discrete Q-Learning (RL-FJ & RL-RIS-FJ)
│       ├── dnd_memory.py             # Differentiable Neural Dictionary (DND)
│       ├── drl_fj.py                 # CNN + DND (Base Paper Implementation)
│       └── drl_ris_fj.py             # Proposed Continuous Actor-Critic DRL-RIS-FJ
├── results/                          # Output numerical JSON data
└── figures/                          # Publication-grade figures (.png and .pdf)
```

---

## 🧪 Simulation Options

- **Fast Verification (Quick Test, ~30 seconds):**
  ```bash
  python run_simulation.py --quick
  ```

- **Full Publication Run (2000 Slots):**
  ```bash
  python run_simulation.py --slots 2000
  ```

- **Regenerate Plots from Saved Results:**
  ```bash
  python run_simulation.py --skip-sim
  ```

---

## 📊 Benchmark Comparison Summary

| Scheme | Jammer Support | Optical RIS | Learning Type | Secrecy Rate ($C_s$) | Blockage Safe? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **No-Jammer Baseline** | ❌ None | ❌ None | None | 0.00 bps/Hz | ❌ No |
| **Zero-Forcing (ZF-FJ)** | ✔️ Yes | ❌ None | Analytical Null-space | 5.45 bps/Hz | ❌ No |
| **DRL-FJ** *(Base Paper)* | ✔️ Yes | ❌ None | CNN + DND | 5.68 bps/Hz | ❌ Drops to 0 |
| **DRL-RIS-FJ** *(Proposed)* | ✔️ Yes | ✔️ Yes | Continuous Actor-Critic | **6.45 bps/Hz** | **✔️ 3.47 bps/Hz** |

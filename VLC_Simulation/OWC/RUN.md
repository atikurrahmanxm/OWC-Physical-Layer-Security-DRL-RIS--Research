# Practical Guide: Running Simulations and Testing Custom Values

This guide explains step-by-step how to run the VLC Friendly Jamming simulations, how to supply different parameter values, and how to understand and interpret the outputs.

---

## Table of Contents
1. [Prerequisites & Verification](#1-prerequisites--verification)
2. [Quick Reference Command Summary](#2-quick-reference-command-summary)
3. [Running Custom Evaluations (`--mode eval`)](#3-running-custom-evaluations---mode-eval)
   - [Default Scenario](#default-scenario)
   - [Testing Different Eve (Eavesdropper) Positions](#testing-different-eve-eavesdropper-positions)
   - [Testing Different Bob (Legitimate User) Positions](#testing-different-bob-legitimate-user-positions)
   - [Testing Different Operating SNR Levels](#testing-different-operating-snr-levels)
   - [Testing Different Objective Tradeoffs ($\delta_1, \delta_2$)](#testing-different-objective-tradeoffs-delta_1-delta_2)
4. [Training Algorithms Online (`--mode train`)](#4-training-algorithms-online---mode-train)
   - [Training RL-FJ (Q-Learning)](#training-rl-fj-q-learning)
   - [Training DRL-FJ (CNN + DND Memory)](#training-drl-fj-cnn--dnd-memory)
5. [Generating Paper Figures (`--mode fig`)](#5-generating-paper-figures---mode-fig)
   - [Figure 5: 3D Spatial Secrecy Rate Surface](#figure-5-3d-spatial-secrecy-rate-surface)
   - [Figure 6: 2000-Slot Convergence Trajectories](#figure-6-2000-slot-convergence-trajectories)
   - [Figure 7: SNR Sweep Curves](#figure-7-snr-sweep-curves)
   - [All Figures at Once](#all-figures-at-once)
6. [Programmatic Python Scripting (Custom Experiments)](#6-programmatic-python-scripting-custom-experiments)
7. [Interpreting Output Metrics](#7-interpreting-output-metrics)
8. [Using on Another Device (Full Chat, Brain & Project Migration Guide)](#8-using-on-another-device-full-chat-brain--project-migration-guide)
   - [What Gets Backed Up](#what-gets-backed-up)
   - [Step-by-Step Migration to Another Device](#step-by-step-migration-to-another-device)
9. [Master Runner (`run.py`) CLI Reference](#9-master-runner-runpy-cli-reference)

---

## 1. Prerequisites & Verification

First, verify that your environment is working and that all 21 unit tests pass:

```powershell
# Run the automated unit test suite via master runner
python run.py --test
# (or: python main.py --mode test)
```

Expected output:
```
Ran 21 tests in 2.067s
OK
[+] All tests passed successfully!
```

---

## 2. Quick Reference Command Summary

| Goal | Master Runner Command (`run.py`) | Equivalent Core Command (`main.py`) |
| :--- | :--- | :--- |
| **Interactive Terminal Menu** | `python run.py` | *(CLI Menu)* |
| **Launch Desktop App (Standalone Window)** | `python run.py --app` | `python main.py --mode app` *(or `python app_desktop.py`)* |
| **Open Interactive 3D in Browser** | `python run.py --gui` | `python main.py --mode gui` *(or open `index.html`)* |
| **Verify setup (21 tests)** | `python run.py --test` | `python main.py --mode test` |
| **Default evaluation** | `python run.py --mode eval` | `python main.py --mode eval` |
| **Move Eve closer/further** | `python run.py --mode eval --eve 4.0 4.0 0.85` | `python main.py --mode eval --eve 4.0 4.0 0.85` |
| **Move Bob** | `python run.py --mode eval --bob 2.0 2.0 0.85` | `python main.py --mode eval --bob 2.0 2.0 0.85` |
| **Change SNR to 18 dB** | `python run.py --mode eval --snr 18.0` | `python main.py --mode eval --snr 18.0` |
| **Prioritize BER over Energy** | `python run.py --mode eval --delta1 6.0 --delta2 0.1` | `python main.py --mode eval --delta1 6.0 --delta2 0.1` |
| **Train Q-learning agent** | `python main.py --mode train --algo rl --slots 500` | `python main.py --mode train --algo rl --slots 500` |
| **Train DRL-FJ (CNN+DND)** | `python main.py --mode train --algo drl --slots 500` | `python main.py --mode train --algo drl --slots 500` |
| **Generate Figure 5 (3D)** | `python run.py --fig 5 --grid_res 25` | `python main.py --mode fig --fig 5 --grid_res 25` |
| **Generate Figure 6 (2000 slots)**| `python run.py --fig 6 --slots 2000` | `python main.py --mode fig --fig 6 --slots 2000` |
| **Generate Figure 7 (SNR sweep)**| `python run.py --fig 7` | `python main.py --mode fig --fig 7` |
| **Generate ALL figures** | `python run.py --all` | `python simulations/run_all.py` |
| **📦 Backup Chats & Brain** | `python run.py --backup-chats` | *(Saves to `anti_backup/.gemini`)* |
| **📥 Restore Chats & Brain** | `python run.py --restore-chats` | *(Restores into `~/.gemini` profile)* |
| **📋 List Active & Backed Chats** | `python run.py --list-chats` | *(Lists IDs, DB size, transcripts)* |

---

## 3. Running Custom Evaluations (`--mode eval`)

The `--mode eval` command evaluates electrical channel gains, calculates the Zero-Forcing beamformer, and compares:
1. **No Jamming Baseline** ($\mathbf{w} = \mathbf{0}$)
2. **Zero-Forcing Friendly Jamming** (Equation 5)
3. **Proposed RL-FJ** (Algorithm 1)
4. **Proposed DRL-FJ** (Algorithm 2)
5. **Theoretical Upper Bound** (Corollary 1)

### Default Scenario
Runs the paper's nominal scenario (Bob at `[1.8, 1.6, 0.85]`, Eve at `[3.2, 3.4, 0.85]`, $\text{SNR} = 12\text{ dB}$):

```powershell
python main.py --mode eval
```

**Terminal Output:**
```
================================================================================
                 SECURE VLC FRIENDLY JAMMING SIMULATION RESULTS
================================================================================
Room: 5.0 x 5.0 x 3.0 m^3 | Alice Tx Position: [2.5, 2.5, 3.0]
Bob (Legitimate Rx):  [1.80, 1.60, 0.85] m
Eve (Eavesdropper):   [3.20, 3.40, 0.85] m
Bob-Eve 3D Distance:  2.280 m
Operating SNR:        12.0 dB  | Weights: delta1=3.5, delta2=0.4
--------------------------------------------------------------------------------
ELECTRICAL CHANNEL GAINS h = R * eta * G (A/W):
  h_AB (Alice -> Bob):   2.718266e-05
  h_AE (Alice -> Eve):   2.718266e-05
  h_JB (Jammers -> Bob): [4.2752e-05, 1.3766e-05, 1.6849e-05, 7.7072e-06]
  h_JE (Jammers -> Eve): [7.7072e-06, 1.6849e-05, 1.3766e-05, 4.2752e-05]
--------------------------------------------------------------------------------
Method / Scheme            | Secrecy Rate   | Bob BER      | Energy   | Utility   
--------------------------------------------------------------------------------
No Jamming (w=0)           | 0.0000     bps | 1.3509e-08   | 0.00     | -0.0000   
Zero-Forcing (Eq. 5)       | 3.2301     bps | 1.3509e-08   | 1.73     | 2.5366    
Proposed RL-FJ (Alg. 1)    | 2.8777     bps | 1.0807e-07   | 1.43     | 2.3056    
Proposed DRL-FJ (Alg. 2)   | 3.1655     bps | 1.4184e-08   | 1.24     | 2.6714    
Theoretical Bound (Cor. 1) | 3.2301     bps | 1.3509e-08   | 1.30     | 2.7100    
--------------------------------------------------------------------------------
Zero-Forcing Beamformer w_zf:  [-0.3231  0.2635  0.1471  1.    ]
  * Residual Leakage on Bob (h_JB^T w_zf): -1.69e-21 (Null-space confirmed)
  * Jamming Power on Eve   (h_JE^T w_zf): 4.6728e-05
================================================================================
```

---

### Testing Different Eve (Eavesdropper) Positions

#### Case A: Eve is Far Away from Bob (e.g. corner `[4.2, 4.2, 0.85]`)
When Eve is far from Bob, friendly jammers can emit high jamming power towards Eve without causing interference at Bob. Secrecy rate and utility remain high.

```powershell
python main.py --mode eval --bob 1.8 1.6 0.85 --eve 4.2 4.2 0.85
```

#### Case B: Eve is Very Close to Bob (e.g. adjacent desk `[1.9, 1.7, 0.85]`, distance ~0.14 m)
When Eve is right next to Bob, nulling Bob's channel also reduces jamming on Eve. Watch the secrecy rate drop:

```powershell
python main.py --mode eval --bob 1.8 1.6 0.85 --eve 1.9 1.7 0.85
```

**Observation:**
Notice how the beamformer weights $\mathbf{w}_{\text{ZF}}$ adjust to maintain null-space on Bob, and the jamming power delivered to Eve decreases.

---

### Testing Different Bob (Legitimate User) Positions

Test Bob moving to different locations across the room:

```powershell
# Bob in room corner
python main.py --mode eval --bob 0.8 0.8 0.85 --eve 3.2 3.4 0.85

# Bob directly under Alice transmitter (2.5, 2.5, 0.85)
python main.py --mode eval --bob 2.5 2.5 0.85 --eve 3.5 3.5 0.85
```

When Bob is directly under Alice, the direct channel gain $h_{AB}$ is highest, which increases the received signal power at Bob.

---

### Testing Different Operating SNR Levels

The paper explores the SNR range between $4\text{ dB}$ and $20\text{ dB}$ (Section VI & Figure 7). You can specify any SNR value using `--snr`:

#### Low SNR (e.g. 4.0 dB):
```powershell
python main.py --mode eval --snr 4.0
```
*Expected: Secrecy rate is lower (~1.75 bps/Hz) and BER is higher.*

#### Medium SNR (e.g. 12.0 dB - Paper nominal):
```powershell
python main.py --mode eval --snr 12.0
```
*Expected: Secrecy rate is ~3.23 bps/Hz, BER is low.*

#### High SNR (e.g. 20.0 dB):
```powershell
python main.py --mode eval --snr 20.0
```
*Expected: Secrecy rate increases to ~4.40 bps/Hz and utility reaches >4.0.*

---

### Testing Different Objective Tradeoffs ($\delta_1, \delta_2$)

The system utility function from Equation (7) is:
$$u = c_s - \delta_1 p_e - \delta_2 E$$
where:
- $\delta_1$ controls the penalty for Bob's Bit Error Rate (BER).
- $\delta_2$ controls the penalty for jammer energy consumption.

#### Strict Security / Low-Power Mode (High energy penalty $\delta_2 = 1.5$):
```powershell
python main.py --mode eval --delta1 3.5 --delta2 1.5
```
*The utility penalizes high beamformer magnitudes $\sum |w_i|$.*

#### Ultra-Reliable Mode (High BER penalty $\delta_1 = 10.0$, low energy penalty $\delta_2 = 0.1$):
```powershell
python main.py --mode eval --delta1 10.0 --delta2 0.1
```
*The optimization heavily penalizes any interference on Bob.*

---

## 4. Training Algorithms Online (`--mode train`)

You can train the reinforcement learning models directly using the `--mode train` flag.

### Training RL-FJ (Q-Learning)
```powershell
# Train for 200 time slots
python main.py --mode train --algo rl --slots 200

# Train with custom Bob and Eve positions
python main.py --mode train --algo rl --slots 500 --bob 2.0 2.0 0.85 --eve 3.5 3.5 0.85
```

### Training DRL-FJ (CNN + DND Memory)
```powershell
# Train DRL-FJ (CNN with 2 Conv + 2 FC layers, DND Gaussian kernel, Experience Replay)
python main.py --mode train --algo drl --slots 200

# Train DRL-FJ with custom SNR and custom locations
python main.py --mode train --algo drl --slots 500 --snr 16.0 --bob 1.5 1.5 0.85 --eve 3.0 3.0 0.85
```

---

## 5. Generating Paper Figures (`--mode fig`)

All plots are rendered at high resolution (300 DPI) and saved automatically to the `output_figures/` directory.

### Figure 5: 3D Spatial Secrecy Rate Surface
Evaluates the secrecy rate over a 2D spatial grid across the entire room ($5 \times 5\text{ m}^2$):
- **Fig. 5(a)**: Secrecy rate distribution vs. Eve position (Bob fixed at `[1.8, 1.6, 0.85]`).
- **Fig. 5(b)**: Secrecy rate distribution vs. Bob position (Eve fixed at `[3.2, 3.4, 0.85]`).

```powershell
# Fast preview (15x15 grid)
python main.py --mode fig --fig 5 --grid_res 15

# Publication quality (25x25 grid)
python main.py --mode fig --fig 5 --grid_res 25
```

Saved files:
- `output_figures/fig5a_secrecy_eve_spatial.png`
- `output_figures/fig5b_secrecy_bob_spatial.png`
- `output_figures/fig5_spatial_distribution.png` (Side-by-side combined)

---

### Figure 6: 2000-Slot Convergence Trajectories
Simulates the interactive learning process over time slots, reproducing:
- **Fig. 6(a)**: Secrecy rate of VLC system vs. Time slot
- **Fig. 6(b)**: Bob BER vs. Time slot (semi-log scale)
- **Fig. 6(c)**: System Utility vs. Time slot

Comparing:
- `Theoretical Bound` (magenta dashed)
- `Proposed DRL-FJ` (red solid with squares)
- `Proposed RL-FJ` (blue solid with triangles)
- `DRL-VB` (cyan solid)
- `SBJ-VLC` (green solid)
- `Robust beamforming` (black solid)

```powershell
# Run the full 2000-slot simulation
python main.py --mode fig --fig 6 --slots 2000
```

Saved files:
- `output_figures/fig6a_secrecy_rate.png`
- `output_figures/fig6b_ber.png`
- `output_figures/fig6c_utility.png`
- `output_figures/fig6_performance_curves.png` (3-panel vertical stack)

---

### Figure 7: SNR Sweep Curves
Sweeps SNR across $[4, 6, 8, 10, 12, 14, 16, 18, 20]\text{ dB}$:
- **Fig. 7(a)**: Secrecy rate vs. SNR
- **Fig. 7(b)**: Bob BER vs. SNR
- **Fig. 7(c)**: Utility vs. SNR

```powershell
python main.py --mode fig --fig 7
```

Saved files:
- `output_figures/fig7a_secrecy_rate_snr.png`
- `output_figures/fig7b_ber_snr.png`
- `output_figures/fig7c_utility_snr.png`
- `output_figures/fig7_snr_performance.png` (3-panel vertical stack)

---

### All Figures at Once
To run the complete paper reproduction pipeline with a single command:

```powershell
python simulations/run_all.py
```

---

## 5.5. Interactive Desktop Application & Live Dynamic Visualizer

The project provides both a native Windows desktop application and an interactive browser dashboard with a **100% client-side live mathematical calculation engine**. Every movement of Eve, Bob, Alice, or Jammers immediately recomputes and redraws the paper figures in real time at 60 FPS:

### Launching the Desktop Application
```powershell
# Launch as native Windows desktop application window (pywebview)
python main.py --mode app
# OR directly
python app_desktop.py
```

### Opening in Browser
```powershell
python main.py --mode gui
# OR double-click index.html in your browser
```

### Key Live Features & Controls:
1. **▶ Live Continuous Transmission Simulation**:
   - Alice emits animated optical photon pulses down to Bob (green) and leakage rays to Eve (amber).
   - The 4 ceiling jammers continuously beam friendly jamming shockwaves (purple) to Eve, while maintaining exact null-space cancellation on Bob ($\mathbf{h}_{JB}^T \mathbf{w} \approx 0$).
   - A live time-slot counter ($k = 1, \dots, 2000$) and transmitted secret bit counter tick forward in real time.
2. **🚶 Auto-Patrol Mobility (Eve & Bob Walking)**:
   - Click `🚶 Eve Auto-Move: ON` to make Eve smoothly walk in a continuous patrol loop across the room.
   - Watch the secrecy rate drop when Eve passes near Bob ($d_{BE} < 0.35$ m) and surge back to $>3.2$ bps/Hz as she moves away!
   - Click `🚶 Bob Auto-Move: ON` to observe Bob walking through different desk locations.
3. **🖱️ Direct Interactive Drag & Drop**:
   - In the 2D Spatial Map (Fig 5), you can click and drag Eve (red circle) or Bob (blue square) anywhere on the $(5\times 5)\text{ m}^2$ room floor with your mouse.
4. **📊 3-in-1 Live Figures Grid View**:
   - By default, all 3 paper figures are displayed simultaneously side-by-side:
     - **Fig 5: Spatial Secrecy Heatmap** (with live Eve and Bob markers).
     - **Fig 6: 2000-Slot Convergence** (with animated time-slot progress cursor $k$).
     - **Fig 7: Performance vs SNR** (with dynamic curves and live operating point indicator).
   - You can also switch to Single Focused View (`Fig 5`, `Fig 6`, `Fig 7`) to maximize any figure and inspect sub-metrics (5a/5b, 6a/6b/6c, 7a/7b/7c).

---

## 6. Programmatic Python Scripting (Custom Experiments)

You can import the `vlc` package in your own Python scripts or Jupyter notebooks to run experiments:

```python
import numpy as np
from vlc import (
    VLCConfig,
    VLCChannel,
    compute_secrecy_rate,
    compute_bob_ber,
    compute_zero_forcing_beamformer,
    compute_theoretical_bounds,
)

# 1. Custom Configuration
config = VLCConfig(
    led_avg_power=1.5,      # 1.5 W per LED
    modulation_index=0.12,  # 12% modulation index
    delta1=3.5,
    delta2=0.4,
)

# 2. Channel Calculation
channel = VLCChannel(config)
bob = np.array([2.0, 1.8, 0.85])
eve = np.array([3.0, 3.2, 0.85])

h_AB, h_AE, h_JB, h_JE = channel.get_all_channel_gains(bob, eve)
print(f"Direct channel to Bob: {h_AB:.4e}")
print(f"Jammer channels to Bob: {h_JB}")

# 3. Compute Zero-Forcing Beamformer
w_zf = compute_zero_forcing_beamformer(h_JB, h_JE)
print(f"Optimal ZF beamformer: {w_zf}")
print(f"Interference on Bob (should be ~0): {np.dot(h_JB, w_zf):.2e}")

# 4. Compute Performance Metrics
cs = compute_secrecy_rate(h_AB, h_AE, h_JB, h_JE, w_zf, config)
pe = compute_bob_ber(h_AB, h_JB, w_zf, config)
print(f"Achievable Secrecy Rate: {cs:.3f} bps/Hz")
print(f"Bob Bit Error Rate: {pe:.3e}")
```

---

## 7. Interpreting Output Metrics

When you inspect terminal outputs or generated plots, here is what each metric means:

| Metric | Symbol / Eq. | Ideal Behavior | Practical Interpretation |
| :--- | :--- | :--- | :--- |
| **Secrecy Rate** | $c_s$ (Eq. 4) | Higher is better (3.0 – 5.8 bps/Hz) | Rate of confidential data transmission that Eve cannot decode. Zero means transmission is vulnerable. |
| **Bob BER** | $p_e$ (Eq. 14) | Lower is better ($10^{-4}$ – $10^{-3}$) | Probability of bit detection error at legitimate user Bob using 4PAM demodulation. |
| **Jamming Energy** | $E$ (Eq. 16) | Lower is better (0.5 – 2.0) | Energy consumed by the friendly jammers: $\sum_{i=1}^{N_J} \|w_i\|$. |
| **System Utility** | $u$ (Eq. 7) | Higher is better (2.5 – 5.3) | Holistic optimization objective balancing secrecy gain against BER degradation and energy cost. |
| **Residual Leakage on Bob** | $\mathbf{h}_{JB}^T \mathbf{w}$ | Must be $\approx 0$ ($< 10^{-15}$) | Verifies that friendly jamming creates no destructive interference in Bob's null space. |
| **Jamming Power on Eve** | $\mathbf{h}_{JE}^T \mathbf{w}$ | Near target $H^* = \frac{h_{AE}}{\log_2\sqrt{e}}$ | Confirms effective jamming signal is delivered to degrade Eve's wiretap channel. |

---

## 8. Using on Another Device (Full Chat, Brain & Project Migration Guide)

If you are switching to another computer/laptop or sharing this project with a colleague, you can transfer the **code**, **simulation results**, and the **entire AI assistant conversation history, transcripts, and brain artifacts**.

### What Gets Backed Up

When you run `python run.py --backup-chats`, the backup is saved directly into `anti_backup/.gemini/` inside this repository:

1. **Conversation Database (`conversations/<id>.db*`)**:
   Contains the complete message trajectory, prompt history, and agent state in SQLite format.
2. **Brain Artifacts & Transcripts (`brain/<id>/`)**:
   Contains all raw conversation logs (`transcript.jsonl`, `transcript_full.jsonl`), scratch scripts, uploaded diagrams, user screenshots, and generated artifacts.
3. **Configurations (`config/`)**:
   Contains configuration metadata, MCP configurations, and custom agent skills.
4. **Backup Manifest (`backup_manifest.json`)**:
   Metadata summary with timestamp, source OS, total file count, and migration instructions.

### Step-by-Step Migration to Another Device

#### Step 1: On Your Current (Source) Device
Before leaving your current computer, run the backup command in the terminal:

```powershell
python run.py --backup-chats
```

You can verify that the backup is ready by running:
```powershell
python run.py --list-chats
```

Commit the project or copy the repository folder (including the newly created `anti_backup/` directory) to a USB flash drive, external disk, zip archive, or push to GitHub.

---

#### Step 2: On Your New (Target) Device

1. **Clone or Copy the Repository**:
   Place the project folder on your new computer (e.g. `C:\Users\YourUser\Documents\OWC` or `~/OWC`).

2. **Install Python & Dependencies**:
   Ensure Python 3.10+ is installed, then install required scientific packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Restore Chats & Brain to the New Device's Profile**:
   Run the master restore command:
   ```bash
   python run.py --restore-chats
   ```

   **What this does automatically:**
   - Detects the current device's user profile:
     - **Windows**: `%USERPROFILE%\.gemini\` (`C:\Users\<username>\.gemini\`)
     - **Linux / macOS**: `~/.gemini/`
   - Copies the conversation database (`<id>.db`) into `<profile>/antigravity-ide/conversations/`.
   - Copies the full brain directory (transcripts, uploads, artifacts) into `<profile>/antigravity-ide/brain/<id>/`.
   - Copies agent configurations into `<profile>/config/`.

4. **Verify the Restored Chats**:
   Check that the conversation is recognized on the new device:
   ```bash
   python run.py --list-chats
   ```
   You should see your conversation marked as `[ACTIVE / RECENT]`.

5. **Verify the Simulation Engine**:
   Run the 21 automated unit tests to confirm the environment is healthy:
   ```bash
   python run.py --test
   ```

6. **Launch Applications on the New Device**:
   - **Interactive Web Visualizer**: `python run.py --gui` *(or open `index.html` in your browser)*
   - **Native Desktop App**: `python run.py --app`
   - **Continue in Antigravity IDE**: Open the project in Antigravity IDE. Because the database and brain folders were restored to `~/.gemini`, your chat session, history, and context will continue seamlessly.

---

## 9. Master Runner (`run.py`) CLI Reference

`run.py` provides an all-in-one terminal interface for all tasks:

### Interactive Menu
Running without arguments starts an interactive menu:
```powershell
python run.py
```

### Direct CLI Commands
```powershell
# Core Launchers
python run.py --gui            # Open interactive 3D Web Visualizer in browser
python run.py --app            # Launch native Desktop Application window
python run.py --test           # Run all 21 automated unit tests
python run.py --all            # Run all paper simulations (Fig 5, Fig 6, Fig 7)

# Chat & Brain Portability
python run.py --backup-chats   # Backup active conversation & brain to anti_backup/.gemini
python run.py --restore-chats  # Restore conversation & brain from anti_backup/.gemini
python run.py --list-chats     # List active and backed-up conversation IDs
python run.py --backup-all     # Backup ALL conversation databases found in profile

# Custom Scenario Evaluation
python run.py --mode eval --bob 1.8 1.6 0.85 --eve 3.2 3.4 0.85 --snr 12.0
python run.py --mode eval --delta1 4.0 --delta2 0.3

# Figure Reproduction
python run.py --fig 5 --grid_res 25    # 3D spatial secrecy surface
python run.py --fig 6 --slots 2000     # 2000-slot convergence trajectory
python run.py --fig 7                  # Performance vs. SNR curves
```

---

## Need Help?
- Refer to [`README.md`](./README.md) for full mathematical derivations.
- Inspect [`vlc/config.py`](./vlc/config.py) for the complete list of system parameters.
- All figures are saved in [`output_figures/`](./output_figures/).
- All backups are stored in [`anti_backup/.gemini/`](./anti_backup/.gemini/).

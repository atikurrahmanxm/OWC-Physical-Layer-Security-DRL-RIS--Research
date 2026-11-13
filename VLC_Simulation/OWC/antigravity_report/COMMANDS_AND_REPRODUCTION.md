# Commands & Reproduction Playbook

All commands are executed from the workspace root:  
`D:\SCRIPTS\GitHub\OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC`

---

## 1. Verifying Code Integrity (Run First)

```powershell
# Run the complete regression test suite (all 87 tests)
python -B -m unittest discover -s tests -v

# Run the strict paper equation check
python -B paper_audit/check_paper_match.py --equations-only

# Run browser and loopback HTTP parity check
node paper_audit/check_browser_match.js
```

---

## 2. 2024 Paper Baseline Simulations

```powershell
# Evaluate default nominal geometry under Table I noise (-98.79 dBm)
python main.py --mode eval

# Run spatial secrecy rate distribution (Figure 5)
python main.py --mode fig --fig 5 --grid_res 25

# Run 2,000-slot convergence simulation across all schemes (Figure 6)
python main.py --mode fig --fig 6 --slots 2000

# Run SNR sweep across [4, 6, ..., 20] dB (Figure 7)
python main.py --mode fig --fig 7 --slots 2000
```

---

## 3. Optical RIS Simulation Studies

```powershell
# Run matched nominal RIS study (seeds 42, 43, 44, signed and L1 energy models)
python -u -B main.py --mode ris --slots 2000 --seeds 42 43 44 --ris-energy-sensitivity --save_dir output_figures/ris/nominal

# Run near-Bob adversarial scenario (Eve 7 cm from Bob)
python -u -B main.py --mode ris --slots 2000 --seeds 42 43 44 --ris-scenarios near_bob --energy-model l1 --save_dir output_figures/ris/near_bob

# Run colocated physical boundary test (Eve at Bob location)
python -u -B main.py --mode ris --slots 2000 --seeds 42 43 44 --ris-scenarios colocated --energy-model l1 --save_dir output_figures/ris/colocated
```

---

## 4. Interactive Dashboards & Live Visualizers

```powershell
# Launch interactive 3D laboratory and real-time math breakdown
python run.py --gui

# Open desktop app wrapper (pywebview)
python run.py --app
```
* **Ports & Host:** Serves loopback HTTP on `http://127.0.0.1:8000/`.
* **RIS Visualizer:** Available at `http://127.0.0.1:8000/ris.html`.
* **Core Visualizer:** Available at `http://127.0.0.1:8000/index.html` (identical to `visualizer.html`).


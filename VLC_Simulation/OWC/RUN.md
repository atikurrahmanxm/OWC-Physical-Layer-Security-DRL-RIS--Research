# Running the corrected implementation

See [README.md](README.md) for model assumptions and [PAPER_REPRODUCTION.md](PAPER_REPRODUCTION.md) for the remaining limits.

For the consistent current-domain alternative, run `python main.py --mode all --model physical --slots 2000`. It uses a separate `output_figures/physical/` destination by default. See [PHYSICAL_MODEL.md](PHYSICAL_MODEL.md). The default paper mode preserves the earlier printed-equation experiment; physical mode does not claim to reproduce the paper's continuous-input capacity curve.

```powershell
pip install -r requirements.txt
python run.py --gui
```

Use **Train Python agents** for the active scenario or **Train SNR sweep** for Figure 7. These run the actual PyTorch CNN/DND and Q-learning implementations. Curves remain unavailable until their own scenario has finished training. Download raw run data with the dashboard button.

```powershell
python main.py --mode train --algo drl --slots 2000 --seed 42
python main.py --mode eval --bob 1.8 1.6 0.85 --eve 3.2 3.4 0.85 --slots 2000
python main.py --mode train --algo rl --snr 12 --snr-definition eq4 --energy-model l1 --slots 2000
python run.py --fig 5 --grid_res 25
python run.py --fig 6 --slots 2000
python run.py --fig 7 --slots 2000
python run.py --all --slots 2000
python run.py --test
```

```powershell
# Optical RIS matched multi-seed experiments
python -u -B main.py --mode ris --slots 2000 --seeds 42 43 44 --ris-energy-sensitivity --save_dir output_figures/ris/nominal
python -u -B main.py --mode ris --slots 2000 --seeds 42 43 44 --ris-scenarios near_bob --energy-model l1 --save_dir output_figures/ris/near_bob
python -u -B main.py --mode ris --slots 2000 --seeds 42 43 44 --ris-scenarios colocated --energy-model l1 --save_dir output_figures/ris/colocated
```

Both launchers use Table I noise when `--snr` is omitted. Default energy is the nonnegative `l1` interpretation of Eq. (16); default SNR is Bob's interference-free Eq. (4) SINR (`eq4`). This prevents negative energy credits and includes modulation scaling in the SNR conversion. These assumptions are recorded in each run, and are not verified author conventions. The old behavior remains available with `--energy-model paper_signed --snr-definition electrical`.

Each figure run exports JSON alongside the PNG files. JSON contains raw slot data, seed, configuration, provenance and unresolved reproduction issues. The Figure 6 display uses EMA50; Figure 7 averages all slots. A smoke preview can use `--slots 24`, and its metadata will state 24 rather than claim a 2000-slot experiment.

For desktop hosting, install pywebview through requirements and run `python run.py --app`. Directly opening the HTML supports physics only; training requires the Python service.

Generate current calculated reports with `python create_math_report.py`. The original bundled hand-calculation reports are historical and contain claims invalidated by the audit.

`python paper_audit/check_paper_match.py` performs strict published-target comparison and currently exits 1 because reproduction fails. `python paper_audit/check_paper_match.py --equations-only` checks the implementation without claiming a numerical match. Both write the current evidence, PDF curve reference and comparison plot in `paper_audit/`.

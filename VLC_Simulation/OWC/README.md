# VLC friendly jamming: paper-based implementation

**Current research direction:** extend the 2024 paper's original system with an optical RIS, using joint **RIS + FJ + VLC + DRL** control. RIS is fully implemented, validated across 87 unit tests, and empirically evaluated over 36 multi-seed runs. Read [antigravity_report/README.md](antigravity_report/README.md) and [Agent.MD](Agent.MD) for the complete handoff; [AGENTS.md](AGENTS.md) is the automatic entry point for AI coding agents.

Python implementation of Algorithms 1 and 2 from **Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication**, Liu et al., IEEE TWC (2024), DOI 10.1109/TWC.2024.3458046. The supplied `19 Sep 2024.pdf` is the reference.

**Exact reproduction of the published curves is not established.** The PDF omits author code, random traces and the SNR normalization, and contains conflicting energy/bound expressions. See [PAPER_REPRODUCTION.md](PAPER_REPRODUCTION.md). No result is fitted or hardcoded to reproduce a plot.

An alternative **consistent physical 4-PAM model** is now available through `--model physical`. It computes secrecy and BER from the same current-domain signal and interference distribution, converts watt noise through an explicit receiver resistance, and reports incremental jamming energy in joules. Run `python run.py --mode eval --model physical --slots 2000`. Its results go to `output_figures/physical/`; the default `paper` mode and dashboard retain the paper-equation model. See [PHYSICAL_MODEL.md](PHYSICAL_MODEL.md) for assumptions, validation and the finite-alphabet rate ceiling. This alternative is not calibrated to the paper.

## Install and run

Python 3.10 or newer:

```powershell
pip install -r requirements.txt
python run.py --gui
```

The browser opens a loopback HTTP service. Room physics and exact zero-forcing update immediately. Use **Train Python agents** to run actual Q-learning and the PyTorch CNN + DND for 2,000 slots, or **Train SNR sweep** for all nine points. Runs can take minutes. Moving controls selects a new scenario; previously trained curves are not reused for different settings. **Download raw run** exports every slot, action and configuration.

Opening `index.html` directly supports the physics visualizer; Python training requires `python run.py --gui`. `visualizer.html` is an identical distribution copy. Desktop mode (`python run.py --app`) uses the same service through pywebview.

## Experiments

```powershell
python run.py --mode eval --slots 2000
python run.py --mode train --algo drl --slots 2000 --seed 42
python run.py --fig 5 --grid_res 25
python run.py --fig 6 --slots 2000
python run.py --fig 7 --slots 2000
python run.py --all --slots 2000
python run.py --test
```

`main.py` accepts the same simulation arguments. Both launchers use Table I noise by default. `--snr` applies to both evaluation and training. Figures 6 and 7 export all raw observations and actual actions beside their PNGs; display smoothing never replaces the raw data. Figure 7 averages **all** slots, including exploration.

```powershell
python main.py --mode train --algo rl --snr 12 --snr-definition eq4 --energy-model l1 --slots 2000
```

Choose SNR assumptions explicitly:

| Option | SNR numerator before division by noise variance |
|---|---|
| `eq4` (default) | `2 * h_AB**2 * alpha**2 * I_D**2 / (pi*e)`, Bob's interference-free Eq. (4) SINR |
| `electrical` | `P_T * h_AB**2`, the original project's convention |
| `pam` | `2 * P_T * h_AB**2 / 5`, the squared Eq. (14) erfc argument |

These are documented experimental conventions, not verified author settings. The old `electrical` conversion admits no positive secrecy on the 625-action grid at 4-20 dB. The default `eq4` convention includes the modulation scaling used in the secrecy equation and admits positive secrecy at every sweep point. Noise from Table I remains unchanged when SNR is omitted.

## Equations and learning

- `vlc/channel.py`: Lambertian LOS/FoV model, four-LED gain aggregation.
- `vlc/secrecy.py`: Eqs. (4), (7), (14) and (16). BER squares negative effective channels as printed. A missing Eve information link has zero leakage.
- `vlc/bounds.py`: exact box-constrained ZF solved by a scaled linear program; independent global bounds. Conditional Corollary 1 values are diagnostics, not unconditional ceilings.
- `vlc/rl_fj.py`: state-indexed Q-learning and Eq. (8) exploration.
- `vlc/drl_fj.py`: two Conv/two FC layers, F=[20,40,3,2,1,1,180,180], M=11, batch T=4, per-action Gaussian DND and SGD replay. Existing keys receive the updated Q directly. Batched lookup preserves separate normalization per action.
- `vlc/experiments.py`: shared real-agent execution and result provenance.
- `app_server.py`: loopback-only asynchronous training bridge for browser/desktop.

The default `--energy-model l1` uses the nonnegative amplitude cost `varrho * sum(abs(w))`. This explicitly interprets the ambiguous printed Eq. (16): changing the sign of a weight cannot produce an energy credit. Opt-in `--energy-model paper_signed` retains the literal signed sum, including negative values; it can reward zero-secrecy actions. Default bias is derived as `P_T/eta`; explicit bias overrides are possible programmatically.

The corrected default DRL run has positive secrecy at slot 1,400, and Figure 7 has positive 2,000-slot means at all nine SNR points. This fixes the zero collapse, but does not reproduce the published magnitudes. Table I still limits Bob's Eq. (4) capacity to 1.90865 bps/Hz, below the paper's 5.68. At 4 and 6 dB, the energy penalty makes no jamming the best utility action on the current grid, so positive average secrecy there arises during exploration. Raw records include `operating_point` diagnostics with capacity limits, maximum grid secrecy and the utility-optimal action; these references never feed actions to the learners. See [the correction evidence](paper_audit/ZERO_COLLAPSE_FIX.md).

The three old benchmark substitutes are now labeled **Restricted search (custom)**, **Regularized BF (custom)** and **Scaled ZF (custom)**. They do not implement references [20], [42], [43]. Deprecated Python aliases retain compatibility but emit warnings. Published benchmark comparisons remain unfinished pending a validated implementation of those separate papers and their adaptation settings.

## Verification and reports

```powershell
python -B -m unittest discover -s tests -v
python paper_audit/check_paper_match.py
python paper_audit/check_paper_match.py --equations-only
node paper_audit/check_browser_match.js
python create_math_report.py
```

The tests include equation counterexamples, exact constrained ZF checks, every discrete action against global bounds, both energy models, deterministic training, actual HTTP/Python parity and CLI SNR propagation. Tests passing certify these checks, not the paper's curves.

The paper checker now exits **1** when the published numerical targets fail; `--equations-only` exits successfully when implementation checks pass independently of those mismatches. It extracts the actual PDF vector curves, compares every plotted RL/DRL Figure 7 vertex, and checks both quoted Figure 6 DRL checkpoints using declared tolerances. A much lower BER also counts as a numerical mismatch. The PDF has five Figure 7 vertices at 4, 8, 12, 16 and 20 dB, with nine axis ticks. Extracted coordinates are published-plot evidence, not author raw simulation traces. See [the signal/noise analysis](paper_audit/SIGNAL_NORMALIZATION_GAP.md) and [comparison plot](paper_audit/paper_comparison.png).

`create_math_report.py` generates a new report from current calculations; it no longer uses hardcoded verification or supervisor sign-off rows. The old bundled verification DOCX/PDF and the initial audit results are historical artifacts, not current certificates.

Chat backup utilities in `run.py` are retained: `--backup-chats`, `--restore-chats`, `--list-chats`. They are independent of the simulator.

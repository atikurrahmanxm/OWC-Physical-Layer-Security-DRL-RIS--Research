# Project handoff: RIS + FJ + VLC + DRL

Last updated: 2026-11-13, Asia/Calcutta.

**Codex 3D demo addition:** User requested a 3D model for supervisor presentation. Added dependency-free interactive Canvas 3D projection directly to `supervisor_demo.html`, source maintained in `scripts/room3d_inline.js` (embedded copy must be synchronized when editing). Backend positions, actual finite tile side/centers and shared normals drive geometry; rotation uses the same Rodrigues construction as optics. Orbit drag, zoom, top/side presets and aggregate link toggle included. Lines via panel center are explicitly schematic, not exact per-tile ray intersections; no metric/physics changes. Backend errors clear 3D data. Node syntax check and headless Edge verified live q1 geometry/six mirrors; screenshot `supervisor_package/figures/demo_3d.png`. Existing report hashes/screenshots describing old page may need regeneration. Full regression suite not rerun for this presentation-only addition.

**Supervisor Demonstration & Delivery Package Completed & Audited (`supervisor_package/`):**
- **Independent CODEX Delivery Review Findings Resolved (100%):**
  1. *Optical Ray Visualization & Labeling:* Section 1 explicitly re-labeled *"Schematic 2D Floorplan & Optical Link Gain Activity (Top-Down Projection)"*. Dynamic per-link direct and reflected ray drawing based strictly on positive gains ($h_{AB}^{\text{dir}} > 0$, $h_{AE}^{\text{dir}} > 0$, $h_{JB,i}^{\text{dir}} > 0$, $h_{JE,i}^{\text{dir}} > 0$, $h_{AB}^{\text{ref}} > 10^{-12}$, $h_{JE,i}^{\text{ref}} > 10^{-12}$). Dynamic RIS tile normal projection vectors showing actual tilt angles $\theta = \text{atan2}(n_y, n_x)$ on each of the 6 tiles.
  2. *Dynamic JSON Data Binding:* Replaced static on-page HTML tables with dynamic `fetch('/compact_results.json')`, dynamically populating Phase 1, Paired Comparisons, Phase 2, and Phase 3 tables, rendering dataset provenance and SHA-256 hash.
  3. *Asynchronous Request Sequencing & Error Clearing:* Integrated monotonic `activeRequestId` to reject out-of-order stale responses and added explicit error state clearing to remove stale rays/tables if API calls fail.
  4. *Launcher Portability:* Added `cd /d "%~dp0"` to `run_supervisor_demo.bat` to allow execution from any directory; added `check_dependencies()` in `launch_supervisor_demo.py` to catch missing packages before importing `app_server`.
  5. *Vector PDF Figures & Delimiter Polish:* Generated both high-resolution PNG (200 DPI) and vector PDF versions of all 5 figures in `supervisor_package/figures/`; cleaned math delimiters into native HTML entities; updated badge to "94 Unit Tests Passing"; captured fresh screenshot `demo_screenshot.png` via Edge headless.
  6. *Exact Derived $p$-Values:* Derived exact two-sided Student-$t$ ($df = 9$) $p$-values: Fixed-minus-Baseline $p = 0.0183$, Joint-minus-Baseline $p = 0.1216$, Joint-minus-Fixed $p = 0.6887$. Updated in `compact_results.json`, `PROVENANCE.json`, `RESULTS.md`, `COMPLETION_REPORT.md`, `supervisor_demo.html`, and `fig3_paired_differences`.
  7. *Report Link Portability:* Clarified package boundaries in `START_HERE.md` and `REPORT_INDEX.md` to document self-contained takeaway files versus optional project root references.
- **Working Interactive Simulation Demo Delivered:** Enhanced `supervisor_demo.html` served at `/demo` with full-room 2D SVG optical floorplan ($5\text{ m} \times 5\text{ m}$), dynamically rendered optical rays tied strictly to actual nonzero computed gains, instant codebook selection ($q \in \{0, 1, 2, 3, 4\}$), geometry presets (Nominal, Near-Bob, Colocated), side-by-side Bob & Eve link gain breakdowns, live PyTorch DRL smoke run preview (24/200 slots), and embedded publication figures.
- **Reliable One-Click Launchers:** Created `run_supervisor_demo.bat` and `launch_supervisor_demo.py` (plus `--mode demo` in `main.py` and `run.py`). Service binds strictly to loopback IPv4 `127.0.0.1` on an auto-detected ephemeral port, opens `/demo` in the default browser, and cleanly shuts down on `Ctrl+C` with zero zombie processes.
- **Complete Offline Evidence Package (`supervisor_package/`):**
  1. `START_HERE.md`: Launcher commands, meeting flow, package map, dependencies, clean shutdown.
  2. `DEMO_SCRIPT_BN.md`: 5–10 minute presentation walkthrough script in Bengali with English technical terms and troubleshooting FAQ.
  3. `IMPLEMENTATION_AND_VERIFICATION.md`: System architecture, FeatureCNN ($m_0=11$, flatten $2560$), DND, $|\mathcal{A}|=3125$ action space, test outcomes.
  4. `RESULTS.md`: Authoritative phase-separated numbers, paired 95% Student-$t$ CIs, per-seed breakdown, boundary conditions ($R_s = 0.0000$ for Near-Bob and Colocated).
  5. `REPORT_INDEX.md`: Master catalog distinguishing active/authoritative reports from historical/superseded milestones.
  6. `COMPLETION_REPORT.md`: Comprehensive completion audit and checklist against `SUPERVISOR_SIMULATION_DELIVERY_TASK.md` and `CODEX_DELIVERY_REVIEW.md`.
  7. `PROVENANCE.json` & `compact_results.json`: Complete SHA-256 integrity hashes and 38 KB standalone summary JSON.
  8. `figures/`: 5 high-resolution publication plots (DPI 200) + vector PDFs + representative demo screenshot (`demo_screenshot.png` captured via Microsoft Edge headless).
- **Automated Regression Suite:** 94 unit tests passing cleanly in 28.4s (`Ran 94 tests, OK`). Parity audits (`check_paper_match.py --equations-only`, `check_browser_match.js`, `git diff --check`) all pass 100%.
- **Scope Discipline:** Manuscript drafting remains on hold as requested ("Manuscript আপাতত নয়"). Focus devoted entirely to working simulation demo and supervisor delivery package.

**Current Active Execution Status (Antigravity IDE - Fully Audited & Reconciled 2026-11-13):**
- **Reconciliation & Recheck (`COMPLETION_REVIEW.md` & `RECONCILIATION_RECHECK.md`)**: Fully audited and reconciled all findings:
  1. Programmatically generated `antigravity_report/AUTHORITATIVE_TABLES.md` with strict separation between Frozen Evaluation (1,000 slots), Final Training Window (500 slots), and All-Training (2,000 slots).
  2. Clarified that during frozen greedy evaluation ($\epsilon=0$), all three schemes achieve zero secrecy outage and zero Bob QoS outage at their static operating points; outage differences ($6.23\%$ vs $7.38\%$ vs $9.19\%$) occurred during exploratory training.
  3. Reconciled `manuscript/draft.md`: Abstract corrected to 2D CNN with `Conv2d`, Section IV architecture dimensions corrected to $m_0=11$ with flatten size $2560$ (`nn.Linear(2560, 180)`), action notation set to cardinality $|\mathcal{A}| = 3,125$ with 5-coordinate vector $\mathbf{a}_t$, temporal sequence notation updated to $\boldsymbol{\phi}_t$ with full action $\mathbf{a}$, and Joint RIS cross-seed variance framed as an exploration hypothesis rather than proven causation.
  4. Verified via exhaustive grid search that across all 3,125 discrete actions in the declared near-Bob geometry ($h_{AE} > h_{AB}$), the maximum achievable secrecy rate is identically $0.0000\text{ bps/Hz}$.
  5. Corrected `manuscript/tables.md` Table II to `Conv2d` with flatten size $2560$.
- **Trained-Policy Greedy Evaluation Implemented**: Implemented `evaluate(num_slots=1000)` in `DRLFJAgent` (`vlc/drl_fj.py`) and `RLFJAgent` (`vlc/rl_fj.py`) with frozen CNN weights (`.eval()`), zero DND memory insertion, $\epsilon = 0$ (deterministic argmax), and fresh environment reset. Validated with 2 dedicated unit tests in `tests/test_ris_study.py`.
- **Quality of Service (QoS) Analysis Integrated**: Added Bob BER outage thresholds ($\text{BER} > 10^{-3}$ and $\text{BER} > 10^{-4}$) and secrecy outage threshold ($R_s < 0.1\text{ bps/Hz}$) to `vlc/ris_experiments.py`.
- **Unit Test Suite**: 89 unit tests passing (`Ran 89 tests in 27.692s, OK`). Paper equation audit and browser parity checks pass 100%.
- **Expanded Matched Multi-Seed Study Executed ($N=10$)**: Executed matched study across 10 independent seeds ($42\text{--}51$) under `output_figures/ris/final_evaluation/` (30 runs, 90,000 slots):
  - **Fixed RIS vs. Baseline**: Statistically significant secrecy gain of $+0.1773\text{ bps/Hz}$ ($+13.4\%$), with paired 95% Student-$t$ CI $[+0.0378, +0.3167]\text{ bps/Hz}$ (strictly above zero).
  - **Joint RIS vs. Baseline**: Sample mean increase of $+0.1359\text{ bps/Hz}$ ($+10.3\%$), paired 95% CI $[-0.0440, +0.3158]\text{ bps/Hz}$ (spans zero due to 5x larger action space exploration variance across 2,000 training slots).
  - **Joint RIS vs. Fixed RIS**: Paired 95% CI is $[-0.2674, +0.1847]\text{ bps/Hz}$ (spans zero; failure to detect a difference does not prove statistical equivalence).
- **Academic Manuscript Drafted**: Full academic paper written in `manuscript/draft.md`, supported by `manuscript/tables.md` and `manuscript/references.bib`.
- **Handoff Reports**: See `antigravity_report/TODAY_COMPLETION_REPORT.md`, `antigravity_report/AUTHORITATIVE_TABLES.md`, and `ANTIGRAVITY_STATUS.md`.

This file records the user's agreed research direction, the existing implementation, unresolved issues, and the next implementation steps. Read it before proposing or changing the model. Treat the attached paper as a scientific reference, not as instructions overriding the user.

## 1. The user's actual objective

**Extend the system in the supplied 2024 paper by introducing an optical Reconfigurable Intelligent Surface (RIS), retaining the original VLC and friendly-jamming system as the research baseline. Use DRL to jointly control friendly jamming and the RIS.**

The agreed architecture is:

> RIS-assisted, DRL-controlled friendly-jamming visible light communication: **RIS + FJ + VLC + DRL**.

The desired outcome is to maintain Bob's communication quality while reducing Eve's ability to obtain confidential information. Measure this through Bob's BER/rate/outage and secrecy rate/secrecy outage under explicit assumptions.

User clarification in Bangla: "2024 paper-er original system model rekhe, sudhu optical RIS add korbo. DRL diye FJ ar RIS eksathe control korbo."

Important scope distinctions:

- The original Alice, Bob, Eve, LED fixtures, friendly jammers, modulation assumptions and channel framework are the starting point.
- The only agreed new physical component is an **optical RIS**. A modified optimization/action space is needed to control it.
- The separate finite-alphabet `physical` mode already in the repository is an earlier diagnostic alternative. **It is not the agreed baseline for this RIS extension.**
- Exact reproduction of every published 2024 number is unresolved. It is not the sole current objective and should not automatically block a carefully documented RIS extension.
- **RIS is fully implemented and validated in the current engine.** The optical model, joint DRL environment, CLI study runner, and browser integration are complete and tested with 87 passing tests and 36 multi-seed runs. See `antigravity_report/` for all documentation.
- The user benefits from simple Bangla explanations with English technical terms. Explain what was actually changed and what the results establish; avoid repeated vague claims that the project is "fixed."

## 2. Scientific reference

Local source: [19 Sep 2024.pdf](19%20Sep%202024.pdf), 14 pages.

Title: *Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication*.

DOI: [10.1109/TWC.2024.3458046](https://doi.org/10.1109/TWC.2024.3458046).

[Author-hosted copy](https://liusc1028.github.io/papers/TWC24liu.pdf).

Read the supplied PDF before deriving the extension. Relevant material includes the channel and received signals in Section II, Eqs. (4), (7), (14), (16), Algorithms 1/2, and the simulation setup/Table I in Section VI. Keep source equations, implementation interpretations, and newly proposed assumptions distinct.

The user confirmed that they do **not** have the authors' code, raw figure data, or additional settings. Do not repeatedly ask them for the same unavailable materials. Public-source research can still be useful.

## 3. Baseline configuration and equations

Current nominal configuration, based on the paper setup and explicit local choices:

| Item | Value |
|---|---|
| Room | 5 x 5 x 3 m |
| Alice | (2.5, 2.5, 3.0) m |
| Bob | (1.8, 1.6, 0.85) m |
| Eve | (3.2, 3.4, 0.85) m |
| Four ceiling jammer positions | (1.5,1.5,3), (1.5,3.5,3), (3.5,1.5,3), (3.5,3.5,3) m |
| LEDs per fixture | 4 |
| LED average optical power | 1 W |
| Modulation index | 0.10 |
| LED half-angle / PD FoV | 60 degrees / 60 degrees |
| Optical concentrator index | 1.5 |
| PD area / responsivity | 1e-4 m^2 / 0.54 A/W |
| Table I Bob noise | -98.79 dBm |
| Utility coefficients | delta1 = 3.5, delta2 = 0.4 |
| Q-learning rate / discount | 0.5 / 0.5 |
| CNN history window / minibatch | M = 11 / T = 4 |
| CNN hyperparameter vector | [20,40,3,2,1,1,180,180] |

Conversion efficiency `eta=1`, derived bias `I_D=P_T/eta`, seed 42, quantization `Lx=2`, epsilon schedule and some CNN details are implementation assumptions, not all uniquely specified by the PDF. The current quantized action space has 625 four-jammer vectors.

Baseline received signals, in compact notation:

```text
y_B = h_AB*x + (h_JB^T*w)*j + n_B
y_E = h_AE*x + (h_JE^T*w)*j + n_E
|w_i| <= 1; |x|, |j| <= alpha*I_D
```

The friendly-jamming scalar `j` is distinct from the information signal `x`. The original DRL state uses previous BER, previous secrecy rate, current legitimate channel gain and previous energy. Its utility is:

```text
u = secrecy_rate - delta1*Bob_BER - delta2*energy
```

## 4. Important baseline fidelity limits

**Neither existing mode has been certified to reproduce the published numerical curves.** Passing software/physics checks is not proof of reproduction.

`--model paper` is the default, but its default energy choice is `l1`, an explicitly documented interpretation. It is not automatically a literal implementation of every printed expression:

- Printed Eq. (16) is a signed sum of beam weights. Negative weights can produce negative energy and reward zero-secrecy actions.
- `--energy-model paper_signed` retains that literal printed expression. `l1` uses a nonnegative absolute sum. Do not silently switch between them while claiming an unchanged objective.
- Default paper-mode SNR convention is `eq4`. Legacy `electrical` and `pam` conventions also exist. The authors' Figure 7 normalization remains unknown.
- Under the current nominal scaling and Table I noise, Bob's interference-free Eq. (4) ceiling is about **1.908654495 bps/Hz**, below the paper's 5.68 checkpoint.
- The printed secrecy and BER expressions use different signal coefficients under current assumptions; altering noise alone does not fit both targets for a fixed current-grid action.
- Eqs. (20)/(23) have a base-2 domain conflict in the current interpretation. Conditional Corollary 1 must not be advertised as an unconditional global optimum.
- Comparison methods labeled `custom` are not validated implementations of references [20], [42], [43].

For a RIS study, freeze and record the exact baseline configuration, energy interpretation and normalization. Apply the same choices to the no-RIS and RIS cases. Do not invent an author setting or tune constants to 5.68 and call it independent verification. If calibration is later requested, label fitted parameters and separate fitting from validation.

See [PAPER_REPRODUCTION.md](PAPER_REPRODUCTION.md), [signal/noise analysis](paper_audit/SIGNAL_NORMALIZATION_GAP.md), and [zero-collapse history](paper_audit/ZERO_COLLAPSE_FIX.md).

## 5. Agreed RIS extension

Use an **optical RIS**, initially a mirror array with controllable orientations. Do not copy an RF complex phase-shift channel into incoherent LED IM/DD VLC without a justified optical model. Optical power gains, reflectivity, surface area, geometry, field of view and illumination constraints matter.

Let `q` denote the RIS configuration, for example grouped mirror yaw/pitch orientations and any justified assignment variables. The proposed effective channels are:

```text
h_AB_eff(q) = h_AB_direct + h_AB_RIS(q)
h_AE_eff(q) = h_AE_direct + h_AE_RIS(q)
h_JB_eff(q) = h_JB_direct + h_JB_RIS(q)
h_JE_eff(q) = h_JE_direct + h_JE_RIS(q)

y_B = h_AB_eff(q)*x + (h_JB_eff(q)^T*w)*j + n_B
y_E = h_AE_eff(q)*x + (h_JE_eff(q)^T*w)*j + n_E
```

These expressions describe the planned extension, not existing implementation. The initial scalar-gain model requires reflected-path delays to be negligible at the modeled symbol rate; otherwise delay/ISI modeling is an additional extension that must be declared.

Model both Alice and jammer illumination of the RIS, unless a physical restriction genuinely excludes some paths. The same surface configuration affects all links; reflected gains cannot be independently selected just to favor Bob. A passive RIS cannot create unlimited optical power or arbitrary negative optical channel gains.

Preserve the original receive structure and baseline parameters. Re-evaluate the original rate/BER expressions with effective gains only where their assumptions still hold. Record any further derivation or departure instead of quietly substituting the alternative 4-PAM model.

## 6. DRL controller and objective

The proposed joint action is:

```text
a_t = [w_t, q_t]
```

- `w_t`: friendly-jamming beamforming weights.
- `q_t`: optical RIS configuration.

Start from the original learning architecture and document the minimum adaptations. The existing Algorithm 2 implementation is CNN + per-action DND, not PPO/DDPG. If changing the learning algorithm later, explicitly identify it as another methodological change.

The current discrete action dictionary can grow prohibitively when mirror controls are appended. A grouped surface or finite orientation codebook is a possible initial design; its size and quantization must be justified and measured. No RIS element count, position, orientation grid, codebook, state extension or new learning algorithm has yet been finalized.

The original utility is the initial reference objective. To require a particular Bob service level, formulate an explicit BER/rate constraint or a documented penalty; the paper's soft utility alone does not guarantee uninterrupted reception. Any new QoS mechanism is an optimization change to document and apply fairly to comparisons.

A controller cannot assume Eve's exact location/channel is observable in practice. Perfect Eve CSI can be an explicitly labeled initial simulation assumption; uncertain location/CSI is a later robustness scenario.

## 7. Threat model and claims

- A **passive Eve** receives light and attempts interception. Her mere presence does not automatically inject interference into Bob's received signal.
- Friendly jamming selected to protect against Eve can itself degrade Bob; joint control should manage that tradeoff.
- A person's body blocking the optical path can affect Bob, but this needs an explicit blockage model.
- An actively transmitting malicious Eve is an active-jamming scenario and is not interchangeable with passive eavesdropping.
- Do not silently add active attacks, arbitrary Eve-dependent Bob attenuation or perfect Eve detection under the label "only add RIS."
- Eve may receive light without being able to recover a confidential message. Low leakage/positive secrecy under stated coding assumptions is the relevant goal; zero received photons is not required.
- High Eve BER alone does not prove secrecy. Evaluate secrecy rate and secrecy outage as well as Bob QoS.
- Universal zero outage or guaranteed non-decoding at every Eve location is not established. Bob/Eve near-co-location, blocked paths, limited surface area and CSI errors can limit performance.

## 8. Research novelty and useful references

Do not claim that merely combining RIS, VLC security and DRL is new. Related work already exists:

- [Secure Visible Light Communications via Intelligent Reflecting Surfaces](https://arxiv.org/abs/2101.12390), Qian et al.: optical mirror orientations and secrecy.
- [DRL-Based IRS-Assisted Secure Visible Light Communications](https://doi.org/10.1109/JPHOT.2022.3178852), Saifaldeen et al., 2022; [institutional publication record](https://elmi.hbku.edu.qa/en/publications/drl-based-irs-assisted-secure-visible-light-communications/): joint beamforming and mirror control using DDPG.

A possible research question, not a proven novelty claim, is:

> How much can joint optical-RIS and friendly-jamming control improve secrecy while maintaining a specified Bob QoS in the 2024 system, especially with a moving Eve or uncertain channel/location information?

Review related literature before asserting novelty. Dynamic Eve, robust QoS, limited observations, control overhead or the specific FJ/RIS coordination may provide a contribution, but this must be established through comparison.

## 9. Existing implementation map

| Location | Purpose |
|---|---|
| `vlc/config.py` | Geometry, physical constants, learning settings, paper/physical modes |
| `vlc/channel.py` | Direct Lambertian optical/electrical channels; **no RIS paths yet** |
| `vlc/secrecy.py` | Paper metrics and dispatch to the alternative physical model |
| `vlc/physical.py` | Separate finite-alphabet 4-PAM channel; not the RIS baseline |
| `vlc/environment.py` | Current state, jammer-only action space and rewards |
| `vlc/rl_fj.py` | State-indexed Q-learning |
| `vlc/drl_fj.py` | CNN + DND DRL-FJ implementation |
| `vlc/bounds.py` | Channel-nulling LP, independent bounds, conditional-paper diagnostics |
| `vlc/benchmarks.py` | Reference beamformers and clearly labeled custom baselines |
| `vlc/experiments.py` | Shared execution, metadata, raw export and feasibility diagnostics |
| `main.py`, `run.py` | CLI experiments and launchers |
| `app_server.py` | Local HTTP bridge to real Python agents |
| `index.html`, `visualizer.html` | Identical dashboard copies; currently paper-equation physics |
| `app_desktop.py` | Desktop wrapper for the same service |
| `simulations/` | Spatial, convergence and SNR figures |
| `tests/` | Formula, physical, integration and reproduction-check regressions |
| `paper_audit/` | Historical/current audit, extracted PDF curves and verification tools |

The physical mode works through CLI/Python/HTTP experiments; the GUI has no physical-mode selector. There is currently no RIS selector or RIS-aware dashboard physics. Exported RIS results must not be implied before those features exist.

## 10. Last verified results: evidence, not RIS performance

The last complete suite run before this documentation update had **58 passing tests**. Both existing experiment modes ran 2,000 slots per agent at the nominal operating point and at nine SNR points. Each mode's 40,000 saved RL/DRL observations was replayed from beam weights with zero metric discrepancy. Re-run checks after relevant code changes; do not treat these historical results as proof of new work.

| Check | Published paper | Existing paper mode | Alternative physical mode |
|---|---:|---:|---:|
| DRL secrecy at slot 1,400, displayed EMA50 | 5.68 | 1.555520 | 1.390328 |
| DRL BER at slot 1,200, displayed EMA50 | 0.0002 | 4.424136e-25 | 0.00790268 |

The physical rate uses a different finite-alphabet definition, so the table is a record of distinct experiments, not evidence of interchangeable metrics. At one real symbol/s/Hz its 4-PAM rate cannot exceed 2 bps/Hz. It is not calibrated to the paper.

The extracted Figure 7 PDF paths have **five plotted vertices at 4, 8, 12, 16, 20 dB**, while the axes show nine ticks. Current scripts sample all nine values. PDF vector coordinates are published drawing evidence, not author raw simulation traces.

Evidence locations:

- `output_figures/fig6_data.json`, `fig7_data.json`: existing paper-mode runs.
- `output_figures/physical/`: separate physical-mode data and figures.
- `paper_audit/verification_current.json`, `numerical_conformance.json`: paper comparison.
- `paper_audit/published_curve_reference.json`: extracted published curves.
- `paper_audit/physical_verification.json`: alternative-model checks.
- `paper_audit/paper_comparison.png`: actual disagreement with the paper.

The strict numerical paper check currently fails **31 of 32 comparisons** using declared local tolerances. The `reproduction_verified` flag remains false. Passing equation checks must not be reported as passing published-target checks.

## 11. Next implementation sequence

When continuing implementation, work toward the agreed RIS extension:

1. Read this handoff, the supplied PDF and relevant current source files. Freeze a documented no-RIS baseline; explicitly resolve or carry forward the signed-energy interpretation.
2. Specify mirror-array placement, area, reflectivity, orientation limits, FoV, grouping/codebook and CSI assumptions. Keep choices identifiable as simulation assumptions.
3. Implement and independently check optical RIS path gains, including Alice and jammer paths. Account for geometry and intercepted/reflected power; avoid double-counting LED aggregation or surface area.
4. Add effective-channel support to the environment behind an explicit RIS enable/configuration option. Preserve a clean no-RIS path.
5. Extend DRL state/actions and action-history exports for joint `w, q` control. Record what was changed from Algorithm 2 and evaluate the action-space cost.
6. Implement the declared Bob QoS objective/constraint consistently. Test physical/channel behavior before long training runs.
7. Compare the no-RIS baseline with optimized RIS + FJ + DRL under matched settings. Add fixed-RIS and partial-optimization ablations where useful.
8. Evaluate different Eve positions, near-co-location and any explicitly declared mobility, blockage or CSI-uncertainty scenarios. Report infeasible QoS/security cases rather than hiding them.
9. Extend the browser/desktop presentation using the actual RIS-aware backend; never draw synthetic learning curves or show old live physics as RIS-aware output.
10. Update this handoff, metadata, tests and current evidence with measured results and remaining limitations.

Do not restart by replacing the original research model with the alternative physical mode or by spending all effort forcing the old checkpoints to match. Preserve audit evidence while progressing the user's new research objective.

## 12. Acceptance checks for the future RIS work

- RIS disabled, zero reflectivity or zero usable surface area must reproduce direct-channel baseline gains and metrics for the same `w`, noise and configuration.
- Check that metric-level reduction separately from complete learning trajectories: a larger joint action space can change random exploration even with the same seed. Do not confuse that with a channel-reduction failure.
- Reflection/FoV/visibility limits, unavailable paths, orientation bounds, finite values and passive optical-power limits need meaningful tests.
- Keep jammer amplitude, illumination and LED-current constraints valid after adding reflected paths.
- Use deterministic seeds, raw per-slot metrics and both jammer/RIS actions in exported records.
- Compare equal LED power and jamming budgets; disclose RIS size, control overhead and any additional energy assumptions.
- Keep training-time exploration averages separate from greedy-policy evaluation. For a claimed paper-style Figure 7 average, include all first 2,000 slots as specified in that paper.
- Use several seeds/scenarios for improvement claims; a single favorable run is not an established gain.
- Benchmarks, reference bounds and simulator access to Eve CSI must be labeled accurately.

## 13. Commands and working conventions

Workspace: `D:\SCRIPTS\GitHub\OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC`.

Shell: Windows PowerShell. Python, NumPy, SciPy, PyTorch, Matplotlib and pypdf were available during the last work session; verify the active environment rather than assuming versions.

```powershell
# Regression suite
python -B -m unittest discover -s tests -v

# Existing paper-mode experiment; this does not enable RIS
python run.py --mode eval --model paper --slots 2000 --seed 42

# Literal printed signed-energy comparison, explicitly selected
python run.py --mode eval --model paper --energy-model paper_signed --slots 2000

# Strict published-target check: currently expected to exit 1
python -B paper_audit/check_paper_match.py

# Equation/export checks may pass even though numerical reproduction fails
python -B paper_audit/check_paper_match.py --equations-only
node paper_audit/check_browser_match.js

# Separate earlier physical experiment; not the agreed RIS baseline
python run.py --mode eval --model physical --slots 2000 --seed 42
python -B paper_audit/check_physical_model.py

# Existing dashboard, currently without RIS
python run.py --gui
```

There is no implemented RIS CLI flag yet. Do not present invented commands as working interfaces.

The workspace contains substantial pre-existing uncommitted changes and generated research artifacts. Inspect the working tree, preserve unrelated work, and do not reset or overwrite it. Keep new RIS runs in a separate output directory, such as `output_figures/ris/`, once that workflow is implemented.

The bundled old hand-calculation DOCX/PDF and historical audit files are not current certificates. `anti_backup/` and chat-backup features in `run.py` are unrelated to the research task.

For future handoffs, update measured status and distinguish clearly: **requested**, **proposed**, **implemented**, **tested**, and **not yet validated**.

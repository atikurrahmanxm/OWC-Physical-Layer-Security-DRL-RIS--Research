"""Run matched RIS + FJ + VLC + DRL study on changed Bob/Eve positions.

Scenario: Changed Positions
Bob: [2.0, 3.0, 0.85] m (Northwest quadrant)
Eve: [3.5, 1.5, 0.85] m (Southeast quadrant)
Euclidean distance d_BE = 2.1213 m

Preserves historical datasets under output_figures/ris/final_evaluation/.
Exports:
- Raw JSON: output_figures/ris/changed_positions/ris_study_data.json
- Summary JSON: output_figures/ris/changed_positions/ris_study_summary.json
- Scenario-labeled figures in both PNG (200 DPI) and vector PDF formats
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from vlc.config import VLCConfig
from vlc.channel import VLCChannel
from vlc.ris import OpticalRISConfig, OpticalRIS
from vlc.ris_experiments import run_ris_study, SCHEMES

OUTPUT_DIR = ROOT / "output_figures" / "ris" / "changed_positions"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR = OUTPUT_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
PKG_FIGURES_DIR = ROOT / "supervisor_package" / "figures" / "scenario_changed"
PKG_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Scenario definition
CHANGED_SCENARIO = {
    'name': 'changed_positions',
    'label': 'Changed Positions (Bob=[2.0, 3.0, 0.85]m, Eve=[3.5, 1.5, 0.85]m)',
    'bob': [2.0, 3.0, 0.85],
    'eve': [3.5, 1.5, 0.85]
}

SCHEME_COLORS = {
    'baseline': '#1f77b4',     # Blue
    'fixed_ris': '#2ca02c',    # Green
    'joint_ris': '#d62728'     # Red
}
SCHEME_LABELS = {
    'baseline': 'Baseline (No RIS)',
    'fixed_ris': 'Fixed RIS (Config 1: Alice→Bob)',
    'joint_ris': 'Joint RIS + FJ (Adaptive Codebook)'
}


def smooth_curve(arr, window=50):
    if len(arr) < window:
        return arr
    weights = np.ones(window) / window
    smoothed = np.convolve(arr, weights, mode='valid')
    prefix = [np.mean(arr[:i+1]) for i in range(window - 1)]
    return np.concatenate([prefix, smoothed])


def run_experiment(slots=1000, eval_slots=500, seeds=(42, 43, 44)):
    print(f"=== Starting Real Changed-Positions Experiment ===")
    print(f"Scenario: Bob={CHANGED_SCENARIO['bob']}, Eve={CHANGED_SCENARIO['eve']}")
    print(f"Protocol: {slots} training slots + {eval_slots} frozen evaluation slots | Seeds: {seeds}")
    
    config = VLCConfig(model='paper', energy_model='l1', snr_definition='eq4')
    ris_cfg = OpticalRISConfig()
    
    record = run_ris_study(
        config=config,
        ris_config=ris_cfg,
        slots=slots,
        eval_slots=eval_slots,
        seeds=seeds,
        scenarios=[CHANGED_SCENARIO],
        energy_models=['l1'],
        output_dir=str(OUTPUT_DIR),
        fixed_configuration=1,
        final_window=500,
        include_exhaustive=True
    )
    print(f"Experiment completed: {len(record['runs'])} matched runs executed.")
    return record


def save_plot(fig, name):
    for d in [FIGURES_DIR, PKG_FIGURES_DIR]:
        png_p = d / f"{name}.png"
        pdf_p = d / f"{name}.pdf"
        fig.savefig(png_p, dpi=200, bbox_inches='tight')
        fig.savefig(pdf_p, bbox_inches='tight')
        print(f"Saved: {png_p.name} and {pdf_p.name}")
    plt.close(fig)


def generate_scenario_labeled_figures(record):
    runs = record['runs']
    schemes = ['baseline', 'fixed_ris', 'joint_ris']
    seeds = sorted(list({r['seed'] for r in runs}))
    n_seeds = len(seeds)

    # -------------------------------------------------------------------------
    # Fig 1: Training Convergence Curves (EMA 50 with 95% CI bands across seeds)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    for scheme in schemes:
        scheme_runs = [r for r in runs if r['scheme'] == scheme]
        curves = np.array([smooth_curve(np.array(r['history']['secrecy_rate']), 50) for r in scheme_runs])
        mean_curve = np.mean(curves, axis=0)
        std_err = np.std(curves, axis=0, ddof=1) / np.sqrt(n_seeds) if n_seeds > 1 else np.zeros_like(mean_curve)
        ci_mult = stats.t.ppf(0.975, df=n_seeds - 1) if n_seeds > 1 else 1.96
        ci_lower = mean_curve - ci_mult * std_err
        ci_upper = mean_curve + ci_mult * std_err

        slots_x = np.arange(1, len(mean_curve) + 1)
        ax.plot(slots_x, mean_curve, color=SCHEME_COLORS[scheme], label=SCHEME_LABELS[scheme], linewidth=2.0)
        ax.fill_between(slots_x, ci_lower, ci_upper, color=SCHEME_COLORS[scheme], alpha=0.18)

    ax.set_title(
        f"Figure 1: Training Convergence (EMA 50, 95% CI across {n_seeds} seeds)\n"
        f"Scenario: Changed Positions (Bob=[2.0, 3.0, 0.85]m, Eve=[3.5, 1.5, 0.85]m, d_BE=2.12m) | L1 Energy",
        fontsize=11, fontweight='bold', pad=10
    )
    ax.set_xlabel("Training Time-Slot k", fontsize=10.5)
    ax.set_ylabel("Achievable Secrecy Rate R_s (bps/Hz)", fontsize=10.5)
    ax.grid(True, linestyle="--", alpha=0.45)
    ax.legend(loc="lower right", fontsize=9.5, framealpha=0.95)
    save_plot(fig, "fig1_changed_training_convergence")

    # -------------------------------------------------------------------------
    # Fig 2: Frozen Greedy Evaluation Secrecy Rate (Separate 500 Slots, epsilon=0)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5.5), constrained_layout=True)
    eval_means = []
    eval_cis = []
    per_seed_eval = {s: [] for s in schemes}

    for scheme in schemes:
        scheme_runs = [r for r in runs if r['scheme'] == scheme]
        rates = []
        for r in scheme_runs:
            eval_hist = r.get('eval_history')
            if eval_hist and 'secrecy_rate' in eval_hist:
                rates.append(np.mean(eval_hist['secrecy_rate']))
            else:
                rates.append(np.mean(r['history']['secrecy_rate'][-500:]))
        per_seed_eval[scheme] = rates
        m = np.mean(rates)
        eval_means.append(m)
        se = np.std(rates, ddof=1) / np.sqrt(n_seeds) if n_seeds > 1 else 0.0
        ci_val = stats.t.ppf(0.975, df=n_seeds - 1) * se if n_seeds > 1 else 0.0
        eval_cis.append(ci_val)

    x_pos = np.arange(len(schemes))
    bars = ax.bar(x_pos, eval_means, yerr=eval_cis, capsize=6,
                  color=[SCHEME_COLORS[s] for s in schemes],
                  edgecolor='black', linewidth=1.2, width=0.55, alpha=0.85)

    # Plot individual seed markers
    for idx, s in enumerate(schemes):
        ax.scatter([x_pos[idx]] * len(per_seed_eval[s]), per_seed_eval[s],
                   color='black', zorder=5, s=36, alpha=0.8, label='Per-Seed Mean' if idx == 0 else "")

    for bar, val in zip(bars, eval_means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                f"{val:.4f}\nbps/Hz", ha='center', va='center', color='white', fontweight='bold', fontsize=10)

    ax.set_xticks(x_pos)
    ax.set_xticklabels([SCHEME_LABELS[s] for s in schemes], fontsize=9.5)
    ax.set_ylabel("Mean Secrecy Rate (bps/Hz)", fontsize=10.5)
    ax.set_title(
        f"Figure 2: Phase 1 Frozen Greedy Evaluation (500 slots, epsilon=0, {n_seeds} seeds)\n"
        f"Scenario: Changed Positions (Bob=[2.0, 3.0, 0.85]m, Eve=[3.5, 1.5, 0.85]m)",
        fontsize=11, fontweight='bold', pad=10
    )
    ax.grid(axis='y', linestyle='--', alpha=0.45)
    save_plot(fig, "fig2_changed_frozen_evaluation")

    # -------------------------------------------------------------------------
    # Fig 3: Paired Differences (Fixed minus Baseline, Joint minus Baseline)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    fixed_diffs = np.array(per_seed_eval['fixed_ris']) - np.array(per_seed_eval['baseline'])
    joint_diffs = np.array(per_seed_eval['joint_ris']) - np.array(per_seed_eval['baseline'])

    comparisons = [
        ("Fixed RIS minus Baseline", fixed_diffs, '#2ca02c'),
        ("Joint RIS minus Baseline", joint_diffs, '#d62728')
    ]

    y_pos = np.arange(len(comparisons))
    for idx, (label, diffs, color) in enumerate(comparisons):
        m = np.mean(diffs)
        se = np.std(diffs, ddof=1) / np.sqrt(n_seeds) if n_seeds > 1 else 0.0
        ci_half = stats.t.ppf(0.975, df=n_seeds - 1) * se if n_seeds > 1 else 0.0
        p_val = stats.ttest_1samp(diffs, 0.0)[1] if n_seeds > 1 else 1.0

        ax.errorbar(m, y_pos[idx], xerr=ci_half, fmt='o', color=color, ecolor=color,
                    elinewidth=2.2, capsize=6, markersize=8,
                    label=f"{label}: Δ = {m:+.4f} (p = {p_val:.4f})")
        ax.scatter(diffs, [y_pos[idx]] * len(diffs), color=color, alpha=0.4, s=30)

    ax.axvline(0.0, color='gray', linestyle='--', linewidth=1.5, label='Zero Reference')
    ax.set_yticks(y_pos)
    ax.set_yticklabels([c[0] for c in comparisons], fontsize=10)
    ax.set_xlabel("Paired Difference in Secrecy Rate ΔR_s (bps/Hz)", fontsize=10.5)
    ax.set_title(
        f"Figure 3: Paired Difference Forest Plot (95% Student-t CI, df={n_seeds-1})\n"
        f"Scenario: Changed Positions (Bob=[2.0, 3.0, 0.85]m, Eve=[3.5, 1.5, 0.85]m)",
        fontsize=11, fontweight='bold', pad=10
    )
    ax.grid(True, linestyle='--', alpha=0.45)
    ax.legend(loc='lower right', fontsize=9.5)
    save_plot(fig, "fig3_changed_paired_differences")

    # -------------------------------------------------------------------------
    # Fig 4: Optical Channel Gain Decomposition at Changed Coordinates
    # -------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    vlc_cfg = VLCConfig()
    ris_cfg = OpticalRISConfig()
    bob = np.array(CHANGED_SCENARIO['bob'])
    eve = np.array(CHANGED_SCENARIO['eve'])
    ch = VLCChannel(vlc_cfg)
    ris_model = OpticalRIS(vlc_cfg, ris_cfg, bob, eve)
    h_AB_dir_val, h_AE_dir_val, _, _ = ch.get_all_channel_gains(bob, eve)

    q_indices = [0, 1, 2, 3, 4]
    q_names = ['0: Off', '1: Aim Bob', '2: Aim Eve', '3: Split', '4: Neutral']
    h_AB_dir, h_AB_ref, h_AE_dir, h_AE_ref = [], [], [], []

    for q in q_indices:
        h_AB_r, h_AE_r, _, _ = ris_model.get_reflected_gains(q)
        h_AB_dir.append(h_AB_dir_val)
        h_AB_ref.append(h_AB_r)
        h_AE_dir.append(h_AE_dir_val)
        h_AE_ref.append(h_AE_r)

    x = np.arange(len(q_indices))
    width = 0.35

    # Bob gains
    ax1.bar(x, np.array(h_AB_dir) * 1e5, width, label='Direct LOS (h_AB^dir)', color='#3b82f6')
    ax1.bar(x, np.array(h_AB_ref) * 1e5, width, bottom=np.array(h_AB_dir) * 1e5,
            label='Reflected (h_AB^ref)', color='#10b981')
    ax1.set_title("Bob Channel Gains (10^-5 A/W)", fontsize=10.5, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(q_names, rotation=25, fontsize=8.5)
    ax1.set_ylabel("Gain (x 10^-5 A/W)", fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.45)
    ax1.legend(fontsize=8.5)

    # Eve gains
    ax2.bar(x, np.array(h_AE_dir) * 1e5, width, label='Direct LOS (h_AE^dir)', color='#f59e0b')
    ax2.bar(x, np.array(h_AE_ref) * 1e5, width, bottom=np.array(h_AE_dir) * 1e5,
            label='Reflected (h_AE^ref)', color='#ec4899')
    ax2.set_title("Eve Channel Gains (10^-5 A/W)", fontsize=10.5, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(q_names, rotation=25, fontsize=8.5)
    ax2.set_ylabel("Gain (x 10^-5 A/W)", fontsize=10)
    ax2.grid(axis='y', linestyle='--', alpha=0.45)
    ax2.legend(fontsize=8.5)

    fig.suptitle(
        f"Figure 4: Direct vs Reflected Optical Channel Decomposition\n"
        f"Scenario: Changed Positions (Bob=[2.0, 3.0, 0.85]m, Eve=[3.5, 1.5, 0.85]m)",
        fontsize=11.5, fontweight='bold'
    )
    save_plot(fig, "fig4_changed_optical_breakdown")

    # -------------------------------------------------------------------------
    # Fig 5: Cross-Scenario Spatial Comparison (Nominal vs Changed vs Near-Bob)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    # Load historical nominal frozen eval means
    nom_summary_p = ROOT / "output_figures" / "ris" / "final_evaluation" / "ris_study_summary.json"
    with open(nom_summary_p, 'r', encoding='utf-8') as f:
        nom_summary = json.load(f)
    nom_means = [
        nom_summary['aggregates'][0]['evaluation']['secrecy_rate']['mean'],
        nom_summary['aggregates'][1]['evaluation']['secrecy_rate']['mean'],
        nom_summary['aggregates'][2]['evaluation']['secrecy_rate']['mean']
    ]

    scenarios_list = [
        ("Nominal (d_BE = 2.28m)", nom_means),
        ("Changed Positions (d_BE = 2.12m)", eval_means),
        ("Near-Bob (d_BE = 0.07m)", [0.0, 0.0, 0.0])
    ]

    x_scen = np.arange(len(scenarios_list))
    bar_w = 0.25
    for s_idx, scheme in enumerate(schemes):
        vals = [scen[1][s_idx] for scen in scenarios_list]
        ax.bar(x_scen + (s_idx - 1) * bar_w, vals, width=bar_w,
               color=SCHEME_COLORS[scheme], label=SCHEME_LABELS[scheme],
               edgecolor='black', linewidth=1.0, alpha=0.88)

    ax.set_xticks(x_scen)
    ax.set_xticklabels([s[0] for s in scenarios_list], fontsize=10, fontweight='bold')
    ax.set_ylabel("Frozen Evaluation Secrecy Rate (bps/Hz)", fontsize=10.5)
    ax.set_title(
        "Figure 5: Cross-Scenario Spatial Comparison of Achievable Secrecy Rate\n"
        "Nominal vs Changed Positions vs Near-Bob Boundary Condition",
        fontsize=11, fontweight='bold', pad=10
    )
    ax.grid(axis='y', linestyle='--', alpha=0.45)
    ax.legend(loc='upper right', fontsize=9.5)
    save_plot(fig, "fig5_cross_scenario_comparison")

    print("\nAll scenario-labeled figures generated in both PNG and vector PDF formats.")


def main():
    data_path = OUTPUT_DIR / "ris_study_data.json"
    if data_path.exists():
        print(f"Loading existing completed study data from {data_path}...")
        with open(data_path, 'r', encoding='utf-8') as f:
            record = json.load(f)
    else:
        record = run_experiment(slots=1000, eval_slots=500, seeds=(42, 43, 44))
    generate_scenario_labeled_figures(record)


if __name__ == "__main__":
    main()

"""
Simulation Script for Figure 6:
Interactive learning process over 2000 time slots comparing:
1. Independently valid global bounds
2. Proposed DRL-FJ (Algorithm 2: CNN + DND Memory)
3. Proposed RL-FJ (Algorithm 1: Q-learning)
4. Restricted search (custom)
5. Scaled ZF (custom)
6. Regularized BF (custom)

Produces:
- Fig. 6(a): Secrecy rate of the VLC system
- Fig. 6(b): Bit Error Rate (BER) of legitimate user Bob (log scale)
- Fig. 6(c): Utility of the VLC system
"""

import os
import sys
import argparse

# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import numpy as np
import matplotlib.pyplot as plt

from vlc.config import VLCConfig
from vlc.environment import VLCEnvironment
from vlc.rl_fj import RLFJAgent
from vlc.drl_fj import DRLFJAgent
from vlc.benchmarks import BenchmarkRunner
from vlc.experiments import metadata, save_record, diagnose_operating_point, tag_figure
import torch


def smooth_curve(arr: np.ndarray, window: int = 15) -> np.ndarray:
    """Computes a causal running exponential moving average for clean visualization."""
    res = np.zeros_like(arr)
    alpha = 2.0 / (window + 1.0)
    if len(arr) == 0:
        return res
    res[0] = arr[0]
    for i in range(1, len(arr)):
        res[i] = alpha * arr[i] + (1.0 - alpha) * res[i - 1]
    return res


def simulate_fig6(
    num_slots: int = 2000,
    save_dir: str = "output_figures",
    seed: int = 42,
    show_plots: bool = False,
    config=None,
):
    os.makedirs(save_dir, exist_ok=True)
    np.random.seed(seed)

    config = config or VLCConfig(seed=seed)
    torch.set_num_threads(1)
    torch.manual_seed(config.seed)
    if num_slots < 1:
        raise ValueError("num_slots must be positive")
    print(f"Running Figure 6 Convergence Simulation over {num_slots} time slots...")

    # Initialize environment
    env = VLCEnvironment(config=config)

    # 1. Theoretical Upper Bound
    print("Computing Global bounds...")
    runner = BenchmarkRunner(env, config)
    res_theo = runner.run_theoretical_bound(num_slots=num_slots)

    # 2. Benchmarks: Regularized BF (custom), Scaled ZF (custom), Restricted search (custom)
    print("Computing Regularized BF (custom) baseline...")
    res_robust = runner.run_regularized(num_slots=num_slots)

    print("Computing Scaled ZF (custom) baseline...")
    res_sbj = runner.run_scaled_zf(num_slots=num_slots)

    print("Computing Restricted search (custom) baseline...")
    res_drl_vb = runner.run_restricted_search(num_slots=num_slots)

    # 3. Proposed RL-FJ (Algorithm 1)
    print("Training Proposed RL-FJ Agent (Q-learning)...")
    env_rl = VLCEnvironment(config=config)
    rl_agent = RLFJAgent(env_rl, config)
    res_rl = rl_agent.train(num_slots=num_slots)

    cs_rl = smooth_curve(np.asarray(res_rl["secrecy_rate"], dtype=np.float64), window=50)
    pe_rl = smooth_curve(np.asarray(res_rl["ber"], dtype=np.float64), window=50)
    u_rl = smooth_curve(np.asarray(res_rl["utility"], dtype=np.float64), window=50)

    # 4. Proposed DRL-FJ (Algorithm 2: CNN + DND Memory)
    print("Training Proposed DRL-FJ Agent (CNN + DND)...")
    env_drl = VLCEnvironment(config=config)
    drl_agent = DRLFJAgent(env_drl, config)
    res_drl = drl_agent.train(num_slots=num_slots)

    cs_drl = smooth_curve(np.asarray(res_drl["secrecy_rate"], dtype=np.float64), window=50)
    pe_drl = smooth_curve(np.asarray(res_drl["ber"], dtype=np.float64), window=50)
    u_drl = smooth_curve(np.asarray(res_drl["utility"], dtype=np.float64), window=50)

    save_record(os.path.join(save_dir, "fig6_data.json"), {
        "metadata": metadata(config, slots=num_slots, smoothing="EMA50; raw data retained", channel_model="stationary Lambertian LOS"),
        "histories": {"rl": res_rl, "drl": res_drl, "global_bounds": res_theo,
                      "custom_restricted": res_drl_vb, "custom_regularized": res_robust, "custom_scaled_zf": res_sbj},
        "actions": {"rl": rl_agent.action_history, "drl": drl_agent.action_history},
        "operating_point": diagnose_operating_point(env)})
    slots = np.arange(1, num_slots + 1)

    # Smooth benchmarks for clear visualization
    cs_vb = smooth_curve(np.asarray(res_drl_vb["secrecy_rate"], dtype=np.float64), window=50)
    pe_vb = smooth_curve(np.asarray(res_drl_vb["ber"], dtype=np.float64), window=50)
    u_vb = smooth_curve(np.asarray(res_drl_vb["utility"], dtype=np.float64), window=50)

    # Line formatting matching the paper
    styles = {
        "Global bounds": {"color": "magenta", "ls": "--", "lw": 1.8},
        "Proposed DRL-FJ": {"color": "red", "ls": "-", "lw": 1.5, "marker": "s", "ms": 4, "markevery": max(1, num_slots // 25)},
        "Proposed RL-FJ": {"color": "blue", "ls": "-", "lw": 1.5, "marker": "^", "ms": 4, "markevery": max(1, num_slots // 25)},
        "Restricted search (custom)": {"color": "cyan", "ls": "-", "lw": 1.2},
        "Scaled ZF (custom)": {"color": "green", "ls": "-", "lw": 1.2},
        "Regularized BF (custom)": {"color": "black", "ls": "-", "lw": 1.0},
    }

    cs_all = np.concatenate([res_theo["secrecy_rate"], cs_drl, cs_rl, cs_vb, res_sbj["secrecy_rate"], res_robust["secrecy_rate"]])
    cs_ymin = max(0.0, float(np.min(cs_all)) - 0.15)
    cs_ymax = max(cs_ymin + 0.5, float(np.max(cs_all)) + 0.25)

    # ---------------- Fig 6(a): Secrecy Rate ----------------
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(slots, res_theo["secrecy_rate"], **styles["Global bounds"], label="Global bounds")
    plt.plot(slots, cs_drl, **styles["Proposed DRL-FJ"], label="Proposed DRL-FJ")
    plt.plot(slots, cs_rl, **styles["Proposed RL-FJ"], label="Proposed RL-FJ")
    plt.plot(slots, cs_vb, **styles["Restricted search (custom)"], label="Restricted search (custom)")
    plt.plot(slots, res_sbj["secrecy_rate"], **styles["Scaled ZF (custom)"], label="Scaled ZF (custom)")
    plt.plot(slots, res_robust["secrecy_rate"], **styles["Regularized BF (custom)"], label="Regularized BF (custom)")

    plt.xlabel("Time slot", fontsize=11)
    plt.ylabel("Secrecy rate (bps/Hz)", fontsize=11)
    plt.title("(a) Secrecy rate of the VLC system", fontsize=12)
    plt.xlim(0, num_slots)
    plt.ylim(cs_ymin, cs_ymax)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=8, framealpha=0.9)
    plt.tight_layout()
    path_6a = os.path.join(save_dir, "fig6a_secrecy_rate.png")
    tag_figure(config)
    plt.savefig(path_6a)
    print(f"Saved: {path_6a}")
    if show_plots:
        plt.show()
    plt.close()

    # Guard zeros solely for matplotlib log-axis rendering
    ber_floor = 1e-12
    pe_theo_plot = np.maximum(np.asarray(res_theo["ber"], dtype=np.float64), ber_floor)
    pe_drl_plot = np.maximum(pe_drl, ber_floor)
    pe_rl_plot = np.maximum(pe_rl, ber_floor)
    pe_vb_plot = np.maximum(pe_vb, ber_floor)
    pe_sbj_plot = np.maximum(np.asarray(res_sbj["ber"], dtype=np.float64), ber_floor)
    pe_rob_plot = np.maximum(np.asarray(res_robust["ber"], dtype=np.float64), ber_floor)

    # ---------------- Fig 6(b): BER of Bob ----------------
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(slots, pe_theo_plot, **styles["Global bounds"], label="Global bounds")
    plt.plot(slots, pe_drl_plot, **styles["Proposed DRL-FJ"], label="Proposed DRL-FJ")
    plt.plot(slots, pe_rl_plot, **styles["Proposed RL-FJ"], label="Proposed RL-FJ")
    plt.plot(slots, pe_vb_plot, **styles["Restricted search (custom)"], label="Restricted search (custom)")
    plt.plot(slots, pe_sbj_plot, **styles["Scaled ZF (custom)"], label="Scaled ZF (custom)")
    plt.plot(slots, pe_rob_plot, **styles["Regularized BF (custom)"], label="Regularized BF (custom)")

    plt.yscale("log")
    plt.xlabel("Time slot", fontsize=11)
    plt.ylabel("BER", fontsize=11)
    plt.title("(b) BER of the legitimate user Bob", fontsize=12)
    plt.xlim(0, num_slots)
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend(loc="lower left", fontsize=8, framealpha=0.9)
    plt.tight_layout()
    path_6b = os.path.join(save_dir, "fig6b_ber.png")
    tag_figure(config)
    plt.savefig(path_6b)
    print(f"Saved: {path_6b}")
    if show_plots:
        plt.show()
    plt.close()

    u_all = np.concatenate([res_theo["utility"], u_drl, u_rl, u_vb, res_sbj["utility"], res_robust["utility"]])
    u_ymin = float(np.min(u_all)) - 0.25
    u_ymax = max(u_ymin + 0.5, float(np.max(u_all)) + 0.25)

    # ---------------- Fig 6(c): Utility ----------------
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(slots, res_theo["utility"], **styles["Global bounds"], label="Global bounds")
    plt.plot(slots, u_drl, **styles["Proposed DRL-FJ"], label="Proposed DRL-FJ")
    plt.plot(slots, u_rl, **styles["Proposed RL-FJ"], label="Proposed RL-FJ")
    plt.plot(slots, u_vb, **styles["Restricted search (custom)"], label="Restricted search (custom)")
    plt.plot(slots, res_sbj["utility"], **styles["Scaled ZF (custom)"], label="Scaled ZF (custom)")
    plt.plot(slots, res_robust["utility"], **styles["Regularized BF (custom)"], label="Regularized BF (custom)")

    plt.xlabel("Time slot", fontsize=11)
    plt.ylabel("Utility", fontsize=11)
    plt.title("(c) Utility of the VLC system", fontsize=12)
    plt.xlim(0, num_slots)
    plt.ylim(u_ymin, u_ymax)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="lower right", fontsize=8, framealpha=0.9)
    plt.tight_layout()
    path_6c = os.path.join(save_dir, "fig6c_utility.png")
    tag_figure(config)
    plt.savefig(path_6c)
    print(f"Saved: {path_6c}")
    if show_plots:
        plt.show()
    plt.close()

    # ---------------- Combined Figure 6 (3 Panels) ----------------
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 12), dpi=300)

    # (a)
    ax1.plot(slots, res_theo["secrecy_rate"], **styles["Global bounds"], label="Global bounds")
    ax1.plot(slots, cs_drl, **styles["Proposed DRL-FJ"], label="Proposed DRL-FJ")
    ax1.plot(slots, cs_rl, **styles["Proposed RL-FJ"], label="Proposed RL-FJ")
    ax1.plot(slots, cs_vb, **styles["Restricted search (custom)"], label="Restricted search (custom)")
    ax1.plot(slots, res_sbj["secrecy_rate"], **styles["Scaled ZF (custom)"], label="Scaled ZF (custom)")
    ax1.plot(slots, res_robust["secrecy_rate"], **styles["Regularized BF (custom)"], label="Regularized BF (custom)")
    ax1.set_xlabel("Time slot")
    ax1.set_ylabel("Secrecy rate (bps/Hz)")
    ax1.set_title("(a) Secrecy rate of the VLC system")
    ax1.set_xlim(0, num_slots)
    ax1.set_ylim(cs_ymin, cs_ymax)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="lower right", fontsize=7.5, framealpha=0.9)

    # (b)
    ax2.plot(slots, pe_theo_plot, **styles["Global bounds"], label="Global bounds")
    ax2.plot(slots, pe_drl_plot, **styles["Proposed DRL-FJ"], label="Proposed DRL-FJ")
    ax2.plot(slots, pe_rl_plot, **styles["Proposed RL-FJ"], label="Proposed RL-FJ")
    ax2.plot(slots, pe_vb_plot, **styles["Restricted search (custom)"], label="Restricted search (custom)")
    ax2.plot(slots, pe_sbj_plot, **styles["Scaled ZF (custom)"], label="Scaled ZF (custom)")
    ax2.plot(slots, pe_rob_plot, **styles["Regularized BF (custom)"], label="Regularized BF (custom)")
    ax2.set_yscale("log")
    ax2.set_xlabel("Time slot")
    ax2.set_ylabel("BER")
    ax2.set_title("(b) BER of the legitimate user Bob")
    ax2.set_xlim(0, num_slots)
    ax2.grid(True, which="both", linestyle=":", alpha=0.6)
    ax2.legend(loc="lower left", fontsize=7.5, framealpha=0.9)

    # (c)
    ax3.plot(slots, res_theo["utility"], **styles["Global bounds"], label="Global bounds")
    ax3.plot(slots, u_drl, **styles["Proposed DRL-FJ"], label="Proposed DRL-FJ")
    ax3.plot(slots, u_rl, **styles["Proposed RL-FJ"], label="Proposed RL-FJ")
    ax3.plot(slots, u_vb, **styles["Restricted search (custom)"], label="Restricted search (custom)")
    ax3.plot(slots, res_sbj["utility"], **styles["Scaled ZF (custom)"], label="Scaled ZF (custom)")
    ax3.plot(slots, res_robust["utility"], **styles["Regularized BF (custom)"], label="Regularized BF (custom)")
    ax3.set_xlabel("Time slot")
    ax3.set_ylabel("Utility")
    ax3.set_title("(c) Utility of the VLC system")
    ax3.set_xlim(0, num_slots)
    ax3.set_ylim(u_ymin, u_ymax)
    ax3.grid(True, linestyle=":", alpha=0.6)
    ax3.legend(loc="lower right", fontsize=7.5, framealpha=0.9)

    plt.tight_layout()
    path_combined = os.path.join(save_dir, "fig6_performance_curves.png")
    tag_figure(config)
    plt.savefig(path_combined)
    print(f"Saved: {path_combined}")
    if show_plots:
        plt.show()
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate Figure 6 (Learning Convergence)")
    parser.add_argument("--slots", type=int, default=2000, help="Number of time slots (default 2000)")
    parser.add_argument("--save_dir", type=str, default="output_figures", help="Directory to save figures")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--show", action="store_true", help="Display interactive plots")
    args = parser.parse_args()

    simulate_fig6(num_slots=args.slots, save_dir=args.save_dir, seed=args.seed, show_plots=args.show)

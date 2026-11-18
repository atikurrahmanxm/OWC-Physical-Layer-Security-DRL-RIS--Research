"""
Simulation Script for Figure 7:
Performance of proposed intelligent friendly jamming beamforming schemes
with respect to SNR (dB) in range [4, 20] dB.

Figure 7(a): Secrecy rate of the VLC system vs SNR
Figure 7(b): BER of the legitimate receiver Bob vs SNR (log scale)
Figure 7(c): Utility of the VLC system vs SNR
"""

import os
import sys
import argparse
from typing import Optional, List

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


def simulate_fig7(
    snr_points: Optional = None,
    num_slots: int = 2000,
    save_dir: str = "output_figures",
    show_plots: bool = False,
    config=None,
    seed: int = 42,
):
    os.makedirs(save_dir, exist_ok=True)
    if snr_points is None:
        snr_points = np.arange(4, 22, 2)  # [4, 6, 8, 10, 12, 14, 16, 18, 20] dB

    config = config or VLCConfig(seed=seed)
    torch.set_num_threads(1)
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    if num_slots < 1 or len(snr_points) == 0:
        raise ValueError("num_slots and SNR points must be nonempty")
    records = []
    print(f"Running Figure 7 SNR Sweep across {[int(x) for x in snr_points]} dB (avg over {num_slots} slots)...")

    # Data arrays for each scheme
    drl_cs, drl_pe, drl_u = [], [], []
    rl_cs, rl_pe, rl_u = [], [], []
    sbj_cs, sbj_pe, sbj_u = [], [], []
    rob_cs, rob_pe, rob_u = [], [], []

    for snr_db in snr_points:
        print(f"Training actual agents at {snr_db:g} dB ({config.snr_definition})...", flush=True)
        # Convert the explicitly selected SNR convention to noise variance.
        env_base = VLCEnvironment(config=config)
        h_AB = env_base.h_AB
        sigma_sq = config.noise_variance_from_snr(h_AB, float(snr_db))

        # 1. Proposed DRL-FJ (Algorithm 2): average over num_slots
        env_drl = VLCEnvironment(config=config, sigma_B_sq=sigma_sq)
        drl_agent = DRLFJAgent(env_drl, config)
        hist_drl = drl_agent.train(num_slots=num_slots)
        drl_cs.append(float(np.mean(hist_drl["secrecy_rate"])))
        drl_pe.append(float(np.mean(hist_drl["ber"])))
        drl_u.append(float(np.mean(hist_drl["utility"])))

        # 2. Proposed RL-FJ (Algorithm 1): average over num_slots
        env_rl = VLCEnvironment(config=config, sigma_B_sq=sigma_sq)
        rl_agent = RLFJAgent(env_rl, config)
        hist_rl = rl_agent.train(num_slots=num_slots)
        rl_cs.append(float(np.mean(hist_rl["secrecy_rate"])))
        rl_pe.append(float(np.mean(hist_rl["ber"])))
        rl_u.append(float(np.mean(hist_rl["utility"])))

        # 3 & 4. Benchmarks (Scaled ZF (custom) and Robust Beamforming) evaluated physically
        runner = BenchmarkRunner(VLCEnvironment(config=config, sigma_B_sq=sigma_sq), config)
        hist_sbj = runner.run_scaled_zf(num_slots=num_slots)
        hist_rob = runner.run_regularized(num_slots=num_slots)

        sbj_cs.append(float(np.mean(hist_sbj["secrecy_rate"])))
        sbj_pe.append(float(np.mean(hist_sbj["ber"])))
        sbj_u.append(float(np.mean(hist_sbj["utility"])))

        rob_cs.append(float(np.mean(hist_rob["secrecy_rate"])))
        rob_pe.append(float(np.mean(hist_rob["ber"])))
        rob_u.append(float(np.mean(hist_rob["utility"])))

        records.append({"snr_db": float(snr_db), "sigma_B_sq": sigma_sq,
                        "histories": {"rl": hist_rl, "drl": hist_drl,
                                      "custom_scaled_zf": hist_sbj, "custom_regularized": hist_rob},
                        "actions": {"rl": rl_agent.action_history, "drl": drl_agent.action_history},
                        "operating_point": diagnose_operating_point(env_drl)})

    save_record(os.path.join(save_dir, "fig7_data.json"), {
        "metadata": metadata(config, slots=num_slots, aggregation="mean of every slot, including exploration"), "points": records})
    cs_all = np.concatenate([drl_cs, rl_cs, sbj_cs, rob_cs])
    u_all = np.concatenate([drl_u, rl_u, sbj_u, rob_u])
    cs_ymin = max(0.0, float(np.min(cs_all)) - 0.15)
    cs_ymax = max(cs_ymin + 0.5, float(np.max(cs_all)) + 0.25)
    u_ymin = float(np.min(u_all)) - 0.25
    u_ymax = max(u_ymin + 0.5, float(np.max(u_all)) + 0.25)

    ber_floor = 1e-12
    drl_pe_p = np.maximum(drl_pe, ber_floor)
    rl_pe_p = np.maximum(rl_pe, ber_floor)
    sbj_pe_p = np.maximum(sbj_pe, ber_floor)
    rob_pe_p = np.maximum(rob_pe, ber_floor)

    # Styling identical to Fig. 7
    style_drl = {"color": "red", "ls": "-", "marker": "s", "label": "Proposed DRL-FJ"}
    style_rl = {"color": "blue", "ls": "-", "marker": "^", "label": "Proposed RL-FJ"}
    style_sbj = {"color": "green", "ls": "-", "marker": "o", "label": "Scaled ZF (custom)"}
    style_rob = {"color": "black", "ls": "-", "marker": "x", "label": "Regularized BF (custom)"}

    # ---------------- Fig 7(a): Secrecy Rate vs SNR ----------------
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(snr_points, drl_cs, **style_drl)
    plt.plot(snr_points, rl_cs, **style_rl)
    plt.plot(snr_points, sbj_cs, **style_sbj)
    plt.plot(snr_points, rob_cs, **style_rob)
    plt.xlabel("SNR (dB)", fontsize=11)
    plt.ylabel("Secrecy rate (bps/Hz)", fontsize=11)
    plt.title("(a) Secrecy rate of the VLC system", fontsize=12)
    plt.xticks(snr_points)
    plt.xlim(4, 20)
    plt.ylim(cs_ymin, cs_ymax)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper left", fontsize=8.5, framealpha=0.9)
    plt.tight_layout()
    path_7a = os.path.join(save_dir, "fig7a_secrecy_rate_snr.png")
    tag_figure(config)
    plt.savefig(path_7a)
    print(f"Saved: {path_7a}")
    if show_plots:
        plt.show()
    plt.close()

    # ---------------- Fig 7(b): BER vs SNR ----------------
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(snr_points, drl_pe_p, **style_drl)
    plt.plot(snr_points, rl_pe_p, **style_rl)
    plt.plot(snr_points, sbj_pe_p, **style_sbj)
    plt.plot(snr_points, rob_pe_p, **style_rob)
    plt.yscale("log")
    plt.xlabel("SNR (dB)", fontsize=11)
    plt.ylabel("BER", fontsize=11)
    plt.title("(b) BER of the legitimate receiver Bob", fontsize=12)
    plt.xticks(snr_points)
    plt.xlim(4, 20)
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend(loc="lower left", fontsize=8.5, framealpha=0.9)
    plt.tight_layout()
    path_7b = os.path.join(save_dir, "fig7b_ber_snr.png")
    tag_figure(config)
    plt.savefig(path_7b)
    print(f"Saved: {path_7b}")
    if show_plots:
        plt.show()
    plt.close()

    # ---------------- Fig 7(c): Utility vs SNR ----------------
    plt.figure(figsize=(7, 5), dpi=300)
    plt.plot(snr_points, drl_u, **style_drl)
    plt.plot(snr_points, rl_u, **style_rl)
    plt.plot(snr_points, sbj_u, **style_sbj)
    plt.plot(snr_points, rob_u, **style_rob)
    plt.xlabel("SNR (dB)", fontsize=11)
    plt.ylabel("Utility", fontsize=11)
    plt.title("(c) Utility of the VLC system", fontsize=12)
    plt.xticks(snr_points)
    plt.xlim(4, 20)
    plt.ylim(u_ymin, u_ymax)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(loc="upper left", fontsize=8.5, framealpha=0.9)
    plt.tight_layout()
    path_7c = os.path.join(save_dir, "fig7c_utility_snr.png")
    tag_figure(config)
    plt.savefig(path_7c)
    print(f"Saved: {path_7c}")
    if show_plots:
        plt.show()
    plt.close()

    # ---------------- Combined Figure 7 (3 Panels) ----------------
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7.5, 12), dpi=300)

    # (a)
    ax1.plot(snr_points, drl_cs, **style_drl)
    ax1.plot(snr_points, rl_cs, **style_rl)
    ax1.plot(snr_points, sbj_cs, **style_sbj)
    ax1.plot(snr_points, rob_cs, **style_rob)
    ax1.set_xlabel("SNR (dB)")
    ax1.set_ylabel("Secrecy rate (bps/Hz)")
    ax1.set_title("(a) Secrecy rate of the VLC system")
    ax1.set_xticks(snr_points)
    ax1.set_xlim(4, 20)
    ax1.set_ylim(cs_ymin, cs_ymax)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(loc="upper left", fontsize=8, framealpha=0.9)

    # (b)
    ax2.plot(snr_points, drl_pe_p, **style_drl)
    ax2.plot(snr_points, rl_pe_p, **style_rl)
    ax2.plot(snr_points, sbj_pe_p, **style_sbj)
    ax2.plot(snr_points, rob_pe_p, **style_rob)
    ax2.set_yscale("log")
    ax2.set_xlabel("SNR (dB)")
    ax2.set_ylabel("BER")
    ax2.set_title("(b) BER of the legitimate receiver Bob")
    ax2.set_xticks(snr_points)
    ax2.set_xlim(4, 20)
    ax2.grid(True, which="both", linestyle=":", alpha=0.6)
    ax2.legend(loc="lower left", fontsize=8, framealpha=0.9)

    # (c)
    ax3.plot(snr_points, drl_u, **style_drl)
    ax3.plot(snr_points, rl_u, **style_rl)
    ax3.plot(snr_points, sbj_u, **style_sbj)
    ax3.plot(snr_points, rob_u, **style_rob)
    ax3.set_xlabel("SNR (dB)")
    ax3.set_ylabel("Utility")
    ax3.set_title("(c) Utility of the VLC system")
    ax3.set_xticks(snr_points)
    ax3.set_xlim(4, 20)
    ax3.set_ylim(u_ymin, u_ymax)
    ax3.grid(True, linestyle=":", alpha=0.6)
    ax3.legend(loc="upper left", fontsize=8, framealpha=0.9)

    plt.tight_layout()
    path_combined = os.path.join(save_dir, "fig7_snr_performance.png")
    tag_figure(config)
    plt.savefig(path_combined)
    print(f"Saved: {path_combined}")
    if show_plots:
        plt.show()
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate Figure 7 (Performance vs SNR)")
    parser.add_argument("--save_dir", type=str, default="output_figures", help="Directory to save figures")
    parser.add_argument("--show", action="store_true", help="Display interactive plots")
    args = parser.parse_args()

    simulate_fig7(save_dir=args.save_dir, show_plots=args.show)

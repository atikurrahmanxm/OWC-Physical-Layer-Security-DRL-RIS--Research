"""
IEEE Publication-Grade Visualization Module.
Generates publication-quality figures:
- fig1_convergence_curves.png & .pdf (Secrecy Rate, BER, Utility, SEE vs Time Slots)
- fig2_spatial_secrecy_heatmaps.png & .pdf (2D Spatial comparison of DRL-FJ vs DRL-RIS-FJ)
- fig3_snr_performance.png & .pdf (Metrics vs Transmit SNR 4-20 dB)
- fig4_ris_elements_scaling.png & .pdf (Impact of RIS array size)
- fig5_blockage_resilience.png & .pdf (Resilience under direct LoS blockage)
- fig6_3d_indoor_setup.png & .pdf (3D physical spatial geometry of room)
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from src.config import Config

FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "figures")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Set IEEE-style plotting parameters
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 12
plt.rcParams['grid.alpha'] = 0.35
plt.rcParams['grid.linestyle'] = '--'

def smooth(y, box_pts=25):
    """Moving average filter for smoothing learning curves."""
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    # Edge fix
    y_smooth[:box_pts] = y[:box_pts]
    y_smooth[-box_pts:] = y[-box_pts:]
    return y_smooth

class Visualizer:
    def __init__(self):
        self.cfg = Config()

    def plot_fig1_convergence(self):
        filepath = os.path.join(RESULTS_DIR, "exp1_convergence.json")
        if not os.path.exists(filepath):
            print(f"[Warning] {filepath} not found. Skipping Fig 1.")
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        slots = np.array(data["time_slots"])
        schemes = [
            ("No-Jammer", "tab:gray", ":", 1.5),
            ("ZF-FJ", "tab:blue", "--", 1.8),
            ("RL-FJ", "tab:orange", "-.", 1.8),
            ("DRL-FJ", "tab:green", "-", 2.0),
            ("RL-RIS-FJ", "tab:purple", "-.", 2.0),
            ("DRL-RIS-FJ", "crimson", "-", 2.4),
        ]

        fig, axes = plt.subplots(2, 2, figsize=(12, 9))
        fig.suptitle("Convergence and Learning Dynamics in Nonstationary Indoor VLC Environment", fontsize=13, fontweight='bold')

        # Subplot (a): Secrecy Rate
        ax = axes[0, 0]
        for name, color, ls, lw in schemes:
            raw = np.array(data[name]["secrecy_rate"])
            sm = smooth(raw, box_pts=35)
            ax.plot(slots, sm, label=name, color=color, linestyle=ls, linewidth=lw)
        ax.set_xlabel("Time Slot (k)")
        ax.set_ylabel("Achievable Secrecy Rate (bps/Hz)")
        ax.set_title("(a) Achievable Secrecy Rate vs. Time Slot")
        ax.grid(True)
        ax.legend(loc="lower right", framealpha=0.9)

        # Subplot (b): BER
        ax = axes[0, 1]
        for name, color, ls, lw in schemes:
            raw = np.array(data[name]["ber"])
            sm = smooth(raw, box_pts=35)
            ax.semilogy(slots, sm, label=name, color=color, linestyle=ls, linewidth=lw)
        ax.set_xlabel("Time Slot (k)")
        ax.set_ylabel("Bit Error Rate (BER) of Bob")
        ax.set_title("(b) Bob's BER (4-PAM) vs. Time Slot")
        ax.grid(True, which="both")
        ax.set_ylim(1e-4, 1.0)
        ax.legend(loc="upper right", framealpha=0.9)

        # Subplot (c): System Utility
        ax = axes[1, 0]
        for name, color, ls, lw in schemes:
            raw = np.array(data[name]["utility"])
            sm = smooth(raw, box_pts=35)
            ax.plot(slots, sm, label=name, color=color, linestyle=ls, linewidth=lw)
        ax.set_xlabel("Time Slot (k)")
        ax.set_ylabel("System Utility u(k)")
        ax.set_title("(c) System Utility vs. Time Slot")
        ax.grid(True)
        ax.legend(loc="lower right", framealpha=0.9)

        # Subplot (d): Secrecy Energy Efficiency (SEE)
        ax = axes[1, 1]
        for name, color, ls, lw in schemes:
            raw = np.array(data[name]["see"])
            sm = smooth(raw, box_pts=35)
            ax.plot(slots, sm, label=name, color=color, linestyle=ls, linewidth=lw)
        ax.set_xlabel("Time Slot (k)")
        ax.set_ylabel("Secrecy Energy Efficiency (bps/Hz/W)")
        ax.set_title("(d) Secrecy Energy Efficiency (SEE) vs. Time Slot")
        ax.grid(True)
        ax.legend(loc="lower right", framealpha=0.9)

        plt.tight_layout()
        out_png = os.path.join(FIGURES_DIR, "fig1_convergence_curves.png")
        out_pdf = os.path.join(FIGURES_DIR, "fig1_convergence_curves.pdf")
        plt.savefig(out_png, dpi=300)
        plt.savefig(out_pdf)
        plt.close()
        print(f"[Figure 1] Generated: {out_png}")

    def plot_fig2_spatial(self):
        filepath = os.path.join(RESULTS_DIR, "exp2_spatial.json")
        if not os.path.exists(filepath):
            print(f"[Warning] {filepath} not found. Skipping Fig 2.")
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        x_vals = np.array(data["x_vals"])
        y_vals = np.array(data["y_vals"])
        bob_pos = data["bob_pos"]
        sr_no_ris = np.array(data["sr_no_ris"])
        sr_ris = np.array(data["sr_ris"])

        X, Y = np.meshgrid(x_vals, y_vals)
        vmin = 0.0
        vmax = max(np.max(sr_no_ris), np.max(sr_ris))

        fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
        fig.suptitle("Spatial Secrecy Rate Distribution Across Room Plane (z = 0.85 m)", fontsize=13, fontweight='bold')

        # Map 1: Without RIS (Base Paper DRL-FJ)
        ax = axes[0]
        c1 = ax.contourf(X, Y, sr_no_ris, levels=30, cmap='viridis', vmin=vmin, vmax=vmax)
        ax.scatter([bob_pos[0]], [bob_pos[1]], color='red', marker='*', s=200, edgecolors='black', label='Bob Terminal')
        ax.set_title("(a) Without RIS (DRL-FJ, Base Paper)")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.legend(loc="upper left")
        fig.colorbar(c1, ax=ax, label="Secrecy Rate (bps/Hz)")

        # Map 2: With RIS (Proposed DRL-RIS-FJ)
        ax = axes[1]
        c2 = ax.contourf(X, Y, sr_ris, levels=30, cmap='viridis', vmin=vmin, vmax=vmax)
        ax.scatter([bob_pos[0]], [bob_pos[1]], color='red', marker='*', s=200, edgecolors='black', label='Bob Terminal')
        # Mark RIS position on top wall
        ax.plot([2.3, 2.7], [4.5, 4.5], color='magenta', linewidth=4, label='Wall-Mounted RIS')
        ax.set_title("(b) With Optical RIS (Proposed DRL-RIS-FJ)")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.legend(loc="upper left")
        fig.colorbar(c2, ax=ax, label="Secrecy Rate (bps/Hz)")

        plt.tight_layout()
        out_png = os.path.join(FIGURES_DIR, "fig2_spatial_secrecy_heatmaps.png")
        out_pdf = os.path.join(FIGURES_DIR, "fig2_spatial_secrecy_heatmaps.pdf")
        plt.savefig(out_png, dpi=300)
        plt.savefig(out_pdf)
        plt.close()
        print(f"[Figure 2] Generated: {out_png}")

    def plot_fig3_snr(self):
        filepath = os.path.join(RESULTS_DIR, "exp3_snr.json")
        if not os.path.exists(filepath):
            print(f"[Warning] {filepath} not found. Skipping Fig 3.")
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        snr = data["snr_db"]
        schemes = [
            ("No-Jammer", "tab:gray", ":", "o"),
            ("ZF-FJ", "tab:blue", "--", "s"),
            ("DRL-FJ", "tab:green", "-.", "^"),
            ("DRL-RIS-FJ", "crimson", "-", "D"),
        ]

        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
        fig.suptitle("Performance Evaluation across Transmit Optical SNR Range (4 dB to 20 dB)", fontsize=13, fontweight='bold')

        # (a) Secrecy Rate
        ax = axes[0]
        for name, color, ls, mk in schemes:
            ax.plot(snr, data[name]["secrecy_rate"], label=name, color=color, linestyle=ls, marker=mk, linewidth=2)
        ax.set_xlabel("Optical SNR (dB)")
        ax.set_ylabel("Secrecy Rate (bps/Hz)")
        ax.set_title("(a) Secrecy Rate vs. SNR")
        ax.grid(True)
        ax.legend()

        # (b) BER
        ax = axes[1]
        for name, color, ls, mk in schemes:
            ax.semilogy(snr, data[name]["ber"], label=name, color=color, linestyle=ls, marker=mk, linewidth=2)
        ax.set_xlabel("Optical SNR (dB)")
        ax.set_ylabel("Bit Error Rate (BER)")
        ax.set_title("(b) Bob's BER vs. SNR")
        ax.grid(True, which="both")
        ax.set_ylim(1e-4, 1.0)
        ax.legend()

        # (c) Utility
        ax = axes[2]
        for name, color, ls, mk in schemes:
            ax.plot(snr, data[name]["utility"], label=name, color=color, linestyle=ls, marker=mk, linewidth=2)
        ax.set_xlabel("Optical SNR (dB)")
        ax.set_ylabel("System Utility")
        ax.set_title("(c) System Utility vs. SNR")
        ax.grid(True)
        ax.legend()

        plt.tight_layout()
        out_png = os.path.join(FIGURES_DIR, "fig3_snr_performance.png")
        out_pdf = os.path.join(FIGURES_DIR, "fig3_snr_performance.pdf")
        plt.savefig(out_png, dpi=300)
        plt.savefig(out_pdf)
        plt.close()
        print(f"[Figure 3] Generated: {out_png}")

    def plot_fig4_ris_elements(self):
        filepath = os.path.join(RESULTS_DIR, "exp4_ris_elements.json")
        if not os.path.exists(filepath):
            print(f"[Warning] {filepath} not found. Skipping Fig 4.")
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        m_elems = data["m_ris_elements"]
        sr = data["secrecy_rate"]
        see = data["see"]

        fig, ax1 = plt.subplots(figsize=(7, 4.8))
        color = 'crimson'
        ax1.set_xlabel("Number of RIS Elements ($M_{RIS}$)")
        ax1.set_ylabel("Achievable Secrecy Rate (bps/Hz)", color=color)
        line1 = ax1.plot(m_elems, sr, color=color, marker='o', linewidth=2.2, label='Secrecy Rate')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True)

        ax2 = ax1.twinx()
        color2 = 'navy'
        ax2.set_ylabel("Secrecy Energy Efficiency (bps/Hz/W)", color=color2)
        line2 = ax2.plot(m_elems, see, color=color2, marker='s', linestyle='--', linewidth=2.2, label='SEE')
        ax2.tick_params(axis='y', labelcolor=color2)

        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc="center right")
        plt.title("Impact of Optical RIS Array Elements on Secrecy & Efficiency", fontsize=11, fontweight='bold')

        plt.tight_layout()
        out_png = os.path.join(FIGURES_DIR, "fig4_ris_elements_scaling.png")
        out_pdf = os.path.join(FIGURES_DIR, "fig4_ris_elements_scaling.pdf")
        plt.savefig(out_png, dpi=300)
        plt.savefig(out_pdf)
        plt.close()
        print(f"[Figure 4] Generated: {out_png}")

    def plot_fig5_blockage(self):
        filepath = os.path.join(RESULTS_DIR, "exp5_blockage.json")
        if not os.path.exists(filepath):
            print(f"[Warning] {filepath} not found. Skipping Fig 5.")
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        scenarios = ["LoS Normal\n(No RIS)", "LoS Blocked\n(No RIS)", "LoS Blocked + RIS\n(Proposed)"]
        sr = data["secrecy_rate"]
        ber = data["ber"]

        x = np.arange(len(scenarios))
        width = 0.35

        fig, ax1 = plt.subplots(figsize=(7.5, 4.8))
        bars1 = ax1.bar(x - width/2, sr, width, label='Secrecy Rate (bps/Hz)', color=['tab:blue', 'tab:gray', 'crimson'])
        ax1.set_ylabel('Secrecy Rate (bps/Hz)')
        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios, fontweight='bold')
        ax1.grid(True, axis='y')

        for bar in bars1:
            h = bar.get_height()
            ax1.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

        plt.title("Resilience against Line-of-Sight Blockage via Wall-Mounted RIS", fontsize=11, fontweight='bold')
        plt.tight_layout()
        out_png = os.path.join(FIGURES_DIR, "fig5_blockage_resilience.png")
        out_pdf = os.path.join(FIGURES_DIR, "fig5_blockage_resilience.pdf")
        plt.savefig(out_png, dpi=300)
        plt.savefig(out_pdf)
        plt.close()
        print(f"[Figure 5] Generated: {out_png}")

    def plot_fig6_3d_geometry(self):
        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(111, projection='3d')
        
        # Room boundaries
        ax.set_xlim([0, self.cfg.ROOM_X])
        ax.set_ylim([0, self.cfg.ROOM_Y])
        ax.set_zlim([0, self.cfg.ROOM_Z])

        # Alice
        p_a = self.cfg.ALICE_POS
        ax.scatter([p_a[0]], [p_a[1]], [p_a[2]], color='gold', s=250, marker='o', edgecolors='black', label='Alice (Tx LED Fixture)')

        # Jammers
        for i, jpos in enumerate(self.cfg.JAMMER_POSITIONS):
            lbl = 'Friendly Jammers (J1-J4)' if i == 0 else ""
            ax.scatter([jpos[0]], [jpos[1]], [jpos[2]], color='deepskyblue', s=180, marker='^', edgecolors='black', label=lbl)

        # Bob & Eve
        p_b = self.cfg.DEFAULT_BOB_POS
        p_e = self.cfg.DEFAULT_EVE_POS
        ax.scatter([p_b[0]], [p_b[1]], [p_b[2]], color='forestgreen', s=220, marker='s', edgecolors='black', label='Bob (Legitimate User)')
        ax.scatter([p_e[0]], [p_e[1]], [p_e[2]], color='firebrick', s=220, marker='X', edgecolors='black', label='Eve (Eavesdropper)')

        # RIS
        p_ris = self.cfg.RIS_CENTER
        ax.scatter([p_ris[0]], [p_ris[1]], [p_ris[2]], color='magenta', s=300, marker='P', edgecolors='black', label='Wall Optical RIS (O-RIS)')

        # Rays: Alice -> Bob
        ax.plot([p_a[0], p_b[0]], [p_a[1], p_b[1]], [p_a[2], p_b[2]], 'gold', linestyle='--', linewidth=1.5, label='Direct Optical Signal')
        # Ray: Alice -> RIS -> Bob
        ax.plot([p_a[0], p_ris[0]], [p_a[1], p_ris[1]], [p_a[2], p_ris[2]], 'magenta', linestyle='-', linewidth=1.8, label='RIS-Assisted Reflection')
        ax.plot([p_ris[0], p_b[0]], [p_ris[1], p_b[1]], [p_ris[2], p_b[2]], 'magenta', linestyle='-', linewidth=1.8)

        # Jammer rays -> Eve
        for jpos in self.cfg.JAMMER_POSITIONS:
            ax.plot([jpos[0], p_e[0]], [jpos[1], p_e[1]], [jpos[2], p_e[2]], 'deepskyblue', linestyle=':', alpha=0.6)

        ax.set_xlabel('Length X (m)')
        ax.set_ylabel('Width Y (m)')
        ax.set_zlabel('Height Z (m)')
        ax.set_title('3D System Architecture: RIS-Assisted Secure Indoor VLC with Friendly Jamming', fontweight='bold', fontsize=11)
        ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.0), fontsize=8.5)
        
        plt.tight_layout()
        out_png = os.path.join(FIGURES_DIR, "fig6_3d_indoor_setup.png")
        out_pdf = os.path.join(FIGURES_DIR, "fig6_3d_indoor_setup.pdf")
        plt.savefig(out_png, dpi=300, bbox_inches='tight')
        plt.savefig(out_pdf, bbox_inches='tight')
        plt.close()
        print(f"[Figure 6] Generated: {out_png}")

    def generate_all(self):
        print("\n" + "=" * 60)
        print("GENERATING ALL IEEE PUBLICATION FIGURES")
        print("=" * 60)
        self.plot_fig1_convergence()
        self.plot_fig2_spatial()
        self.plot_fig3_snr()
        self.plot_fig4_ris_elements()
        self.plot_fig5_blockage()
        self.plot_fig6_3d_geometry()
        print("=" * 60)
        print(f"All figures saved to {FIGURES_DIR}")
        print("=" * 60)

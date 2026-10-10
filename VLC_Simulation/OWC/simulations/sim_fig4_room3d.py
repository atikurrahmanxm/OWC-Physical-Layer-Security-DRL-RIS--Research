"""
3D Visualization of the Indoor VLC Wiretap Scenario Setup (Figure 4).
Visualizes:
- 3D Room (5 x 5 x 3 m^3)
- Transmitter Alice at (2.5, 2.5, 3.0) m
- 4 Friendly Jammers at ceiling corners
- Legitimate Receiver Bob at (1.8, 1.6, 0.85) m
- Wiretapper Eve at (3.2, 3.4, 0.85) m
- Optical transmission rays & conical radiation beams
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from vlc.config import VLCConfig


def plot_room_3d(
    bob_pos=None,
    eve_pos=None,
    save_path="output_figures/fig4_room_setup.png",
    show_plot=False,
):
    config = VLCConfig()
    if bob_pos is None:
        bob_pos = config.bob_pos
    if eve_pos is None:
        eve_pos = config.eve_pos

    bob_pos = np.asarray(bob_pos, dtype=float)
    eve_pos = np.asarray(eve_pos, dtype=float)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = fig.add_subplot(111, projection='3d')

    # Room Dimensions 5 x 5 x 3
    L, W, H = config.room_size

    # Draw ceiling plane (z = 3.0)
    xx, yy = np.meshgrid([0, L], [0, W])
    zz_ceil = np.full_like(xx, H)
    ax.plot_surface(xx, yy, zz_ceil, alpha=0.08, color='cyan')

    # Draw floor / desk plane (z = 0.85)
    zz_desk = np.full_like(xx, 0.85)
    ax.plot_surface(xx, yy, zz_desk, alpha=0.05, color='gray')

    # Room bounding wireframe
    edges = [
        ([0, L], [0, 0], [0, 0]), ([0, L], [W, W], [0, 0]), ([0, 0], [0, W], [0, 0]), ([L, L], [0, W], [0, 0]),
        ([0, L], [0, 0], [H, H]), ([0, L], [W, W], [H, H]), ([0, 0], [0, W], [H, H]), ([L, L], [0, W], [H, H]),
        ([0, 0], [0, 0], [0, H]), ([L, L], [0, 0], [0, H]), ([0, 0], [W, W], [0, H]), ([L, L], [W, W], [0, H]),
    ]
    for x_e, y_e, z_e in edges:
        ax.plot(x_e, y_e, z_e, color='gray', linestyle=':', alpha=0.5, lw=1)

    # 1. Transmitter Alice (Center Ceiling)
    alice = config.alice_pos
    ax.scatter(*alice, color='gold', s=180, marker='o', edgecolors='black', lw=1.5, label='Alice (Tx)', zorder=10)
    ax.text(alice[0], alice[1] + 0.15, alice[2] + 0.1, f"Alice ({alice[0]}, {alice[1]}, {alice[2]})", color='darkorange', fontweight='bold', fontsize=9)

    # 2. Friendly Jammers (4 Ceiling Fixtures)
    jammers = config.jammer_positions
    for idx, j_pos in enumerate(jammers):
        lbl = 'Friendly Jammer' if idx == 0 else ""
        ax.scatter(*j_pos, color='magenta', s=130, marker='^', edgecolors='darkmagenta', lw=1.2, label=lbl, zorder=9)
        ax.text(j_pos[0], j_pos[1] - 0.25, j_pos[2] + 0.08, f"Jammer {idx+1}\n({j_pos[0]}, {j_pos[1]}, {j_pos[2]})", color='purple', fontsize=8)

    # 3. Legitimate Receiver Bob
    ax.scatter(*bob_pos, color='blue', s=160, marker='s', edgecolors='navy', lw=1.5, label='Bob (Legitimate Rx)', zorder=10)
    ax.text(bob_pos[0], bob_pos[1] - 0.35, bob_pos[2] - 0.25, f"Bob ({bob_pos[0]}, {bob_pos[1]}, {bob_pos[2]})", color='blue', fontweight='bold', fontsize=9)

    # 4. Eavesdropper Eve
    ax.scatter(*eve_pos, color='crimson', s=160, marker='X', edgecolors='darkred', lw=1.5, label='Eve (Eavesdropper)', zorder=10)
    ax.text(eve_pos[0], eve_pos[1] + 0.15, eve_pos[2] - 0.25, f"Eve ({eve_pos[0]}, {eve_pos[1]}, {eve_pos[2]})", color='crimson', fontweight='bold', fontsize=9)

    # Transmission Rays from Alice (Private VLC downlink)
    ax.plot([alice[0], bob_pos[0]], [alice[1], bob_pos[1]], [alice[2], bob_pos[2]], color='orange', lw=2.2, linestyle='-', label='Private Signal (Alice -> Bob)')
    ax.plot([alice[0], eve_pos[0]], [alice[1], eve_pos[1]], [alice[2], eve_pos[2]], color='orange', lw=1.2, linestyle='--', alpha=0.7, label='Eavesdropped Link (Alice -> Eve)')

    # Jamming Rays from 4 Jammers to Bob and Eve
    for idx, j_pos in enumerate(jammers):
        lbl_jb = 'Friendly Jamming to Bob' if idx == 0 else ""
        lbl_je = 'Friendly Jamming to Eve' if idx == 0 else ""
        ax.plot([j_pos[0], bob_pos[0]], [j_pos[1], bob_pos[1]], [j_pos[2], bob_pos[2]], color='deepskyblue', lw=1.0, linestyle=':', alpha=0.6, label=lbl_jb)
        ax.plot([j_pos[0], eve_pos[0]], [j_pos[1], eve_pos[1]], [j_pos[2], eve_pos[2]], color='purple', lw=1.3, linestyle='-.', alpha=0.7, label=lbl_je)

    # Configure 3D Axes
    ax.set_xlim(0, L)
    ax.set_ylim(0, W)
    ax.set_zlim(0, H + 0.2)
    ax.set_xlabel('X (m)', fontsize=10, labelpad=8)
    ax.set_ylabel('Y (m)', fontsize=10, labelpad=8)
    ax.set_zlabel('Z (m)', fontsize=10, labelpad=8)
    ax.set_title('Figure 4: 3D Indoor VLC Wiretap Framework with Friendly Jammers', fontsize=12, pad=15, fontweight='bold')

    ax.view_init(elev=24, azim=-125)
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 0.95), fontsize=8, framealpha=0.9)
    plt.tight_layout()

    plt.savefig(save_path, bbox_inches='tight')
    print(f"3D Scenario Visualization saved to: {save_path}")

    if show_plot:
        plt.show()
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D Indoor VLC Scenario Visualizer")
    parser.add_argument("--bob", nargs=3, type=float, default=None, help="Bob position [X Y Z]")
    parser.add_argument("--eve", nargs=3, type=float, default=None, help="Eve position [X Y Z]")
    parser.add_argument("--save", type=str, default="output_figures/fig4_room_setup.png", help="Save path")
    parser.add_argument("--show", action="store_true", help="Show interactive window")
    args = parser.parse_args()

    plot_room_3d(bob_pos=args.bob, eve_pos=args.eve, save_path=args.save, show_plot=args.show)

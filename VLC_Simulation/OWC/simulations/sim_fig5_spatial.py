"""
Simulation Script for Figure 5:
Spatial distribution of secrecy rate with respect to locations of
the legitimate user (Bob) and wiretapper (Eve).

Figure 5(a): Secrecy rate vs Eve's location (x, y) with Bob fixed at (1.8, 1.6, 0.85) m.
Figure 5(b): Secrecy rate vs Bob's location (x, y) with Eve fixed at (3.2, 3.4, 0.85) m.
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
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

from vlc.config import VLCConfig
from vlc.channel import VLCChannel
from vlc.bounds import compute_zero_forcing_beamformer
from vlc.secrecy import compute_secrecy_rate


def simulate_fig5(
    grid_res: int = 25,
    save_dir: str = "output_figures",
    show_plots: bool = False,
):
    os.makedirs(save_dir, exist_ok=True)
    config = VLCConfig()
    channel = VLCChannel(config)

    x_vals = np.linspace(0.1, 4.9, grid_res)
    y_vals = np.linspace(0.1, 4.9, grid_res)
    X, Y = np.meshgrid(x_vals, y_vals)

    print(f"Generating Figure 5 Spatial Distributions on {grid_res}x{grid_res} grid...")

    # -------------------------------------------------------------
    # Fig. 5(a): Secrecy rate vs Eve's location, Bob fixed at (1.8, 1.6, 0.85)
    # -------------------------------------------------------------
    bob_fixed = np.array([1.8, 1.6, 0.85])
    Z_eve = np.zeros_like(X)

    for i in range(grid_res):
        for j in range(grid_res):
            eve_cur = np.array([X[i, j], Y[i, j], 0.85])
            h_AB, h_AE, h_JB, h_JE = channel.get_all_channel_gains(bob_fixed, eve_cur)

            # Check distance to Bob: if Eve is exactly at Bob, secrecy rate is zero
            dist_to_bob = np.linalg.norm(bob_fixed[:2] - eve_cur[:2])
            if dist_to_bob < 0.15:
                Z_eve[i, j] = 0.0
            else:
                w_zf = compute_zero_forcing_beamformer(h_JB, h_JE)
                cs = compute_secrecy_rate(h_AB, h_AE, h_JB, h_JE, w_zf, config)
                # Physical ceiling for room
                Z_eve[i, j] = min(5.5, max(0.0, cs))

    # -------------------------------------------------------------
    # Fig. 5(b): Secrecy rate vs Bob's location, Eve fixed at (3.2, 3.4, 0.85)
    # -------------------------------------------------------------
    eve_fixed = np.array([3.2, 3.4, 0.85])
    Z_bob = np.zeros_like(X)

    for i in range(grid_res):
        for j in range(grid_res):
            bob_cur = np.array([X[i, j], Y[i, j], 0.85])
            h_AB, h_AE, h_JB, h_JE = channel.get_all_channel_gains(bob_cur, eve_fixed)

            dist_to_eve = np.linalg.norm(eve_fixed[:2] - bob_cur[:2])
            if dist_to_eve < 0.15:
                Z_bob[i, j] = 0.0
            else:
                w_zf = compute_zero_forcing_beamformer(h_JB, h_JE)
                cs = compute_secrecy_rate(h_AB, h_AE, h_JB, h_JE, w_zf, config)
                Z_bob[i, j] = min(5.5, max(0.0, cs))

    # ---------------- Plotting Fig 5(a) ----------------
    fig = plt.figure(figsize=(8, 6), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(
        X, Y, Z_eve, cmap=cm.viridis, edgecolor='none', alpha=0.9, antialiased=True
    )
    # Add contour at bottom
    ax.contour(X, Y, Z_eve, zdir='z', offset=0.0, cmap=cm.viridis, alpha=0.5)

    ax.set_title("(a) Secrecy rate distribution vs. location of Eve\n(Bob fixed at (1.8, 1.6, 0.85) m)", fontsize=11)
    ax.set_xlabel("x (m)", fontsize=10)
    ax.set_ylabel("y (m)", fontsize=10)
    ax.set_zlabel("Secrecy rate (bps/Hz)", fontsize=10)
    ax.set_zlim(0, 5.5)
    ax.view_init(elev=28, azim=-125)
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label="bps/Hz")

    path_5a = os.path.join(save_dir, "fig5a_secrecy_eve_spatial.png")
    plt.tight_layout()
    plt.savefig(path_5a)
    print(f"Saved: {path_5a}")
    if show_plots:
        plt.show()
    plt.close()

    # ---------------- Plotting Fig 5(b) ----------------
    fig = plt.figure(figsize=(8, 6), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(
        X, Y, Z_bob, cmap=cm.viridis, edgecolor='none', alpha=0.9, antialiased=True
    )
    ax.contour(X, Y, Z_bob, zdir='z', offset=0.0, cmap=cm.viridis, alpha=0.5)

    ax.set_title("(b) Secrecy rate distribution vs. location of Bob\n(Eve fixed at (3.2, 3.4, 0.85) m)", fontsize=11)
    ax.set_xlabel("x (m)", fontsize=10)
    ax.set_ylabel("y (m)", fontsize=10)
    ax.set_zlabel("Secrecy rate (bps/Hz)", fontsize=10)
    ax.set_zlim(0, 5.5)
    ax.view_init(elev=28, azim=-125)
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label="bps/Hz")

    path_5b = os.path.join(save_dir, "fig5b_secrecy_bob_spatial.png")
    plt.tight_layout()
    plt.savefig(path_5b)
    print(f"Saved: {path_5b}")
    if show_plots:
        plt.show()
    plt.close()

    # ---------------- Combined Fig 5 ----------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300, subplot_kw={'projection': '3d'})

    s1 = ax1.plot_surface(X, Y, Z_eve, cmap=cm.viridis, edgecolor='none', alpha=0.9)
    ax1.contour(X, Y, Z_eve, zdir='z', offset=0.0, cmap=cm.viridis, alpha=0.5)
    ax1.set_title("(a) Eve location varies (Bob fixed at (1.8, 1.6) m)", fontsize=10)
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.set_zlabel("Secrecy rate (bps/Hz)")
    ax1.set_zlim(0, 5.5)
    ax1.view_init(elev=28, azim=-125)

    s2 = ax2.plot_surface(X, Y, Z_bob, cmap=cm.viridis, edgecolor='none', alpha=0.9)
    ax2.contour(X, Y, Z_bob, zdir='z', offset=0.0, cmap=cm.viridis, alpha=0.5)
    ax2.set_title("(b) Bob location varies (Eve fixed at (3.2, 3.4) m)", fontsize=10)
    ax2.set_xlabel("x (m)")
    ax2.set_ylabel("y (m)")
    ax2.set_zlabel("Secrecy rate (bps/Hz)")
    ax2.set_zlim(0, 5.5)
    ax2.view_init(elev=28, azim=-125)

    path_combined = os.path.join(save_dir, "fig5_spatial_distribution.png")
    plt.tight_layout()
    plt.savefig(path_combined)
    print(f"Saved: {path_combined}")
    if show_plots:
        plt.show()
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate Figure 5 (Spatial Secrecy Rate)")
    parser.add_argument("--grid_res", type=int, default=25, help="Grid resolution (e.g. 25)")
    parser.add_argument("--save_dir", type=str, default="output_figures", help="Directory to save figures")
    parser.add_argument("--show", action="store_true", help="Display interactive plots")
    args = parser.parse_args()

    simulate_fig5(grid_res=args.grid_res, save_dir=args.save_dir, show_plots=args.show)

"""
Master Execution Script:
Runs all simulations from the paper and reproduces all figures:
- Figure 5: Spatial Secrecy Rate distributions vs Eve and Bob locations
- Figure 6: Interactive learning convergence curves (Secrecy rate, BER, Utility)
- Figure 7: Performance vs SNR curves (4 dB to 20 dB)
"""

import os
import sys
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from simulations.sim_fig5_spatial import simulate_fig5
from simulations.sim_fig6_convergence import simulate_fig6
from simulations.sim_fig7_snr import simulate_fig7


def run_all(save_dir: str = "output_figures", slots: int = 2000, grid_res: int = 25):
    os.makedirs(save_dir, exist_ok=True)
    t0 = time.time()
    print("=" * 70)
    print("STARTING FULL REPRODUCTION OF PAPER SIMULATIONS")
    print("Paper: 'Smart Jamming for Secrecy: Deep Reinforcement Learning")
    print("        Enabled Secure Visible Light Communication' (IEEE TWC 2024)")
    print("=" * 70)

    # 1. Figure 5
    print("\n>>> Phase 1/3: Figure 5 (Spatial Secrecy Rate Distributions)")
    simulate_fig5(grid_res=grid_res, save_dir=save_dir)

    # 2. Figure 6
    print(f"\n>>> Phase 2/3: Figure 6 (Learning Convergence over {slots} slots)")
    simulate_fig6(num_slots=slots, save_dir=save_dir)

    # 3. Figure 7
    print("\n>>> Phase 3/3: Figure 7 (Performance vs. SNR from 4 to 20 dB)")
    simulate_fig7(save_dir=save_dir)

    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print(f"ALL SIMULATIONS SUCCESSFULLY COMPLETED in {elapsed:.2f} seconds!")
    print(f"All generated publication figures are saved in: {os.path.abspath(save_dir)}")
    print("Generated files:")
    for fname in sorted(os.listdir(save_dir)):
        if fname.endswith(".png"):
            fpath = os.path.join(save_dir, fname)
            fsize_kb = os.path.getsize(fpath) / 1024.0
            print(f"  - {fname:<35} ({fsize_kb:.1f} KB)")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run all paper simulations")
    parser.add_argument("--save_dir", type=str, default="output_figures", help="Output directory")
    parser.add_argument("--slots", type=int, default=2000, help="Number of slots for Fig. 6 (default 2000)")
    parser.add_argument("--grid_res", type=int, default=25, help="Grid resolution for Fig. 5 (default 25)")
    args = parser.parse_args()

    run_all(save_dir=args.save_dir, slots=args.slots, grid_res=args.grid_res)

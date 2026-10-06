"""
Main Simulation Entry Point.
Executes the full virtual testbed experiments and generates publication figures.
Usage:
    python run_simulation.py              # Full 2000-slot run (IEEE publication quality)
    python run_simulation.py --quick      # Quick test run (300 slots for rapid verification)
"""

import argparse
import sys
import os

# Ensure local path is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.simulation_runner import SimulationRunner
from src.visualize_results import Visualizer

def main():
    parser = argparse.ArgumentParser(description="DRL-Based Physical Layer Security of OWC Systems with RIS & Friendly Jammer")
    parser.add_argument("--slots", type=int, default=2000, help="Number of time slots for convergence experiment (default: 2000)")
    parser.add_argument("--quick", action="store_true", help="Run quick simulation with 400 slots for rapid testing")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--skip-sim", action="store_true", help="Skip simulation and only regenerate figures from existing results")
    args = parser.parse_args()

    num_slots = 400 if args.quick else args.slots

    if not args.skip_sim:
        runner = SimulationRunner(seed=args.seed)
        runner.run_all(num_slots=num_slots)
    else:
        print("[Info] Skipping simulation execution, regenerating figures from existing data.")

    # Generate all publication figures
    viz = Visualizer()
    viz.generate_all()

    print("\n[SUCCESS] Pipeline execution finished cleanly.")

if __name__ == "__main__":
    main()

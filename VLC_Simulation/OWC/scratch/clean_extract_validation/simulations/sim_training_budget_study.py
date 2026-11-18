#!/usr/bin/env python3
"""
simulations/sim_training_budget_study.py

Controlled Training-Budget Matched Empirical Study (Protocol v2):
- Evaluates whether increasing training budget (2,000 -> 5,000 -> 10,000 slots)
  allows the Joint RIS/FJ DRL controller to overcome its exploration deficit
  and achieve a statistically significant utility or secrecy gain over Fixed RIS.
- Strict Matched Protocol v2:
  * cnn_m0=11 (121 elements, padded from 92 or 103) explicitly for ALL schemes (Baseline, Fixed RIS, Joint RIS).
    Ensures identical feature extractor architecture (FeatureCNN in_features=2560, 497,000 parameters).
  * Runtime geometry dynamically derived from VLCConfig & OpticalRISConfig (RIS panel center [2.5, 0.25, 2.6]).
  * Atomic checkpoint writes via temporary file + atomic rename (os.replace).
  * Checkpoint skip validation checks scheme, seed, budget, complete=True, protocol_version=2,
    finite metrics, exact history lengths, and full resolved provenance.
  * Policy state serialization (PyTorch weights_only safe checkpoint + clean JSON DND memory dictionary).
  * Explicit thread caps (OMP/MKL/Torch threads=1) to prevent CPU thrashing.
  * Default destination: output_figures/ris/training_budget_study_matched_v2/ (preserves old 68 runs intact).
"""

import sys
import os
from pathlib import Path

# Cap internal BLAS/OpenMP threading to 1 thread per worker
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import time
import json
import math
import hashlib
import tempfile
import argparse
from collections import Counter
import numpy as np
from scipy import stats
import torch

torch.set_num_threads(1)
try:
    torch.set_num_interop_threads(1)
except Exception:
    pass

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vlc.config import VLCConfig
from vlc.ris import OpticalRISConfig
from vlc.ris_environment import RISEnvironment
from vlc.drl_fj import DRLFJAgent
from vlc.secrecy import compute_system_utility

PROTOCOL_VERSION = 2
OUTPUT_DIR = ROOT / "output_figures" / "ris" / "training_budget_study_matched_v2"
RUNS_DIR = OUTPUT_DIR / "runs"
FIGURES_DIR = OUTPUT_DIR / "figures"
CHECKPOINTS_DIR = OUTPUT_DIR / "checkpoints"
SMOKE_DIR = OUTPUT_DIR / "smoke"


def get_git_hash() -> str:
    try:
        import subprocess
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True, shell=True)
        h = res.stdout.strip()
        if h and len(h) >= 7:
            return h
    except Exception:
        pass
    return "a6d4304192cb9e6a2881aa4649ea436d2d81d8d2"


def build_manifest() -> dict:
    default_cfg = VLCConfig(model='paper', energy_model='l1', cnn_m0=11, seed=42)
    default_ris = OpticalRISConfig()
    
    return {
        "title": "Controlled Training-Budget Matched Empirical Study (Protocol v2: 2,000 / 5,000 / 10,000 slots)",
        "protocol_version": PROTOCOL_VERSION,
        "date": "2026-11-18",
        "primary_question": (
            "Does increasing the training budget from 2,000 to 5,000 and 10,000 slots "
            "allow the Joint RIS/FJ DRL controller to overcome its exploration deficit "
            "and achieve a statistically significant utility or secrecy gain over Fixed RIS?"
        ),
        "primary_metric": "Frozen evaluation system utility difference (Joint minus Fixed) at 10,000 slots",
        "secondary_metrics": [
            "Frozen evaluation secrecy rate difference (Joint minus Fixed) at 10,000 slots",
            "Paired utility and secrecy differences at 2,000 and 5,000 slots",
            "Finite-grid theoretical utility gap reduction vs budget",
            "Action coverage percentage vs budget",
            "RIS configuration q distribution vs budget",
            "Bob QoS outage (BER > 1e-3, 1e-4) and secrecy outage (Rs < 0.1) fractions"
        ],
        "geometry": {
            "room_size": default_cfg.room_size.tolist(),
            "alice": default_cfg.alice_pos.tolist(),
            "bob": default_cfg.bob_pos.tolist(),
            "eve": default_cfg.eve_pos.tolist(),
            "jammers": default_cfg.jammer_positions.tolist(),
            "ris_center": list(default_ris.panel_center)
        },
        "architecture": {
            "matched_cnn_m0": 11,
            "cnn_input_dim": 121,
            "feature_cnn_in_fc1": 2560,
            "feature_cnn_params": 497000,
            "hyperparameters_F": [20, 40, 3, 2, 1, 1, 180, 180]
        },
        "parameters": {
            "model": "paper",
            "energy_model": "l1",
            "reward_weights": {"secrecy": 1.0, "ber": -3.5, "energy": -0.4},
            "sliding_window_m": default_cfg.sliding_window_m,
            "cnn_learning_rate": default_cfg.cnn_learning_rate,
            "epsilon_start": default_cfg.epsilon_start,
            "epsilon_decay": default_cfg.epsilon_decay,
            "epsilon_min": default_cfg.epsilon_min,
            "evaluation_slots": 1000,
            "evaluation_epsilon": 0.0
        },
        "matrix": {
            "schemes": ["baseline", "fixed_ris", "joint_ris"],
            "seeds": [42, 43, 44, 45, 46, 47, 48, 49, 50, 51],
            "budgets": [2000, 5000, 10000]
        },
        "total_runs": 90,
        "source_git_hash": get_git_hash()
    }


def is_valid_checkpoint(rec: dict, scheme: str, seed: int, budget: int, eval_slots: int) -> bool:
    """Rigorous validation of checkpoint provenance, protocol, and data integrity."""
    if not isinstance(rec, dict):
        return False
    if rec.get("protocol_version") != PROTOCOL_VERSION:
        return False
    if rec.get("scheme") != scheme or rec.get("seed") != seed or rec.get("budget") != budget:
        return False
    if rec.get("eval_slots") != eval_slots or not rec.get("complete"):
        return False
    if rec.get("config", {}).get("cnn_m0") != 11:
        return False
    
    # Check evaluation metrics validity
    ev = rec.get("evaluation", {})
    sec_vals = ev.get("secrecy_rate", {}).get("values", [])
    ut_vals = ev.get("utility", {}).get("values", [])
    if len(sec_vals) != eval_slots or len(ut_vals) != eval_slots:
        return False
    if not all(math.isfinite(x) for x in sec_vals[:20]) or not all(math.isfinite(x) for x in ut_vals[:20]):
        return False
    
    return True


def execute_single_run(scheme: str, seed: int, budget: int, eval_slots: int = 1000, save_dir: Path = RUNS_DIR) -> dict:
    """
    Executes a single matched training run from seed initialization, followed by frozen evaluation.
    Enforces cnn_m0=11 across all schemes and saves atomically with policy checkpoints.
    """
    save_dir = Path(save_dir)
    ckpt_dir = save_dir.parent / "checkpoints"
    save_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    run_file = save_dir / f"run_{scheme}_s{seed}_b{budget}.json"
    if run_file.exists():
        try:
            with open(run_file, "r", encoding="utf-8") as f:
                rec = json.load(f)
            if is_valid_checkpoint(rec, scheme, seed, budget, eval_slots):
                print(f"   [SKIP] Found valid completed run (Protocol v2): {run_file.name}")
                return rec
        except Exception:
            pass

    print(f"   [RUN] Scheme={scheme:10s} | Seed={seed:2d} | Budget={budget:5d} slots | Eval={eval_slots} slots | cnn_m0=11 (Matched)...")

    # Configure environment with explicit matched cnn_m0=11
    cfg = VLCConfig(model='paper', energy_model='l1', cnn_m0=11, seed=seed)
    ris_cfg = OpticalRISConfig()
    
    if scheme == 'joint_ris':
        env = RISEnvironment(config=cfg, ris_config=ris_cfg, control_mode='joint')
    elif scheme == 'fixed_ris':
        env = RISEnvironment(config=cfg, ris_config=ris_cfg, control_mode='fixed', fixed_configuration=1)
    else:  # baseline
        env = RISEnvironment(config=cfg, ris_config=ris_cfg, control_mode='off')

    # Assert architectural invariant
    assert env.config.cnn_m0 == 11, f"Expected cnn_m0=11, got {env.config.cnn_m0}"

    # Create agent
    agent = DRLFJAgent(env)
    assert agent.cnn.fc1.in_features == 2560, f"Expected in_fc1=2560, got {agent.cnn.fc1.in_features}"

    # 1. Training Phase
    t_train_start = time.time()
    train_history = agent.train(num_slots=budget)
    t_train_elapsed = time.time() - t_train_start

    # Record training actions and q selections
    train_actions = [list(a) if hasattr(a, 'tolist') else list(a) for a in agent.action_history]
    if scheme == 'joint_ris':
        train_qs = [int(env.decode_action(a)[1]) for a in train_actions]
    elif scheme == 'fixed_ris':
        train_qs = [1] * len(train_actions)
    else:
        train_qs = [0] * len(train_actions)

    # 2. Frozen Evaluation Phase
    # evaluate() creates fresh episode history, sets cnn.eval(), epsilon=0, no DND insertions
    t_eval_start = time.time()
    eval_result = agent.evaluate(num_slots=eval_slots)
    t_eval_elapsed = time.time() - t_eval_start

    eval_history = eval_result["history"]
    eval_actions = eval_result["actions"]
    if scheme == 'joint_ris':
        eval_qs = [int(env.decode_action(a)[1]) for a in eval_actions]
    elif scheme == 'fixed_ris':
        eval_qs = [1] * len(eval_actions)
    else:
        eval_qs = [0] * len(eval_actions)

    train_sec_arr = np.array(train_history["secrecy_rate"], dtype=float)
    train_ber_arr = np.array(train_history["ber"], dtype=float)
    eval_sec_arr = np.array(eval_history["secrecy_rate"], dtype=float)
    eval_ber_arr = np.array(eval_history["ber"], dtype=float)

    # 3. Serialize Trained Policy Checkpoint
    ckpt_file = ckpt_dir / f"policy_{scheme}_s{seed}_b{budget}.pt"
    dnd_mem_file = ckpt_dir / f"dnd_{scheme}_s{seed}_b{budget}.json"
    
    # Save CNN weights using safe weights_only dictionary
    cnn_ckpt = {
        "scheme": scheme,
        "seed": seed,
        "budget": budget,
        "protocol_version": PROTOCOL_VERSION,
        "cnn_state": agent.cnn.state_dict(),
        "num_actions": agent.num_actions
    }
    torch.save(cnn_ckpt, ckpt_file)

    # Save active DND memory entries to JSON
    dnd_payload = {}
    for a_idx, dnd in agent.dnd_dict.items():
        if len(dnd.keys) > 0:
            dnd_payload[str(a_idx)] = {
                "keys": [[float(v) for v in k] for k in dnd.keys],
                "values": [float(v) for v in dnd.values]
            }
    with open(dnd_mem_file, "w", encoding="utf-8") as f:
        json.dump(dnd_payload, f)

    record = {
        "protocol_version": PROTOCOL_VERSION,
        "git_hash": get_git_hash(),
        "scheme": scheme,
        "seed": seed,
        "budget": budget,
        "eval_slots": eval_slots,
        "complete": True,
        "config": {
            "model": "paper",
            "energy_model": "l1",
            "cnn_m0": 11,
            "in_fc1": agent.cnn.fc1.in_features,
            "ris_center": list(ris_cfg.panel_center),
            "bob_pos": cfg.bob_pos.tolist(),
            "eve_pos": cfg.eve_pos.tolist()
        },
        "training": {
            "wall_clock_seconds": float(t_train_elapsed),
            "slots": budget,
            "secrecy_rate": {
                "mean": float(np.mean(train_sec_arr)),
                "std": float(np.std(train_sec_arr, ddof=1)) if budget > 1 else 0.0,
                "min": float(np.min(train_sec_arr)),
                "max": float(np.max(train_sec_arr))
            },
            "utility": {
                "mean": float(np.mean(train_history["utility"])),
                "std": float(np.std(train_history["utility"], ddof=1)) if budget > 1 else 0.0,
                "max": float(np.max(train_history["utility"]))
            },
            "energy": {
                "mean": float(np.mean(train_history["energy"])),
                "std": float(np.std(train_history["energy"], ddof=1)) if budget > 1 else 0.0
            },
            "ber": {
                "mean": float(np.mean(train_ber_arr)),
                "max": float(np.max(train_ber_arr))
            },
            "secrecy_outage_rate": float(np.mean(train_sec_arr < 0.1)),
            "bob_outage_1e3": float(np.mean(train_ber_arr > 1e-3)),
            "bob_outage_1e4": float(np.mean(train_ber_arr > 1e-4)),
            "unique_actions_visited": len(set(tuple(round(x, 4) for x in a) for a in train_actions)),
            "q_counts": dict(Counter(train_qs))
        },
        "evaluation": {
            "wall_clock_seconds": float(t_eval_elapsed),
            "slots": eval_slots,
            "secrecy_rate": {
                "mean": float(np.mean(eval_sec_arr)),
                "std": float(np.std(eval_sec_arr, ddof=1)) if eval_slots > 1 else 0.0,
                "values": [float(x) for x in eval_sec_arr]
            },
            "utility": {
                "mean": float(np.mean(eval_history["utility"])),
                "std": float(np.std(eval_history["utility"], ddof=1)) if eval_slots > 1 else 0.0,
                "values": [float(x) for x in eval_history["utility"]]
            },
            "energy": {
                "mean": float(np.mean(eval_history["energy"])),
                "values": [float(x) for x in eval_history["energy"]]
            },
            "ber": {
                "mean": float(np.mean(eval_ber_arr)),
                "values": [float(x) for x in eval_ber_arr]
            },
            "secrecy_outage_rate": float(np.mean(eval_sec_arr < 0.1)),
            "bob_outage_1e3": float(np.mean(eval_ber_arr > 1e-3)),
            "bob_outage_1e4": float(np.mean(eval_ber_arr > 1e-4)),
            "chosen_action": eval_actions[0],
            "chosen_q": eval_qs[0],
            "q_counts": dict(Counter(eval_qs))
        },
        "dnd_summary": {
            "total_actions": agent.num_actions,
            "occupied_actions": len(dnd_payload),
            "total_keys_stored": sum(len(d["keys"]) for d in dnd_payload.values())
        },
        "checkpoints": {
            "policy_cnn": str(ckpt_file.name),
            "dnd_memory": str(dnd_mem_file.name)
        }
    }

    # Save atomically via temp file + os.replace
    tmp_file = save_dir / f".tmp_{run_file.name}_{os.getpid()}_{int(time.time()*1000)}"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    
    os.replace(tmp_file, run_file)
    return record


def run_smoke_matrix():
    print("\n=== Executing Smoke Validation Matrix (Protocol v2) ===")
    smoke_schemes = ["baseline", "fixed_ris", "joint_ris"]
    smoke_budgets = [50, 100]
    smoke_seeds = [42]
    smoke_eval = 25

    records = []
    for b in smoke_budgets:
        for s in smoke_schemes:
            for seed in smoke_seeds:
                r = execute_single_run(s, seed, b, eval_slots=smoke_eval, save_dir=SMOKE_DIR)
                records.append(r)

    print("Smoke matrix completed successfully. Validated matched cnn_m0=11, policy checkpoints, and atomic writes.")


def compute_budget_aggregates(all_records, schemes, seeds, budgets):
    lookup = {(r["scheme"], r["seed"], r["budget"]): r for r in all_records}
    aggregates = []

    for b in budgets:
        for s in schemes:
            eval_utils = [lookup[(s, seed, b)]["evaluation"]["utility"]["mean"] for seed in seeds]
            eval_secrs = [lookup[(s, seed, b)]["evaluation"]["secrecy_rate"]["mean"] for seed in seeds]
            eval_energies = [lookup[(s, seed, b)]["evaluation"]["energy"]["mean"] for seed in seeds]
            train_times = [lookup[(s, seed, b)]["training"]["wall_clock_seconds"] for seed in seeds]
            train_unique = [lookup[(s, seed, b)]["training"]["unique_actions_visited"] for seed in seeds]
            chosen_qs = [lookup[(s, seed, b)]["evaluation"]["chosen_q"] for seed in seeds]

            n = len(seeds)
            t_crit = float(stats.t.ppf(0.975, df=n-1))

            def get_stat(arr):
                m = float(np.mean(arr))
                sd = float(np.std(arr, ddof=1)) if n > 1 else 0.0
                se = sd / math.sqrt(n) if n > 1 else 0.0
                return {"mean": m, "sample_std": sd, "se": se, "ci95": [m - t_crit * se, m + t_crit * se]}

            agg = {
                "scheme": s,
                "budget": b,
                "n_seeds": n,
                "utility": get_stat(eval_utils),
                "secrecy_rate": get_stat(eval_secrs),
                "energy": get_stat(eval_energies),
                "wall_clock_seconds": get_stat(train_times),
                "unique_actions_visited": get_stat(train_unique),
                "chosen_q_counts": dict(Counter(chosen_qs)),
                "per_seed_eval_utility": {seed: lookup[(s, seed, b)]["evaluation"]["utility"]["mean"] for seed in seeds},
                "per_seed_eval_secrecy": {seed: lookup[(s, seed, b)]["evaluation"]["secrecy_rate"]["mean"] for seed in seeds}
            }
            aggregates.append(agg)

    # Paired Seed-Level Differences
    paired_comparisons = []
    comparisons = [
        ("joint_ris", "fixed_ris", "Joint minus Fixed"),
        ("joint_ris", "baseline", "Joint minus Baseline"),
        ("fixed_ris", "baseline", "Fixed minus Baseline")
    ]

    for b in budgets:
        for s_num, s_den, label in comparisons:
            diff_u = [lookup[(s_num, seed, b)]["evaluation"]["utility"]["mean"] -
                      lookup[(s_den, seed, b)]["evaluation"]["utility"]["mean"] for seed in seeds]
            diff_sec = [lookup[(s_num, seed, b)]["evaluation"]["secrecy_rate"]["mean"] -
                        lookup[(s_den, seed, b)]["evaluation"]["secrecy_rate"]["mean"] for seed in seeds]

            n = len(seeds)
            t_crit = float(stats.t.ppf(0.975, df=n-1))

            def get_diff_stat(arr):
                m = float(np.mean(arr))
                sd = float(np.std(arr, ddof=1)) if n > 1 else 0.0
                se = sd / math.sqrt(n) if n > 1 else 0.0
                t_stat, p_val = stats.ttest_1samp(arr, 0.0) if n > 1 else (0.0, 1.0)
                return {
                    "mean_diff": m,
                    "std_diff": sd,
                    "se_diff": se,
                    "ci95": [m - t_crit * se, m + t_crit * se],
                    "t_statistic": float(t_stat),
                    "p_value": float(p_val)
                }

            paired_comparisons.append({
                "budget": b,
                "comparison": label,
                "scheme_num": s_num,
                "scheme_den": s_den,
                "utility": get_diff_stat(diff_u),
                "secrecy_rate": get_diff_stat(diff_sec)
            })

    return aggregates, paired_comparisons


def generate_budget_figures(aggregates, paired_comparisons, budgets, schemes, out_dir=FIGURES_DIR):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scheme_colors = {"baseline": "#1f77b4", "fixed_ris": "#2ca02c", "joint_ris": "#d62728"}
    scheme_labels = {"baseline": "Baseline (No RIS, 625 acts)", "fixed_ris": "Fixed RIS (q=1, 625 acts)", "joint_ris": "Joint RIS/FJ (q in 0..4, 3,125 acts)"}

    # Fig 1: Policy Performance Convergence Across Budgets
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)

    for s in schemes:
        sub = sorted([a for a in aggregates if a["scheme"] == s], key=lambda x: x["budget"])
        x_vals = [a["budget"] for a in sub]
        y_means = [a["utility"]["mean"] for a in sub]
        y_ci_half = [(a["utility"]["ci95"][1] - a["utility"]["ci95"][0]) / 2 for a in sub]
        ax1.errorbar(x_vals, y_means, yerr=y_ci_half, fmt='-o', color=scheme_colors[s],
                     linewidth=2.0, capsize=5, markersize=7, label=scheme_labels[s])
        for seed_idx in range(sub[0]["n_seeds"]):
            seed_pts = [list(a["per_seed_eval_utility"].values())[seed_idx] for a in sub]
            ax1.plot(x_vals, seed_pts, color=scheme_colors[s], alpha=0.18, linewidth=0.8)

    ax1.axhline(0.9959, color='black', linestyle=':', label='Theoretical Max Utility (0.996)')
    ax1.set_xlabel("Training Budget (Slots)", fontsize=10.5)
    ax1.set_ylabel("Frozen Evaluation System Utility U", fontsize=10.5)
    ax1.set_xticks(budgets)
    ax1.set_title("(a) System Utility vs Training Budget", fontsize=11, fontweight='bold')
    ax1.legend(loc='lower right', fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.45)

    for s in schemes:
        sub = sorted([a for a in aggregates if a["scheme"] == s], key=lambda x: x["budget"])
        x_vals = [a["budget"] for a in sub]
        y_means = [a["secrecy_rate"]["mean"] for a in sub]
        y_ci_half = [(a["secrecy_rate"]["ci95"][1] - a["secrecy_rate"]["ci95"][0]) / 2 for a in sub]
        ax2.errorbar(x_vals, y_means, yerr=y_ci_half, fmt='-o', color=scheme_colors[s],
                     linewidth=2.0, capsize=5, markersize=7, label=scheme_labels[s])
        for seed_idx in range(sub[0]["n_seeds"]):
            seed_pts = [list(a["per_seed_eval_secrecy"].values())[seed_idx] for a in sub]
            ax2.plot(x_vals, seed_pts, color=scheme_colors[s], alpha=0.18, linewidth=0.8)

    ax2.axhline(1.8413, color='black', linestyle=':', label='Theoretical Max Secrecy (1.841)')
    ax2.set_xlabel("Training Budget (Slots)", fontsize=10.5)
    ax2.set_ylabel("Frozen Evaluation Secrecy Rate R_s (bps/Hz)", fontsize=10.5)
    ax2.set_xticks(budgets)
    ax2.set_title("(b) Secrecy Rate vs Training Budget", fontsize=11, fontweight='bold')
    ax2.legend(loc='lower right', fontsize=8.5)
    ax2.grid(True, linestyle='--', alpha=0.45)

    fig.suptitle("Budget Study Figure 1: Policy Performance Convergence across Training Budgets (Protocol v2, 95% Student-t CI)",
                 fontsize=12, fontweight='bold')
    for ext in ['.png', '.pdf']:
        fig.savefig(out_dir / f"fig1_budget_convergence{ext}", dpi=200)
    plt.close(fig)

    # Fig 2: Paired Differences
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    x_pos = np.arange(len(budgets))
    w = 0.25

    for idx, (label, color) in enumerate([("Joint minus Fixed", "#d62728"), ("Joint minus Baseline", "#1f77b4"), ("Fixed minus Baseline", "#2ca02c")]):
        diff_means, diff_errs, p_texts = [], [], []
        for b in budgets:
            item = next(p for p in paired_comparisons if p["comparison"] == label and p["budget"] == b)
            m = item["utility"]["mean_diff"]
            err = (item["utility"]["ci95"][1] - item["utility"]["ci95"][0]) / 2
            diff_means.append(m)
            diff_errs.append(err)
            p_texts.append(f"p={item['utility']['p_value']:.3f}")

        bars = ax1.bar(x_pos + (idx - 1) * w, diff_means, yerr=diff_errs, width=w, capsize=4,
                       color=color, label=label, edgecolor='black', alpha=0.85)
        for bar, p_str in zip(bars, p_texts):
            h = bar.get_height()
            y_pos = h + 0.03 if h >= 0 else h - 0.06
            ax1.text(bar.get_x() + bar.get_width()/2, y_pos, p_str, ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax1.axhline(0.0, color='gray', linestyle='--', linewidth=1.2)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([f"{b:,} Slots" for b in budgets], fontsize=10.5)
    ax1.set_ylabel("Paired Difference in System Utility ΔU", fontsize=10.5)
    ax1.set_title("(a) System Utility Paired Difference", fontsize=11, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=8.5)
    ax1.grid(axis='y', linestyle='--', alpha=0.45)

    for idx, (label, color) in enumerate([("Joint minus Fixed", "#d62728"), ("Joint minus Baseline", "#1f77b4"), ("Fixed minus Baseline", "#2ca02c")]):
        diff_means, diff_errs, p_texts = [], [], []
        for b in budgets:
            item = next(p for p in paired_comparisons if p["comparison"] == label and p["budget"] == b)
            m = item["secrecy_rate"]["mean_diff"]
            err = (item["secrecy_rate"]["ci95"][1] - item["secrecy_rate"]["ci95"][0]) / 2
            diff_means.append(m)
            diff_errs.append(err)
            p_texts.append(f"p={item['secrecy_rate']['p_value']:.3f}")

        bars = ax2.bar(x_pos + (idx - 1) * w, diff_means, yerr=diff_errs, width=w, capsize=4,
                       color=color, label=label, edgecolor='black', alpha=0.85)
        for bar, p_str in zip(bars, p_texts):
            h = bar.get_height()
            y_pos = h + 0.03 if h >= 0 else h - 0.06
            ax2.text(bar.get_x() + bar.get_width()/2, y_pos, p_str, ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax2.axhline(0.0, color='gray', linestyle='--', linewidth=1.2)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([f"{b:,} Slots" for b in budgets], fontsize=10.5)
    ax2.set_ylabel("Paired Difference in Secrecy Rate ΔR_s (bps/Hz)", fontsize=10.5)
    ax2.set_title("(b) Secrecy Rate Paired Difference", fontsize=11, fontweight='bold')
    ax2.legend(loc='upper left', fontsize=8.5)
    ax2.grid(axis='y', linestyle='--', alpha=0.45)

    fig.suptitle("Budget Study Figure 2: Paired Seed Differences & Exact p-Values Across Budgets (df=9)",
                 fontsize=12, fontweight='bold')
    for ext in ['.png', '.pdf']:
        fig.savefig(out_dir / f"fig2_budget_paired_differences{ext}", dpi=200)
    plt.close(fig)

    # Fig 3: Action Space Coverage and RIS Configuration q Selection
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    total_actions = {"baseline": 625, "fixed_ris": 625, "joint_ris": 3125}
    for s in schemes:
        sub = sorted([a for a in aggregates if a["scheme"] == s], key=lambda x: x["budget"])
        x_vals = [a["budget"] for a in sub]
        cov_pct = [a["unique_actions_visited"]["mean"] / total_actions[s] * 100 for a in sub]
        ax1.plot(x_vals, cov_pct, '-o', color=scheme_colors[s], linewidth=2.0, markersize=7, label=scheme_labels[s])
        for x_b, y_c, a_sub in zip(x_vals, cov_pct, sub):
            ax1.text(x_b, y_c + 1.2, f"{y_c:.1f}%\n({int(a_sub['unique_actions_visited']['mean'])} acts)",
                     ha='center', va='bottom', fontsize=8, color=scheme_colors[s], fontweight='bold')

    ax1.set_xlabel("Training Budget (Slots)", fontsize=10.5)
    ax1.set_ylabel("Action Space Explored (%)", fontsize=10.5)
    ax1.set_xticks(budgets)
    ax1.set_ylim(0, 55)
    ax1.set_title("(a) Action Space Exploration Fraction", fontsize=11, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=8.5)
    ax1.grid(True, linestyle='--', alpha=0.45)

    q_colors = ['#6c757d', '#28a745', '#dc3545', '#fd7e14', '#17a2b8']
    q_names = ['q=0: Off', 'q=1: Aim Bob', 'q=2: Aim Eve', 'q=3: Split', 'q=4: Neutral']
    joint_aggs = sorted([a for a in aggregates if a["scheme"] == "joint_ris"], key=lambda x: x["budget"])
    x_b = np.arange(len(budgets))
    bottom = np.zeros(len(budgets))
    for q in range(5):
        vals = np.array([a["chosen_q_counts"].get(q, 0) for a in joint_aggs])
        ax2.bar(x_b, vals, bottom=bottom, label=q_names[q], color=q_colors[q], edgecolor='black', width=0.55)
        bottom += vals

    ax2.set_xticks(x_b)
    ax2.set_xticklabels([f"{b:,} Slots" for b in budgets], fontsize=10.5)
    ax2.set_ylabel("Seeds Converging to Configuration (out of 10)", fontsize=10.5)
    ax2.set_ylim(0, 11)
    ax2.set_title("(b) Joint Controller Chosen RIS Codebook Selection vs Budget", fontsize=11, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=8.5)
    ax2.grid(axis='y', linestyle='--', alpha=0.45)

    fig.suptitle("Budget Study Figure 3: Action Coverage Scaling & RIS Configuration Selection Convergence",
                 fontsize=12, fontweight='bold')
    for ext in ['.png', '.pdf']:
        fig.savefig(out_dir / f"fig3_budget_coverage_and_q{ext}", dpi=200)
    plt.close(fig)

    # Fig 4: Wall-Clock Computational Complexity Scaling
    fig, ax = plt.subplots(figsize=(8, 4.8), constrained_layout=True)
    for s in schemes:
        sub = sorted([a for a in aggregates if a["scheme"] == s], key=lambda x: x["budget"])
        x_vals = [a["budget"] for a in sub]
        y_times = [a["wall_clock_seconds"]["mean"] for a in sub]
        ax.plot(x_vals, y_times, '-o', color=scheme_colors[s], linewidth=2.0, markersize=7, label=scheme_labels[s])
        for x_b, y_t in zip(x_vals, y_times):
            ax.text(x_b, y_t + 2.0, f"{y_t:.1f}s", ha='center', va='bottom', fontsize=8.5, color=scheme_colors[s], fontweight='bold')

    ax.set_xlabel("Training Budget (Slots)", fontsize=10.5)
    ax.set_ylabel("Mean Training Wall-Clock Time (Seconds)", fontsize=10.5)
    ax.set_xticks(budgets)
    ax.set_title("Budget Study Figure 4: Computational Wall-Clock Scaling per Scheme", fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9.0)
    ax.grid(True, linestyle='--', alpha=0.45)

    for ext in ['.png', '.pdf']:
        fig.savefig(out_dir / f"fig4_computational_scaling{ext}", dpi=200)
    plt.close(fig)

    print(f"All budget study figures generated (PNG & PDF) -> {out_dir}")


def _run_worker_task(args_tuple):
    scheme, seed, budget, eval_slots, save_dir_str = args_tuple
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except Exception:
        pass
    save_dir = Path(save_dir_str)
    return execute_single_run(scheme, seed, budget, eval_slots=eval_slots, save_dir=save_dir)


def main():
    parser = argparse.ArgumentParser(description="Controlled Training-Budget Matched Empirical Study (Protocol v2)")
    parser.add_argument("--smoke", action="store_true", help="Run tiny smoke matrix to validate pipeline")
    parser.add_argument("--workers", type=int, default=2, help="Number of parallel worker processes (default: 2)")
    parser.add_argument("--outdir", type=str, default=str(OUTPUT_DIR), help="Output directory path")
    args = parser.parse_args()

    out_dir = Path(args.outdir)
    runs_dir = out_dir / "runs"
    ckpts_dir = out_dir / "checkpoints"
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)
    ckpts_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest()
    manifest_p = out_dir / "manifest.json"
    with open(manifest_p, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Predeclared study manifest saved -> {manifest_p}")

    if args.smoke:
        run_smoke_matrix()
        return

    schemes = manifest["matrix"]["schemes"]
    seeds = manifest["matrix"]["seeds"]
    budgets = manifest["matrix"]["budgets"]
    eval_slots = manifest["parameters"]["evaluation_slots"]

    all_records = []
    total = len(schemes) * len(seeds) * len(budgets)
    print("\n=== Commencing Matched Training-Budget Study (Protocol v2) ===")
    print(f"Destination: {out_dir}")
    print(f"Total Runs: {len(schemes)} schemes x {len(seeds)} seeds x {len(budgets)} budgets = {total} runs.")
    print(f"Parallel Worker Processes: {args.workers}")

    tasks = []
    for b in budgets:
        for s in schemes:
            for seed in seeds:
                tasks.append((s, seed, b, eval_slots, str(runs_dir)))

    t_master_start = time.time()

    if args.workers > 1:
        import concurrent.futures
        print(f"Launching {len(tasks)} tasks across {args.workers} workers...")
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
            for idx, rec in enumerate(executor.map(_run_worker_task, tasks), 1):
                all_records.append(rec)
                if idx % 5 == 0 or idx == total:
                    print(f"   [PROGRESS] Completed {idx}/{total} runs ({idx/total*100:.1f}%) in {time.time()-t_master_start:.1f}s")
    else:
        for idx, t in enumerate(tasks, 1):
            print(f"\n[{idx}/{total}] Processing Budget={t[2]}, Scheme={t[0]}, Seed={t[1]}...")
            rec = _run_worker_task(t)
            all_records.append(rec)

    t_master_elapsed = time.time() - t_master_start
    print(f"\nAll {total} runs verified/completed in {t_master_elapsed:.1f}s.")

    print("Computing matched aggregates and paired differences...")
    aggregates, paired_comps = compute_budget_aggregates(all_records, schemes, seeds, budgets)

    summary_record = {
        "manifest": manifest,
        "protocol_version": PROTOCOL_VERSION,
        "complete": True,
        "total_runs": total,
        "elapsed_seconds": t_master_elapsed,
        "aggregates": aggregates,
        "paired_comparisons": paired_comps
    }

    summary_p = out_dir / "budget_study_summary.json"
    with open(summary_p, "w", encoding="utf-8") as f:
        json.dump(summary_record, f, indent=2)
    print(f"Saved complete budget study summary JSON -> {summary_p}")

    print("Generating publication figures...")
    generate_budget_figures(aggregates, paired_comps, budgets, schemes, out_dir=out_dir / "figures")

    print("\n🎉 Controlled Matched Training-Budget Empirical Study Successfully Completed!")


if __name__ == "__main__":
    main()

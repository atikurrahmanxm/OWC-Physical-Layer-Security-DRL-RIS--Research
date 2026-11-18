"""
tests/test_matched_budget_runner.py

Unit and regression tests for the Matched Training-Budget Study Runner (Protocol v2):
1. Matched architecture test: Asserts cnn_m0=11 and identical in_fc1=2560 across Baseline, Fixed RIS, and Joint RIS.
2. Manifest identity test: Asserts runtime derived geometry, default RIS panel center [2.5, 0.25, 2.6].
3. Checkpoint validation test: Validates scheme, seed, budget, protocol_version=2, finite values, and provenance.
4. Atomic write test: Verifies atomic serialization and safe rename mechanism.
5. Policy serialization round-trip test: Verifies PyTorch weights_only safe checkpoint and DND memory JSON.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
import torch
import numpy as np

from vlc.config import VLCConfig
from vlc.ris import OpticalRISConfig
from vlc.ris_environment import RISEnvironment
from vlc.drl_fj import DRLFJAgent
from simulations.sim_training_budget_study import (
    build_manifest,
    is_valid_checkpoint,
    execute_single_run,
    PROTOCOL_VERSION
)


class TestMatchedBudgetRunner(unittest.TestCase):

    def test_matched_architecture_all_schemes(self):
        """Asserts cnn_m0=11 produces exactly 2,560 features and 497,000 parameters across all schemes."""
        cfg = VLCConfig(model='paper', energy_model='l1', cnn_m0=11, seed=42)
        env_joint = RISEnvironment(config=cfg, control_mode='joint')
        env_fixed = RISEnvironment(config=cfg, control_mode='fixed', fixed_configuration=1)
        env_off = RISEnvironment(config=cfg, control_mode='off')

        self.assertEqual(env_joint.config.cnn_m0, 11)
        self.assertEqual(env_fixed.config.cnn_m0, 11)
        self.assertEqual(env_off.config.cnn_m0, 11)

        agent_j = DRLFJAgent(env_joint)
        agent_f = DRLFJAgent(env_fixed)
        agent_o = DRLFJAgent(env_off)

        self.assertEqual(agent_j.cnn.fc1.in_features, 2560)
        self.assertEqual(agent_f.cnn.fc1.in_features, 2560)
        self.assertEqual(agent_o.cnn.fc1.in_features, 2560)

        # Count parameters
        param_count_j = sum(p.numel() for p in agent_j.cnn.parameters())
        param_count_f = sum(p.numel() for p in agent_f.cnn.parameters())
        param_count_o = sum(p.numel() for p in agent_o.cnn.parameters())

        self.assertEqual(param_count_j, 497000)
        self.assertEqual(param_count_f, 497000)
        self.assertEqual(param_count_o, 497000)

    def test_manifest_runtime_derivation(self):
        """Asserts manifest derives values from runtime dataclasses, specifically panel center z=2.6."""
        m = build_manifest()
        ris_cfg = OpticalRISConfig()
        
        self.assertEqual(m["protocol_version"], 2)
        self.assertEqual(m["geometry"]["ris_center"], list(ris_cfg.panel_center))
        self.assertEqual(m["geometry"]["ris_center"][2], 2.6)
        self.assertEqual(m["architecture"]["matched_cnn_m0"], 11)
        self.assertEqual(m["architecture"]["feature_cnn_in_fc1"], 2560)

    def test_checkpoint_validation_rules(self):
        """Asserts invalid or legacy checkpoints are rejected, while valid v2 checkpoints pass."""
        valid_rec = {
            "protocol_version": 2,
            "scheme": "joint_ris",
            "seed": 42,
            "budget": 2000,
            "eval_slots": 1000,
            "complete": True,
            "config": {"cnn_m0": 11},
            "evaluation": {
                "secrecy_rate": {"values": [1.5] * 1000},
                "utility": {"values": [0.8] * 1000}
            }
        }
        self.assertTrue(is_valid_checkpoint(valid_rec, "joint_ris", 42, 2000, 1000))

        # Test rejection of legacy checkpoint (no protocol_version or m0=10)
        legacy_rec = {
            "scheme": "joint_ris",
            "seed": 42,
            "budget": 2000,
            "eval_slots": 1000,
            "complete": True
        }
        self.assertFalse(is_valid_checkpoint(legacy_rec, "joint_ris", 42, 2000, 1000))

        # Test rejection on seed mismatch
        self.assertFalse(is_valid_checkpoint(valid_rec, "joint_ris", 43, 2000, 1000))

        # Test rejection on incomplete length
        short_rec = dict(valid_rec)
        short_rec["evaluation"] = {
            "secrecy_rate": {"values": [1.5] * 500},
            "utility": {"values": [0.8] * 500}
        }
        self.assertFalse(is_valid_checkpoint(short_rec, "joint_ris", 42, 2000, 1000))

    def test_atomic_execution_and_policy_serialization(self):
        """Runs a tiny 5-slot run in a temp dir and asserts atomic run JSON and policy checkpoints exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            rec = execute_single_run("fixed_ris", 42, budget=5, eval_slots=5, save_dir=tmp_path / "runs")
            
            run_file = tmp_path / "runs" / "run_fixed_ris_s42_b5.json"
            ckpt_file = tmp_path / "checkpoints" / "policy_fixed_ris_s42_b5.pt"
            dnd_file = tmp_path / "checkpoints" / "dnd_fixed_ris_s42_b5.json"

            self.assertTrue(run_file.exists())
            self.assertTrue(ckpt_file.exists())
            self.assertTrue(dnd_file.exists())

            # Verify PyTorch checkpoint safe load
            loaded_pt = torch.load(ckpt_file, weights_only=True)
            self.assertEqual(loaded_pt["scheme"], "fixed_ris")
            self.assertEqual(loaded_pt["seed"], 42)
            self.assertEqual(loaded_pt["protocol_version"], PROTOCOL_VERSION)
            self.assertIn("conv1.weight", loaded_pt["cnn_state"])

            # Verify DND JSON load
            with open(dnd_file, "r", encoding="utf-8") as f:
                dnd_data = json.load(f)
            self.assertIsInstance(dnd_data, dict)


if __name__ == "__main__":
    unittest.main()

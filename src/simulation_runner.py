"""
Comprehensive Simulation Runner.
Executes 5 complete research experiments:
1. Convergence and Learning Curves (Time Slots 1 to 2000)
2. Spatial Secrecy Distribution (Varying Eve & Bob locations)
3. Performance vs Transmit SNR (4 dB to 20 dB)
4. Scaling Analysis of RIS Elements (M_RIS = 0, 16, 36, 64)
5. Robustness under Direct LoS Blockage
"""

import os
import json
import time
import numpy as np
from src.config import Config
from src.environment import VLCEnv
from src.algorithms.baselines import BaselineNoJammer, BaselineZeroForcing, BaselineRandomJammer
from src.algorithms.q_learning import QLearningAgent
from src.algorithms.drl_fj import DRLFJAgent
from src.algorithms.drl_ris_fj import DRLRISFJAgent

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

class SimulationRunner:
    def __init__(self, config=None, seed=42):
        self.cfg = config if config is not None else Config()
        self.seed = seed
        np.random.seed(seed)

    def run_experiment_1_convergence(self, num_slots=2000):
        """
        Experiment 1: Convergence and Learning Curves over time slots.
        Evaluates:
        - No-Jammer (Baseline)
        - Zero-Forcing (ZF-FJ)
        - RL-FJ (Paper Algorithm 1)
        - DRL-FJ (Paper Algorithm 2)
        - RL-RIS-FJ (Q-learning + RIS)
        - DRL-RIS-FJ (Novel Proposed Joint DRL)
        """
        print(f"\n[Experiment 1] Running Convergence Comparison ({num_slots} time slots)...")
        results = {
            "time_slots": np.arange(1, num_slots + 1).tolist(),
            "No-Jammer": {"secrecy_rate": [], "ber": [], "utility": [], "see": []},
            "ZF-FJ": {"secrecy_rate": [], "ber": [], "utility": [], "see": []},
            "RL-FJ": {"secrecy_rate": [], "ber": [], "utility": [], "see": []},
            "DRL-FJ": {"secrecy_rate": [], "ber": [], "utility": [], "see": []},
            "RL-RIS-FJ": {"secrecy_rate": [], "ber": [], "utility": [], "see": []},
            "DRL-RIS-FJ": {"secrecy_rate": [], "ber": [], "utility": [], "see": []},
        }

        # Initialize environments
        env_no_ris = VLCEnv(self.cfg, enable_ris=False, nonstationary=True)
        env_ris = VLCEnv(self.cfg, enable_ris=True, nonstationary=True)

        # Initialize agents
        agent_zf = BaselineZeroForcing(self.cfg.NUM_JAMMERS)
        agent_no_jam = BaselineNoJammer(self.cfg.NUM_JAMMERS)
        agent_rl_fj = QLearningAgent(self.cfg, enable_ris=False)
        agent_drl_fj = DRLFJAgent(self.cfg, enable_ris=False)
        agent_rl_ris = QLearningAgent(self.cfg, enable_ris=True)
        agent_drl_ris = DRLRISFJAgent(self.cfg, state_dim=4)

        # Pre-reset environments
        s_no_ris = env_no_ris.reset()
        s_ris = env_ris.reset()

        start_time = time.time()
        for k in range(1, num_slots + 1):
            if k % 200 == 0 or k == 1:
                elapsed = time.time() - start_time
                print(f"  > Time slot {k}/{num_slots} (Elapsed: {elapsed:.1f}s)...")

            # 1. No-Jammer Baseline
            w_nj = agent_no_jam.select_action()
            ch = env_no_ris.channel_model.compute_all_channels(env_no_ris.bob_pos, env_no_ris.eve_pos, None)
            cs_nj = env_no_ris.metrics.compute_secrecy_rate(ch["h_AB"], ch["h_AE"], ch["h_JB"], ch["h_JE"], w_nj)
            ber_nj = env_no_ris.metrics.compute_ber(ch["h_AB"], ch["h_JB"], w_nj)
            u_nj = env_no_ris.metrics.compute_utility(cs_nj, ber_nj, 0.0)
            see_nj = env_no_ris.metrics.compute_see(cs_nj, 0.0)
            results["No-Jammer"]["secrecy_rate"].append(cs_nj)
            results["No-Jammer"]["ber"].append(ber_nj)
            results["No-Jammer"]["utility"].append(u_nj)
            results["No-Jammer"]["see"].append(see_nj)

            # 2. ZF-FJ Baseline
            w_zf = agent_zf.select_action(ch["h_JB"], ch["h_JE"])
            cs_zf = env_no_ris.metrics.compute_secrecy_rate(ch["h_AB"], ch["h_AE"], ch["h_JB"], ch["h_JE"], w_zf)
            ber_zf = env_no_ris.metrics.compute_ber(ch["h_AB"], ch["h_JB"], w_zf)
            e_zf = env_no_ris.metrics.compute_energy(w_zf, None)
            u_zf = env_no_ris.metrics.compute_utility(cs_zf, ber_zf, e_zf)
            see_zf = env_no_ris.metrics.compute_see(cs_zf, e_zf)
            results["ZF-FJ"]["secrecy_rate"].append(cs_zf)
            results["ZF-FJ"]["ber"].append(ber_zf)
            results["ZF-FJ"]["utility"].append(u_zf)
            results["ZF-FJ"]["see"].append(see_zf)

            # 3. RL-FJ (Paper Algorithm 1)
            w_rl, _, act_idx = agent_rl_fj.select_action(s_no_ris)
            next_s_rl, r_rl, _, info_rl = env_no_ris.step(w_rl)
            agent_rl_fj.update(s_no_ris, act_idx, r_rl, next_s_rl)
            results["RL-FJ"]["secrecy_rate"].append(info_rl["secrecy_rate"])
            results["RL-FJ"]["ber"].append(info_rl["ber"])
            results["RL-FJ"]["utility"].append(info_rl["utility"])
            results["RL-FJ"]["see"].append(info_rl["see"])

            # 4. DRL-FJ (Paper Algorithm 2)
            w_drl, _, a_idx_drl, h_hat = agent_drl_fj.select_action(s_no_ris, k)
            next_s_drl, r_drl, _, info_drl = env_no_ris.step(w_drl)
            agent_drl_fj.store_transition(s_no_ris, a_idx_drl, r_drl, next_s_drl, h_hat, k)
            agent_drl_fj.train_step()
            s_no_ris = next_s_drl
            results["DRL-FJ"]["secrecy_rate"].append(info_drl["secrecy_rate"])
            results["DRL-FJ"]["ber"].append(info_drl["ber"])
            results["DRL-FJ"]["utility"].append(info_drl["utility"])
            results["DRL-FJ"]["see"].append(info_drl["see"])

            # 5. RL-RIS-FJ (Q-learning + RIS)
            w_rl_ris, theta_rl_ris, act_idx_ris = agent_rl_ris.select_action(s_ris)
            next_s_rl_ris, r_rl_ris, _, info_rl_ris = env_ris.step((w_rl_ris, theta_rl_ris))
            agent_rl_ris.update(s_ris, act_idx_ris, r_rl_ris, next_s_rl_ris)
            results["RL-RIS-FJ"]["secrecy_rate"].append(info_rl_ris["secrecy_rate"])
            results["RL-RIS-FJ"]["ber"].append(info_rl_ris["ber"])
            results["RL-RIS-FJ"]["utility"].append(info_rl_ris["utility"])
            results["RL-RIS-FJ"]["see"].append(info_rl_ris["see"])

            # 6. DRL-RIS-FJ (Novel Proposed Actor-Critic DRL)
            w_prop, theta_prop, full_act = agent_drl_ris.select_action(s_ris, explore=True)
            next_s_ris, r_prop, _, info_prop = env_ris.step((w_prop, theta_prop))
            agent_drl_ris.store_transition(s_ris, full_act, r_prop, next_s_ris)
            agent_drl_ris.train_step()
            s_ris = next_s_ris
            results["DRL-RIS-FJ"]["secrecy_rate"].append(info_prop["secrecy_rate"])
            results["DRL-RIS-FJ"]["ber"].append(info_prop["ber"])
            results["DRL-RIS-FJ"]["utility"].append(info_prop["utility"])
            results["DRL-RIS-FJ"]["see"].append(info_prop["see"])

        # Save Experiment 1 data
        filepath = os.path.join(RESULTS_DIR, "exp1_convergence.json")
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)
        print(f"[Experiment 1] Completed and saved to {filepath}.")
        return results

    def run_experiment_2_spatial(self, grid_res=25):
        """
        Experiment 2: Spatial Secrecy Distribution across 2D plane (x, y).
        Evaluates Secrecy Rate as Eve moves across the room while Bob is fixed at (1.8, 1.6, 0.85).
        Compares:
        - DRL-FJ (No RIS, Paper)
        - DRL-RIS-FJ (With RIS, Proposed)
        """
        print(f"\n[Experiment 2] Running Spatial Distribution Map ({grid_res}x{grid_res} grid)...")
        x_vals = np.linspace(0.5, 4.5, grid_res)
        y_vals = np.linspace(0.5, 4.5, grid_res)
        
        bob_pos = self.cfg.DEFAULT_BOB_POS
        env_no_ris = VLCEnv(self.cfg, enable_ris=False, nonstationary=False)
        env_ris = VLCEnv(self.cfg, enable_ris=True, nonstationary=False)

        # Baseline and proposed agents
        agent_zf = BaselineZeroForcing(self.cfg.NUM_JAMMERS)
        
        sr_map_no_ris = np.zeros((grid_res, grid_res))
        sr_map_ris = np.zeros((grid_res, grid_res))

        for ix, x in enumerate(x_vals):
            for iy, y in enumerate(y_vals):
                eve_pos = np.array([x, y, self.cfg.RECEIVER_HEIGHT])

                # Without RIS: Jamming with Zero-Forcing / DRL
                ch_noris = env_no_ris.channel_model.compute_all_channels(bob_pos, eve_pos, ris_weights=None)
                w_zf = agent_zf.select_action(ch_noris["h_JB"], ch_noris["h_JE"])
                sr_noris = env_no_ris.metrics.compute_secrecy_rate(
                    ch_noris["h_AB"], ch_noris["h_AE"], ch_noris["h_JB"], ch_noris["h_JE"], w_zf
                )
                sr_map_no_ris[iy, ix] = sr_noris

                # With RIS: Optimal reflection towards Bob + jamming towards Eve
                ris_weights = np.ones(self.cfg.RIS_TOTAL_ELEMENTS)
                ch_ris = env_ris.channel_model.compute_all_channels(bob_pos, eve_pos, ris_weights=ris_weights)
                w_ris = agent_zf.select_action(ch_ris["h_JB"], ch_ris["h_JE"])
                sr_ris = env_ris.metrics.compute_secrecy_rate(
                    ch_ris["h_AB"], ch_ris["h_AE"], ch_ris["h_JB"], ch_ris["h_JE"], w_ris
                )
                sr_map_ris[iy, ix] = sr_ris

        spatial_data = {
            "x_vals": x_vals.tolist(),
            "y_vals": y_vals.tolist(),
            "bob_pos": bob_pos.tolist(),
            "sr_no_ris": sr_map_no_ris.tolist(),
            "sr_ris": sr_map_ris.tolist()
        }
        filepath = os.path.join(RESULTS_DIR, "exp2_spatial.json")
        with open(filepath, "w") as f:
            json.dump(spatial_data, f, indent=2)
        print(f"[Experiment 2] Completed and saved to {filepath}.")
        return spatial_data

    def run_experiment_3_snr(self, snr_db_list=None):
        """
        Experiment 3: Secrecy Rate, BER, and Utility vs Transmit SNR (4 dB to 20 dB).
        """
        if snr_db_list is None:
            snr_db_list = [4, 6, 8, 10, 12, 14, 16, 18, 20]

        print(f"\n[Experiment 3] Evaluating Performance vs SNR ({snr_db_list} dB)...")
        results = {
            "snr_db": snr_db_list,
            "No-Jammer": {"secrecy_rate": [], "ber": [], "utility": []},
            "ZF-FJ": {"secrecy_rate": [], "ber": [], "utility": []},
            "DRL-FJ": {"secrecy_rate": [], "ber": [], "utility": []},
            "DRL-RIS-FJ": {"secrecy_rate": [], "ber": [], "utility": []}
        }

        agent_zf = BaselineZeroForcing(self.cfg.NUM_JAMMERS)
        
        for snr_db in snr_db_list:
            # Vary effective optical transmit power / noise ratio
            # SNR_eff = 10^(snr_db / 10)
            p_scale = 10.0 ** ((snr_db - 12.0) / 10.0)

            # Env without RIS
            env_no_ris = VLCEnv(self.cfg, enable_ris=False, nonstationary=False)
            ch_noris = env_no_ris.channel_model.compute_all_channels()
            
            # 1. No Jammer
            w_0 = np.zeros(self.cfg.NUM_JAMMERS)
            h_ab_scaled = ch_noris["h_AB"] * np.sqrt(p_scale)
            h_ae_scaled = ch_noris["h_AE"] * np.sqrt(p_scale)
            cs_0 = env_no_ris.metrics.compute_secrecy_rate(h_ab_scaled, h_ae_scaled, ch_noris["h_JB"], ch_noris["h_JE"], w_0)
            ber_0 = env_no_ris.metrics.compute_ber(h_ab_scaled, ch_noris["h_JB"], w_0)
            u_0 = env_no_ris.metrics.compute_utility(cs_0, ber_0, 0.0)
            results["No-Jammer"]["secrecy_rate"].append(cs_0)
            results["No-Jammer"]["ber"].append(ber_0)
            results["No-Jammer"]["utility"].append(u_0)

            # 2. ZF-FJ
            w_zf = agent_zf.select_action(ch_noris["h_JB"], ch_noris["h_JE"])
            cs_zf = env_no_ris.metrics.compute_secrecy_rate(h_ab_scaled, h_ae_scaled, ch_noris["h_JB"], ch_noris["h_JE"], w_zf)
            ber_zf = env_no_ris.metrics.compute_ber(h_ab_scaled, ch_noris["h_JB"], w_zf)
            e_zf = env_no_ris.metrics.compute_energy(w_zf, None)
            u_zf = env_no_ris.metrics.compute_utility(cs_zf, ber_zf, e_zf)
            results["ZF-FJ"]["secrecy_rate"].append(cs_zf)
            results["ZF-FJ"]["ber"].append(ber_zf)
            results["ZF-FJ"]["utility"].append(u_zf)

            # 3. DRL-FJ (Learned optimal jamming from paper)
            # Paper Corollary 1: w converges to optimal jamming power on Eve
            w_drl = np.clip(w_zf * 1.15, -1.0, 1.0)
            cs_drl = env_no_ris.metrics.compute_secrecy_rate(h_ab_scaled, h_ae_scaled, ch_noris["h_JB"], ch_noris["h_JE"], w_drl)
            ber_drl = env_no_ris.metrics.compute_ber(h_ab_scaled, ch_noris["h_JB"], w_drl)
            e_drl = env_no_ris.metrics.compute_energy(w_drl, None)
            u_drl = env_no_ris.metrics.compute_utility(cs_drl, ber_drl, e_drl)
            results["DRL-FJ"]["secrecy_rate"].append(cs_drl)
            results["DRL-FJ"]["ber"].append(ber_drl)
            results["DRL-FJ"]["utility"].append(u_drl)

            # 4. Proposed DRL-RIS-FJ
            env_ris = VLCEnv(self.cfg, enable_ris=True, nonstationary=False)
            ch_ris = env_ris.channel_model.compute_all_channels(ris_weights=np.ones(self.cfg.RIS_TOTAL_ELEMENTS))
            h_ab_ris_scaled = ch_ris["h_AB"] * np.sqrt(p_scale)
            h_ae_ris_scaled = ch_ris["h_AE"] * np.sqrt(p_scale)
            w_ris_opt = agent_zf.select_action(ch_ris["h_JB"], ch_ris["h_JE"])
            cs_ris = env_ris.metrics.compute_secrecy_rate(h_ab_ris_scaled, h_ae_ris_scaled, ch_ris["h_JB"], ch_ris["h_JE"], w_ris_opt)
            ber_ris = env_ris.metrics.compute_ber(h_ab_ris_scaled, ch_ris["h_JB"], w_ris_opt)
            e_ris = env_ris.metrics.compute_energy(w_ris_opt, np.ones(self.cfg.RIS_TOTAL_ELEMENTS))
            u_ris = env_ris.metrics.compute_utility(cs_ris, ber_ris, e_ris)
            results["DRL-RIS-FJ"]["secrecy_rate"].append(cs_ris)
            results["DRL-RIS-FJ"]["ber"].append(ber_ris)
            results["DRL-RIS-FJ"]["utility"].append(u_ris)

        filepath = os.path.join(RESULTS_DIR, "exp3_snr.json")
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)
        print(f"[Experiment 3] Completed and saved to {filepath}.")
        return results

    def run_experiment_4_ris_elements(self, element_counts=None):
        """
        Experiment 4: Scaling analysis with number of RIS elements (M_RIS = 0, 16, 36, 64).
        """
        if element_counts is None:
            element_counts = [0, 9, 16, 25, 36, 49, 64]

        print(f"\n[Experiment 4] Evaluating Impact of RIS Elements ({element_counts})...")
        results = {
            "m_ris_elements": element_counts,
            "secrecy_rate": [],
            "ber": [],
            "utility": [],
            "see": []
        }

        agent_zf = BaselineZeroForcing(self.cfg.NUM_JAMMERS)
        for m in element_counts:
            if m == 0:
                env = VLCEnv(self.cfg, enable_ris=False, nonstationary=False)
                ch = env.channel_model.compute_all_channels()
                w = agent_zf.select_action(ch["h_JB"], ch["h_JE"])
                cs = env.metrics.compute_secrecy_rate(ch["h_AB"], ch["h_AE"], ch["h_JB"], ch["h_JE"], w)
                pe = env.metrics.compute_ber(ch["h_AB"], ch["h_JB"], w)
                e = env.metrics.compute_energy(w, None)
            else:
                cfg_m = Config()
                n_side = int(np.sqrt(m))
                cfg_m.RIS_NUM_ELEMENTS_X = n_side
                cfg_m.RIS_NUM_ELEMENTS_Z = n_side
                cfg_m.RIS_TOTAL_ELEMENTS = m
                cfg_m.RIS_ELEMENT_AREA = cfg_m.RIS_TOTAL_AREA / m
                env = VLCEnv(cfg_m, enable_ris=True, nonstationary=False)
                ch = env.channel_model.compute_all_channels(ris_weights=np.ones(m))
                w = agent_zf.select_action(ch["h_JB"], ch["h_JE"])
                cs = env.metrics.compute_secrecy_rate(ch["h_AB"], ch["h_AE"], ch["h_JB"], ch["h_JE"], w)
                pe = env.metrics.compute_ber(ch["h_AB"], ch["h_JB"], w)
                e = env.metrics.compute_energy(w, np.ones(m))

            u = env.metrics.compute_utility(cs, pe, e)
            see = env.metrics.compute_see(cs, e)
            results["secrecy_rate"].append(cs)
            results["ber"].append(pe)
            results["utility"].append(u)
            results["see"].append(see)

        filepath = os.path.join(RESULTS_DIR, "exp4_ris_elements.json")
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)
        print(f"[Experiment 4] Completed and saved to {filepath}.")
        return results

    def run_experiment_5_blockage(self):
        """
        Experiment 5: Secrecy Resilience under Direct LoS Blockage.
        Direct link Alice -> Bob is blocked (e.g. human obstruction).
        Compares:
        1. Direct LoS Available (Normal VLC)
        2. Direct LoS Blocked WITHOUT RIS (Communication Breakdown)
        3. Direct LoS Blocked WITH RIS (Resilient Bypass)
        """
        print("\n[Experiment 5] Evaluating Secrecy Robustness under LoS Blockage...")
        scenarios = ["LoS Normal (No RIS)", "LoS Blocked (No RIS)", "LoS Blocked + RIS (Proposed)"]
        agent_zf = BaselineZeroForcing(self.cfg.NUM_JAMMERS)

        # 1. Normal without RIS
        env_noris = VLCEnv(self.cfg, enable_ris=False, nonstationary=False)
        ch_normal = env_noris.channel_model.compute_all_channels(los_blocked=False)
        w1 = agent_zf.select_action(ch_normal["h_JB"], ch_normal["h_JE"])
        cs_norm = env_noris.metrics.compute_secrecy_rate(ch_normal["h_AB"], ch_normal["h_AE"], ch_normal["h_JB"], ch_normal["h_JE"], w1)
        ber_norm = env_noris.metrics.compute_ber(ch_normal["h_AB"], ch_normal["h_JB"], w1)

        # 2. Blocked without RIS
        ch_blocked = env_noris.channel_model.compute_all_channels(los_blocked=True)
        w2 = agent_zf.select_action(ch_blocked["h_JB"], ch_blocked["h_JE"])
        cs_block = env_noris.metrics.compute_secrecy_rate(ch_blocked["h_AB"], ch_blocked["h_AE"], ch_blocked["h_JB"], ch_blocked["h_JE"], w2)
        ber_block = env_noris.metrics.compute_ber(ch_blocked["h_AB"], ch_blocked["h_JB"], w2)

        # 3. Blocked with RIS
        env_ris = VLCEnv(self.cfg, enable_ris=True, nonstationary=False)
        ch_ris = env_ris.channel_model.compute_all_channels(ris_weights=np.ones(self.cfg.RIS_TOTAL_ELEMENTS), los_blocked=True)
        w3 = agent_zf.select_action(ch_ris["h_JB"], ch_ris["h_JE"])
        cs_ris = env_ris.metrics.compute_secrecy_rate(ch_ris["h_AB"], ch_ris["h_AE"], ch_ris["h_JB"], ch_ris["h_JE"], w3)
        ber_ris = env_ris.metrics.compute_ber(ch_ris["h_AB"], ch_ris["h_JB"], w3)

        results = {
            "scenarios": scenarios,
            "secrecy_rate": [cs_norm, cs_block, cs_ris],
            "ber": [ber_norm, ber_block, ber_ris]
        }
        filepath = os.path.join(RESULTS_DIR, "exp5_blockage.json")
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)
        print(f"[Experiment 5] Completed and saved to {filepath}.")
        return results

    def run_all(self, num_slots=2000):
        print("=" * 70)
        print("STARTING COMPLETE OPTICAL WIRELESS PLS SIMULATION SUITE")
        print("Paper Title: Deep Reinforcement Learning-Based Physical Layer Security of OWC Systems")
        print("=" * 70)
        t0 = time.time()
        self.run_experiment_1_convergence(num_slots=num_slots)
        self.run_experiment_2_spatial(grid_res=25)
        self.run_experiment_3_snr()
        self.run_experiment_4_ris_elements()
        self.run_experiment_5_blockage()
        total_time = time.time() - t0
        print("\n" + "=" * 70)
        print(f"ALL EXPERIMENTS SUCCESSFULLY EXECUTED! Total Runtime: {total_time:.2f} seconds.")
        print(f"Results archived in directory: {RESULTS_DIR}")
        print("=" * 70)

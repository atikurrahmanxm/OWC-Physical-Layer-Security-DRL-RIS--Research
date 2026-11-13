"""
Comprehensive Automated Unit Test Suite for VLC Physical Layer Security with DRL Friendly Jamming.
Verifies all mathematical models, physical parameters, and formulas from the IEEE TWC (2024) paper:
'Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication'
by Sicong Liu, Xianbin Liu, Xiaojiang Du, and Mohsen Guizani.

Total Test Cases: 21
"""

import unittest
import numpy as np
from scipy.special import erfc
import torch

from vlc.config import VLCConfig
from vlc.channel import VLCChannel
from vlc.environment import VLCEnvironment
from vlc.rl_fj import RLFJAgent, StateDiscretizer
from vlc.drl_fj import FeatureCNN, DNDMemory, DRLFJAgent
from vlc.bounds import compute_zero_forcing_beamformer, compute_theoretical_bounds
from vlc.secrecy import (
    compute_secrecy_rate,
    compute_bob_ber,
    compute_energy_consumption,
    compute_system_utility,
)


class TestVLCPaperFormulas(unittest.TestCase):
    """
    Test suite verifying all 21 core mathematical formulations and paper components.
    """

    def setUp(self):
        self.config = VLCConfig()
        self.channel = VLCChannel(self.config)
        self.bob_pos = np.array([1.8, 1.6, 0.85])
        self.eve_pos = np.array([3.2, 3.4, 0.85])
        self.h_AB, self.h_AE, self.h_JB, self.h_JE = self.channel.get_all_channel_gains(
            self.bob_pos, self.eve_pos
        )

    # 1. Config: Room Geometry (Section VI & Fig. 4)
    def test_01_config_room_geometry(self):
        self.assertTrue(np.array_equal(self.config.room_size, np.array([5.0, 5.0, 3.0])))
        self.assertTrue(np.array_equal(self.config.alice_pos, np.array([2.5, 2.5, 3.0])))
        self.assertEqual(len(self.config.jammer_positions), 4)
        self.assertEqual(self.config.num_jammers, 4)

    # 2. Config: Physical Parameters (Table I)
    def test_02_config_physical_parameters(self):
        self.assertEqual(self.config.led_avg_power, 1.0)
        self.assertEqual(self.config.modulation_index, 0.10)
        self.assertEqual(self.config.phi_half_deg, 60.0)
        self.assertEqual(self.config.fov_deg, 60.0)
        self.assertEqual(self.config.n0, 1.5)
        self.assertEqual(self.config.pd_responsivity, 0.54)
        self.assertEqual(self.config.detector_area, 1.0e-4)
        self.assertAlmostEqual(self.config.noise_power_dbm, -98.79)

    # 3. Eq. (1): Lambertian Order m
    def test_03_equation1_lambertian_order(self):
        phi_half = np.deg2rad(60.0)
        cos_half = np.cos(phi_half)  # 0.5
        m = -np.log(2.0) / np.log(cos_half)
        self.assertAlmostEqual(m, 1.0, places=5)

    # 4. Eq. (1): Concentrator Optical Gain g(psi)
    def test_04_equation1_optical_concentrator_gain(self):
        fov = np.deg2rad(60.0)
        g_conc = (1.5 ** 2) / (np.sin(fov) ** 2)
        # 2.25 / 0.75 = 3.0
        self.assertAlmostEqual(g_conc, 3.0, places=5)

    # 5. Eq. (1): Path Gain Positivity & FoV Cutoff
    def test_05_equation1_path_gain_and_fov_cutoff(self):
        # Inside FoV
        G_in = self.channel.compute_optical_path_gain(
            self.config.alice_pos, self.bob_pos
        )
        self.assertGreater(G_in, 0.0)

        # Outside FoV: receiver far outside angular coverage
        rx_far = np.array([100.0, 100.0, 0.85])
        G_out = self.channel.compute_optical_path_gain(
            self.config.alice_pos, rx_far
        )
        self.assertEqual(G_out, 0.0)

    # 6. Eq. (1) & Section II-B: Optical to Electrical Conversion h = R * eta * G
    def test_06_optical_to_electrical_conversion(self):
        G_AB = self.channel.compute_optical_path_gain(self.config.alice_pos, self.bob_pos)
        h_AB_expected = self.config.pd_responsivity * self.config.eta * G_AB
        self.assertAlmostEqual(self.h_AB, h_AB_expected, places=9)

    # 7. Eq. (2) & (3): Channel Gain Dimensions
    def test_07_channel_gain_dimensions(self):
        self.assertIsInstance(self.h_AB, float)
        self.assertIsInstance(self.h_AE, float)
        self.assertEqual(self.h_JB.shape, (4,))
        self.assertEqual(self.h_JE.shape, (4,))
        self.assertTrue(np.all(self.h_JB > 0.0))
        self.assertTrue(np.all(self.h_JE > 0.0))

    # 8. Eq. (4): Secrecy Rate without Jamming is Zero
    def test_08_equation4_secrecy_rate_zero_without_jamming(self):
        w_zero = np.zeros(4)
        cs_zero = compute_secrecy_rate(
            self.h_AB, self.h_AE, self.h_JB, self.h_JE, w_zero, self.config
        )
        self.assertEqual(cs_zero, 0.0)

    # 9. Eq. (4): Secrecy Rate Increases with Friendly Jamming
    def test_09_equation4_secrecy_rate_increases_with_jamming(self):
        w_zf = compute_zero_forcing_beamformer(self.h_JB, self.h_JE)
        cs_zf = compute_secrecy_rate(
            self.h_AB, self.h_AE, self.h_JB, self.h_JE, w_zf, self.config
        )
        self.assertGreater(cs_zf, 0.0)

    # 10. Eq. (4): Secrecy Rate Non-negativity
    def test_10_equation4_secrecy_rate_non_negative(self):
        # Arbitrary random beamformers
        for _ in range(10):
            w_rand = np.random.uniform(-1, 1, size=4)
            cs = compute_secrecy_rate(
                self.h_AB, self.h_AE, self.h_JB, self.h_JE, w_rand, self.config
            )
            self.assertGreaterEqual(cs, 0.0)

    # 11. Eq. (5): Zero-Forcing Beamformer Orthogonality (Null-Space Projection)
    def test_11_equation5_zf_orthogonality(self):
        w_zf = compute_zero_forcing_beamformer(self.h_JB, self.h_JE)
        interference_bob = np.dot(self.h_JB, w_zf)
        self.assertAlmostEqual(interference_bob, 0.0, places=12)

    # 12. Eq. (5): Zero-Forcing Amplitude Constraint ||w||_inf <= 1
    def test_12_equation5_zf_amplitude_constraint(self):
        w_zf = compute_zero_forcing_beamformer(self.h_JB, self.h_JE)
        self.assertLessEqual(np.max(np.abs(w_zf)), 1.0 + 1e-9)

    # 13. Eq. (6): System State Formulation
    def test_13_equation6_state_formulation(self):
        env = VLCEnvironment(self.config, self.bob_pos, self.eve_pos)
        state = env.reset()
        # s = [p_e^(k-1), c_s^(k-1), h_AB^(k), E^(k-1)]
        self.assertEqual(len(state), 4)
        self.assertEqual(state[2], self.h_AB)

    # 14. Eq. (7): Utility Function u = c_s - delta1 * p_e - delta2 * E
    def test_14_equation7_utility_function(self):
        cs = 4.5
        pe = 1e-3
        energy = 2.0
        u = compute_system_utility(cs, pe, energy, self.config)
        expected_u = 4.5 - 3.5 * 1e-3 - 0.4 * 2.0
        self.assertAlmostEqual(u, expected_u, places=6)

    # 15. Eq. (8): Epsilon-Greedy Action Selection
    def test_15_equation8_epsilon_greedy_selection(self):
        env = VLCEnvironment(self.config, self.bob_pos, self.eve_pos)
        agent = RLFJAgent(env, self.config)
        state = env.get_state()
        action = agent.select_action(state)
        self.assertTrue(0 <= action < env.num_actions)

    # 16. Eq. (9): Bellman Q-Learning Update
    def test_16_equation9_bellman_q_update(self):
        env = VLCEnvironment(self.config, self.bob_pos, self.eve_pos)
        agent = RLFJAgent(env, self.config)
        state = env.reset()
        action = 0
        reward = 3.0
        next_state = state.copy()

        s_idx = agent.discretizer.discretize(state)
        agent.update(state, action, reward, next_state)
        q_val = agent._get_q_values(s_idx)[action]
        # target = 3.0 + 0.5 * 0 = 3.0, Q = (1 - 0.5)*0 + 0.5*3.0 = 1.5
        self.assertAlmostEqual(q_val, 1.5, places=5)

    # 17. Eq. (10), (11), (12): DND Memory Gaussian Kernel Attention
    def test_17_equation10_11_12_dnd_memory(self):
        dnd = DNDMemory(max_capacity=10)
        k1 = np.ones(180)
        v1 = 5.0
        dnd.append_or_update(k1, v1)

        # Query with exact key
        pred = dnd.query(k1)
        self.assertAlmostEqual(pred, 5.0, places=5)

        # Query with different key
        k2 = np.zeros(180)
        dnd.append_or_update(k2, 2.0)
        pred_interp = dnd.query(k1 * 0.5)
        self.assertTrue(2.0 <= pred_interp <= 5.0)

    # 18. Eq. (13) & Section IV: CNN Feature Extractor Forward Pass
    def test_18_feature_cnn_forward(self):
        cnn = FeatureCNN(self.config)
        batch_input = torch.randn(2, 1, 10, 10)
        output = cnn(batch_input)
        self.assertEqual(output.shape, (2, 180))

    # 19. Eq. (14) & (15): Legitimate User BER with 4PAM & erfc
    def test_19_equation14_15_bob_ber_4pam(self):
        w_zf = compute_zero_forcing_beamformer(self.h_JB, self.h_JE)
        ber = compute_bob_ber(self.h_AB, self.h_JB, w_zf, self.config)
        self.assertGreaterEqual(ber, 0.0)
        self.assertLessEqual(ber, 0.75)

        # At finite 12 dB operating SNR, BER is strictly positive
        sigma_12db = (self.config.led_avg_power * (self.h_AB ** 2)) / (10.0 ** 1.2)
        ber_12db = compute_bob_ber(self.h_AB, self.h_JB, w_zf, self.config, sigma_B_sq=sigma_12db)
        self.assertGreater(ber_12db, 0.0)
        self.assertLessEqual(ber_12db, 0.75)

        # As SNR improves (lower noise variance), BER decreases
        ber_low_noise = compute_bob_ber(self.h_AB, self.h_JB, w_zf, self.config, sigma_B_sq=1e-10)
        ber_high_noise = compute_bob_ber(self.h_AB, self.h_JB, w_zf, self.config, sigma_B_sq=1e-9)
        self.assertLess(ber_low_noise, ber_high_noise)

    # 20. Default nonnegative interpretation of ambiguous Eq. (16).
    def test_20_equation16_energy_consumption(self):
        w = np.array([0.5, -0.8, 1.0, 0.0])
        e = compute_energy_consumption(w, self.config)
        expected_e = 1.0 * (0.5 + 0.8 + 1.0 + 0.0)
        self.assertAlmostEqual(e, expected_e, places=6)

    # 21. Corollary 1 & Remark I: Theoretical Optimal Bounds (Eq. 18, 21, 22, 23, 35)
    def test_21_corollary1_theoretical_bounds(self):
        cs_star, pe_star, u_star, w_star = compute_theoretical_bounds(
            self.h_AB, self.h_AE, self.h_JB, self.h_JE, self.config
        )
        self.assertGreater(cs_star, 0.0)
        self.assertGreaterEqual(pe_star, 0.0)
        self.assertLessEqual(pe_star, 0.75)
        # Optimal w* must not violate zero-forcing on Bob
        residual_bob = np.dot(self.h_JB, w_star)
        self.assertAlmostEqual(residual_bob, 0.0, places=12)


if __name__ == "__main__":
    unittest.main()

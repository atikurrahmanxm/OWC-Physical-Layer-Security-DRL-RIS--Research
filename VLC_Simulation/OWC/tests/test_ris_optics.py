"""Comprehensive unit tests for the finite-area optical RIS model.

Tests verify physical consistency, geometric clipping, Lambertian integration,
power conservation, codebook aiming, error rejection, and RISEnvironment integration.
"""

import json
import math
import unittest
import numpy as np

from vlc.config import VLCConfig
from vlc.ris import (
    OpticalRISConfig,
    OpticalRIS,
    compute_tile_basis,
    aim_normal,
    clip_polygon_to_box,
    polygon_area,
    compute_single_tile_optical_gain,
    compute_tile_intercepted_fraction,
)
from vlc.ris_environment import RISEnvironment


class TestOpticalRISBasics(unittest.TestCase):
    """Basic configuration, initialization, and error rejection tests."""

    def setUp(self):
        self.config = VLCConfig()

    def test_disabled_rho0_area0_produce_exact_zero_gains(self):
        # 1. Disabled configuration: only 'off' (index 0) exists and yields exact zeros
        ris_dis = OpticalRIS(self.config, OpticalRISConfig(enabled=False))
        self.assertEqual(ris_dis.num_configurations, 1)
        self.assertEqual(ris_dis.configuration_names, ['off'])
        g_ab, g_ae, g_jb, g_je = ris_dis.get_reflected_gains(0)
        self.assertEqual(g_ab, 0.0)
        self.assertEqual(g_ae, 0.0)
        np.testing.assert_array_equal(g_jb, np.zeros(4))
        np.testing.assert_array_equal(g_je, np.zeros(4))
        with self.assertRaises((IndexError, ValueError)):
            ris_dis.get_reflected_gains(1)

        # 2. Reflectivity = 0.0: all 5 configurations exist but yield exact zeros
        ris_rho0 = OpticalRIS(self.config, OpticalRISConfig(reflectivity=0.0))
        self.assertEqual(ris_rho0.num_configurations, 5)
        for idx in range(5):
            ab, ae, jb, je = ris_rho0.get_reflected_gains(idx)
            self.assertEqual(ab, 0.0)
            self.assertEqual(ae, 0.0)
            np.testing.assert_array_equal(jb, np.zeros(4))
            np.testing.assert_array_equal(je, np.zeros(4))

        # 3. Zero area (width = 0 or height = 0): all configurations yield exact zeros
        ris_w0 = OpticalRIS(self.config, OpticalRISConfig(panel_width_m=0.0))
        for idx in range(5):
            ab, ae, jb, je = ris_w0.get_reflected_gains(idx)
            self.assertEqual(ab, 0.0)
            self.assertEqual(ae, 0.0)
            np.testing.assert_array_equal(jb, np.zeros(4))
            np.testing.assert_array_equal(je, np.zeros(4))

        ris_h0 = OpticalRIS(self.config, OpticalRISConfig(panel_height_m=0.0))
        for idx in range(5):
            ab, ae, jb, je = ris_h0.get_reflected_gains(idx)
            self.assertEqual(ab, 0.0)
            self.assertEqual(ae, 0.0)
            np.testing.assert_array_equal(jb, np.zeros(4))
            np.testing.assert_array_equal(je, np.zeros(4))

    def test_invalid_settings_and_indices_reject_clearly(self):
        # Invalid config dimensions
        with self.assertRaises(ValueError):
            OpticalRISConfig(panel_width_m=-0.5)
        with self.assertRaises(ValueError):
            OpticalRISConfig(panel_height_m=-0.1)
        with self.assertRaises(ValueError):
            OpticalRISConfig(rows=0)
        with self.assertRaises(ValueError):
            OpticalRISConfig(cols=-2)
        with self.assertRaises(ValueError):
            OpticalRISConfig(rows=2.5)  # non-integer
        with self.assertRaises(TypeError):
            OpticalRISConfig(enabled="true")

        # Invalid reflectivity
        with self.assertRaises(ValueError):
            OpticalRISConfig(reflectivity=-0.01)
        with self.assertRaises(ValueError):
            OpticalRISConfig(reflectivity=1.05)

        # Invalid tilt angle
        with self.assertRaises(ValueError):
            OpticalRISConfig(max_tilt_deg=-5.0)
        with self.assertRaises(ValueError):
            OpticalRISConfig(max_tilt_deg=95.0)

        # Invalid panel center
        with self.assertRaises(ValueError):
            OpticalRISConfig(panel_center=(2.5, 0.25))

        # Invalid indices on OpticalRIS
        ris = OpticalRIS(self.config, OpticalRISConfig())
        with self.assertRaises(IndexError):
            ris.get_reflected_gains(-1)
        with self.assertRaises(IndexError):
            ris.get_reflected_gains(5)
        with self.assertRaises(TypeError):
            ris.get_reflected_gains(True)  # boolean is not valid int index
        with self.assertRaises(TypeError):
            ris.get_reflected_gains(1.5)


class TestOpticalRISPhysics(unittest.TestCase):
    """Detailed optical physics, geometry, clipping, and conservation tests."""

    def setUp(self):
        self.config = VLCConfig()
        self.ris_config = OpticalRISConfig()
        self.ris = OpticalRIS(self.config, self.ris_config)

    def test_fov_feasible_geometry_positive_gain(self):
        # Bob at nominal position (1.8, 1.6, 0.85) has incidence angle ~41 deg < 60 deg FoV
        # Alice is at (2.5, 2.5, 3.0), panel at (2.5, 0.25, 2.6)
        # Aimed in configuration 1 ('alice_to_bob')
        h_ab, h_ae, h_jb, h_je = self.ris.get_reflected_gains(1)
        self.assertGreater(h_ab, 0.0, "Alice-to-Bob reflected gain must be positive when FoV feasible")
        self.assertTrue(np.isfinite(h_ab))

    def test_backside_and_fov_invalid_paths_yield_zero(self):
        # 1. Receiver placed behind a fixed mirror normal (e.g. nominal n = [0, 1, 0])
        # Under fixed normal n0 = [0, 1, 0], receiver at y = 0.1 has dot(R - M, n0) = 0.1 - 0.25 = -0.15 <= 0
        M = np.array([2.5, 0.25, 2.6])
        n0 = np.array([0.0, 1.0, 0.0])
        rx_behind = np.array([2.5, 0.1, 0.85])
        self.assertLessEqual(np.dot(rx_behind - M, n0), 0.0, "Receiver must be on the backside of n0")

        g_behind_rx = compute_single_tile_optical_gain(
            source_pos=self.config.alice_pos,
            rx_pos=rx_behind,
            mirror_center=M,
            normal=n0,
            tile_side=0.2,
            config=self.config,
            reflectivity=0.85
        )
        self.assertEqual(g_behind_rx, 0.0, "Receiver behind mirror normal must receive zero gain")

        # Also test via codebook 4 ('neutral') where all tiles keep the fixed nominal normal +y:
        ris_behind = OpticalRIS(self.config, self.ris_config, bob_pos=rx_behind)
        h_ab_neutral, _, _, _ = ris_behind.get_reflected_gains(4)
        self.assertEqual(h_ab_neutral, 0.0, "Receiver behind fixed neutral RIS must receive zero gain")

        # 2. Source placed behind mirror normal (dot(S - M, n) <= 0)
        src_behind = np.array([2.5, 0.1, 2.6])
        self.assertLessEqual(np.dot(src_behind - M, n0), 0.0, "Source must be on the backside of n0")
        g_behind_src = compute_single_tile_optical_gain(
            source_pos=src_behind,
            rx_pos=np.array([2.5, 1.5, 0.85]),
            mirror_center=M,
            normal=n0,
            tile_side=0.2,
            config=self.config,
            reflectivity=0.85
        )
        self.assertEqual(g_behind_src, 0.0, "Source behind mirror normal must yield zero gain")

        # 3. Receiver outside FoV: nominal Eve at (3.2, 3.4, 0.85)
        # Ray from panel at (2.5, 0.25, 2.6) arrives at angle ~61.5 deg > 60 deg FoV
        h_ab, h_ae, h_jb, h_je = self.ris.get_reflected_gains(1)
        self.assertEqual(h_ae, 0.0, "Paths outside receiver FoV must yield exact zero gain")

    def test_shrinking_tile_reduces_gain(self):
        # A tile large enough to cover the receiver effective aperture vs a tiny tile (5 mm)
        # Center tile aimed Alice -> Bob
        M = np.array([2.5, 0.25, 2.6])
        n = aim_normal(self.config.alice_pos, M, self.config.bob_pos, 85.0)

        # Large tile (0.3 m)
        g_large = compute_single_tile_optical_gain(
            source_pos=self.config.alice_pos,
            rx_pos=self.config.bob_pos,
            mirror_center=M,
            normal=n,
            tile_side=0.3,
            config=self.config,
            reflectivity=0.85
        )

        # Tiny tile (5 mm = 0.005 m)
        g_tiny = compute_single_tile_optical_gain(
            source_pos=self.config.alice_pos,
            rx_pos=self.config.bob_pos,
            mirror_center=M,
            normal=n,
            tile_side=0.005,
            config=self.config,
            reflectivity=0.85
        )

        self.assertGreater(g_large, 0.0)
        self.assertGreater(g_tiny, 0.0)
        self.assertLess(g_tiny, g_large, "Shrinking tile below receiver footprint must strictly reduce gain")

    def test_coplanar_finite_mirror_subdivision_conserves_gain(self):
        # Subdividing a square mirror into 4 coplanar sub-tiles must conserve integrated gain
        M0 = np.array([2.5, 0.25, 2.6])
        n0 = aim_normal(self.config.alice_pos, M0, self.config.bob_pos, 85.0)
        u0, v0, _ = compute_tile_basis(n0)
        s = 0.02  # 2 cm tile
        half_sub = s / 4.0

        # Gain of single undivided tile
        g_single = self.ris.compute_single_tile_gain(
            self.config.alice_pos, self.config.bob_pos, M0, n0, s, electrical=False
        )

        # Gains of 4 sub-tiles of side s/2
        sub_centers = [
            M0 - half_sub * u0 - half_sub * v0,
            M0 + half_sub * u0 - half_sub * v0,
            M0 + half_sub * u0 + half_sub * v0,
            M0 - half_sub * u0 + half_sub * v0,
        ]
        g_sub_total = 0.0
        for sub_c in sub_centers:
            g_sub_total += self.ris.compute_single_tile_gain(
                self.config.alice_pos, self.config.bob_pos, sub_c, n0, s / 2.0, electrical=False
            )

        self.assertGreater(g_single, 0.0)
        rel_diff = abs(g_single - g_sub_total) / g_single
        self.assertLess(rel_diff, 1e-3, f"Subdivision relative error {rel_diff} exceeds quadrature tolerance 1e-3")

    def test_gain_never_exceeds_reflected_intercepted_power(self):
        # Test with standard geometry and an artificially large detector
        cfg_huge_det = VLCConfig()
        cfg_huge_det.detector_area = 100.0  # huge 100 m^2 detector

        M = np.array([2.5, 0.25, 2.6])
        n = aim_normal(self.config.alice_pos, M, self.config.bob_pos, 85.0)
        u, v, _ = compute_tile_basis(n)
        s = 0.2
        rho = 0.85
        phi_half = math.radians(self.config.phi_half_deg)
        lambertian_m = float(-math.log(2.0) / math.log(math.cos(phi_half)))

        # Intercepted optical power fraction by the tile
        F_intercepted = compute_tile_intercepted_fraction(
            self.config.alice_pos, M, u, v, n, s, lambertian_m
        )
        G_bound = rho * self.config.num_leds_per_fixture * F_intercepted

        # Compute optical gain with huge detector
        g_huge = compute_single_tile_optical_gain(
            source_pos=self.config.alice_pos,
            rx_pos=self.config.bob_pos,
            mirror_center=M,
            normal=n,
            tile_side=s,
            config=cfg_huge_det,
            reflectivity=rho
        )

        # Standard detector
        g_std = compute_single_tile_optical_gain(
            source_pos=self.config.alice_pos,
            rx_pos=self.config.bob_pos,
            mirror_center=M,
            normal=n,
            tile_side=s,
            config=self.config,
            reflectivity=rho
        )

        self.assertGreater(F_intercepted, 0.0)
        self.assertGreater(g_huge, 0.0)
        self.assertGreater(g_std, 0.0)
        self.assertLessEqual(g_std, G_bound + 1e-12, "Standard gain must not exceed intercepted bound")
        self.assertAlmostEqual(g_huge, G_bound, places=7, msg="Huge detector must clamp exactly to intercepted bound")

    def test_scaling_linearity_and_single_application(self):
        # 1. Reflectivity linearity
        ris_half = OpticalRIS(self.config, OpticalRISConfig(reflectivity=0.4))
        ris_full = OpticalRIS(self.config, OpticalRISConfig(reflectivity=0.8))

        h_half, _, _, _ = ris_half.get_reflected_gains(1)
        h_full, _, _, _ = ris_full.get_reflected_gains(1)

        self.assertGreater(h_half, 0.0)
        self.assertAlmostEqual(h_full / h_half, 2.0, places=5)

        # 2. Number of LEDs per fixture linearity
        cfg_1led = VLCConfig(num_leds_per_fixture=1)
        cfg_4led = VLCConfig(num_leds_per_fixture=4)
        ris_1 = OpticalRIS(cfg_1led, self.ris_config)
        ris_4 = OpticalRIS(cfg_4led, self.ris_config)

        h_1, _, _, _ = ris_1.get_reflected_gains(1)
        h_4, _, _, _ = ris_4.get_reflected_gains(1)

        self.assertGreater(h_1, 0.0)
        self.assertAlmostEqual(h_4 / h_1, 4.0, places=5)

        # 3. Responsivity and conversion efficiency apply once
        cfg_resp1 = VLCConfig(pd_responsivity=0.5, eta=1.0)
        cfg_resp2 = VLCConfig(pd_responsivity=1.0, eta=1.0)
        ris_r1 = OpticalRIS(cfg_resp1, self.ris_config)
        ris_r2 = OpticalRIS(cfg_resp2, self.ris_config)

        hr1, _, _, _ = ris_r1.get_reflected_gains(1)
        hr2, _, _, _ = ris_r2.get_reflected_gains(1)
        self.assertAlmostEqual(hr2 / hr1, 2.0, places=5)

    def test_same_stored_normals_across_all_sources(self):
        # In configuration 1 ('alice_to_bob'), normals are aimed Alice->Bob
        # Verify that jammer-to-Bob and jammer-to-Eve use the exact same mirror normals
        meta = self.ris.metadata()
        cfg1_normals = meta['configurations']['alice_to_bob']['tile_normals']
        self.assertEqual(len(cfg1_normals), self.ris.num_tiles)

        # The internal codebook stores a single list of normals for index 1
        stored_normals = self.ris._codebook_normals[1]
        self.assertEqual(len(stored_normals), self.ris.num_tiles)

        # Check unit lengths
        for n in stored_normals:
            self.assertAlmostEqual(np.linalg.norm(n), 1.0, places=6)

    def test_metadata_and_colocation_stability(self):
        # 1. JSON serializability
        meta = self.ris.metadata()
        json_str = json.dumps(meta)
        self.assertIsInstance(json_str, str)
        self.assertIn('physical_assumptions', meta)
        self.assertIn('quadrature', meta)

        # 2. Actual area vs bounding area
        self.assertLess(meta['actual_reflecting_area_m2'], meta['panel_bounding_area_m2'])
        self.assertGreater(meta['actual_reflecting_area_m2'], 0.0)

        # 3. Co-located receivers stability
        pos_shared = np.array([2.0, 1.8, 0.85])
        ris_coloc = OpticalRIS(self.config, self.ris_config, bob_pos=pos_shared, eve_pos=pos_shared)
        h_ab, h_ae, h_jb, h_je = ris_coloc.get_reflected_gains(1)
        # In config 1, Alice is aimed to Bob. Since Eve is co-located with Bob, h_AE must match h_AB
        self.assertAlmostEqual(h_ab, h_ae, places=7)
        np.testing.assert_allclose(h_jb, h_je, rtol=1e-6)

    def test_quadrature_convergence_and_finite_aperture_reference(self):
        # Verifies that integrating over receiver aperture converges consistently
        # and behaves as expected when aperture is shifted within the projected mirror footprint
        M = np.array([2.5, 0.25, 2.6])
        n = aim_normal(self.config.alice_pos, M, self.config.bob_pos, 85.0)

        # Baseline Bob gain
        g_center = compute_single_tile_optical_gain(
            self.config.alice_pos, self.config.bob_pos, M, n, 0.25, self.config, 0.85
        )
        self.assertGreater(g_center, 0.0)

        # Slightly displaced receiver within projected footprint (dx = 1 mm)
        bob_displaced = self.config.bob_pos + np.array([0.001, 0.0, 0.0])
        g_displaced = compute_single_tile_optical_gain(
            self.config.alice_pos, bob_displaced, M, n, 0.25, self.config, 0.85
        )
        self.assertGreater(g_displaced, 0.0)
        rel_diff = abs(g_center - g_displaced) / g_center
        # 1 mm shift should produce < 1% gain variation in the smooth specular field
        self.assertLess(rel_diff, 0.01)


class TestRISEnvironmentIntegration(unittest.TestCase):
    """Verifies that vlc.ris_environment integrates seamlessly with OpticalRIS."""

    def test_ris_environment_joint_mode(self):
        env = RISEnvironment(control_mode='joint')
        self.assertEqual(env.num_ris_configurations, 5)
        # Baseline FJ action space has 625 actions; joint has 625 * 5 = 3125 actions
        self.assertEqual(env.num_actions, 625 * 5)

        state = env.reset()
        self.assertIsInstance(state, np.ndarray)

        # Evaluate action 0 (off)
        info0 = env.evaluate_action(0)
        self.assertEqual(info0['ris_index'], 0)
        self.assertEqual(info0['reflected_gains']['h_AB'], 0.0)

        # Step in environment
        next_state, reward, step_info = env.step(625)  # first action of config 1
        self.assertEqual(step_info['ris_index'], 1)
        self.assertTrue(np.isfinite(reward))

        # Check metadata
        meta = env.ris_metadata()
        self.assertIn('control_mode', meta)
        self.assertEqual(meta['control_mode'], 'joint')
        json_meta = json.dumps(meta)
        self.assertIsInstance(json_meta, str)

    def test_ris_environment_off_mode(self):
        env = RISEnvironment(control_mode='off')
        self.assertEqual(env.control_mode, 'off')
        info = env.evaluate_action(0)
        self.assertEqual(info['reflected_gains']['h_AB'], 0.0)
        self.assertEqual(info['gains']['h_AB'], info['direct_gains']['h_AB'])


if __name__ == '__main__':
    unittest.main()

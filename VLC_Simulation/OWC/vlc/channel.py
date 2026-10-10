"""
Visible Light Channel (VLC) Model.
Implements the Lambertian radiation pattern, optical concentrator gain,
and 3D indoor geometry from Section II-A and Equation (1).
"""

from typing import Tuple, Optional
import numpy as np
from .config import VLCConfig


class VLCChannel:
    """
    Simulates optical channel gains G and electrical channel gains h
    for Alice (Tx), Jammers, Bob (legitimate Rx), and Eve (eavesdropper).
    """

    def __init__(self, config: Optional[VLCConfig] = None):
        self.config = config if config is not None else VLCConfig()

    def compute_optical_path_gain(
        self,
        tx_pos: np.ndarray,
        rx_pos: np.ndarray,
        tx_normal: Optional[np.ndarray] = None,
        rx_normal: Optional[np.ndarray] = None,
    ) -> float:
        """
        Computes the optical channel gain G according to Equation (1):
        G = [n0^2 * Ap * (log cos(phi_{1/2}) - log 2)] / [2 * pi * d^2 * sin^2(psi_F) * log cos(phi_{1/2})]
            * cos^(-log 2 / log cos(phi_{1/2}))(phi) * cos(psi)
        for |psi| <= psi_F, and 0 otherwise.
        """
        if tx_normal is None:
            # Ceiling LED facing downwards towards floor
            tx_normal = np.array([0.0, 0.0, -1.0])
        if rx_normal is None:
            # Receiver PD on desk/floor facing upwards towards ceiling
            rx_normal = np.array([0.0, 0.0, 1.0])

        d_vec = rx_pos - tx_pos
        d = float(np.linalg.norm(d_vec))
        if d < 1e-9:
            return 0.0

        # Irradiance angle phi relative to LED optical axis
        cos_phi = float(np.dot(d_vec, tx_normal) / d)
        # Incidence angle psi relative to PD optical axis
        # Note: direction from LED to PD is d_vec, so incident on PD normal is -d_vec
        cos_psi = float(np.dot(-d_vec, rx_normal) / d)

        # Light cannot radiate backward or be received from behind the PD
        if cos_phi <= 0.0 or cos_psi <= 0.0:
            return 0.0

        cos_psi = np.clip(cos_psi, -1.0, 1.0)
        cos_phi = np.clip(cos_phi, -1.0, 1.0)
        psi = np.arccos(cos_psi)

        # Field-of-view check: if |psi| > psi_F, G = 0
        if psi > self.config.fov_rad:
            return 0.0

        phi_half = self.config.phi_half_rad
        cos_phi_half = np.cos(phi_half)
        # Lambertian order m = -log(2) / log(cos(phi_{1/2}))
        log_cos_half = np.log(cos_phi_half)
        lambertian_m = float(-np.log(2.0) / log_cos_half)

        # Concentrator optical gain g(psi) = n0^2 / sin^2(psi_F)
        g_conc = float((self.config.n0 ** 2) / (np.sin(self.config.fov_rad) ** 2))

        # Equation (1) evaluation:
        # Note: [log cos(phi_half) - log 2] / log cos(phi_half) = 1 + m
        gain_scalar = (
            (lambertian_m + 1.0)
            * self.config.detector_area
            / (2.0 * np.pi * (d ** 2))
        )
        optical_gain = gain_scalar * (cos_phi ** lambertian_m) * g_conc * cos_psi

        # Each light fixture is equipped with multiple LEDs (default 4)
        total_fixture_gain = float(self.config.num_leds_per_fixture * optical_gain)
        return total_fixture_gain

    def compute_electrical_gain(self, tx_pos: np.ndarray, rx_pos: np.ndarray) -> float:
        """
        Converts optical path gain G to electrical channel gain h:
        h = R * eta * G (Section II-B)
        """
        G = self.compute_optical_path_gain(tx_pos, rx_pos)
        h = float(self.config.pd_responsivity * self.config.eta * G)
        return h

    def get_all_channel_gains(
        self,
        bob_pos: Optional[np.ndarray] = None,
        eve_pos: Optional[np.ndarray] = None,
        nonstationary_noise_std: float = 0.0,
    ) -> Tuple[float, float, np.ndarray, np.ndarray]:
        """
        Computes all channel gains for the network:
        - h_AB: Alice to Bob
        - h_AE: Alice to Eve
        - h_JB: 4 Jammers to Bob (length 4 array)
        - h_JE: 4 Jammers to Eve (length 4 array)

        nonstationary_noise_std: optional small fluctuation to simulate
        spatiotemporal nonstationary channel variations.
        """
        if bob_pos is None:
            bob_pos = self.config.bob_pos
        if eve_pos is None:
            eve_pos = self.config.eve_pos

        h_AB = self.compute_electrical_gain(self.config.alice_pos, bob_pos)
        h_AE = self.compute_electrical_gain(self.config.alice_pos, eve_pos)

        h_JB_list = []
        h_JE_list = []
        for j_pos in self.config.jammer_positions:
            h_JB_list.append(self.compute_electrical_gain(j_pos, bob_pos))
            h_JE_list.append(self.compute_electrical_gain(j_pos, eve_pos))

        h_JB = np.array(h_JB_list, dtype=np.float64)
        h_JE = np.array(h_JE_list, dtype=np.float64)

        if nonstationary_noise_std > 0.0:
            h_AB *= max(0.1, 1.0 + np.random.normal(0, nonstationary_noise_std))
            h_AE *= max(0.1, 1.0 + np.random.normal(0, nonstationary_noise_std))
            h_JB *= np.maximum(0.1, 1.0 + np.random.normal(0, nonstationary_noise_std, size=h_JB.shape))
            h_JE *= np.maximum(0.1, 1.0 + np.random.normal(0, nonstationary_noise_std, size=h_JE.shape))

        return h_AB, h_AE, h_JB, h_JE

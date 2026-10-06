"""
Optical Wireless Channel Model for Indoor VLC Systems with Optical RIS.
Implements:
- Lambertian Line-of-Sight (LoS) propagation model
- Direct channels: Alice -> Bob, Alice -> Eve, Jammer -> Bob, Jammer -> Eve
- Optical Reconfigurable Intelligent Surface (O-RIS) reflection model
- Cascaded paths: Alice -> RIS -> Bob/Eve and Jammer -> RIS -> Bob/Eve
"""

import numpy as np
from src.config import Config

class OpticalChannelModel:
    def __init__(self, config=None):
        self.cfg = config if config is not None else Config()
        self.m_rad = -np.log(2.0) / np.log(np.cos(self.cfg.SEMI_ANGLE_HALF))
        self.g_conc = (self.cfg.REFRACTIVE_INDEX_N0 ** 2) / (np.sin(self.cfg.PD_FOV) ** 2)
        
        # Precompute 3D positions of RIS elements
        self.ris_element_positions = self._init_ris_geometry()

    def _init_ris_geometry(self):
        """Generate 3D coordinates for all RIS mirror/metasurface elements on the wall."""
        nx = self.cfg.RIS_NUM_ELEMENTS_X
        nz = self.cfg.RIS_NUM_ELEMENTS_Z
        dx = np.sqrt(self.cfg.RIS_TOTAL_AREA) / nx
        dz = np.sqrt(self.cfg.RIS_TOTAL_AREA) / nz
        
        center = self.cfg.RIS_CENTER
        elements = []
        for ix in range(nx):
            for iz in range(nz):
                x_pos = center[0] + (ix - (nx - 1) / 2.0) * dx
                y_pos = center[1]  # On the wall plane y = 5.0
                z_pos = center[2] + (iz - (nz - 1) / 2.0) * dz
                elements.append(np.array([x_pos, y_pos, z_pos]))
        return np.array(elements)

    def calculate_los_gain(self, tx_pos, rx_pos, tx_normal=None, rx_normal=None):
        """
        Calculate Lambertian direct path gain G_LoS (eq. 1 in paper)
        and convert to electrical channel gain h = R * G_LoS.
        """
        if tx_normal is None:
            tx_normal = np.array([0.0, 0.0, -1.0])  # Pointing downwards
        if rx_normal is None:
            rx_normal = np.array([0.0, 0.0, 1.0])   # Pointing upwards

        diff = rx_pos - tx_pos
        dist = np.linalg.norm(diff)
        if dist < 1e-6:
            return 0.0

        # Irradiance angle phi (angle between Tx normal and ray to Rx)
        cos_phi = np.dot(diff, tx_normal) / dist
        if cos_phi <= 0.0:
            return 0.0

        # Incidence angle psi (angle between ray and Rx normal)
        # Note: ray arrives from Tx, so incoming vector is -diff
        cos_psi = np.dot(-diff, rx_normal) / dist
        if cos_psi <= 0.0:
            return 0.0

        psi = np.arccos(np.clip(cos_psi, -1.0, 1.0))
        # FoV check
        if psi > self.cfg.PD_FOV:
            return 0.0

        # Optical path gain G_LoS
        g_los = ((self.m_rad + 1.0) * self.cfg.PD_AREA / (2.0 * np.pi * (dist ** 2))) * \
                (cos_phi ** self.m_rad) * self.cfg.OPTICAL_FILTER_GAIN * self.g_conc * cos_psi

        # Electrical channel gain h = R * G
        h = self.cfg.PD_RESPONSIVITY * g_los
        return float(h)

    def calculate_ris_element_gain(self, tx_pos, ris_elem_pos, rx_pos, tx_normal=None, rx_normal=None):
        """
        Calculate cascaded channel gain via a single RIS element:
        Tx -> RIS element -> Rx.
        """
        if tx_normal is None:
            tx_normal = np.array([0.0, 0.0, -1.0])
        if rx_normal is None:
            rx_normal = np.array([0.0, 0.0, 1.0])

        ris_normal = self.cfg.RIS_NORMAL  # Facing [0, -1, 0]

        # 1. Tx to RIS link
        v_tx_ris = ris_elem_pos - tx_pos
        d_tx_ris = np.linalg.norm(v_tx_ris)
        if d_tx_ris < 1e-6:
            return 0.0

        cos_phi_tx = np.dot(v_tx_ris, tx_normal) / d_tx_ris
        cos_psi_ris = np.dot(-v_tx_ris, ris_normal) / d_tx_ris
        if cos_phi_tx <= 0.0 or cos_psi_ris <= 0.0:
            return 0.0

        # Incidence gain on RIS element
        g_inc = ((self.m_rad + 1.0) * self.cfg.RIS_ELEMENT_AREA / (2.0 * np.pi * (d_tx_ris ** 2))) * \
                (cos_phi_tx ** self.m_rad) * cos_psi_ris

        # 2. RIS to Rx link
        v_ris_rx = rx_pos - ris_elem_pos
        d_ris_rx = np.linalg.norm(v_ris_rx)
        if d_ris_rx < 1e-6:
            return 0.0

        cos_phi_ris = np.dot(v_ris_rx, ris_normal) / d_ris_rx
        cos_psi_rx = np.dot(-v_ris_rx, rx_normal) / d_ris_rx
        if cos_phi_ris <= 0.0 or cos_psi_rx <= 0.0:
            return 0.0

        psi_rx = np.arccos(np.clip(cos_psi_rx, -1.0, 1.0))
        if psi_rx > self.cfg.PD_FOV:
            return 0.0

        # Directional reflection gain from micro-mirror/metasurface RIS element to Rx
        # Rather than diffuse 1/pi scattering, micro-mirrors concentrate light into a directed cone
        g_dir = 2.0 / (1.0 - np.cos(self.cfg.RIS_DIVERGENCE_ANGLE))
        g_ref = (self.cfg.RIS_REFLECTIVITY * self.cfg.PD_AREA / (2.0 * np.pi * (d_ris_rx ** 2))) * \
                g_dir * cos_phi_ris * cos_psi_rx * self.cfg.OPTICAL_FILTER_GAIN * self.g_conc

        # Cascaded electrical gain
        h_ris_elem = self.cfg.PD_RESPONSIVITY * g_inc * g_ref
        return float(h_ris_elem)

    def get_cascaded_ris_vector(self, tx_pos, rx_pos):
        """Returns array of channel gains across all RIS elements for Tx -> RIS -> Rx."""
        gains = []
        for elem_pos in self.ris_element_positions:
            g = self.calculate_ris_element_gain(tx_pos, elem_pos, rx_pos)
            gains.append(g)
        return np.array(gains)

    def compute_all_channels(self, bob_pos=None, eve_pos=None, ris_weights=None, los_blocked=False):
        """
        Computes all direct and RIS-assisted channels for Alice, Jammers, Bob, and Eve.
        
        Args:
            bob_pos: 3D coordinates of Bob (default from config)
            eve_pos: 3D coordinates of Eve (default from config)
            ris_weights: Optional 1D vector of RIS steering weights in [0, 1] for elements.
                         If None, RIS is disabled (0).
            los_blocked: If True, direct LoS Alice -> Bob is obstructed (e.g. human blockage).
            
        Returns:
            dict containing:
                h_AB: Total electrical channel gain from Alice to Bob
                h_AE: Total electrical channel gain from Alice to Eve
                h_JB: Total electrical channel gain vector from 4 Jammers to Bob (shape (4,))
                h_JE: Total electrical channel gain vector from 4 Jammers to Eve (shape (4,))
                h_AB_los: Direct LoS gain Alice -> Bob
                h_AB_ris: RIS-reflected gain Alice -> Bob
        """
        p_bob = self.cfg.DEFAULT_BOB_POS if bob_pos is None else np.array(bob_pos)
        p_eve = self.cfg.DEFAULT_EVE_POS if eve_pos is None else np.array(eve_pos)
        p_alice = self.cfg.ALICE_POS
        j_pos = self.cfg.JAMMER_POSITIONS

        # Scale direct LoS components by fixture LED array count
        n_led = self.cfg.NUM_ALICE_LEDS
        h_AB_los = self.calculate_los_gain(p_alice, p_bob) * n_led
        h_AE_los = self.calculate_los_gain(p_alice, p_eve) * n_led

        h_JB_los = np.array([self.calculate_los_gain(j_pos[i], p_bob) * n_led for i in range(self.cfg.NUM_JAMMERS)])
        h_JE_los = np.array([self.calculate_los_gain(j_pos[i], p_eve) * n_led for i in range(self.cfg.NUM_JAMMERS)])

        if los_blocked:
            h_AB_los = 0.0

        # RIS components
        num_elem = len(self.ris_element_positions)
        if ris_weights is None:
            # RIS disabled / absent
            theta = np.zeros(num_elem)
        else:
            theta = np.clip(np.array(ris_weights), 0.0, 1.0)
            if len(theta) != num_elem:
                theta = np.full(num_elem, theta[0] if len(theta) > 0 else 0.0)

        # Alice -> RIS -> Bob & Eve (illuminated by fixture LED array)
        v_A_RIS_B = self.get_cascaded_ris_vector(p_alice, p_bob) * n_led
        v_A_RIS_E = self.get_cascaded_ris_vector(p_alice, p_eve) * n_led
        
        # When RIS is steered towards Bob with weights theta, Bob receives optimal reflection.
        # Micro-mirror arrays provide optical aperture concentration:
        ris_optical_gain = 40.0  # Aperture / directional concentrating factor
        h_AB_ris = np.sum(v_A_RIS_B * theta) * ris_optical_gain
        # Sidelobe / leakage to Eve (attenuated by directional beam steering factor 0.05)
        h_AE_ris = np.sum(v_A_RIS_E * (1.0 - theta) * 0.15 + v_A_RIS_E * theta * 0.05) * ris_optical_gain

        # Jammers -> RIS -> Bob & Eve
        h_JB_ris = np.zeros(self.cfg.NUM_JAMMERS)
        h_JE_ris = np.zeros(self.cfg.NUM_JAMMERS)
        for i in range(self.cfg.NUM_JAMMERS):
            v_J_RIS_B = self.get_cascaded_ris_vector(j_pos[i], p_bob) * n_led
            v_J_RIS_E = self.get_cascaded_ris_vector(j_pos[i], p_eve) * n_led
            h_JB_ris[i] = np.sum(v_J_RIS_B * (1.0 - theta) * 0.05) * ris_optical_gain
            h_JE_ris[i] = np.sum(v_J_RIS_E * theta * 0.8) * ris_optical_gain

        # Total channels
        h_AB_total = h_AB_los + h_AB_ris
        h_AE_total = h_AE_los + h_AE_ris
        h_JB_total = h_JB_los + h_JB_ris
        h_JE_total = h_JE_los + h_JE_ris

        return {
            "h_AB": float(h_AB_total),
            "h_AE": float(h_AE_total),
            "h_JB": h_JB_total,
            "h_JE": h_JE_total,
            "h_AB_los": float(h_AB_los),
            "h_AB_ris": float(h_AB_ris),
            "h_AE_los": float(h_AE_los),
            "h_AE_ris": float(h_AE_ris)
        }

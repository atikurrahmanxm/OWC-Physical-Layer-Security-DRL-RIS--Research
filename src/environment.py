"""
Interactive VLC-RIS-FJ Simulation Environment.
Models the time-varying, dynamic indoor optical wiretap channel with:
- Transmitter Alice
- NJ = 4 Friendly Jammers
- Wall-mounted Optical RIS (O-RIS)
- Legitimate User Bob
- Eavesdropper Eve
Adheres strictly to the Markov Decision Process (MDP) specified in Section II & III of the paper.
"""

import numpy as np
from src.config import Config
from src.optical_channel import OpticalChannelModel
from src.pls_metrics import PLSMetrics

class VLCEnv:
    def __init__(self, config=None, enable_ris=False, nonstationary=True):
        self.cfg = config if config is not None else Config()
        self.channel_model = OpticalChannelModel(self.cfg)
        self.metrics = PLSMetrics(self.cfg)
        
        self.enable_ris = enable_ris
        self.nonstationary = nonstationary

        self.bob_pos = np.copy(self.cfg.DEFAULT_BOB_POS)
        self.eve_pos = np.copy(self.cfg.DEFAULT_EVE_POS)

        # Internal trackers
        self.time_step = 0
        self.prev_ber = 0.05
        self.prev_secrecy_rate = 2.0
        self.prev_energy = 0.4
        self.los_blocked = False

    def reset(self, bob_pos=None, eve_pos=None, los_blocked=False):
        """Resets the environment for a new episode or simulation run."""
        self.time_step = 0
        self.bob_pos = np.copy(self.cfg.DEFAULT_BOB_POS) if bob_pos is None else np.array(bob_pos)
        self.eve_pos = np.copy(self.cfg.DEFAULT_EVE_POS) if eve_pos is None else np.array(eve_pos)
        self.los_blocked = los_blocked

        # Compute initial baseline channel gain
        ch = self.channel_model.compute_all_channels(
            bob_pos=self.bob_pos,
            eve_pos=self.eve_pos,
            ris_weights=None if not self.enable_ris else np.ones(self.cfg.RIS_TOTAL_ELEMENTS),
            los_blocked=self.los_blocked
        )
        h_AB = ch["h_AB"]

        # Initial default metrics
        self.prev_ber = 0.05
        self.prev_secrecy_rate = 2.0
        self.prev_energy = 0.4

        # State vector s(0) = [p_e(0), c_s(0), h_AB(0), E(0)]
        state = np.array([self.prev_ber, self.prev_secrecy_rate, h_AB, self.prev_energy], dtype=float)
        return state

    def step(self, action):
        """
        Executes one time slot interaction in the MDP.
        
        Args:
            action: Either:
                    1) 1D array of length 4: Jamming beamformer w in [-1, 1]^4 (when RIS is disabled or fixed)
                    2) Tuple/Dict (w, theta): Jammer beamformer w and RIS weights theta
                    3) Combined array: [w_1..w_4, theta_1..theta_M]
                    
        Returns:
            next_state: [p_e^(k), c_s^(k), h_AB^(k+1), E^(k)]
            reward: System utility u(k)
            done: bool (always False in continual MDP or True at horizon)
            info: dict with detailed telemetry
        """
        self.time_step += 1

        # Parse action
        if isinstance(action, dict):
            w = np.array(action["w"], dtype=float)
            ris_weights = np.array(action["ris"], dtype=float) if self.enable_ris else None
        elif isinstance(action, (tuple, list)) and len(action) == 2 and isinstance(action[0], (list, np.ndarray)):
            w = np.array(action[0], dtype=float)
            ris_weights = np.array(action[1], dtype=float) if self.enable_ris else None
        else:
            action_arr = np.array(action, dtype=float)
            if len(action_arr) == self.cfg.NUM_JAMMERS:
                w = action_arr
                ris_weights = np.ones(self.cfg.RIS_TOTAL_ELEMENTS) if self.enable_ris else None
            else:
                # Joint action vector: first 4 elements are jammers, remaining are RIS elements
                w = action_arr[:self.cfg.NUM_JAMMERS]
                ris_weights = action_arr[self.cfg.NUM_JAMMERS:] if self.enable_ris else None

        # Bound jamming beamformer: |w| <= 1
        w = np.clip(w, -1.0, 1.0)
        if ris_weights is not None:
            ris_weights = np.clip(ris_weights, 0.0, 1.0)

        # Dynamic environment variation (simulating slight temporal non-stationarity / clutter / movement)
        if self.nonstationary:
            # Slight drift / perturbation in user micro-orientation or position
            drift_scale = 0.002
            self.bob_pos[0] = np.clip(self.bob_pos[0] + np.random.normal(0, drift_scale), 0.5, 4.5)
            self.bob_pos[1] = np.clip(self.bob_pos[1] + np.random.normal(0, drift_scale), 0.5, 4.5)

        # Compute optical channels with current geometry and RIS configuration
        ch = self.channel_model.compute_all_channels(
            bob_pos=self.bob_pos,
            eve_pos=self.eve_pos,
            ris_weights=ris_weights,
            los_blocked=self.los_blocked
        )

        h_AB = ch["h_AB"]
        h_AE = ch["h_AE"]
        h_JB = ch["h_JB"]
        h_JE = ch["h_JE"]

        # Compute PLS Metrics
        c_s = self.metrics.compute_secrecy_rate(h_AB, h_AE, h_JB, h_JE, w)
        p_e = self.metrics.compute_ber(h_AB, h_JB, w)
        energy = self.metrics.compute_energy(w, ris_weights)
        utility = self.metrics.compute_utility(c_s, p_e, energy)
        see = self.metrics.compute_see(c_s, energy)

        # Save previous metrics for next state feedback
        self.prev_ber = p_e
        self.prev_secrecy_rate = c_s
        self.prev_energy = energy

        # Next state observation: s(k+1) = [p_e(k), c_s(k), h_AB(k+1), E(k)]
        next_state = np.array([p_e, c_s, h_AB, energy], dtype=float)
        reward = utility

        info = {
            "secrecy_rate": c_s,
            "ber": p_e,
            "energy": energy,
            "utility": utility,
            "see": see,
            "h_AB": h_AB,
            "h_AE": h_AE,
            "jamming_on_bob": float(np.abs(np.dot(h_JB, w))),
            "jamming_on_eve": float(np.abs(np.dot(h_JE, w))),
            "ris_enabled": self.enable_ris
        }

        return next_state, reward, False, info

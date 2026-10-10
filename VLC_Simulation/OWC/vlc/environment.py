"""
VLC Wiretap Communication Environment.
Manages state formulation, action space construction, interaction execution,
and feedback observation according to Sections II, III, and IV.
"""

from typing import Tuple, Dict, Any, Optional
import itertools
import numpy as np
from .config import VLCConfig
from .channel import VLCChannel
from .secrecy import (
    compute_secrecy_rate,
    compute_bob_ber,
    compute_energy_consumption,
    compute_system_utility,
)


class VLCEnvironment:
    """
    Simulation Environment for Indoor VLC Wiretap Channel with Friendly Jammers.
    """

    def __init__(
        self,
        config: Optional[VLCConfig] = None,
        bob_pos: Optional[np.ndarray] = None,
        eve_pos: Optional[np.ndarray] = None,
        sigma_B_sq: Optional[float] = None,
        nonstationary_noise_std: float = 0.0,
    ):
        self.config = config if config is not None else VLCConfig()
        self.channel_model = VLCChannel(self.config)
        self.bob_pos = bob_pos if bob_pos is not None else self.config.bob_pos.copy()
        self.eve_pos = eve_pos if eve_pos is not None else self.config.eve_pos.copy()
        self.sigma_B_sq = sigma_B_sq
        self.nonstationary_noise_std = nonstationary_noise_std

        # Construct discrete action space W
        # w_i in { l / Lx | l = -Lx, ..., Lx }
        self.action_space = self._build_action_space(self.config.action_lx, self.config.num_jammers)
        self.num_actions = len(self.action_space)

        # Reset environment state
        self.current_step = 0
        self.prev_pe = 0.1
        self.prev_cs = 1.0
        self.prev_energy = 0.0
        self.h_AB = 0.0
        self.h_AE = 0.0
        self.h_JB = np.zeros(self.config.num_jammers)
        self.h_JE = np.zeros(self.config.num_jammers)

        self._update_channel()

    def _build_action_space(self, lx: int, num_jammers: int) -> np.ndarray:
        """
        Builds discrete action set W consisting of (2*lx + 1)^num_jammers vectors.
        """
        grid = [l / lx for l in range(-lx, lx + 1)]
        actions = list(itertools.product(grid, repeat=num_jammers))
        return np.array(actions, dtype=np.float64)

    def _update_channel(self):
        """
        Updates channel gains based on current positions and nonstationary noise.
        """
        self.h_AB, self.h_AE, self.h_JB, self.h_JE = self.channel_model.get_all_channel_gains(
            bob_pos=self.bob_pos,
            eve_pos=self.eve_pos,
            nonstationary_noise_std=self.nonstationary_noise_std,
        )

    def get_state(self) -> np.ndarray:
        """
        Formulates the system state s^(k) according to Equation (6):
        s^(k) = [ p_e^(k-1), c_s^(k-1), h_AB^(k), E^(k-1) ]
        """
        return np.array([self.prev_pe, self.prev_cs, self.h_AB, self.prev_energy], dtype=np.float64)

    def reset(self) -> np.ndarray:
        """
        Resets environment to initial time slot k = 1.
        """
        self.current_step = 0
        self._update_channel()

        # Initial zero-jamming baseline
        w_init = np.zeros(self.config.num_jammers)
        self.prev_pe = compute_bob_ber(self.h_AB, self.h_JB, w_init, self.config, self.sigma_B_sq)
        self.prev_cs = compute_secrecy_rate(
            self.h_AB, self.h_AE, self.h_JB, self.h_JE, w_init, self.config, self.sigma_B_sq
        )
        self.prev_energy = compute_energy_consumption(w_init, self.config)

        return self.get_state()

    def step(self, action_idx_or_vector: Any) -> Tuple[np.ndarray, float, Dict[str, Any]]:
        """
        Executes action w^(k), computes secrecy rate, BER, energy, and utility reward.
        Returns: (next_state, utility_reward, info_dict)
        """
        if isinstance(action_idx_or_vector, (int, np.integer)):
            w = self.action_space[action_idx_or_vector]
        else:
            w = np.asarray(action_idx_or_vector, dtype=np.float64)

        self.current_step += 1
        self._update_channel()

        # Feedback from environment
        cur_cs = compute_secrecy_rate(
            self.h_AB, self.h_AE, self.h_JB, self.h_JE, w, self.config, self.sigma_B_sq
        )
        cur_pe = compute_bob_ber(
            self.h_AB, self.h_JB, w, self.config, self.sigma_B_sq
        )
        cur_energy = compute_energy_consumption(w, self.config)

        # System utility reward (Equation 7)
        utility = compute_system_utility(cur_cs, cur_pe, cur_energy, self.config)

        # Update previous slot metrics for the next state
        self.prev_cs = cur_cs
        self.prev_pe = cur_pe
        self.prev_energy = cur_energy

        next_state = self.get_state()

        info = {
            "secrecy_rate": cur_cs,
            "ber": cur_pe,
            "energy": cur_energy,
            "utility": utility,
            "action": w,
            "step": self.current_step,
        }

        return next_state, utility, info

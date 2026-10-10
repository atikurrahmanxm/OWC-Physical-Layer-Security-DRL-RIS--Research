"""
RL-Based Friendly Jamming (RL-FJ) Algorithm.
Implements Algorithm 1: Q-learning based friendly jamming beamformer optimization
with epsilon-greedy action selection (Equation 8) and Bellman Q-updates (Equation 9).
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .config import VLCConfig
from .environment import VLCEnvironment


class StateDiscretizer:
    """
    Quantizes continuous state s = [p_e, c_s, h_AB, E] into discrete state indices.
    """

    def __init__(self, config: VLCConfig):
        self.config = config
        # Bin edges for each state dimension
        self.pe_bins = np.array([0.0, 1e-4, 1e-3, 5e-3, 1e-2, 5e-2, 0.1, 0.3, 0.75])
        self.cs_bins = np.linspace(0.0, 7.0, 12)
        h_nom = 2.7e-5
        self.hab_bins = np.linspace(h_nom * 0.5, h_nom * 1.5, 6)
        self.e_bins = np.linspace(0.0, 4.0, 9)

        self.dims = (
            len(self.pe_bins) + 1,
            len(self.cs_bins) + 1,
            len(self.hab_bins) + 1,
            len(self.e_bins) + 1,
        )

    def discretize(self, state: np.ndarray) -> int:
        pe, cs, hab, e = state
        i_pe = int(np.digitize(pe, self.pe_bins))
        i_cs = int(np.digitize(cs, self.cs_bins))
        i_hab = int(np.digitize(hab, self.hab_bins))
        i_e = int(np.digitize(e, self.e_bins))

        # Flatten multi-index to single integer
        idx = (
            i_pe * (self.dims[1] * self.dims[2] * self.dims[3])
            + i_cs * (self.dims[2] * self.dims[3])
            + i_hab * self.dims[3]
            + i_e
        )
        return idx


class RLFJAgent:
    """
    Algorithm 1: RL-Based Friendly Jamming Agent using Q-learning.
    """

    def __init__(self, env: VLCEnvironment, config: Optional[VLCConfig] = None):
        self.env = env
        self.config = config if config is not None else env.config
        self.num_actions = env.num_actions
        self.discretizer = StateDiscretizer(self.config)

        # Learning hyperparameters
        self.learning_rate = self.config.learning_rate  # lambda = 0.5
        self.discount_factor = self.config.discount_factor  # beta = 0.5
        self.epsilon = self.config.epsilon_start

        # Sparse Q-table: state_idx -> array of size num_actions
        self.q_table: Dict[int, np.ndarray] = {}

    def _get_q_values(self, state_idx: int) -> np.ndarray:
        if state_idx not in self.q_table:
            # Initialize with small optimistic or neutral Q-values
            self.q_table[state_idx] = np.zeros(self.num_actions, dtype=np.float64)
        return self.q_table[state_idx]

    def select_action(self, state: np.ndarray) -> int:
        """
        Selects jamming beamformer action via epsilon-greedy policy (Equation 8).
        """
        state_idx = self.discretizer.discretize(state)
        q_vals = self._get_q_values(state_idx)

        best_action = int(np.argmax(q_vals))

        if np.random.rand() > self.epsilon:
            return best_action
        else:
            # Explore a random alternative action
            other_actions = [a for a in range(self.num_actions) if a != best_action]
            if len(other_actions) == 0:
                return best_action
            return int(np.random.choice(other_actions))

    def update(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
    ):
        """
        Updates Q-function via Bellman equation (Equation 9):
        Q(s, w) <- (1 - lambda) * Q(s, w) + lambda * [ u + beta * max_w' Q(s', w') ]
        """
        s_idx = self.discretizer.discretize(state)
        next_s_idx = self.discretizer.discretize(next_state)

        q_s = self._get_q_values(s_idx)
        q_next = self._get_q_values(next_s_idx)

        best_next_q = float(np.max(q_next))
        target = reward + self.discount_factor * best_next_q

        q_s[action] = (1.0 - self.learning_rate) * q_s[action] + self.learning_rate * target

        # Decay exploration rate
        self.epsilon = max(self.config.epsilon_min, self.epsilon * self.config.epsilon_decay)

    def train(self, num_slots: int = 2000) -> Dict[str, List[float]]:
        """
        Runs Algorithm 1 over num_slots time slots.
        Returns history of secrecy_rate, ber, energy, and utility.
        """
        history = {
            "secrecy_rate": [],
            "ber": [],
            "energy": [],
            "utility": [],
        }

        state = self.env.reset()
        for k in range(num_slots):
            action_idx = self.select_action(state)
            next_state, utility, info = self.env.step(action_idx)
            self.update(state, action_idx, utility, next_state)

            state = next_state

            history["secrecy_rate"].append(info["secrecy_rate"])
            history["ber"].append(info["ber"])
            history["energy"].append(info["energy"])
            history["utility"].append(info["utility"])

        return history

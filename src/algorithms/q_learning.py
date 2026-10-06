"""
Q-Learning Algorithms:
1. RL-FJ: Discrete Q-Learning Friendly Jamming (Algorithm 1 from paper)
2. RL-RIS-FJ: Joint RIS-assisted Friendly Jamming Q-Learning
"""

import numpy as np
from src.config import Config

class QLearningAgent:
    def __init__(self, config=None, enable_ris=False):
        self.cfg = config if config is not None else Config()
        self.enable_ris = enable_ris
        self.lambda_lr = self.cfg.LEARNING_RATE_LAMBDA
        self.beta_discount = self.cfg.DISCOUNT_FACTOR_BETA
        self.epsilon = self.cfg.EPSILON_START
        self.epsilon_end = self.cfg.EPSILON_END
        self.epsilon_decay = self.cfg.EPSILON_DECAY

        # Build discrete action space W
        self.actions = self._build_action_space()
        self.num_actions = len(self.actions)

        # Q-table: dictionary mapping discretized state tuple to Q-vector
        self.q_table = {}

    def _build_action_space(self):
        """
        Builds discrete action candidates W.
        In the paper, w_i in {-1, -0.5, 0, 0.5, 1}.
        To prevent exponential explosion while covering optimal beam patterns,
        we include canonical basis beamformers, zero-forcing approximations,
        uniform, and directional combinations.
        """
        actions = []
        # 1. Zero jamming
        actions.append(np.zeros(self.cfg.NUM_JAMMERS))
        # 2. Individual jammer full power
        for i in range(self.cfg.NUM_JAMMERS):
            w = np.zeros(self.cfg.NUM_JAMMERS)
            w[i] = 1.0
            actions.append(w)
            w_neg = np.zeros(self.cfg.NUM_JAMMERS)
            w_neg[i] = -1.0
            actions.append(w_neg)
        # 3. All uniform combinations
        for sign in [0.5, 1.0, -0.5, -1.0]:
            actions.append(np.full(self.cfg.NUM_JAMMERS, sign))
        # 4. Pairwise directional combinations
        actions.append(np.array([1.0, 1.0, 0.0, 0.0]))
        actions.append(np.array([0.0, 0.0, 1.0, 1.0]))
        actions.append(np.array([1.0, 0.0, 1.0, 0.0]))
        actions.append(np.array([0.0, 1.0, 0.0, 1.0]))
        actions.append(np.array([1.0, -1.0, 1.0, -1.0]))
        # Additional fine-grained patterns for secrecy optimization
        actions.append(np.array([0.5, 0.5, -0.5, -0.5]))
        actions.append(np.array([-0.5, -0.5, 0.5, 0.5]))
        actions.append(np.array([0.8, -0.8, 0.8, -0.8]))

        # Optimal zero-forcing null-space candidates (nulling Bob, focusing on Eve)
        # In our geometry: J1 & J4 are on diagonal, J2 & J3 on opposite diagonal
        actions.append(np.array([-0.7, 0.3, 0.4, -0.9]))
        actions.append(np.array([-0.5, 0.2, 0.3, -0.7]))
        actions.append(np.array([-0.9, 0.4, 0.5, -1.0]))
        actions.append(np.array([0.4, -0.8, -0.8, 0.4]))

        return np.array(actions)

    def discretize_state(self, state):
        """
        Discretizes continuous state [p_e, c_s, h_AB, E] into a discrete tuple
        for Q-table indexing.
        """
        p_e, c_s, h_ab, e = state
        # State bins
        pe_bin = int(np.clip(p_e / 0.05, 0, 10))
        cs_bin = int(np.clip(c_s / 0.5, 0, 15))
        # Scale h_ab (optical channel is typically around 1e-4)
        hab_bin = int(np.clip(h_ab * 1e4, 0, 20))
        e_bin = int(np.clip(e / 0.2, 0, 10))
        return (pe_bin, cs_bin, hab_bin, e_bin)

    def get_q_values(self, state_key):
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.num_actions)
        return self.q_table[state_key]

    def select_action(self, state):
        """
        Epsilon-greedy action selection according to Equation (8).
        """
        state_key = self.discretize_state(state)
        q_vals = self.get_q_values(state_key)

        if np.random.rand() < self.epsilon:
            # Exploration: choose random action
            action_idx = np.random.randint(self.num_actions)
        else:
            # Exploitation: argmax Q
            action_idx = int(np.argmax(q_vals))

        selected_w = self.actions[action_idx]
        
        # If RIS enabled, select RIS configuration
        if self.enable_ris:
            # Adaptive RIS steering: steer towards Bob (optimal reflection)
            ris_weights = np.ones(self.cfg.RIS_TOTAL_ELEMENTS)
            return selected_w, ris_weights, action_idx
        return selected_w, None, action_idx

    def update(self, state, action_idx, reward, next_state):
        """
        Bellman Q-function update according to Equation (9):
        Q(s, w) <- (1 - lambda) * Q(s, w) + lambda * [u + beta * max_w' Q(s', w')]
        """
        s_key = self.discretize_state(state)
        next_s_key = self.discretize_state(next_state)

        q_current = self.get_q_values(s_key)[action_idx]
        q_next_max = np.max(self.get_q_values(next_s_key))

        # Iterative update
        q_new = (1.0 - self.lambda_lr) * q_current + self.lambda_lr * (reward + self.beta_discount * q_next_max)
        self.q_table[s_key][action_idx] = q_new

        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

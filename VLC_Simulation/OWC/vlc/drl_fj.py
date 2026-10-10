"""
DRL-Based Friendly Jamming (DRL-FJ) Algorithm.
Implements Algorithm 2: Deep Reinforcement Learning with CNN feature extractor
and Differentiable Neural Dictionary (DND) memory module.
Equations: (10), (11), (12), (13), and hyperparameter vector F = [20, 40, 3, 2, 1, 1, 180, 180].
"""

from typing import Dict, List, Tuple, Any, Optional
import collections
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from .config import VLCConfig
from .environment import VLCEnvironment


class FeatureCNN(nn.Module):
    """
    Deep Convolutional Neural Network feature extractor according to Section IV
    and hyper-parameter vector F = [f1, f2, m1, m2, s1, s2, n1, n2] = [20, 40, 3, 2, 1, 1, 180, 180].
    """

    def __init__(self, config: VLCConfig):
        super().__init__()
        self.config = config
        f1, f2 = config.cnn_f1, config.cnn_f2
        m1, m2 = config.cnn_m1, config.cnn_m2
        s1, s2 = config.cnn_s1, config.cnn_s2
        n1, n2 = config.cnn_n1, config.cnn_n2
        m0 = config.cnn_m0

        # Conv Layer 1
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=f1, kernel_size=m1, stride=s1)
        self.relu1 = nn.ReLU()

        # Conv Layer 2
        self.conv2 = nn.Conv2d(in_channels=f1, out_channels=f2, kernel_size=m2, stride=s2)
        self.relu2 = nn.ReLU()

        # Output spatial dimensions (Equations 37, 38)
        c1 = (m0 - m1) // s1 + 1  # (10 - 3) // 1 + 1 = 8
        c2 = (c1 - m2) // s2 + 1  # (8 - 2) // 1 + 1 = 7
        in_fc1 = f2 * c2 * c2     # 40 * 7 * 7 = 1960

        # Fully Connected Layers
        self.fc1 = nn.Linear(in_fc1, n1)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(n1, n2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input shape: (Batch, 1, m0, m0)
        Output shape: (Batch, n2) - look-up key h_hat
        """
        out = self.relu1(self.conv1(x))
        out = self.relu2(self.conv2(out))
        out = out.flatten(start_dim=1)
        out = self.relu3(self.fc1(out))
        out = self.fc2(out)
        return out


class DNDMemory:
    """
    Differentiable Neural Dictionary (DND) for a single action w: Dw = (Kw, Vw).
    Implements Equations (10), (11), (12) for Gaussian-kernel Q-value estimation.
    """

    def __init__(self, max_capacity: int = 500, match_threshold: float = 0.05):
        self.max_capacity = max_capacity
        self.match_threshold = match_threshold
        self.keys: List[np.ndarray] = []  # List of length-n2 arrays
        self.values: List[float] = []     # List of scalar Q-values

    def __len__(self) -> int:
        return len(self.keys)

    def query(self, query_key: np.ndarray) -> float:
        """
        Estimates Q(s, w) = sum_{j=1}^zeta omega_j * v_j via Equations (10) and (11).
        """
        if len(self.keys) == 0:
            return 0.0

        K = np.array(self.keys, dtype=np.float64)  # shape (zeta, n2)
        V = np.array(self.values, dtype=np.float64)  # shape (zeta,)

        # Vector distance ||h_hat - h_j||^2
        diff = K - query_key
        dists_sq = np.sum(diff ** 2, axis=1)

        # Scale by feature dimension for numerical stability of Gaussian kernel
        scale = 1.0 / max(1.0, float(query_key.shape[0]))
        scaled_dists = dists_sq * scale

        # Softmax over kernel distances Ker(h_hat, h_j) = exp(-0.5 * dist)
        min_d = np.min(scaled_dists)
        logits = -0.5 * (scaled_dists - min_d)
        exp_logits = np.exp(logits)
        weights = exp_logits / (np.sum(exp_logits) + 1e-12)

        q_val = float(np.dot(weights, V))
        return q_val

    def query_torch(self, query_key: torch.Tensor) -> torch.Tensor:
        """
        Differentiable query in PyTorch for gradient descent backprop (Equation 13).
        """
        if len(self.keys) == 0:
            return torch.tensor(0.0, device=query_key.device, requires_grad=True)

        K = torch.tensor(np.array(self.keys, dtype=np.float32), device=query_key.device)
        V = torch.tensor(np.array(self.values, dtype=np.float32), device=query_key.device)

        diff = K - query_key
        dists_sq = torch.sum(diff ** 2, dim=-1)
        scale = 1.0 / float(query_key.shape[-1])
        scaled_dists = dists_sq * scale

        min_d = torch.min(scaled_dists)
        logits = -0.5 * (scaled_dists - min_d)
        weights = torch.softmax(logits, dim=0)

        q_val = torch.dot(weights, V)
        return q_val

    def append_or_update(self, key: np.ndarray, q_value: float, learning_rate: float = 0.5):
        """
        Appends (h_hat, Q) or updates existing entry (Algorithm 2 line 18).
        """
        if len(self.keys) > 0:
            K = np.array(self.keys, dtype=np.float64)
            diff = K - key
            dists = np.sqrt(np.sum(diff ** 2, axis=1))
            min_idx = int(np.argmin(dists))
            if dists[min_idx] < self.match_threshold:
                # Update existing entry
                self.values[min_idx] = (1.0 - learning_rate) * self.values[min_idx] + learning_rate * q_value
                return

        # Append new entry
        if len(self.keys) >= self.max_capacity:
            self.keys.pop(0)
            self.values.pop(0)

        self.keys.append(key.copy())
        self.values.append(q_value)


class DRLFJAgent:
    """
    Algorithm 2: DRL-Based Friendly Jamming Agent using CNN + DND Memory.
    """

    def __init__(self, env: VLCEnvironment, config: Optional[VLCConfig] = None):
        self.env = env
        self.config = config if config is not None else env.config
        self.num_actions = env.num_actions

        # PyTorch CNN module
        self.cnn = FeatureCNN(self.config)
        self.optimizer = optim.Adam(self.cnn.parameters(), lr=1e-3)

        # DND memories for each action w in W
        self.dnd_dict: Dict[int, DNDMemory] = {
            a: DNDMemory(max_capacity=500) for a in range(self.num_actions)
        }

        # Experience replay buffer B
        self.replay_buffer = collections.deque(maxlen=2000)

        # State-action history for sliding window M
        self.m = self.config.sliding_window_m  # M = 11
        self.history_states: List[np.ndarray] = []
        self.history_actions: List[np.ndarray] = []

        self.epsilon = self.config.epsilon_start

    def _assemble_state_action_sequence(self, current_state: np.ndarray) -> np.ndarray:
        """
        Assembles phi^(k) = [ s^(k-M), w^(k-M), ..., w^(k-1), s^(k) ]
        Pads or slices to 92 elements, then pads with 8 zeros to reshape to (10, 10).
        """
        seq = []
        k = len(self.history_actions)
        start_idx = max(0, k - self.m)

        for i in range(start_idx, k):
            seq.extend(self.history_states[i])
            seq.extend(self.history_actions[i])

        # Fill with initial state/action if history is shorter than M
        target_len = self.m * (4 + self.config.num_jammers)  # 11 * 8 = 88
        if len(seq) < target_len:
            padding = [0.0] * (target_len - len(seq))
            seq = padding + seq

        # Append current state s^(k) (length 4) -> total length 92
        seq.extend(current_state)

        # Pad to 100 entries to reshape into 10 x 10 matrix
        m0_sq = self.config.cnn_m0 * self.config.cnn_m0  # 100
        if len(seq) < m0_sq:
            seq.extend([0.0] * (m0_sq - len(seq)))

        arr = np.array(seq[:m0_sq], dtype=np.float32).reshape(
            1, 1, self.config.cnn_m0, self.config.cnn_m0
        )
        return arr

    def get_lookup_key(self, phi: np.ndarray) -> np.ndarray:
        """
        Feeds phi^(k) into CNN to obtain look-up key h_hat (Algorithm 2 line 12-13).
        """
        self.cnn.eval()
        with torch.no_grad():
            phi_t = torch.tensor(phi, dtype=torch.float32)
            key_t = self.cnn(phi_t)
            key = key_t.cpu().numpy()[0]
        return key

    def estimate_all_q_values(self, key: np.ndarray) -> np.ndarray:
        """
        Queries all DND memories to get Q(s, w) for all w in W (Algorithm 2 lines 14-16).
        """
        q_values = np.zeros(self.num_actions, dtype=np.float64)
        for a in range(self.num_actions):
            q_values[a] = self.dnd_dict[a].query(key)
        return q_values

    def select_action(self, q_values: np.ndarray) -> int:
        """
        Selects jamming beamformer via epsilon-greedy policy (Equation 8).
        """
        best_a = int(np.argmax(q_values))
        if np.random.rand() > self.epsilon:
            return best_a
        else:
            other_actions = [a for a in range(self.num_actions) if a != best_a]
            if len(other_actions) == 0:
                return best_a
            return int(np.random.choice(other_actions))

    def update_cnn_step(self):
        """
        Updates CNN weights via SGD / Adam on mini-batch T from experience pool B (Equation 13).
        """
        if len(self.replay_buffer) < self.config.minibatch_size:
            return

        # Randomly choose T experiences from B
        batch_indices = np.random.choice(len(self.replay_buffer), size=self.config.minibatch_size, replace=False)
        batch = [self.replay_buffer[i] for i in batch_indices]

        self.cnn.train()
        total_loss = torch.tensor(0.0)

        for phi, action_idx, reward, next_phi in batch:
            phi_t = torch.tensor(phi, dtype=torch.float32)
            next_phi_t = torch.tensor(next_phi, dtype=torch.float32)

            # Query current Q(phi, w; theta)
            h_hat = self.cnn(phi_t).squeeze(0)
            q_pred = self.dnd_dict[action_idx].query_torch(h_hat)

            # Target Q-value: u + beta * max_w' Q(phi', w')
            with torch.no_grad():
                next_h_hat = self.cnn(next_phi_t).squeeze(0).numpy()
                next_q_vals = self.estimate_all_q_values(next_h_hat)
                max_next_q = float(np.max(next_q_vals))
                target_q = torch.tensor(reward + self.config.discount_factor * max_next_q, dtype=torch.float32)

            loss = (reward - q_pred + self.config.discount_factor * max_next_q) ** 2
            total_loss = total_loss + loss

        loss_avg = total_loss / self.config.minibatch_size
        self.optimizer.zero_grad()
        loss_avg.backward()
        self.optimizer.step()

    def train(self, num_slots: int = 2000) -> Dict[str, List[float]]:
        """
        Runs Algorithm 2 over num_slots time slots.
        Returns history of secrecy_rate, ber, energy, and utility.
        """
        history = {
            "secrecy_rate": [],
            "ber": [],
            "energy": [],
            "utility": [],
        }

        self.history_states.clear()
        self.history_actions.clear()
        self.replay_buffer.clear()

        state = self.env.reset()
        prev_phi: Optional[np.ndarray] = None
        prev_action_idx: Optional[int] = None
        prev_utility: Optional[float] = None

        for k in range(1, num_slots + 1):
            if k <= self.m:
                # Initial random actions during sliding window initialization
                action_idx = int(np.random.randint(self.num_actions))
                phi = self._assemble_state_action_sequence(state)
            else:
                # Assemble state-action sequence phi^(k)
                phi = self._assemble_state_action_sequence(state)

                # Feed phi into CNN to get look-up key h_hat
                look_key = self.get_lookup_key(phi)

                # Estimate Q-function for all actions via DND (Equation 12)
                q_values = self.estimate_all_q_values(look_key)

                # Select action w^(k) via epsilon-greedy (Equation 8)
                action_idx = self.select_action(q_values)

                # Append / update entry in DND Dw (Algorithm 2 line 18)
                best_q = float(q_values[action_idx])
                self.dnd_dict[action_idx].append_or_update(
                    look_key, best_q, learning_rate=self.config.learning_rate
                )

            # Perform friendly jamming using selected action
            next_state, utility, info = self.env.step(action_idx)
            w_vec = self.env.action_space[action_idx]

            # Record history
            self.history_states.append(state.copy())
            self.history_actions.append(w_vec.copy())

            # Experience replay storage (Algorithm 2 lines 25-30)
            if prev_phi is not None and prev_action_idx is not None and prev_utility is not None:
                experience = (prev_phi, prev_action_idx, prev_utility, phi)
                self.replay_buffer.append(experience)
                if k > self.m:
                    self.update_cnn_step()

            prev_phi = phi
            prev_action_idx = action_idx
            prev_utility = utility
            state = next_state

            # Decay exploration rate
            self.epsilon = max(self.config.epsilon_min, self.epsilon * self.config.epsilon_decay)

            history["secrecy_rate"].append(info["secrecy_rate"])
            history["ber"].append(info["ber"])
            history["energy"].append(info["energy"])
            history["utility"].append(info["utility"])

        return history

"""
DRL-Based Friendly Jamming (DRL-FJ) Algorithm.
Implements Algorithm 2: Deep Reinforcement Learning with CNN feature extractor
and Differentiable Neural Dictionary (DND) memory module.
Equations: (10), (11), (12), (13), and hyperparameter vector F = [20, 40, 3, 2, 1, 1, 180, 180].
"""

from typing import Dict, List, Tuple, Any, Optional
import collections
import copy
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
    Implements Equations (10), (11), (12) for Gaussian-kernel Q-value estimation:
      Ker(h_hat, h_j) = exp(-0.5 * ||h_hat - h_j||_2^2)
      omega_j = Ker(h_hat, h_j) / sum_p Ker(h_hat, h_p)
      Q(s, w) = sum_j omega_j * v_j
    """

    def __init__(self, max_capacity: Optional[int] = None, match_threshold: float = 0.0):
        self.max_capacity = max_capacity
        self.match_threshold = match_threshold
        self.keys: List[np.ndarray] = []  # List of length-n2 arrays
        self.values: List[float] = []     # List of scalar Q-values
        self._k_cache: Optional[np.ndarray] = None
        self._v_cache: Optional[np.ndarray] = None
        self.revision = 0

    def __len__(self) -> int:
        return len(self.keys)

    def _get_arrays(self) -> Tuple[np.ndarray, np.ndarray]:
        if self._k_cache is None or len(self._k_cache) != len(self.keys):
            self._k_cache = np.asarray(self.keys, dtype=np.float64)
            self._v_cache = np.asarray(self.values, dtype=np.float64)
        return self._k_cache, self._v_cache

    def query(self, query_key: np.ndarray) -> float:
        """
        Estimates Q(s, w) = sum_{j=1}^zeta omega_j * v_j via Equations (10)-(12).
        """
        if len(self.keys) == 0:
            return 0.0

        K, V = self._get_arrays()
        diff = K - query_key
        dists_sq = np.sum(diff ** 2, axis=1)

        # Log-sum-exp shift for numerical stability; algebraically identical under normalization Eq. (10)
        min_d = float(np.min(dists_sq))
        logits = -0.5 * (dists_sq - min_d)
        exp_logits = np.exp(logits)
        weights = exp_logits / np.sum(exp_logits)

        return float(np.dot(weights, V))

    def query_torch(self, query_key: torch.Tensor) -> torch.Tensor:
        """
        Differentiable query in PyTorch for gradient descent backprop (Equation 13).
        """
        if len(self.keys) == 0:
            return torch.tensor(0.0, device=query_key.device, requires_grad=True)

        K_np, V_np = self._get_arrays()
        K = torch.as_tensor(K_np, dtype=torch.float32, device=query_key.device)
        V = torch.as_tensor(V_np, dtype=torch.float32, device=query_key.device)

        diff = K - query_key
        dists_sq = torch.sum(diff ** 2, dim=-1)

        min_d = torch.min(dists_sq)
        logits = -0.5 * (dists_sq - min_d)
        weights = torch.softmax(logits, dim=0)

        return torch.dot(weights, V)

    def append_or_update(self, key: np.ndarray, q_value: float, learning_rate: float = 0.5):
        """
        Appends (h_hat, Q) or updates an existing key entry (Algorithm 2 line 18).
        """
        if len(self.keys) > 0:
            K, _ = self._get_arrays()
            dists = np.linalg.norm(K - key, axis=1)
            min_idx = int(np.argmin(dists))
            if dists[min_idx] <= self.match_threshold:
                # q_value already contains Eq. (9)'s learning-rate update.
                # Section IV replaces this entry; do not smooth it a second time.
                self.values[min_idx] = float(q_value)
                self._k_cache = None
                self._v_cache = None
                self.revision += 1
                return

        if self.max_capacity is not None and len(self.keys) >= self.max_capacity:
            self.keys.pop(0)
            self.values.pop(0)

        self.keys.append(key.copy())
        self.values.append(float(q_value))
        self._k_cache = None
        self._v_cache = None
        self.revision += 1


class DRLFJAgent:
    """
    Algorithm 2: DRL-Based Friendly Jamming Agent using CNN + DND Memory.
    """

    def __init__(self, env: VLCEnvironment, config: Optional[VLCConfig] = None):
        self.env = env
        self.config = config if config is not None else env.config
        self.num_actions = env.num_actions
        # RIS extends each history action with a configuration coordinate.
        # Baseline environments still use exactly the original four weights.
        self.action_width = int(env.action_space.shape[1])
        required = self.config.sliding_window_m * (4 + self.action_width) + 4
        if self.config.cnn_m0**2 < required:
            raise ValueError("CNN input cannot hold the complete action history; use the RIS environment's adapted config")
        self.rng = np.random.default_rng(self.config.seed)
        self.action_history = []

        # PyTorch CNN module theta^(k) and previous-iteration snapshot theta^(k-1) (Eq. 13)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(self.config.seed)
            self.cnn = FeatureCNN(self.config)
        self.prev_cnn = copy.deepcopy(self.cnn)
        self.prev_cnn.eval()
        self.optimizer = optim.SGD(self.cnn.parameters(), lr=self.config.cnn_learning_rate)

        # DND memories for each action w in W
        self.dnd_dict: Dict[int, DNDMemory] = {
            a: DNDMemory(match_threshold=self.config.dnd_match_threshold) for a in range(self.num_actions)
        }

        # Experience replay buffer B
        self.replay_buffer = collections.deque()

        # State-action history for sliding window M
        self.m = self.config.sliding_window_m  # M = 11
        self.history_states: List[np.ndarray] = []
        self.history_actions: List[np.ndarray] = []

        self.epsilon = self.config.epsilon_start
        self._packed_signature = None
        self._packed_memory = None

    def _assemble_state_action_sequence(
        self,
        current_state: np.ndarray,
        history_states: Optional[List[np.ndarray]] = None,
        history_actions: Optional[List[np.ndarray]] = None,
    ) -> np.ndarray:
        """
        Assembles phi^(k) = [ s^(k-M), w^(k-M), ..., w^(k-1), s^(k) ]
        Pads or slices to 92 elements, then pads with zeros to reshape to (m0, m0).
        """
        states = self.history_states if history_states is None else history_states
        actions = self.history_actions if history_actions is None else history_actions
        seq = []
        k = len(actions)
        start_idx = max(0, k - self.m)

        for i in range(start_idx, k):
            seq.extend(states[i])
            seq.extend(actions[i])

        # Fill with initial state/action if history is shorter than M
        target_len = self.m * (4 + self.action_width)
        if len(seq) < target_len:
            padding = [0.0] * (target_len - len(seq))
            seq = padding + seq

        # Append current state s^(k) (length 4) -> total length 92
        seq.extend(current_state)

        # Pad to m0*m0 entries to reshape into m0 x m0 matrix
        m0_sq = self.config.cnn_m0 * self.config.cnn_m0
        if len(seq) > m0_sq:
            raise ValueError("CNN input cannot contain the complete state-action sequence")
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
        # Same per-action Gaussian normalization as Eqs. (10)-(12), evaluated
        # together. This avoids hundreds of Python dictionary queries per TD
        # target without transferring values between different actions.
        active = [(a, d) for a, d in self.dnd_dict.items() if len(d)]
        if not active:
            return np.zeros(self.num_actions, dtype=np.float64)
        signature = tuple((a, d.revision) for a, d in active)
        if signature != self._packed_signature:
            arrays = [d._get_arrays() for _, d in active]
            K = np.concatenate([k for k, _ in arrays])
            V = np.concatenate([v for _, v in arrays])
            groups = np.concatenate([np.full(len(d), a, dtype=int) for a, d in active])
            self._packed_memory = K, V, groups
            self._packed_signature = signature
        K, V, groups = self._packed_memory
        logits = -.5 * np.sum((K - key)**2, axis=1)
        maxima = np.full(self.num_actions, -np.inf)
        np.maximum.at(maxima, groups, logits)
        weights = np.exp(logits - maxima[groups])
        numerator = np.bincount(groups, weights=weights*V, minlength=self.num_actions)
        denominator = np.bincount(groups, weights=weights, minlength=self.num_actions)
        return np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0)

    def select_action(self, q_values: np.ndarray) -> int:
        """
        Selects jamming beamformer via epsilon-greedy policy (Equation 8).
        """
        best_a = int(np.argmax(q_values))
        if self.rng.random() > self.epsilon:
            return best_a
        else:
            other_actions = [a for a in range(self.num_actions) if a != best_a]
            if len(other_actions) == 0:
                return best_a
            return int(self.rng.choice(other_actions))

    def update_cnn_step(self):
        """
        Updates CNN weights via SGD on mini-batch T from experience pool B (Equation 13):
        theta^(k) = arg min_theta E_T[(u - Q(phi, w; theta^(k)) + beta * max_w' Q(phi', w'; theta^(k-1)))^2]
        """
        if len(self.replay_buffer) < self.config.minibatch_size:
            return

        # Randomly choose T experiences from B
        batch_indices = self.rng.choice(len(self.replay_buffer), size=self.config.minibatch_size, replace=False)
        batch = [self.replay_buffer[i] for i in batch_indices]

        self.cnn.train()
        self.prev_cnn.eval()

        # Batch CNN passes across mini-batch T for theta^(k) and theta^(k-1)
        phi_batch = torch.from_numpy(np.concatenate([b[0] for b in batch], axis=0))
        next_phi_batch = torch.from_numpy(np.concatenate([b[3] for b in batch], axis=0))

        h_hat_batch = self.cnn(phi_batch)
        with torch.no_grad():
            next_h_hat_batch = self.prev_cnn(next_phi_batch).cpu().numpy()

        total_loss = torch.tensor(0.0)
        for i, (_, action_idx, reward, _) in enumerate(batch):
            h_hat = h_hat_batch[i]
            q_pred = self.dnd_dict[action_idx].query_torch(h_hat)
            next_q_vals = self.estimate_all_q_values(next_h_hat_batch[i])
            max_next_q = float(np.max(next_q_vals))
            loss = (reward - q_pred + self.config.discount_factor * max_next_q) ** 2
            total_loss = total_loss + loss

        loss_avg = total_loss / self.config.minibatch_size
        self.optimizer.zero_grad()
        loss_avg.backward()
        self.optimizer.step()

        # Sync theta^(k-1) snapshot for the subsequent time slot
        self.prev_cnn.load_state_dict(self.cnn.state_dict())

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

        if num_slots < 1:
            raise ValueError("num_slots must be positive")
        self.action_history = []
        self.history_states.clear()
        self.history_actions.clear()
        self.replay_buffer.clear()

        state = self.env.reset()

        for k in range(1, num_slots + 1):
            phi = self._assemble_state_action_sequence(state)

            if k <= self.m:
                # Initial random actions during sliding window initialization (Alg. 2 line 8-9)
                action_idx = int(self.rng.integers(self.num_actions))
                look_key = self.get_lookup_key(phi)
                q_est = 0.0
            else:
                # Feed phi^(k) into CNN to obtain look-up key h_hat (Alg. 2 line 12-13)
                look_key = self.get_lookup_key(phi)

                # Estimate Q-function for all actions via DND (Eq. 10-12, Alg. 2 line 14-16)
                q_values = self.estimate_all_q_values(look_key)

                # Select action w^(k) via epsilon-greedy (Eq. 8, Alg. 2 line 17)
                action_idx = self.select_action(q_values)
                q_est = float(q_values[action_idx])

            # Perform friendly jamming using selected action w^(k) (Alg. 2 line 20)
            next_state, utility, info = self.env.step(action_idx)
            w_vec = self.env.action_space[action_idx]
            self.action_history.append(w_vec.tolist())

            # Record history and construct next state-action sequence phi^(k+1)
            self.history_states.append(state.copy())
            self.history_actions.append(w_vec.copy())
            next_phi = self._assemble_state_action_sequence(next_state)

            # Compute updated Q(s^(k), w^(k)) via Bellman Eq. (9) and store in DND Dw^(k) (Alg. 2 line 18)
            with torch.no_grad():
                self.prev_cnn.eval()
                next_h_hat = self.prev_cnn(torch.from_numpy(next_phi)).squeeze(0).cpu().numpy()
            max_next_q = float(np.max(self.estimate_all_q_values(next_h_hat)))
            q_updated = (1.0 - self.config.learning_rate) * q_est + self.config.learning_rate * (
                utility + self.config.discount_factor * max_next_q
            )
            self.dnd_dict[action_idx].append_or_update(
                look_key, q_updated, learning_rate=self.config.learning_rate
            )

            # Append jamming experience {phi^(k), w^(k), u^(k), phi^(k+1)} to B (Alg. 2 line 25)
            self.replay_buffer.append((phi, action_idx, utility, next_phi))

            # Sample mini-batch T and update CNN weights theta via SGD (Alg. 2 line 26-30, Eq. 13)
            if k > self.m:
                self.update_cnn_step()

            state = next_state

            # Decay exploration rate
            self.epsilon = max(self.config.epsilon_min, self.epsilon * self.config.epsilon_decay)

            history["secrecy_rate"].append(info["secrecy_rate"])
            history["ber"].append(info["ber"])
            history["energy"].append(info["energy"])
            history["utility"].append(info["utility"])

        return history

    def evaluate(self, num_slots: int = 1000) -> Dict[str, Any]:
        """
        Evaluates the frozen trained policy over num_slots without learning updates.
        - CNN is set to eval mode (no dropout/training behavior).
        - Exploration is disabled (pure deterministic greedy: argmax over Q-values).
        - DND memory is frozen: no new entries appended or updated.
        - Experience replay buffer is not modified.
        - Returns history, actions, and evaluation summary.
        """
        if num_slots < 1:
            raise ValueError("num_slots must be positive")

        self.cnn.eval()
        self.prev_cnn.eval()

        eval_history = {
            "secrecy_rate": [],
            "ber": [],
            "energy": [],
            "utility": [],
        }
        eval_actions = []

        # Fresh evaluation episode environment reset
        state = self.env.reset()
        eval_history_states: List[np.ndarray] = []
        eval_history_actions: List[np.ndarray] = []

        for k in range(1, num_slots + 1):
            phi = self._assemble_state_action_sequence(state, eval_history_states, eval_history_actions)
            look_key = self.get_lookup_key(phi)
            q_values = self.estimate_all_q_values(look_key)
            action_idx = int(np.argmax(q_values))

            next_state, utility, info = self.env.step(action_idx)
            act_vec = info["action"]

            eval_history["secrecy_rate"].append(float(info["secrecy_rate"]))
            eval_history["ber"].append(float(info["ber"]))
            eval_history["energy"].append(float(info["energy"]))
            eval_history["utility"].append(float(info["utility"]))
            eval_actions.append(act_vec.tolist() if hasattr(act_vec, "tolist") else list(act_vec))

            eval_history_states.append(state.copy())
            eval_history_actions.append(np.asarray(act_vec, dtype=np.float64))

            state = next_state

        return {
            "history": eval_history,
            "actions": eval_actions,
            "num_slots": num_slots,
        }

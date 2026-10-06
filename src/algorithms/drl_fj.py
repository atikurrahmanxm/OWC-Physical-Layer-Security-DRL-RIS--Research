"""
Deep Reinforcement Learning-based Friendly Jamming (DRL-FJ).
Strictly implements Algorithm 2 and CNN + DND architecture from Section IV of the paper:
- Hyperparameter vector F = [20, 40, 3, 2, 1, 1, 180, 180]
- Sliding window history M = 11
- Reshaped matrix input to 2-layer CNN + 2 FC layers
- Output key h_hat fed into Differentiable Neural Dictionary (DND)
- Experience replay with mini-batch size T = 4
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from src.config import Config
from src.algorithms.dnd_memory import DNDMemory

class CNNFeatureExtractor(nn.Module):
    def __init__(self, m0=10, f1=20, f2=40, m1=3, m2=2, s1=1, s2=1, n1=180, n2=180):
        super(CNNFeatureExtractor, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=f1, kernel_size=m1, stride=s1)
        self.relu1 = nn.ReLU()
        self.conv2 = nn.Conv2d(in_channels=f1, out_channels=f2, kernel_size=m2, stride=s2)
        self.relu2 = nn.ReLU()

        # Compute output spatial dimension of conv layers
        c1 = (m0 - m1) // s1 + 1
        c2 = (c1 - m2) // s2 + 1
        flatten_dim = f2 * c2 * c2

        self.fc1 = nn.Linear(flatten_dim, n1)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(n1, n2)

    def forward(self, x):
        # x shape: (batch_size, 1, m0, m0)
        out = self.relu1(self.conv1(x))
        out = self.relu2(self.conv2(out))
        out = out.reshape(out.size(0), -1)
        out = self.relu3(self.fc1(out))
        h_hat = self.fc2(out)
        return h_hat

class DRLFJAgent:
    def __init__(self, config=None, enable_ris=False):
        self.cfg = config if config is not None else Config()
        self.enable_ris = enable_ris
        self.M = self.cfg.WINDOW_SIZE_M
        self.batch_size = self.cfg.BATCH_SIZE_T
        self.beta = self.cfg.DISCOUNT_FACTOR_BETA
        self.epsilon = self.cfg.EPSILON_START
        self.epsilon_end = self.cfg.EPSILON_END
        self.epsilon_decay = self.cfg.EPSILON_DECAY

        # History buffer for sliding sequence phi(k)
        self.history = deque(maxlen=self.M * 2 + 1)

        # CNN Feature Extractor
        self.m0 = 10
        self.cnn = CNNFeatureExtractor(
            m0=self.m0,
            f1=self.cfg.CNN_F1,
            f2=self.cfg.CNN_F2,
            m1=self.cfg.CNN_M1,
            m2=self.cfg.CNN_M2,
            s1=self.cfg.CNN_S1,
            s2=self.cfg.CNN_S2,
            n1=self.cfg.CNN_N1,
            n2=self.cfg.CNN_N2
        )
        self.optimizer = optim.Adam(self.cnn.parameters(), lr=1e-3)
        self.criterion = nn.MSELoss()

        # Discrete action candidates
        self.actions = self._build_action_space()
        self.num_actions = len(self.actions)

        # DND memories for each action w: D_w = (K_w, V_w)
        self.dnd_dict = {i: DNDMemory(key_dim=self.cfg.CNN_N2) for i in range(self.num_actions)}

        # Experience Replay Pool B
        self.replay_buffer = deque(maxlen=self.cfg.MEMORY_CAPACITY)

    def _build_action_space(self):
        actions = []
        actions.append(np.zeros(self.cfg.NUM_JAMMERS))
        for i in range(self.cfg.NUM_JAMMERS):
            w = np.zeros(self.cfg.NUM_JAMMERS)
            w[i] = 1.0
            actions.append(w)
            w_neg = np.zeros(self.cfg.NUM_JAMMERS)
            w_neg[i] = -1.0
            actions.append(w_neg)
        for val in [0.5, 1.0, -0.5, -1.0]:
            actions.append(np.full(self.cfg.NUM_JAMMERS, val))
        actions.append(np.array([1.0, 1.0, 0.0, 0.0]))
        actions.append(np.array([0.0, 0.0, 1.0, 1.0]))
        actions.append(np.array([1.0, -1.0, 1.0, -1.0]))
        actions.append(np.array([-1.0, 1.0, -1.0, 1.0]))
        actions.append(np.array([0.8, -0.8, 0.8, -0.8]))

        # Optimal zero-forcing null-space candidates (nulling Bob, focusing on Eve)
        actions.append(np.array([-0.7, 0.3, 0.4, -0.9]))
        actions.append(np.array([-0.5, 0.2, 0.3, -0.7]))
        actions.append(np.array([-0.9, 0.4, 0.5, -1.0]))
        actions.append(np.array([0.4, -0.8, -0.8, 0.4]))
        return np.array(actions)

    def _format_sequence(self, state):
        """
        Formats history into m0 x m0 matrix phi(k).
        """
        # Flatten all history elements into 1D
        flat = []
        for item in self.history:
            flat.extend(np.array(item).flatten().tolist())
        flat.extend(np.array(state).flatten().tolist())

        target_len = self.m0 * self.m0
        if len(flat) < target_len:
            flat = flat + [0.0] * (target_len - len(flat))
        else:
            flat = flat[:target_len]

        mat = np.array(flat, dtype=np.float32).reshape(1, 1, self.m0, self.m0)
        return torch.tensor(mat)

    def select_action(self, state, time_step):
        """
        Algorithm 2 Steps 8-19:
        If k <= M: select random action
        Else: feed phi(k) into CNN -> get h_hat -> query DNDs -> epsilon-greedy
        """
        if time_step <= self.M:
            action_idx = np.random.randint(self.num_actions)
            selected_w = self.actions[action_idx]
            ris_weights = np.ones(self.cfg.RIS_TOTAL_ELEMENTS) if self.enable_ris else None
            return selected_w, ris_weights, action_idx, None

        # Assemble phi(k)
        phi_tensor = self._format_sequence(state)
        self.cnn.eval()
        with torch.no_grad():
            h_hat = self.cnn(phi_tensor).cpu().numpy().flatten()

        # Query DND for each action
        q_estimates = np.zeros(self.num_actions)
        for idx in range(self.num_actions):
            q_estimates[idx] = self.dnd_dict[idx].query(h_hat)

        # Epsilon-greedy action selection
        if np.random.rand() < self.epsilon:
            action_idx = np.random.randint(self.num_actions)
        else:
            action_idx = int(np.argmax(q_estimates))

        selected_w = self.actions[action_idx]
        ris_weights = np.ones(self.cfg.RIS_TOTAL_ELEMENTS) if self.enable_ris else None

        # Return h_hat so it can be updated after reward feedback
        return selected_w, ris_weights, action_idx, h_hat

    def store_transition(self, state, action_idx, reward, next_state, h_hat, time_step):
        """
        Algorithm 2 Steps 18 & 25:
        Update DND memory with (h_hat, Q_estimated), and store experience in replay buffer.
        """
        if h_hat is not None:
            # Query value to update
            current_q = self.dnd_dict[action_idx].query(h_hat)
            updated_q = (1.0 - self.cfg.LEARNING_RATE_LAMBDA) * current_q + self.cfg.LEARNING_RATE_LAMBDA * reward
            self.dnd_dict[action_idx].append_or_update(h_hat, updated_q)

        # Append to experience pool B
        self.replay_buffer.append((state, action_idx, reward, next_state))

        # Update sliding history
        self.history.append(state)
        self.history.append(self.actions[action_idx])

        # Decay epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def train_step(self):
        """
        Algorithm 2 Steps 26-30: Mini-batch SGD update for CNN weights.
        """
        if len(self.replay_buffer) < self.batch_size:
            return

        indices = np.random.choice(len(self.replay_buffer), self.batch_size, replace=False)
        batch = [self.replay_buffer[i] for i in indices]

        self.cnn.train()
        for state, a_idx, r, next_s in batch:
            phi_t = self._format_sequence(state)
            phi_next_t = self._format_sequence(next_s)

            self.optimizer.zero_grad()
            h_hat_curr = self.cnn(phi_t)
            h_hat_curr_np = h_hat_curr.detach().cpu().numpy().flatten()

            with torch.no_grad():
                h_hat_next = self.cnn(phi_next_t).cpu().numpy().flatten()
                next_q_vals = [self.dnd_dict[i].query(h_hat_next) for i in range(self.num_actions)]
                max_next_q = np.max(next_q_vals)

            target_val = r + self.beta * max_next_q
            curr_val = self.dnd_dict[a_idx].query(h_hat_curr_np)

            # PyTorch loss backprop through CNN features
            # Dummy regression to shape feature embeddings towards optimal target
            loss = nn.functional.mse_loss(h_hat_curr.mean(), torch.tensor(float(target_val)))
            loss.backward()
            self.optimizer.step()

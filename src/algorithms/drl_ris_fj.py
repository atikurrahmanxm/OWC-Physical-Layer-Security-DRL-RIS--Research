"""
Novel Proposed Scheme: DRL-RIS-FJ
Joint Optimization of Friendly Jamming Beamformer and Optical RIS (O-RIS) Reflection.
Architecture:
- Continuous Multi-Action Deep Actor-Critic (DDPG/TD3-inspired)
- Actor: Outputs continuous jamming beamformer w in [-1, 1]^4 and RIS configuration theta in [0, 1]^M
- Critic: Evaluates joint action-value Q(s, a)
- Target Networks + Ornstein-Uhlenbeck / Gaussian Exploration Noise
- Experience Replay with prioritized target updates
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from src.config import Config

class ContinuousActor(nn.Module):
    def __init__(self, state_dim, num_jammers=4, num_ris_elements=16, hidden_dim=256):
        super(ContinuousActor, self).__init__()
        self.num_jammers = num_jammers
        self.num_ris_elements = num_ris_elements

        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU()
        )

        # Jammer output head in [-1, 1]
        self.jammer_head = nn.Sequential(
            nn.Linear(hidden_dim, num_jammers),
            nn.Tanh()
        )

        # RIS output head in [0, 1]
        self.ris_head = nn.Sequential(
            nn.Linear(hidden_dim, num_ris_elements),
            nn.Sigmoid()
        )
        nn.init.constant_(self.ris_head[0].bias, 1.5)

    def forward(self, state):
        features = self.net(state)
        w = self.jammer_head(features)
        theta = self.ris_head(features)
        return torch.cat([w, theta], dim=-1)

class ContinuousCritic(nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super(ContinuousCritic, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, state, action):
        sa = torch.cat([state, action], dim=-1)
        return self.net(sa)

class DRLRISFJAgent:
    def __init__(self, config=None, state_dim=4, lr_actor=1e-4, lr_critic=1e-3, tau=0.005):
        self.cfg = config if config is not None else Config()
        self.state_dim = state_dim
        self.num_jammers = self.cfg.NUM_JAMMERS
        self.num_ris = self.cfg.RIS_TOTAL_ELEMENTS
        self.action_dim = self.num_jammers + self.num_ris
        self.gamma = self.cfg.DISCOUNT_FACTOR_BETA
        self.tau = tau
        self.noise_std = 0.2
        self.noise_decay = 0.999
        self.min_noise = 0.02
        self.batch_size = 32

        # Actor and Critic Networks
        self.actor = ContinuousActor(self.state_dim, self.num_jammers, self.num_ris)
        self.actor_target = ContinuousActor(self.state_dim, self.num_jammers, self.num_ris)
        self.actor_target.load_state_dict(self.actor.state_dict())
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr_actor)

        self.critic = ContinuousCritic(self.state_dim, self.action_dim)
        self.critic_target = ContinuousCritic(self.state_dim, self.action_dim)
        self.critic_target.load_state_dict(self.critic.state_dict())
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=lr_critic)

        # Experience Replay
        self.memory = deque(maxlen=self.cfg.MEMORY_CAPACITY)

    def select_action(self, state, explore=True):
        state_t = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        self.actor.eval()
        with torch.no_grad():
            action = self.actor(state_t).squeeze(0).cpu().numpy()

        if explore:
            noise = np.random.normal(0, self.noise_std, size=self.action_dim)
            action = action + noise

        # Jammer in [-1, 1], RIS in [0, 1]
        w = np.clip(action[:self.num_jammers], -1.0, 1.0)
        theta = np.clip(action[self.num_jammers:], 0.0, 1.0)
        full_action = np.concatenate([w, theta])
        return w, theta, full_action

    def store_transition(self, state, full_action, reward, next_state):
        self.memory.append((state, full_action, reward, next_state))
        self.noise_std = max(self.min_noise, self.noise_std * self.noise_decay)

    def train_step(self):
        if len(self.memory) < self.batch_size:
            return

        batch_indices = np.random.choice(len(self.memory), self.batch_size, replace=False)
        states, actions, rewards, next_states = zip(*[self.memory[i] for i in batch_indices])

        states_t = torch.tensor(np.array(states), dtype=torch.float32)
        actions_t = torch.tensor(np.array(actions), dtype=torch.float32)
        rewards_t = torch.tensor(np.array(rewards), dtype=torch.float32).unsqueeze(1)
        next_states_t = torch.tensor(np.array(next_states), dtype=torch.float32)

        # ----------------- Update Critic -----------------
        self.critic.train()
        self.actor.train()

        with torch.no_grad():
            next_actions_t = self.actor_target(next_states_t)
            target_q = self.critic_target(next_states_t, next_actions_t)
            y_target = rewards_t + self.gamma * target_q

        current_q = self.critic(states_t, actions_t)
        critic_loss = nn.functional.mse_loss(current_q, y_target)

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        # ----------------- Update Actor -----------------
        predicted_actions = self.actor(states_t)
        actor_loss = -self.critic(states_t, predicted_actions).mean()

        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        # ----------------- Soft Update Target Networks -----------------
        for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1.0 - self.tau) * target_param.data)
        for param, target_param in zip(self.actor.parameters(), self.actor_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1.0 - self.tau) * target_param.data)

"""Feasible ZF, rigorous global bounds, and explicitly CUSTOM comparison methods.

The three custom methods are not reproductions of references [20], [42], [43].
Legacy method names remain as deprecated aliases for compatibility only.
"""

from typing import Dict, List, Optional
import numpy as np
from .config import VLCConfig
from .environment import VLCEnvironment
from .bounds import compute_zero_forcing_beamformer, compute_theoretical_bounds
from .secrecy import (
    compute_secrecy_rate,
    compute_bob_ber,
    compute_energy_consumption,
    compute_system_utility,
)


class BenchmarkRunner:
    """
    Simulates the benchmark schemes over a series of time slots.
    """

    def __init__(self, env: VLCEnvironment, config: Optional[VLCConfig] = None):
        self.env = env
        self.config = config if config is not None else env.config
        self.rng = np.random.default_rng(self.config.seed)

    def run_theoretical_bound(self, num_slots: int = 2000) -> Dict[str, List[float]]:
        """
        Calculates independently valid global bounds, not conditional Corollary 1.
        """
        cs_star, pe_star, u_star, w_star = compute_theoretical_bounds(
            self.env.h_AB,
            self.env.h_AE,
            self.env.h_JB,
            self.env.h_JE,
            self.config,
            self.env.sigma_B_sq,
        )
        energy_star = -self.config.num_jammers * self.config.unit_jamming_cost if self.config.energy_model == "paper_signed" else 0.

        # Theoretical bound is an invariant ceiling over the stationary geometry
        return {
            "secrecy_rate": [cs_star] * num_slots,
            "ber": [pe_star] * num_slots,
            "energy": [energy_star] * num_slots,
            "utility": [u_star] * num_slots,
        }

    def run_zero_forcing(self, num_slots: int = 2000) -> Dict[str, List[float]]:
        """
        Evaluates Zero-Forcing Friendly Jamming (Equation 5).
        """
        w_zf = compute_zero_forcing_beamformer(self.env.h_JB, self.env.h_JE)

        history = {"secrecy_rate": [], "ber": [], "energy": [], "utility": []}
        for _ in range(num_slots):
            cs = compute_secrecy_rate(
                self.env.h_AB, self.env.h_AE, self.env.h_JB, self.env.h_JE,
                w_zf, self.config, self.env.sigma_B_sq
            )
            pe = compute_bob_ber(self.env.h_AB, self.env.h_JB, w_zf, self.config, self.env.sigma_B_sq)
            energy = compute_energy_consumption(w_zf, self.config)
            utility = compute_system_utility(cs, pe, energy, self.config)

            history["secrecy_rate"].append(cs)
            history["ber"].append(pe)
            history["energy"].append(energy)
            history["utility"].append(utility)

        return history

    def run_restricted_search(self, num_slots: int = 2000) -> Dict[str, List[float]]:
        """
        CUSTOM restricted-action reward search (not DRL-VB [20])
        (baseline modeled physically through VLCEnvironment using constrained positive/symmetric weights).
        """
        history = {"secrecy_rate": [], "ber": [], "energy": [], "utility": []}

        # Online epsilon-greedy search over the constrained 2-level beamformer subspace (non-cooperative)
        constrained_actions = [w for w in self.env.action_space if np.all(w >= -0.5) and np.all(w <= 0.5)]
        if not constrained_actions:
            constrained_actions = list(self.env.action_space)
        q_est = np.zeros(len(constrained_actions), dtype=np.float64)
        eps = self.config.epsilon_start

        for _ in range(num_slots):
            if self.rng.random() > eps:
                a_idx = int(np.argmax(q_est))
            else:
                a_idx = int(self.rng.integers(len(constrained_actions)))
            w = constrained_actions[a_idx]

            self.env._update_channel()
            cs = compute_secrecy_rate(
                self.env.h_AB, self.env.h_AE, self.env.h_JB, self.env.h_JE,
                w, self.config, self.env.sigma_B_sq
            )
            pe = compute_bob_ber(self.env.h_AB, self.env.h_JB, w, self.config, self.env.sigma_B_sq)
            energy = compute_energy_consumption(w, self.config)
            u = compute_system_utility(cs, pe, energy, self.config)

            q_est[a_idx] = (1.0 - self.config.learning_rate) * q_est[a_idx] + self.config.learning_rate * u
            eps = max(self.config.epsilon_min, eps * self.config.epsilon_decay)

            history["secrecy_rate"].append(cs)
            history["ber"].append(pe)
            history["energy"].append(energy)
            history["utility"].append(u)

        return history

    def run_regularized(self, num_slots: int = 2000) -> Dict[str, List[float]]:
        """
        CUSTOM regularized channel inversion (not robust beamforming [42])
        on the real VLC channel model (Equations 4, 7, 14, 16).
        """
        history = {"secrecy_rate": [], "ber": [], "energy": [], "utility": []}

        # Tikhonov-regularized projection trading Bob interference suppression for Eve uncertainty margin
        h_jb = self.env.h_JB
        h_je = self.env.h_JE
        reg = 0.25 * float(np.dot(h_jb, h_jb)) + 1e-18
        mat = np.outer(h_jb, h_jb) + reg * np.eye(len(h_jb))
        w_dir = np.linalg.solve(mat, h_je)
        max_abs = float(np.max(np.abs(w_dir)))
        w_robust = (w_dir / max_abs) * 0.6 if max_abs > 1e-12 else np.zeros_like(h_jb)

        for _ in range(num_slots):
            self.env._update_channel()
            cs = compute_secrecy_rate(
                self.env.h_AB, self.env.h_AE, self.env.h_JB, self.env.h_JE,
                w_robust, self.config, self.env.sigma_B_sq
            )
            pe = compute_bob_ber(self.env.h_AB, self.env.h_JB, w_robust, self.config, self.env.sigma_B_sq)
            energy = compute_energy_consumption(w_robust, self.config)
            u = compute_system_utility(cs, pe, energy, self.config)

            history["secrecy_rate"].append(cs)
            history["ber"].append(pe)
            history["energy"].append(energy)
            history["utility"].append(u)

        return history

    def run_scaled_zf(self, num_slots: int = 2000) -> Dict[str, List[float]]:
        """
        CUSTOM scalar power search (not SBJ-VLC [43]) using
        the static null-space / utility-optimal beamformer on the real channel model.
        """
        history = {"secrecy_rate": [], "ber": [], "energy": [], "utility": []}

        w_zf = compute_zero_forcing_beamformer(self.env.h_JB, self.env.h_JE)
        # Optimize scalar power allocation s in [0.1, 1.0] maximizing Eq. (7) utility statically
        best_w = w_zf
        best_u = -1e9
        for scale in np.linspace(0.1, 1.0, 19):
            w_cand = w_zf * scale
            cs = compute_secrecy_rate(
                self.env.h_AB, self.env.h_AE, self.env.h_JB, self.env.h_JE,
                w_cand, self.config, self.env.sigma_B_sq
            )
            pe = compute_bob_ber(self.env.h_AB, self.env.h_JB, w_cand, self.config, self.env.sigma_B_sq)
            energy = compute_energy_consumption(w_cand, self.config)
            u = compute_system_utility(cs, pe, energy, self.config)
            if u > best_u:
                best_u = u
                best_w = w_cand

        for _ in range(num_slots):
            self.env._update_channel()
            cs = compute_secrecy_rate(
                self.env.h_AB, self.env.h_AE, self.env.h_JB, self.env.h_JE,
                best_w, self.config, self.env.sigma_B_sq
            )
            pe = compute_bob_ber(self.env.h_AB, self.env.h_JB, best_w, self.config, self.env.sigma_B_sq)
            energy = compute_energy_consumption(best_w, self.config)
            u = compute_system_utility(cs, pe, energy, self.config)

            history["secrecy_rate"].append(cs)
            history["ber"].append(pe)
            history["energy"].append(energy)
            history["utility"].append(u)

        return history

    def run_drl_vb(self, num_slots=2000):
        import warnings
        warnings.warn("run_drl_vb is a custom restricted search, not reference [20]", DeprecationWarning, stacklevel=2)
        return self.run_restricted_search(num_slots)

    def run_robust_beamforming(self, num_slots=2000):
        import warnings
        warnings.warn("run_robust_beamforming is custom regularization, not reference [42]", DeprecationWarning, stacklevel=2)
        return self.run_regularized(num_slots)

    def run_sbj_vlc(self, num_slots=2000):
        import warnings
        warnings.warn("run_sbj_vlc is custom scaled ZF, not reference [43]", DeprecationWarning, stacklevel=2)
        return self.run_scaled_zf(num_slots)

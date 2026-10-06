"""
Benchmark Baseline Schemes:
1. No-Jammer Baseline (Conventional Transmission, Alice only)
2. Zero-Forcing Friendly Jamming (ZF-FJ, equation 5 in paper)
3. Random Friendly Jamming
"""

import numpy as np

class BaselineZeroForcing:
    """
    Zero-Forcing Friendly Jamming (ZF-FJ).
    As described in Equation (5) of the paper:
    w0 = arg max_w c_s s.t. h_JB^T w = 0, |w| <= 1.
    Forces jamming on Bob to strictly zero via projection onto the null-space of h_JB.
    """
    def __init__(self, num_jammers=4):
        self.num_jammers = num_jammers

    def select_action(self, h_JB, h_JE):
        """
        Projects Eve's channel onto null-space of Bob's jamming channel:
        P_null = I - (h_JB h_JB^T) / ||h_JB||^2
        w_zf = P_null * h_JE / norm
        """
        h_jb = np.array(h_JB, dtype=float).reshape(-1, 1)
        h_je = np.array(h_JE, dtype=float).reshape(-1, 1)
        
        norm_sq = np.dot(h_jb.T, h_jb)[0, 0]
        if norm_sq < 1e-12:
            w_raw = np.ones(self.num_jammers)
        else:
            P_null = np.eye(self.num_jammers) - (np.dot(h_jb, h_jb.T) / norm_sq)
            w_opt = np.dot(P_null, h_je).flatten()
            max_abs = np.max(np.abs(w_opt))
            if max_abs > 1e-9:
                w_raw = w_opt / max_abs  # Normalized so |w| <= 1
            else:
                w_raw = np.zeros(self.num_jammers)

        # Scale so it aligns in the direction maximizing h_JE^T w
        if np.dot(h_JE, w_raw) < 0:
            w_raw = -w_raw
            
        return np.clip(w_raw, -1.0, 1.0)

class BaselineNoJammer:
    """No friendly jamming (w = 0). Standard VLC transmission."""
    def __init__(self, num_jammers=4):
        self.num_jammers = num_jammers

    def select_action(self, *args, **kwargs):
        return np.zeros(self.num_jammers)

class BaselineRandomJammer:
    """Random friendly jamming beamformer uniformly sampled in [-1, 1]."""
    def __init__(self, num_jammers=4):
        self.num_jammers = num_jammers

    def select_action(self, *args, **kwargs):
        return np.random.uniform(-1.0, 1.0, size=self.num_jammers)

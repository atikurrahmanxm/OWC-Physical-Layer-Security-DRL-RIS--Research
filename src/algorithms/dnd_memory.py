"""
Differentiable Neural Dictionary (DND) Memory Module.
Strictly implements Section IV (Equations 10, 11, 12) of the paper:
- Maintains key array K_w and value array V_w for each action w
- Gaussian kernel Ker(h_hat, h_j) = exp(-0.5 * ||h_hat - h_j||_2^2)
- Normalized weights omega_j = Ker(h_hat, h_j) / sum(Ker(h_hat, h_p))
- Value estimation Q(s, w) = sum(omega_j * v_j)
- Memory insertion and update mechanism
"""

import numpy as np

class DNDMemory:
    def __init__(self, key_dim=180, max_capacity=2000):
        self.key_dim = key_dim
        self.max_capacity = max_capacity
        self.keys = []     # List of key vectors (length key_dim)
        self.values = []   # List of scalar Q-values

    def is_empty(self):
        return len(self.keys) == 0

    def query(self, h_hat):
        """
        Queries the DND using key h_hat to return estimated Q-value (eq. 12).
        """
        if self.is_empty():
            return 0.0

        h_hat = np.array(h_hat, dtype=float).flatten()
        K = np.array(self.keys)  # shape (zeta, key_dim)
        V = np.array(self.values) # shape (zeta,)

        # Vectorized Euclidean squared distance: ||h_hat - h_j||^2
        diff = K - h_hat
        dist_sq = np.sum(diff ** 2, axis=1)

        # Numerical stabilization for Gaussian kernel
        min_dist = np.min(dist_sq)
        # Shift exponent to avoid float underflow
        kernel_vals = np.exp(-0.5 * (dist_sq - min_dist))

        sum_kernel = np.sum(kernel_vals)
        if sum_kernel < 1e-12:
            return float(np.mean(V))

        weights = kernel_vals / sum_kernel
        q_val = float(np.dot(weights, V))
        return q_val

    def append_or_update(self, h_hat, q_val, threshold=1e-3):
        """
        Appends or updates memory entry (h_hat, q_val).
        If an identical key exists (distance < threshold), update value;
        otherwise append.
        """
        h_hat = np.array(h_hat, dtype=float).flatten()
        if len(self.keys) > 0:
            K = np.array(self.keys)
            dist_sq = np.sum((K - h_hat) ** 2, axis=1)
            min_idx = np.argmin(dist_sq)
            if dist_sq[min_idx] < threshold:
                # Update existing entry
                self.values[min_idx] = float(q_val)
                return

        # Append new entry
        if len(self.keys) >= self.max_capacity:
            # FIFO pop oldest
            self.keys.pop(0)
            self.values.pop(0)

        self.keys.append(h_hat)
        self.values.append(float(q_val))

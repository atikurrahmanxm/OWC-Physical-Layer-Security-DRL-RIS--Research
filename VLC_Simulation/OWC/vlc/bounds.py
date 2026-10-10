"""
Theoretical Upper Bounds and Zero-Forcing (ZF) Beamformer Solution.
Implements:
- Zero-Forcing Friendly Jamming (Equation 5)
- Theoretical Upper Bound on Secrecy Rate, BER, and Utility (Corollary 1, Eq. 18, 21, 22)
- Optimal jamming target on Eve (Remark I, Eq. 23 & 35)
"""

from typing import Tuple, Optional
import numpy as np
from scipy.special import erfc
from .config import VLCConfig
from .secrecy import (
    compute_secrecy_rate,
    compute_bob_ber,
    compute_energy_consumption,
    compute_system_utility,
)


def compute_zero_forcing_beamformer(
    h_JB: np.ndarray,
    h_JE: np.ndarray,
) -> np.ndarray:
    """
    Solves the Zero-Forcing optimization problem from Equation (5):
    w0 = arg max_w c_s, s.t. h_JB^T w = 0, |w| <= 1

    Projects h_JE onto the null-space of h_JB and scales to [-1, 1].
    """
    h_JB = np.asarray(h_JB, dtype=np.float64)
    h_JE = np.asarray(h_JE, dtype=np.float64)

    norm_jb_sq = np.dot(h_JB, h_JB)
    if norm_jb_sq < 1e-15:
        # If jammer-to-Bob gain is zero, beamformer can directly align with h_JE
        w_zf = np.sign(h_JE)
        return w_zf

    # Projection matrix onto null-space of h_JB: P_null = I - (h_JB h_JB^T) / ||h_JB||^2
    n_j = len(h_JB)
    P_null = np.eye(n_j) - np.outer(h_JB, h_JB) / norm_jb_sq

    # Maximal projection along h_JE
    w_dir = P_null @ h_JE

    max_val = np.max(np.abs(w_dir))
    if max_val > 1e-12:
        w_zf = w_dir / max_val
    else:
        w_zf = np.zeros(n_j)

    return w_zf


def compute_theoretical_bounds(
    h_AB: float,
    h_AE: float,
    h_JB: np.ndarray,
    h_JE: np.ndarray,
    config: Optional[VLCConfig] = None,
    sigma_B_sq: Optional[float] = None,
) -> Tuple[float, float, float, np.ndarray]:
    """
    Computes the theoretical optimum for Secrecy Rate, BER, and Utility
    as derived in Corollary 1 (Equations 18, 21, 22) and Remark I (Equation 23):

    - Zero jamming on Bob: h_JB^T w* = 0
    - Jamming power on Eve converges to: H* = h_AE / log2(sqrt(e))
    - cs* = 0.5 * log2(1 + [2 * h_AB^2 * alpha^2 * I_D^2] / [pi * e * sigma_B^2])
            - (log2(log2(sqrt(e))) + 1)
    - pe* = 0.75 * erfc( sqrt( [2 * P_T * h_AB^2] / [5 * sigma_B^2] ) )
    - u*  = cs* - delta1 * pe* - delta2 * E*
    """
    if config is None:
        config = VLCConfig()

    if sigma_B_sq is None:
        sigma_B_sq = config.noise_power_watts / config.snr_scale

    alpha = config.modulation_index
    I_D = config.id_bias
    P_T = config.led_avg_power

    # Theoretical Secrecy Rate (Equation 21)
    snr_num = 2.0 * (h_AB ** 2) * (alpha ** 2) * (I_D ** 2)
    snr_den = np.pi * np.e * sigma_B_sq
    term1 = 0.5 * np.log2(1.0 + max(0.0, snr_num / snr_den))

    log_sqrt_e = np.log2(np.sqrt(np.e))
    term2 = np.log2(log_sqrt_e) + 1.0
    cs_star = float(max(0.0, term1 - term2))

    # Theoretical BER of Bob (Equation 22)
    gamma_bob = (2.0 * P_T * (h_AB ** 2)) / (5.0 * sigma_B_sq)
    pe_star = float(0.75 * erfc(np.sqrt(max(0.0, gamma_bob))))

    # Optimal ZF beamformer direction
    w_star = compute_zero_forcing_beamformer(h_JB, h_JE)

    # Scale w_star to achieve H* = h_AE / log2(sqrt(e)) if possible
    h_je_dot_w = float(np.abs(np.dot(h_JE, w_star)))
    h_star_target = h_AE / log_sqrt_e
    if h_je_dot_w > 1e-12:
        scale_factor = min(1.0, h_star_target / h_je_dot_w)
        w_star = w_star * scale_factor

    energy_star = compute_energy_consumption(w_star, config)
    utility_star = compute_system_utility(cs_star, pe_star, energy_star, config)

    return cs_star, pe_star, utility_star, w_star

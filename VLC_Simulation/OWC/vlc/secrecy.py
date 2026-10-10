"""
Physical Layer Security Metrics for Visible Light Communication.
Implements:
- Achievable Secrecy Rate (Equation 4)
- Bit Error Rate (BER) of Bob with 4PAM (Equation 14)
- Jamming Energy Consumption (Equation 16)
- Overall System Utility Function (Equation 7)
"""

from typing import Optional, Union
import numpy as np
from scipy.special import erfc
from .config import VLCConfig


def compute_secrecy_rate(
    h_AB: float,
    h_AE: float,
    h_JB: np.ndarray,
    h_JE: np.ndarray,
    w: np.ndarray,
    config: Optional[VLCConfig] = None,
    sigma_B_sq: Optional[float] = None,
) -> float:
    """
    Computes the achievable secrecy rate c_s (bps/Hz) of the VLC system
    over the wiretap channel according to Equation (4):

    c_s = 0.5 * log2(1 + [2 * h_AB^2 * alpha^2 * I_D^2] / [pi * e * (sigma_B^2 + 2 * |h_JB^T w|^2 * alpha^2 * I_D^2)])
        - min( log2(h_AE / |h_JE^T w|) + (|h_JE^T w| / h_AE) * log2(sqrt(e)),
               (h_AE / |h_JE^T w|) * log2(sqrt(e)) )
    """
    if config is None:
        config = VLCConfig()

    alpha = config.modulation_index
    I_D = config.id_bias

    # Effective noise variance at Bob
    if sigma_B_sq is None:
        # Scale noise to effective SNR range for the room scenario
        sigma_B_sq = config.noise_power_watts / config.snr_scale

    # Jamming terms on Bob and Eve
    w = np.asarray(w, dtype=np.float64)
    jamming_on_bob = float(np.dot(h_JB, w))
    jamming_on_eve = float(np.abs(np.dot(h_JE, w)))

    # Bob's SINR term (Term 1 in Eq. 4)
    numerator = 2.0 * (h_AB ** 2) * (alpha ** 2) * (I_D ** 2)
    jamming_var_bob = 2.0 * (jamming_on_bob ** 2) * (alpha ** 2) * (I_D ** 2)
    denominator = np.pi * np.e * (sigma_B_sq + jamming_var_bob)

    sinr_bob = numerator / max(denominator, 1e-30)
    term_bob = 0.5 * np.log2(1.0 + max(0.0, sinr_bob))

    # Eve's Wiretapping term (Term 2 in Eq. 4)
    log_sqrt_e = np.log2(np.sqrt(np.e))  # ~ 0.7213475

    eps = 1e-12
    if jamming_on_eve < eps:
        # Without jamming on Eve, secrecy rate is zero / minimal against competent Eve
        term_eve = 10.0
    else:
        ratio = h_AE / jamming_on_eve
        inv_ratio = jamming_on_eve / h_AE
        leak_1 = np.log2(max(eps, ratio)) + inv_ratio * log_sqrt_e
        leak_2 = ratio * log_sqrt_e
        term_eve = min(leak_1, leak_2)

    cs = term_bob - term_eve
    return float(max(0.0, cs))


def compute_bob_ber(
    h_AB: float,
    h_JB: np.ndarray,
    w: np.ndarray,
    config: Optional[VLCConfig] = None,
    sigma_B_sq: Optional[float] = None,
) -> float:
    """
    Computes the Bit Error Rate (BER) of legitimate user Bob using 4PAM modulation
    according to Equation (14):

    p_e = 0.75 * erfc( sqrt( [2 * P_T * (w^T h_JB + h_AB)^2] / [5 * sigma_B^2] ) )
    """
    if config is None:
        config = VLCConfig()

    if sigma_B_sq is None:
        sigma_B_sq = config.noise_power_watts / config.snr_scale

    P_T = config.led_avg_power
    w = np.asarray(w, dtype=np.float64)
    jamming_on_bob = float(np.dot(h_JB, w))

    effective_channel = h_AB + jamming_on_bob
    if effective_channel <= 0.0:
        # Destructive interference completely degrades reception
        return 0.75

    gamma = (2.0 * P_T * (effective_channel ** 2)) / (5.0 * sigma_B_sq)
    ber = 0.75 * erfc(np.sqrt(max(0.0, gamma)))
    return float(np.clip(ber, 1e-8, 0.75))


def compute_energy_consumption(
    w: np.ndarray,
    config: Optional[VLCConfig] = None,
) -> float:
    """
    Computes the energy consumption of the friendly jammers according to Equation (16):
    E = varrho_s * sum_{i=1}^{N_J} |w_i|
    """
    if config is None:
        config = VLCConfig()

    w = np.asarray(w, dtype=np.float64)
    energy = config.unit_jamming_cost * np.sum(np.abs(w))
    return float(energy)


def compute_system_utility(
    cs: float,
    pe: float,
    energy: float,
    config: Optional[VLCConfig] = None,
) -> float:
    """
    Computes the overall system utility function according to Equation (7):
    u = c_s - delta1 * p_e - delta2 * E
    """
    if config is None:
        config = VLCConfig()

    u = cs - config.delta1 * pe - config.delta2 * energy
    return float(u)

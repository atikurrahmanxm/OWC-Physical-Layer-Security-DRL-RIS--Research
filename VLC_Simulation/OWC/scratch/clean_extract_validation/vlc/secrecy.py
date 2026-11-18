"""
Physical Layer Security Metrics for Visible Light Communication.
model=physical dispatches rate and BER to one current-domain 4-PAM channel;
the default paper mode retains the printed equations below.
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

    # Effective noise variance at Bob (Table I: sigma_B^2 = -98.79 dBm)
    if sigma_B_sq is None:
        sigma_B_sq = config.noise_variance

    if config.model == "physical":
        from .physical import secrecy_rate
        return secrecy_rate(h_AB,h_AE,h_JB,h_JE,w,config,sigma_B_sq)

    if not np.isfinite(sigma_B_sq) or sigma_B_sq <= 0:
        raise ValueError("Noise variance must be finite and positive")
    if h_AB < 0 or h_AE < 0:
        raise ValueError("Optical channel gains must be nonnegative")

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

    if h_AE == 0.0:
        return float(term_bob)  # No information link to Eve.
    if jamming_on_eve == 0.0:
        # Without jamming on Eve, leakage term diverges and secrecy rate is 0
        return 0.0
    else:
        ratio = h_AE / jamming_on_eve
        inv_ratio = jamming_on_eve / h_AE
        leak_1 = (np.log2(h_AE) - np.log2(jamming_on_eve)) + inv_ratio * log_sqrt_e
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

    p_e = 0.75 * erfc( sqrt( [2 * P_T * (w^T h_JB + h_AB)(h_AB + h_JB^T w)] / [5 * sigma_B^2] ) )
    """
    if config is None:
        config = VLCConfig()

    if sigma_B_sq is None:
        sigma_B_sq = config.noise_variance

    if config.model == "physical":
        from .physical import pam_bit_error_rate
        amplitude=config.modulation_index*config.id_bias
        return pam_bit_error_rate(abs(h_AB)*amplitude,abs(float(np.dot(h_JB,w)))*amplitude,sigma_B_sq)

    P_T = config.led_avg_power
    if not np.isfinite(sigma_B_sq) or sigma_B_sq <= 0:
        raise ValueError("Noise variance must be finite and positive")
    w = np.asarray(w, dtype=np.float64)
    jamming_on_bob = float(np.dot(h_JB, w))

    effective_channel = h_AB + jamming_on_bob
    # Eq. (14) squares the effective channel, including negative values.
    gamma = (2.0 * P_T * (effective_channel ** 2)) / (5.0 * sigma_B_sq)
    ber = 0.75 * erfc(np.sqrt(max(0.0, gamma)))
    return float(min(0.75, max(0.0, ber)))


def compute_energy_consumption(
    w: np.ndarray,
    config: Optional[VLCConfig] = None,
) -> float:
    """
    Paper mode: nonnegative amplitude cost E = varrho_s * sum_i |w_i|.
    Physical mode: sum_i w_i^2 * A^2/3 * R_driver * slot_duration, joules.
    This is an explicit physical interpretation of the ambiguous Eq. (16).
    energy_model='paper_signed' selects the literal printed sum_i w_i,
    which can be negative and reward zero-secrecy actions.
    """
    if config is None:
        config = VLCConfig()

    w = np.asarray(w, dtype=np.float64)
    if config.model == "physical":
        return float((config.modulation_index*config.id_bias)**2/3 * np.sum(w**2)
                     * config.jammer_resistance_ohm*config.slot_duration_s)
    energy = config.unit_jamming_cost * np.sum(np.abs(w) if config.energy_model == "l1" else w)
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

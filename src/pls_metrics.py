"""
Physical Layer Security (PLS) Metrics and Utility Calculations.
Aligned with IEEE TWC (Sep 2024) paper:
- Achievable Secrecy Rate (eq. 4)
- Legitimate User Bit Error Rate (4-PAM, eq. 14)
- Friendly Jammer & RIS Energy Consumption (eq. 16)
- System Utility Function (eq. 7)
- Secrecy Energy Efficiency (SEE) and Secrecy Outage Probability (SOP)
"""

import numpy as np
import scipy.special as sp
from src.config import Config

class PLSMetrics:
    def __init__(self, config=None):
        self.cfg = config if config is not None else Config()

    def compute_secrecy_rate(self, h_AB, h_AE, h_JB, h_JE, w):
        """
        Calculates achievable secrecy rate c_s according to equation (4) of the paper.
        
        Args:
            h_AB: scalar, electrical channel gain Alice -> Bob
            h_AE: scalar, electrical channel gain Alice -> Eve
            h_JB: array (4,), electrical channel gain Jammers -> Bob
            h_JE: array (4,), electrical channel gain Jammers -> Eve
            w: array (4,), friendly jamming beamformer vector
            
        Returns:
            c_s: achievable secrecy rate in bps/Hz (non-negative)
        """
        alpha = self.cfg.MODULATION_INDEX_ALPHA
        I_D = self.cfg.ID_BIAS
        sigma_B2 = self.cfg.NOISE_POWER_BOB
        sigma_E2 = self.cfg.NOISE_POWER_EVE

        w = np.array(w, dtype=float)
        jamming_on_bob = np.abs(np.dot(h_JB, w))
        jamming_on_eve = np.abs(np.dot(h_JE, w))

        # Bob's achievable rate capacity component
        # numerator: 2 * (h_AB)^2 * alpha^2 * I_D^2
        # denominator: pi * e * (sigma_B^2 + 2 * jamming_on_bob^2 * alpha^2 * I_D^2)
        signal_bob = 2.0 * (h_AB ** 2) * (alpha ** 2) * (I_D ** 2)
        noise_int_bob = np.pi * np.e * (sigma_B2 + 2.0 * (jamming_on_bob ** 2) * (alpha ** 2) * (I_D ** 2))
        sinr_bob = signal_bob / max(noise_int_bob, 1e-25)
        
        c_bob = 0.5 * np.log2(1.0 + sinr_bob)

        # Eve's wiretapping capacity component under jamming
        # According to eq (4):
        # min( log2(h_AE / jam_eve) + (jam_eve / h_AE)*log2(sqrt(e)),  (h_AE / jam_eve)*log2(sqrt(e)) )
        # If jamming_on_eve is extremely small, fallback to unjammed Eve rate
        log2_sqrte = 0.5 * np.log2(np.e)

        # Standard unjammed wiretap capacity of Eve
        signal_eve = 2.0 * (h_AE ** 2) * (alpha ** 2) * (I_D ** 2)
        noise_eve = np.pi * np.e * sigma_E2
        c_eve_unjammed = 0.5 * np.log2(1.0 + signal_eve / noise_eve)

        if jamming_on_eve < 1e-8:
            c_eve = c_eve_unjammed
        else:
            ratio = h_AE / jamming_on_eve
            term1 = np.log2(max(ratio, 1e-12)) + (jamming_on_eve / max(h_AE, 1e-12)) * log2_sqrte
            term2 = ratio * log2_sqrte
            c_eve_jam = max(float(min(term1, term2)), 0.0)
            # Physical bound: jamming can only reduce or equal unjammed interception capacity
            c_eve = min(c_eve_unjammed, c_eve_jam)

        c_s = max(float(c_bob - c_eve), 0.0)
        return c_s

    def compute_ber(self, h_AB, h_JB, w):
        """
        Calculates Bob's BER using 4-PAM according to eq. (14) of the paper.
        pe = (3/4) * erfc( sqrt( 2 * P_T * (h_AB)^2 / (5 * (sigma_B^2 + 2*|h_JB^T w|^2*alpha^2*I_D^2)) ) )
        """
        w = np.array(w, dtype=float)
        jamming_on_bob = np.abs(np.dot(h_JB, w))
        alpha = self.cfg.MODULATION_INDEX_ALPHA
        I_D = self.cfg.ID_BIAS
        P_T = self.cfg.P_OPT_ALICE
        sigma_B2 = self.cfg.NOISE_POWER_BOB

        num = 2.0 * P_T * (h_AB ** 2)
        den = 5.0 * (sigma_B2 + 2.0 * (jamming_on_bob ** 2) * (alpha ** 2) * (I_D ** 2))
        gamma_b = num / max(den, 1e-25)

        # erfc(sqrt(gamma_b))
        pe = 0.75 * sp.erfc(np.sqrt(max(gamma_b, 0.0)))
        # Guard against zero float underflow
        return float(np.clip(pe, 1e-10, 0.75))

    def compute_energy(self, w, ris_weights=None):
        """
        Calculates friendly jammer and RIS energy consumption (eq. 16 extended).
        E = \varrho_s * sum(|w_i|) + P_RIS * sum(|theta_m|)
        """
        w = np.array(w, dtype=float)
        e_jam = self.cfg.UNIT_JAMMING_COST * np.sum(np.abs(w))
        e_ris = 0.0
        if ris_weights is not None:
            e_ris = self.cfg.RIS_ELEMENT_POWER * np.sum(np.abs(ris_weights))
        return float(e_jam + e_ris)

    def compute_utility(self, secrecy_rate, ber, energy):
        """
        Calculates system utility according to eq. (7) of the paper:
        u(k) = c_s(k) - delta_1 * pe(k) - delta_2 * E(k)
        """
        u = secrecy_rate - (self.cfg.DELTA_1 * ber) - (self.cfg.DELTA_2 * energy)
        return float(u)

    def compute_see(self, secrecy_rate, energy):
        """
        Calculates Secrecy Energy Efficiency (SEE) in bps/Hz/Watt.
        SEE = c_s / (P_Alice + E)
        """
        total_p = self.cfg.P_OPT_ALICE + energy
        return float(secrecy_rate / max(total_p, 1e-6))

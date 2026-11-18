"""Exact box-constrained ZF; global bounds and conditional-paper diagnostics."""
from typing import Optional, Tuple
import numpy as np
from scipy.optimize import linprog
from scipy.special import erfc
from .config import VLCConfig


def compute_zero_forcing_beamformer(h_JB: np.ndarray, h_JE: np.ndarray) -> np.ndarray:
    """Solve Eq. (5) using an LP, with scaled channels and |w_i| <= 1.

    On the null space Bob's term is constant and Eq. (4) decreases with
    Eve leakage, so maximizing |h_JE^T w| solves the stated constraint.
    """
    jb, je = np.asarray(h_JB, dtype=float), np.asarray(h_JE, dtype=float)
    if jb.ndim != 1 or jb.shape != je.shape or not len(jb):
        raise ValueError("Jammer vectors must be nonempty with identical shapes")
    if not np.all(np.isfinite(jb)) or not np.all(np.isfinite(je)):
        raise ValueError("Channel vectors must be finite")
    if not np.any(je):
        return np.zeros_like(jb)
    if not np.any(jb):
        return np.sign(je)
    result = linprog(-je / np.max(np.abs(je)),
                     A_eq=[jb / np.max(np.abs(jb))], b_eq=[0.],
                     bounds=[(-1., 1.)] * len(jb), method="highs")
    if not result.success:
        raise RuntimeError(f"Zero-forcing LP failed: {result.message}")
    w = np.clip(result.x, -1., 1.)
    if abs(je @ w) <= 32 * np.finfo(float).eps * np.linalg.norm(je, 1):
        return np.zeros_like(jb)
    return w


def compute_theoretical_bounds(h_AB: float, h_AE: float, h_JB: np.ndarray,
                               h_JE: np.ndarray, config: Optional[VLCConfig] = None,
                               sigma_B_sq: Optional[float] = None) -> Tuple[float, float, float, np.ndarray]:
    """Return global rate upper, BER lower, utility upper and a ZF reference.

    The bounds are independently valid, not necessarily jointly attainable.
    The returned reference action does NOT attain the bounds. Eq. (21)'s
    conditional expression is available separately via corollary_diagnostics.
    """
    c = config or VLCConfig()
    noise = c.noise_variance if sigma_B_sq is None else sigma_B_sq
    if not np.isfinite(noise) or noise <= 0:
        raise ValueError("Noise variance must be finite and positive")
    if c.model == "physical":
        from .physical import pam_mutual_information, pam_bit_map_lower_bound
        peak=abs(h_AB)*c.modulation_index*c.id_bias
        rate=pam_mutual_information(peak,0.,noise)*c.symbol_rate_per_hz
        ber=pam_bit_map_lower_bound(peak,noise)
        return rate,ber,rate-c.delta1*ber,compute_zero_forcing_beamformer(h_JB,h_JE)
    signal = 2 * h_AB**2 * c.modulation_index**2 * c.id_bias**2
    rate_upper = float(.5 * np.log2(1 + signal / (np.pi * np.e * noise)))
    max_effective = abs(h_AB) + np.sum(np.abs(h_JB))
    ber_lower = float(.75 * erfc(np.sqrt(2 * c.led_avg_power * max_effective**2 / (5 * noise))))
    min_energy = -c.unit_jamming_cost * len(h_JB) if c.energy_model == "paper_signed" else 0.
    utility_upper = rate_upper - c.delta1 * ber_lower - c.delta2 * min_energy
    return rate_upper, ber_lower, float(utility_upper), compute_zero_forcing_beamformer(h_JB, h_JE)


def corollary_diagnostics(h_AB, h_AE, h_JB, h_JE, config=None, sigma_B_sq=None):
    """Expose Eq. (21)/(23) without claiming validity outside Eq. (20)."""
    c = config or VLCConfig()
    if c.model == "physical":
        return {"applicable":False,"reason":"Physical 4-PAM channel uses finite-alphabet mutual information; paper Corollary 1 is not applied."}
    ceiling, _, _, w = compute_theoretical_bounds(h_AB, h_AE, h_JB, h_JE, c, sigma_B_sq)
    L = float(np.log2(np.sqrt(np.e)))
    target = h_AE / L
    possible = abs(float(np.dot(h_JE, w)))
    ratio = 1. / L if h_AE > 0 else None
    return {"equation21_value": float(max(0., ceiling - (np.log2(L) + 1.))),
            "equation23_target": float(target), "target_feasible": bool(target <= possible),
            "target_ratio": ratio, "condition20_at_target": bool(h_AE > 0 and ratio <= 1.),
            "applicable": False,
            "reason": "Base-2 Eq. (23) gives H/h_AE=1.386294, outside Eq. (20); author clarification required."}

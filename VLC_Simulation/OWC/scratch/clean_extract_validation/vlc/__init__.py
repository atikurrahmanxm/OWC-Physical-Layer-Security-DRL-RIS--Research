"""
Visible Light Communication Physical-Layer Security (VLC-PLS) Package.
Implements:
'Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication'
IEEE Transactions on Wireless Communications (2024).
"""

from .config import VLCConfig
from .channel import VLCChannel
from .secrecy import (
    compute_secrecy_rate,
    compute_bob_ber,
    compute_energy_consumption,
    compute_system_utility,
)
from .bounds import (
    compute_zero_forcing_beamformer,
    compute_theoretical_bounds,
)
from .environment import VLCEnvironment
from .rl_fj import RLFJAgent
from .drl_fj import DRLFJAgent
from .benchmarks import BenchmarkRunner

__all__ = [
    "VLCConfig",
    "VLCChannel",
    "compute_secrecy_rate",
    "compute_bob_ber",
    "compute_energy_consumption",
    "compute_system_utility",
    "compute_zero_forcing_beamformer",
    "compute_theoretical_bounds",
    "VLCEnvironment",
    "RLFJAgent",
    "DRLFJAgent",
    "BenchmarkRunner",
]

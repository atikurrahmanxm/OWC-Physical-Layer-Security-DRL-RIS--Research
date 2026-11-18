"""Reproducible experiment records shared by CLI, figures and browser."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
from .config import VLCConfig
from .environment import VLCEnvironment
from .rl_fj import RLFJAgent
from .drl_fj import DRLFJAgent
from .benchmarks import BenchmarkRunner
from .bounds import corollary_diagnostics, compute_theoretical_bounds
from .secrecy import compute_secrecy_rate, compute_bob_ber, compute_energy_consumption, compute_system_utility


def json_value(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(type(value).__name__)


def save_record(path, record):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, default=json_value, allow_nan=False, indent=2), encoding="utf-8")


def canonical_config(data):
    """Fill documented legacy paper defaults without rewriting saved evidence."""
    return json.loads(json.dumps(asdict(VLCConfig(**data)), default=json_value))


def tag_figure(config):
    """Identify standalone exports from the alternative physical experiment."""
    if config.model == 'physical':
        import matplotlib.pyplot as plt
        plt.gcf().suptitle('Physical 4-PAM model | explicit assumptions | no paper calibration',fontsize=9)
        plt.gcf().tight_layout(rect=(0,0,1,.95))


def metadata(config, **extra):
    pdf = Path(__file__).resolve().parents[1] / "19 Sep 2024.pdf"
    interpretation = ({"noise_variance_unit":"A^2", "information_input":"Equiprobable Gray 4-PAM, peak alpha*I_D",
        "jamming_input":"Independent shared uniform scalar U[-alpha*I_D, alpha*I_D], beam weights w",
        "rate":"Positive part of I(X;Y_B)-I(X;Y_E), multiplied by symbol_rate_per_hz",
        "BER":"Exact Gray-label midpoint decision errors under the same uniform-plus-AWGN PDF",
        "energy_unit":"J, incremental AC driver energy; excludes DC illumination, circuitry and amplifier efficiency",
        "noise_conversion":"P_noise[W]/receiver_resistance[ohm] = sampled current variance[A^2]",
        "assumptions":"1-ohm receiver/driver loads, 1-second slots, equal Bob/Eve AWGN, 1 symbol/s/Hz unless configured",
        "paper_equations_reproduced":False} if config.model == "physical" else
        {"rate":"Printed Eq. (4), continuous-input expression", "BER":"Printed Eq. (14)",
         "noise_variance_unit":"Legacy numeric Table I watts; impedance convention unresolved",
         "energy_unit":"Normalized cost; selected interpretation recorded in config"})
    return {"config": asdict(config), "model_interpretation":interpretation,
            "numpy": np.__version__, "torch": torch.__version__,
            "paper_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest() if pdf.exists() else None,
            "reproduction_verified": False,
            "unresolved": ["Author SNR normalization and raw traces unavailable",
                           "L1 energy interprets ambiguous Eq. (16); opt-in paper_signed can reward negative energy",
                           "Base-2 Eqs. (20)/(23) conflict; conditional Eq. (21) is not a global bound",
                           "Custom comparison baselines do not implement references [20], [42], [43]"],
            **extra}


def diagnose_operating_point(env):
    """Separate physical/action-grid limitations from learned performance.

    This exhaustive reference never supplies actions or rewards to either agent.
    It also explains when utility maximization rationally selects zero secrecy.
    """
    c = env.config
    sigma = env.sigma_B_sq if env.sigma_B_sq is not None else c.noise_variance
    gains = env.h_AB, env.h_AE, env.h_JB, env.h_JE
    ceiling = compute_theoretical_bounds(*gains, c, sigma)[0]
    rates, utilities = [], []
    for w in env.action_space:
        rate = compute_secrecy_rate(*gains, w, c, sigma)
        pe = compute_bob_ber(env.h_AB, env.h_JB, w, c, sigma)
        energy = compute_energy_consumption(w, c)
        rates.append(rate)
        utilities.append(compute_system_utility(rate, pe, energy, c))
    best = int(np.argmax(utilities))
    return {"noise_variance": sigma, "bob_capacity_ceiling": ceiling,
            "action_count": env.num_actions,
            "maximum_discrete_secrecy_rate": max(rates),
            "maximum_discrete_utility": utilities[best],
            "secrecy_at_maximum_discrete_utility": rates[best],
            "maximum_utility_action": env.action_space[best],
            "reference_only": True}


def run_learning_experiment(config=None, bob=None, eve=None, sigma=None, slots=2000):
    c = config or VLCConfig()
    if not isinstance(slots, int) or slots < 1:
        raise ValueError("slots must be a positive integer")
    torch.set_num_threads(1)
    def environment():
        return VLCEnvironment(c, bob_pos=bob, eve_pos=eve, sigma_B_sq=sigma)
    base = environment()
    histories, actions = {}, {}
    for name, cls in [("rl", RLFJAgent), ("drl", DRLFJAgent)]:
        agent = cls(environment(), c)
        histories[name] = agent.train(slots)
        actions[name] = agent.action_history
    runner = BenchmarkRunner(base, c)
    histories["global_bounds"] = runner.run_theoretical_bound(slots)
    histories["zf"] = runner.run_zero_forcing(slots)
    histories["custom_restricted"] = runner.run_restricted_search(slots)
    histories["custom_regularized"] = runner.run_regularized(slots)
    histories["custom_scaled_zf"] = runner.run_scaled_zf(slots)
    return {"metadata": metadata(c, slots=slots, bob=base.bob_pos, eve=base.eve_pos,
                                  sigma_B_sq=base.sigma_B_sq or c.noise_variance,
                                  channel_model="stationary Lambertian LOS"),
            "histories": histories, "actions": actions,
            "operating_point": diagnose_operating_point(base),
            "corollary": corollary_diagnostics(base.h_AB, base.h_AE, base.h_JB, base.h_JE, c, sigma)}

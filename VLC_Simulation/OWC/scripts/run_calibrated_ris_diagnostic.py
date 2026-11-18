"""Independent, opt-in 4-PAM/RIS finite-grid diagnostic; never trains an agent.

This does not change the historical paper-mode experiment or infer Table I's
missing electrical load. Noise is a declared receiver-current variance fixed
from nominal direct-Bob 4-PAM SNR, then shared across schemes and geometries.
Run through Antigravity as requested by the user. Output is bits/channel use.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

import numpy as np
from scipy.integrate import quad
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vlc.channel import VLCChannel
from vlc.config import VLCConfig
from vlc.physical import pam_mutual_information, pam_bit_error_rate
from vlc.ris import OpticalRIS, OpticalRISConfig


SCENARIOS = {
    'nominal': ((1.8, 1.6, .85), (3.2, 3.4, .85)),
    'changed_positions': ((2., 3., .85), (3.5, 1.5, .85)),
    'colocated': ((1.8, 1.6, .85), (1.8, 1.6, .85)),
}


def independent_checks() -> dict:
    """Integration, waveform Monte Carlo and symmetry checks before enumeration."""
    checks = {}
    levels = np.array([-1., -1/3, 1/3, 1.])
    bits = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])
    amplitude = 2.3

    def integrand(y):
        conditional = norm.pdf(y - amplitude * levels)
        marginal = conditional.mean()
        return np.sum(conditional * np.log2(np.maximum(conditional, 1e-300) /
                                            max(marginal, 1e-300))) / 4

    reference = quad(integrand, -16, 16, epsabs=1e-10)[0]
    implemented = pam_mutual_information(amplitude, 0., 1.)
    assert abs(reference - implemented) < 1e-8, (reference, implemented)
    checks['independent_awgn_integration_absolute_error'] = abs(reference - implemented)

    rng = np.random.default_rng(20261118)
    sent = rng.integers(4, size=300000)
    j = rng.uniform(-1.7, 1.7, len(sent))
    noise = rng.normal(0., np.sqrt(.35), len(sent))
    theoretical = pam_bit_error_rate(2.1, 1.7, .35)
    observed = []
    for sign in [-1., 1.]:
        y = 2.1 * levels[sent] + sign * j + noise
        decoded = np.digitize(y, [-1.4, 0., 1.4])
        ber = float(np.mean(bits[sent] != bits[decoded]))
        assert abs(ber - theoretical) < .0025, (ber, theoretical)
        observed.append(ber)
    checks['waveform_monte_carlo'] = {
        'symbols': len(sent), 'seed': 20261118, 'theoretical_ber': theoretical,
        'negative_jammer_ber': observed[0], 'positive_jammer_ber': observed[1],
        'absolute_tolerance': .0025,
    }

    convergence = []
    for a, j in [(0.1, 0.), (1., 2.), (10., 30.), (100., 1000.)]:
        low = pam_mutual_information(a, j, 1., 24)
        high = pam_mutual_information(a, j, 1., 48)
        assert abs(low - high) < 1e-7, (a, j, low, high)
        assert abs(low - pam_mutual_information(a*1e-6, j*1e-6, 1e-12)) < 1e-9
        convergence.append({'signal_peak': a, 'jammer_peak': j, 'absolute_difference': abs(low-high)})
    checks['quadrature_and_current_scaling'] = convergence
    assert pam_mutual_information(0., 1., 1.) == 0.
    assert pam_bit_error_rate(0., 1., 1.) == .5
    assert pam_mutual_information(50., 0., 1.) > 1.9999
    checks['zero_signal_and_finite_alphabet_ceiling'] = 'passed'
    return checks


def evaluate_grid(gains, weights, noise, amplitude):
    """All q/weight combinations under one explicit input/interference law."""
    rows = []
    for q, (ab, ae, jb, je) in enumerate(gains):
        for w in weights:
            bp = abs(float(np.dot(jb, w))) * amplitude
            ep = abs(float(np.dot(je, w))) * amplitude
            ib = pam_mutual_information(ab * amplitude, bp, noise)
            ie = pam_mutual_information(ae * amplitude, ep, noise)
            ber = pam_bit_error_rate(ab * amplitude, bp, noise)
            rate = max(0., ib - ie)
            assert 0 <= ib <= 2 and 0 <= ie <= 2 and 0 <= rate <= 2 and 0 <= ber <= .5
            rows.append((q, *w, ib, ie, rate, ber, np.sum(np.abs(w))))
    return np.asarray(rows, dtype=float)


def summarize(rows, threshold):
    """Oracle maxima and QoS-feasible maxima; not learned policy performance."""
    def action(row):
        return {
            'q': int(row[0]), 'jammer_weights': row[1:5].tolist(),
            'bob_mi_bits_per_use': row[5], 'eve_mi_bits_per_use': row[6],
            'secrecy_difference_bits_per_use': row[7], 'bob_ber': row[8],
            'l1_amplitude_cost': row[9],
        }
    best = rows[np.argmax(rows[:, 7])]
    feasible = rows[rows[:, 8] <= threshold]
    return {
        'actions': len(rows), 'qos_feasible_actions': len(feasible),
        'maximum_secrecy': action(best),
        'maximum_secrecy_subject_to_bob_ber': action(feasible[np.argmax(feasible[:, 7])]) if len(feasible) else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'output_figures/ris/calibrated_diagnostic_v1')
    parser.add_argument('--snr-db', type=float, nargs='+', default=[10., 20., 30.])
    parser.add_argument('--scenarios', nargs='+', choices=SCENARIOS, default=list(SCENARIOS))
    parser.add_argument('--bob-ber-max', type=float, default=1e-3)
    args = parser.parse_args()
    assert all(np.isfinite(args.snr_db)) and 0 < args.bob_ber_max < .5
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    start = time.time()
    checks = independent_checks()
    cfg = VLCConfig(model='paper', energy_model='l1', cnn_m0=11)
    channel = VLCChannel(cfg)
    direct_reference = channel.get_all_channel_gains()[0]
    amplitude = cfg.modulation_index * cfg.id_bias
    reference_signal_variance = (5/9) * (direct_reference * amplitude)**2
    weights = np.asarray(list(itertools.product([-1., -.5, 0., .5, 1.], repeat=4)))
    results = []
    for scenario in args.scenarios:
        bob, eve = [np.asarray(x) for x in SCENARIOS[scenario]]
        direct = channel.get_all_channel_gains(bob, eve)
        ris = OpticalRIS(cfg, OpticalRISConfig(), bob_pos=bob, eve_pos=eve)
        gains = []
        for q in range(5):
            reflected = ris.get_reflected_gains(q)
            gains.append(tuple(np.asarray(a)+np.asarray(b) for a,b in zip(direct, reflected)))
        for snr in args.snr_db:
            noise = reference_signal_variance / (10.**(snr/10.))
            rows = evaluate_grid(gains, weights, noise, amplitude)
            schemes = {
                'no_ris': summarize(rows[rows[:,0] == 0], args.bob_ber_max),
                'fixed_ris_q1': summarize(rows[rows[:,0] == 1], args.bob_ber_max),
                'joint_ris_oracle': summarize(rows, args.bob_ber_max),
            }
            # Inclusion is a property of feasible action sets, not an RL result.
            joint_max = schemes['joint_ris_oracle']['maximum_secrecy']['secrecy_difference_bits_per_use']
            assert joint_max+1e-12 >= max(s['maximum_secrecy']['secrecy_difference_bits_per_use'] for s in schemes.values())
            if scenario == 'colocated':
                assert np.max(rows[:,7]) < 1e-10, np.max(rows[:,7])
            filename = f'{scenario}_snr{snr:g}.npz'
            np.savez_compressed(output/filename, values=rows,
                                columns=['q','w1','w2','w3','w4','bob_mi','eve_mi','secrecy_difference','bob_ber','l1_cost'])
            results.append({'scenario': scenario, 'bob_position_m': bob.tolist(), 'eve_position_m': eve.tolist(),
                            'reference_snr_db': snr, 'receiver_current_noise_variance_A2': noise,
                            'schemes': schemes, 'raw_grid_file': filename})
            print(scenario, f'{snr:g} dB', f'maximum secrecy {joint_max:.6f} bits/use', flush=True)
    sources = [Path(__file__).resolve()] + [ROOT/'vlc'/name for name in ['physical.py','channel.py','ris.py','config.py']]
    payload = {
        'study': 'calibrated_current_domain_4pam_ris_diagnostic_v1',
        'model_status': 'Explicit alternative diagnostic; not the historical paper-mode baseline or its DRL reward.',
        'signal_model': 'y_r=h_Ar*x+(h_Jr^T*w)*j+n_r; equiprobable Gray 4-PAM x, independent shared uniform j, Gaussian n_r.',
        'noise_convention': 'Current variance derived from nominal direct-Bob 4-PAM symbol SNR and held fixed across schemes and geometries at each SNR.',
        'reference_direct_bob_gain': direct_reference,
        'reference_4pam_signal_variance_A2': reference_signal_variance,
        'information_unit': 'bits per real channel use; no uncalibrated bps/Hz conversion',
        'secrecy_interpretation': 'Positive fixed-input mutual-information difference under the declared independent shared jammer/noise law. No packet-decoding or hardware-security guarantee.',
        'receiver_model': 'Bob uses nominal 4-PAM midpoint decisions for BER; mutual information assumes the stated conditional density.',
        'eve_assumption': 'Eve has no realization of the friendly-jammer waveform as side information; equal receiver-noise variances.',
        'qos_constraint': {'bob_ber_max': args.bob_ber_max},
        'energy': 'L1 amplitude cost recorded for comparability only; no energy in joules or total-energy claim.',
        'policy_status': 'Exhaustive finite-grid oracle; no DRL training, retraining, or learned-policy transfer claim.',
        'checks': checks, 'results': results, 'elapsed_seconds': time.time()-start,
        'sources': [{'path': str(p.relative_to(ROOT)).replace('\\','/'),
                     'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],
    }
    temp = output/'diagnostic_summary.tmp.json'
    temp.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    temp.replace(output/'diagnostic_summary.json')
    print('Complete:', len(results), 'scenario/SNR grids;', len(results)*3125, 'action evaluations.', flush=True)


if __name__ == '__main__':
    main()

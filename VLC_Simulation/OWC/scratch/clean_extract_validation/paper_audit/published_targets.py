"""Extract the supplied PDF's plotted curves and assess numerical agreement.

PDF path coordinates are published figure evidence, not author simulation traces.
Nothing in this module changes rewards, agent actions or simulation observations.
"""
import hashlib
from pathlib import Path

import numpy as np
from pypdf import PdfReader
from pypdf.generic import ContentStream
from scipy.special import erfcinv

ROOT = Path(__file__).resolve().parents[1]
COLORS = {(1., 0., 0.): 'drl', (0., 0., 1.): 'rl'}
# Ranges are read from the axis labels in the supplied PDF (pages 10 and 11).
FIGURES = {
    'figure6': (9, {'secrecy_rate': ('/Im7', 3., 6., False),
                   'ber': ('/Im8', -4., -1., True),
                   'utility': ('/Im9', 2., 5.5, False)}),
    'figure7': (10, {'secrecy_rate': ('/Im10', 1., 4.5, False),
                    'ber': ('/Im11', -4., -1., True),
                    'utility': ('/Im12', -.5, 4., False)}),
}


def extract_published_curves(pdf_path=ROOT / '19 Sep 2024.pdf'):
    pdf_path = Path(pdf_path)
    reader = PdfReader(pdf_path)
    result = {'provenance': {
        'paper_sha256': hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        'method': 'Vector path coordinates, transformed using printed axis ranges',
        'author_raw_data': False,
        'precision': 'Limited by PDF coordinate rounding; no claim of exact author samples',
        'figure7_note': 'Five plotted vertices at 4, 8, 12, 16, 20 dB; nine axis ticks.'}}
    for figure, (page_number, metrics) in FIGURES.items():
        result[figure] = {}
        for metric, (form_name, low, high, logarithmic) in metrics.items():
            form = reader.pages[page_number]['/Resources']['/XObject'][form_name].get_object()
            operations = ContentStream(form, reader).operations
            # The largest rectangle smaller than the full figure background is
            # the plot area; smaller rectangles enclose the legend.
            rectangles = [[float(x) for x in args] for args, op in operations
                          if op == b're' and len(args) == 4 and args[2] > 0 and args[3] > 0]
            background_area = max(r[2] * r[3] for r in rectangles)
            left, bottom, width, height = max(
                (r for r in rectangles if r[2] * r[3] < background_area), key=lambda r: r[2] * r[3])
            curves, color, path = {}, None, []
            for args, op in operations:
                if op == b'RG':
                    color = tuple(float(x) for x in args)
                elif op == b'G':
                    color = None
                elif op == b'm':
                    path = [[float(x) for x in args]]
                elif op == b'l':
                    path.append([float(x) for x in args])
                elif op == b'S':
                    name = COLORS.get(color)
                    expected = 1999 if figure == 'figure6' else 5
                    if name and name not in curves and len(path) == expected:
                        xy = np.asarray(path)
                        axis_x = (xy[:, 0] - left) / width
                        x = axis_x * 2000 if figure == 'figure6' else 4 + axis_x * 16
                        y = low + (xy[:, 1] - bottom) / height * (high - low)
                        if logarithmic:
                            y = 10. ** y
                        curves[name] = {'x': x.tolist(), 'y': y.tolist()}
                    path = []
                elif op in (b'f', b'f*', b'n', b's'):
                    path = []
            if set(curves) != {'rl', 'drl'}:
                raise ValueError(f'Unexpected PDF paths for {figure}/{metric}')
            if figure == 'figure7':
                if not np.allclose(curves['drl']['x'], [4, 8, 12, 16, 20], atol=1e-6):
                    raise ValueError('Unexpected Figure 7 sample positions')
            result[figure][metric] = {'pdf_page': page_number + 1, 'form': form_name,
                                     'axis_logarithmic': logarithmic, 'curves': curves}
    return result


def compare_value(actual, expected, *, absolute=None, factor=None):
    """Two-sided checks: an implausibly low BER is also a mismatch."""
    actual, expected = float(actual), float(expected)
    finite = np.isfinite(actual) and np.isfinite(expected)
    if absolute is not None:
        passed = finite and abs(actual - expected) <= absolute
        tolerance = {'absolute': absolute}
    elif factor is not None:
        passed = finite and expected > 0 and expected / factor <= actual <= expected * factor
        tolerance = {'multiplicative_factor': factor}
    else:
        raise ValueError('A declared tolerance is required')
    return {'paper': expected, 'computed': actual, 'passed': bool(passed),
            'absolute_error': abs(actual - expected), 'tolerance': tolerance}


def assess_published_targets(run, sweep, reference):
    from simulations.sim_fig6_convergence import smooth_curve
    rate = smooth_curve(np.asarray(run['histories']['drl']['secrecy_rate']), 50)[1399]
    ber = smooth_curve(np.asarray(run['histories']['drl']['ber']), 50)[1199]
    checkpoints = {
        'DRL_rate_slot_1400': compare_value(rate, 5.68, absolute=.05),
        'DRL_BER_slot_1200': compare_value(ber, .0002, factor=1.25)}
    comparisons = []
    points = {float(p['snr_db']): p for p in sweep['points']}
    for metric, curves in reference['figure7'].items():
        for agent in ['rl', 'drl']:
            curve = curves['curves'][agent]
            for db, expected in zip(curve['x'], curve['y']):
                point = points[round(db, 6)]
                actual = np.mean(point['histories'][agent][metric])
                kwargs = {'factor': 1.25} if metric == 'ber' else {'absolute': .05}
                comparisons.append({'snr_db': db, 'metric': metric, 'agent': agent,
                                    **compare_value(actual, expected, **kwargs)})
    all_passed = all(c['passed'] for c in checkpoints.values()) and all(c['passed'] for c in comparisons)
    return {'numerical_targets_passed': bool(all_passed),
            'status': 'pass' if all_passed else 'fail',
            'scope': 'Quoted Figure 6 checkpoints and all plotted RL/DRL Figure 7 vertices',
            'tolerance_source': 'Explicit local acceptance thresholds, not author-provided tolerances',
            'checkpoints': checkpoints, 'figure7': comparisons,
            'passed_comparisons': sum(c['passed'] for c in comparisons) + sum(c['passed'] for c in checkpoints.values()),
            'total_comparisons': len(comparisons) + len(checkpoints),
            'reproduction_verified': False,
            'certification_note': 'Numerical agreement alone cannot validate unknown author settings or custom baselines.'}


def noise_compatibility(config, gains, action_space, rate_target=5.68, ber_target=.0002):
    """Invert Eqs. (4)/(14) without altering any physical parameters.

    Per-action inversions concern a fixed operating point. They do not prove
    impossibility for different time slots, randomized averages or unknown traces.
    """
    from vlc.secrecy import compute_secrecy_rate, compute_bob_ber
    from vlc.bounds import compute_theoretical_bounds
    ab, ae, jb, je = gains
    coefficient = config.modulation_index**2 * config.id_bias**2
    inversions = []
    for action in action_space:
        t_b, t_e = float(jb @ action), abs(float(je @ action))
        if t_e == 0 and ae != 0:
            continue
        log_sqrt_e = np.log2(np.sqrt(np.e))
        leakage = 0. if ae == 0 else min(np.log2(ae/t_e) + t_e/ae*log_sqrt_e,
                                        ae/t_e*log_sqrt_e)
        needed_sinr = np.expm1(2 * (rate_target + leakage) * np.log(2.))
        variance_rate = 2 * ab**2 * coefficient / (np.pi * np.e * needed_sinr) - 2 * t_b**2 * coefficient
        if variance_rate <= 0:
            continue
        variance_ber = 2 * config.led_avg_power * (ab + t_b)**2 / (5 * erfcinv(ber_target/.75)**2)
        if variance_ber <= 0:
            continue
        inversions.append({'action': np.asarray(action).tolist(),
                           'noise_for_rate_target': float(variance_rate),
                           'noise_for_ber_target': float(variance_ber),
                           'noise_gap_db': float(10*np.log10(variance_ber/variance_rate)),
                           'rate_recomputed': compute_secrecy_rate(*gains, action, config, variance_rate),
                           'ber_at_rate_target': compute_bob_ber(ab, jb, action, config, variance_rate)})
    variance_zf_ber = 2 * config.led_avg_power * ab**2 / (5 * erfcinv(ber_target/.75)**2)
    result = {'rate_target': rate_target, 'ber_target': ber_target,
              'nominal_noise': config.noise_power_watts,
              'nominal_rate_ceiling': compute_theoretical_bounds(*gains, config)[0],
              'rate_target_feasible_at_nominal_noise': bool(rate_target <= compute_theoretical_bounds(*gains, config)[0]),
              'zero_forcing_noise_for_ber_target': float(variance_zf_ber),
              'zero_forcing_ber_recomputed': compute_bob_ber(ab, jb, np.zeros_like(jb), config, variance_zf_ber),
              'grid_actions_supporting_rate_target_at_some_noise': len(inversions),
              'scope': 'Current config and fixed channel/action grid; not a claim that the paper is universally inconsistent',
              'printed_signal_scales': {'secrecy_alpha_squared_bias_squared': coefficient,
                                        'BER_P_T': config.led_avg_power}}
    if inversions:
        result['closest_single_action_noise_requirements'] = min(inversions, key=lambda r: abs(r['noise_gap_db']))
    return result


def plot_comparison(run, sweep, reference, destination):
    """Show the measured discrepancy; published paths never replace agent data."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from simulations.sim_fig6_convergence import smooth_curve
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
    labels = {'secrecy_rate': 'Secrecy rate (bps/Hz)', 'ber': 'BER', 'utility': 'Utility'}
    for column, metric in enumerate(labels):
        for row, figure in enumerate(['figure6', 'figure7']):
            ax = axes[row, column]
            paper = reference[figure][metric]['curves']['drl']
            ax.plot(paper['x'], paper['y'], color='black', label='Paper DRL (PDF vector path)')
            if figure == 'figure6':
                y = smooth_curve(np.asarray(run['histories']['drl'][metric]), 50)
                x = np.arange(1, len(y)+1)
            else:
                x = [p['snr_db'] for p in sweep['points']]
                y = [np.mean(p['histories']['drl'][metric]) for p in sweep['points']]
            if metric == 'ber':
                y = np.maximum(y, 1e-30)  # Plot display only; raw measurements stay unchanged.
                ax.set_yscale('log')
            ax.plot(x, y, color='tab:red', label='Current DRL (EMA50)' if row == 0 else 'Current DRL (all-slot mean)')
            ax.set_xlabel('Time slot' if row == 0 else 'SNR (dB), configured eq4 convention')
            ax.set_ylabel(labels[metric])
            ax.set_title(f"Figure {6+row}: {metric.replace('_', ' ')}")
            ax.grid(alpha=.3)
            ax.legend(fontsize=8)
    fig.suptitle('Published targets versus actual simulation: numerical reproduction FAILS')
    fig.savefig(destination, dpi=160)
    plt.close(fig)

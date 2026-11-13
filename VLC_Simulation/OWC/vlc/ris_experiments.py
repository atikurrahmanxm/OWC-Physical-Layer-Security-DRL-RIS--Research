"""Matched paper-mode RIS/FJ/DRL experiments with raw observations and references.

All schemes use the same printed rate/BER equations, power budget, energy
interpretation, seed and CNN input size. An exhaustive finite-action reference
is a diagnostic only: it never provides actions or Q-values to the learners.
"""
from dataclasses import asdict, replace
from pathlib import Path
import hashlib
import re
import time
import numpy as np
import torch
from scipy.stats import t as student_t

from .config import VLCConfig
from .channel import VLCChannel
from .drl_fj import DRLFJAgent
from .bounds import compute_zero_forcing_beamformer
from .experiments import metadata, save_record

SCHEMES = {
    'baseline': {'control_mode': 'off', 'label': 'FJ + DRL, no RIS'},
    'fixed_ris': {'control_mode': 'fixed', 'label': 'Fixed RIS + FJ + DRL'},
    'joint_ris': {'control_mode': 'joint', 'label': 'Joint RIS + FJ + DRL'},
}
METRICS = ('secrecy_rate', 'ber', 'energy', 'utility')


def predefined_scenarios(config=None):
    """Static matched locations; these do not establish mobility robustness."""
    c = config or VLCConfig()
    bob = np.asarray(c.bob_pos).tolist()
    near = np.minimum(np.asarray(c.room_size), np.asarray(bob)+[.05,.05,0.]).tolist()
    return [
        {'name': 'nominal', 'bob': bob, 'eve': np.asarray(c.eve_pos).tolist()},
        {'name': 'near_bob', 'bob': bob, 'eve': near},
        {'name': 'colocated', 'bob': bob, 'eve': bob.copy()},
    ]


def estimate_uncertainty(values):
    """Student-t interval over independent seed runs; undefined for one seed."""
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('Uncertainty requires a nonempty finite vector')
    n = len(values)
    mean = float(values.mean())
    if n == 1:
        return {'n': 1, 'mean': mean, 'sample_std': None, 'standard_error': None,
                'ci95': None, 'ci_method': 'Unavailable: only one independent seed'}
    std = float(values.std(ddof=1))
    error = std / np.sqrt(n)
    half = float(student_t.ppf(.975, n-1)*error)
    return {'n': n, 'mean': mean, 'sample_std': std, 'standard_error': float(error),
            'ci95': [mean-half, mean+half], 'ci_method': 'Two-sided Student-t interval across seeds'}


def summarize_history(history, *, final_window=500, qos_ber_max=None, secrecy_target=.1):
    if type(final_window) is not int or final_window<1:
        raise ValueError('final_window must be a positive integer')
    lengths = {len(history[key]) for key in METRICS}
    if len(lengths) != 1 or min(lengths) < 1:
        raise ValueError('Histories must contain equally sized nonempty metric arrays')
    slots = lengths.pop()
    window = min(slots, final_window)
    result = {'slots': slots, 'final_window_slots': window,
              'aggregation': 'All training slots include warmup and epsilon exploration',
              'all_slots': {}, 'final_window': {}}
    for metric in METRICS:
        values = np.asarray(history[metric], dtype=float)
        if not np.isfinite(values).all():
            raise ValueError('History contains nonfinite observations')
        result['all_slots'][metric] = float(values.mean())
        result['final_window'][metric] = float(values[-window:].mean())
    ber, rate = np.asarray(history['ber']), np.asarray(history['secrecy_rate'])
    result['bob_qos_outage_fraction'] = None if qos_ber_max is None else float(np.mean(ber > qos_ber_max))
    result['secrecy_outage_fraction'] = float(np.mean(rate < secrecy_target))
    result['targets'] = {'bob_ber_max': qos_ber_max, 'secrecy_rate_min': secrecy_target}
    return result


def _action_record(env, action):
    info = env.evaluate_action(action)
    w, ris_index = env.decode_action(action)
    result = {key: info[key] for key in METRICS}
    result.update({'action': np.asarray(action, dtype=float).tolist(),
                   'beamformer': np.asarray(w, dtype=float).tolist(), 'ris_index': int(ris_index),
                   'base_utility': float(info.get('base_utility', info['utility'])),
                   'qos_violation': float(info.get('qos_violation', 0.)),
                   'gains': info.get('gains'), 'direct_gains': info.get('direct_gains'),
                   'reflected_gains': info.get('reflected_gains')})
    return result


def exhaustive_reference(env, *, qos_ber_max=None, secrecy_target=.1):
    """Enumerate the available discrete action grid, separately from learning."""
    best_reward = best_rate = best_feasible = None
    maximum_base = -np.inf
    bob_feasible = security_feasible = 0
    templates = {}
    for action in env.action_space:
        r = _action_record(env, action)
        templates.setdefault(r['ris_index'], action)
        if best_reward is None or r['utility'] > best_reward['utility']:
            best_reward = r
        if best_rate is None or r['secrecy_rate'] > best_rate['secrecy_rate']:
            best_rate = r
        maximum_base = max(maximum_base, r['base_utility'])
        feasible = qos_ber_max is None or r['ber'] <= qos_ber_max
        if feasible:
            bob_feasible += 1
            security_feasible += int(r['secrecy_rate'] >= secrecy_target)
            if best_feasible is None or r['utility'] > best_feasible['utility']:
                best_feasible = r
    no_jamming, zf = [], []
    for ris_index, template in templates.items():
        action = np.asarray(template).copy()
        action[:env.config.num_jammers] = 0.
        no_jamming.append(_action_record(env, action))
        gains = no_jamming[-1].get('gains')
        if isinstance(gains, dict) and 'h_JB' in gains and 'h_JE' in gains:
            action[:env.config.num_jammers] = compute_zero_forcing_beamformer(
                np.asarray(gains['h_JB']), np.asarray(gains['h_JE']))
            # A continuous nulling vector is a feasible geometric reference,
            # not an action furnished to the discrete learner.
            zf.append(_action_record(env, action))
    return {'reference_only': True, 'fed_to_agent': False,
            'scope': 'Exact enumeration of this finite codebook/grid, not a continuous global optimum',
            'action_count': env.num_actions, 'maximum_policy_reward': best_reward,
            'maximum_secrecy_rate': best_rate, 'maximum_base_utility': float(maximum_base),
            'bob_ber_feasible_actions': bob_feasible,
            'joint_secrecy_and_bob_feasible_actions': security_feasible,
            'best_bob_feasible_reward': best_feasible,
            'no_jamming_by_configuration': no_jamming,
            'continuous_channel_nulling_by_configuration': zf}


def _normalize_scenarios(config, scenarios):
    scenarios = [predefined_scenarios(config)[0]] if scenarios is None else scenarios
    if not scenarios:
        raise ValueError('At least one scenario is required')
    result, names = [], set()
    for scenario in scenarios:
        name = scenario.get('name')
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',name) or name in names:
            raise ValueError('Scenario names must be unique letters/digits/underscore/hyphen identifiers')
        names.add(name)
        bob, eve = np.asarray(scenario['bob'], dtype=float), np.asarray(scenario['eve'], dtype=float)
        if bob.shape != (3,) or eve.shape != (3,) or not np.isfinite([bob,eve]).all():
            raise ValueError('Scenario receiver positions must be finite three-vectors')
        if np.any(bob<0) or np.any(eve<0) or np.any(bob>config.room_size) or np.any(eve>config.room_size):
            raise ValueError('Scenario receivers must be inside the configured room')
        db = scenario.get('snr_db')
        if db is not None and not np.isfinite(db):
            raise ValueError('Scenario SNR must be finite')
        sigma=scenario.get('sigma_B_sq')
        if sigma is not None and (not np.isfinite(sigma) or sigma<=0 or db is not None):
            raise ValueError('An explicit positive noise override cannot be combined with an SNR override')
        result.append({'name': name, 'bob': bob.tolist(), 'eve': eve.tolist(),
                       'snr_db': None if db is None else float(db),
                       'sigma_B_sq': None if sigma is None else float(sigma)})
    return result


def aggregate_runs(runs):
    """Keep scenarios/energy interpretations distinct; pair differences by seed."""
    groups, paired = [], []
    keys = sorted({(r['scenario']['name'], r['energy_model']) for r in runs})
    for scenario, energy in keys:
        selected = [r for r in runs if r['scenario']['name']==scenario and r['energy_model']==energy]
        for scheme in SCHEMES:
            rows = [r for r in selected if r['scheme']==scheme]
            if not rows:
                continue
            groups.append({'scenario': scenario, 'energy_model': energy, 'scheme': scheme,
                           'seeds': [r['seed'] for r in rows],
                           'all_slots': {metric: estimate_uncertainty([r['summary']['all_slots'][metric] for r in rows]) for metric in METRICS},
                           'final_window': {metric: estimate_uncertainty([r['summary']['final_window'][metric] for r in rows]) for metric in METRICS},
                           'secrecy_outage': estimate_uncertainty([r['summary']['secrecy_outage_fraction'] for r in rows]),
                           'bob_qos_outage': None if rows[0]['summary']['bob_qos_outage_fraction'] is None else
                               estimate_uncertainty([r['summary']['bob_qos_outage_fraction'] for r in rows])})
        by_seed = {(r['seed'],r['scheme']): r for r in selected}
        for scheme in ['fixed_ris','joint_ris']:
            seeds = sorted(s for s,kind in by_seed if kind==scheme and (s,'baseline') in by_seed)
            if not seeds:
                continue
            paired.append({'scenario':scenario,'energy_model':energy,'comparison':scheme+' minus baseline',
                           'seeds':seeds,'all_slots':{metric: estimate_uncertainty([
                               by_seed[s,scheme]['summary']['all_slots'][metric]-by_seed[s,'baseline']['summary']['all_slots'][metric]
                               for s in seeds]) for metric in METRICS}})
    return groups, paired


def run_ris_study(config=None, ris_config=None, *, slots=2000, seeds=(42,), scenarios=None,
                  energy_models=None, output_dir='output_figures/ris', fixed_configuration=1,
                  qos_ber_max=None, qos_penalty=0., secrecy_target=.1, final_window=500,
                  include_exhaustive=True, progress=None):
    """Run matched stationary scenarios. No parameter fitting or gain guarantee."""
    c = config or VLCConfig(model='paper',energy_model='paper_signed')
    if c.model != 'paper':
        raise ValueError('The agreed RIS study uses the 2024 paper model, not physical mode')
    c = replace(c,cnn_m0=max(11,c.cnn_m0))
    if type(slots) is not int or slots<1 or type(final_window) is not int or final_window<1:
        raise ValueError('slots and final_window must be positive integers')
    seeds = tuple(seeds)
    if not seeds or len(set(seeds))!=len(seeds) or any(type(s) is not int or not 0<=s<2**32 for s in seeds):
        raise ValueError('Seeds must be unique unsigned 32-bit integers')
    energies = [c.energy_model] if energy_models is None else list(energy_models)
    if not energies or len(set(energies))!=len(energies) or any(e not in ['paper_signed','l1'] for e in energies):
        raise ValueError('Select unique paper_signed and/or l1 energy interpretations')
    if qos_ber_max is not None and (not np.isfinite(qos_ber_max) or not 0<qos_ber_max<=.75):
        raise ValueError('Bob BER threshold must lie in (0,.75]')
    if not np.isfinite(qos_penalty) or qos_penalty<0 or not np.isfinite(secrecy_target) or secrecy_target<0:
        raise ValueError('QoS penalty and secrecy target must be finite nonnegative values')
    if qos_penalty and qos_ber_max is None:
        raise ValueError('A QoS penalty requires a declared Bob BER threshold')
    scenarios = _normalize_scenarios(c,scenarios)
    # Keep expensive experimental imports lazy so statistical helpers and CLI
    # help remain usable independently from optional RIS implementation modules.
    from .ris_environment import RISEnvironment
    from .ris import OpticalRISConfig
    ris_config = ris_config or OpticalRISConfig()
    torch.set_num_threads(1)
    root = Path(__file__).resolve().parents[1]
    folder = Path(output_dir)
    folder.mkdir(parents=True,exist_ok=True)
    started = time.perf_counter()
    record = {'metadata': metadata(c,experiment='Matched optical RIS + FJ + CNN/DND DRL study',
                 slots_per_run=slots,seeds=seeds,stationarity='Independent static receiver-position scenarios',
                 observation_assumption='Perfect initial receiver geometry for a fixed scenario codebook; no Eve detector is modeled',
                 cnn_input_adaptation='m0=max(11, baseline m0) for ALL schemes; joint action adds normalized RIS code index',
                 aggregation='All training slots include warmup and exploration; final-window means are separately labeled',
                 references_used_for_training=False,paper_reproduction_verified=False),
              'settings': {'scenarios': scenarios,'energy_models':energies,
                           'ris_config': asdict(ris_config),'fixed_configuration':fixed_configuration,
                           'qos_ber_max':qos_ber_max,'qos_penalty':qos_penalty,
                           'secrecy_target':secrecy_target,'final_window':final_window},
              'schemes': SCHEMES, 'runs': [],'complete':False}
    count = len(energies)*len(scenarios)*len(seeds)*len(SCHEMES)
    completed = 0
    for energy in energies:
        for scenario in scenarios:
            for seed in seeds:
                cfg = replace(c,seed=seed,energy_model=energy,cnn_m0=max(11,c.cnn_m0),
                              bob_pos=np.asarray(scenario['bob']),eve_pos=np.asarray(scenario['eve']))
                ab = VLCChannel(cfg).get_all_channel_gains()[0]
                sigma = scenario['sigma_B_sq'] if scenario['sigma_B_sq'] is not None else cfg.noise_variance if scenario['snr_db'] is None else cfg.noise_variance_from_snr(ab,scenario['snr_db'])
                for scheme,details in SCHEMES.items():
                    message=f"RIS study {completed+1}/{count}: {scenario['name']}, energy={energy}, seed={seed}, {scheme}, {slots} slots"
                    if progress is None:
                        print(message,flush=True)
                    else:
                        progress(message)
                    env = RISEnvironment(config=cfg,ris_config=ris_config,
                        bob_pos=np.asarray(scenario['bob']),eve_pos=np.asarray(scenario['eve']),sigma_B_sq=sigma,
                        control_mode=details['control_mode'],fixed_configuration=fixed_configuration,
                        qos_ber_max=qos_ber_max,qos_penalty=qos_penalty)
                    t0 = time.perf_counter()
                    agent = DRLFJAgent(env,env.config)
                    history = agent.train(slots)
                    training_seconds = time.perf_counter()-t0
                    observations = [_action_record(env,a) for a in agent.action_history]
                    replay_errors = {metric:max(abs(o[metric]-history[metric][i]) for i,o in enumerate(observations)) for metric in METRICS}
                    if max(replay_errors.values())>1e-10:
                        raise RuntimeError(f'Saved-action replay mismatch: {replay_errors}')
                    reference = exhaustive_reference(env,qos_ber_max=qos_ber_max,secrecy_target=secrecy_target) if include_exhaustive else None
                    record['runs'].append({'scenario':scenario.copy(),'seed':seed,'energy_model':energy,'scheme':scheme,
                        'config':asdict(env.config),'sigma_B_sq':sigma,'ris':env.ris_metadata(),
                        'history':history,'actions':agent.action_history,'observations':observations,
                        'training_seconds':training_seconds,'action_replay_maximum_errors':replay_errors,
                        'summary':summarize_history(history,final_window=final_window,qos_ber_max=qos_ber_max,secrecy_target=secrecy_target),
                        'discrete_reference':reference})
                    completed += 1
                    # Checkpoints preserve completed runs if a later experiment
                    # fails; complete=False prevents treating partial data as a study.
                    save_record(folder/'ris_study_data.json',record)
    aggregates,paired = aggregate_runs(record['runs'])
    record.update({'aggregates':aggregates,'paired_seed_comparisons':paired,'complete':True,
                   'elapsed_seconds':time.perf_counter()-started,
                   'source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in (root/'vlc').glob('*.py')}})
    save_record(folder/'ris_study_data.json',record)
    save_record(folder/'ris_study_summary.json',{key:record[key] for key in
        ['metadata','settings','complete','elapsed_seconds','aggregates','paired_seed_comparisons','source_sha256']})
    return record

"""Verify current equation behavior and compare actual runs; never certify missing author data.

Historical results.json is deliberately preserved. Run the full figure pipeline first
for all published-figure comparisons: python main.py --mode all --slots 2000
"""
import hashlib
import json
import argparse
from dataclasses import asdict, replace
from pathlib import Path
import sys
import numpy as np
from scipy.special import erfc
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from vlc import VLCConfig,VLCChannel,VLCEnvironment
from vlc.secrecy import compute_secrecy_rate,compute_bob_ber,compute_energy_consumption,compute_system_utility
from vlc.bounds import compute_theoretical_bounds,compute_zero_forcing_beamformer,corollary_diagnostics
from vlc.experiments import metadata,save_record,json_value,canonical_config
from simulations.sim_fig6_convergence import smooth_curve
from paper_audit.published_targets import extract_published_curves, assess_published_targets, noise_compatibility, plot_comparison


def replay_actions(record, c, gains, sigma):
    """Recompute every saved agent observation from the recorded beam weights."""
    ab,ae,jb,je=gains
    errors=dict(secrecy_rate=0.,ber=0.,energy=0.,utility=0.)
    slots=0
    for name in ['rl','drl']:
        actions=record['actions'][name]
        history=record['histories'][name]
        assert len(actions)>=2000
        assert all(len(values)==len(actions) for values in history.values())
        for i,action in enumerate(actions):
            w=np.asarray(action)
            assert w.shape==(c.num_jammers,) and np.isfinite(w).all() and (np.abs(w)<=1).all()
            cs=compute_secrecy_rate(*gains,w,c,sigma)
            pe=compute_bob_ber(ab,jb,w,c,sigma)
            energy=compute_energy_consumption(w,c)
            expected=dict(secrecy_rate=cs,ber=pe,energy=energy,
                          utility=compute_system_utility(cs,pe,energy,c))
            for metric,value in expected.items():
                errors[metric]=max(errors[metric],abs(value-history[metric][i]))
            slots+=1
    assert max(errors.values())<1e-10, errors
    return {'slots_replayed':slots,'maximum_metric_errors':errors}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--equations-only', action='store_true',
                        help='Exit successfully for equation checks even if published numerical targets fail')
    args=parser.parse_args(argv)
    c=VLCConfig(); gains=VLCChannel(c).get_all_channel_gains();ab,ae,jb,je=gains
    rng=np.random.default_rng(2026);cases=[];errors=[]
    for _ in range(100):
        w=rng.uniform(-1,1,4);sigma=10**rng.uniform(-13,-9)
        pe=.75*erfc(np.sqrt(2*c.led_avg_power*(ab+jb@w)**2/(5*sigma)))
        actual=compute_bob_ber(ab,jb,w,c,sigma)
        errors.append(abs(pe-actual))
        if len(cases)<32:
            high,low,upper,_=compute_theoretical_bounds(*gains,c,sigma)
            cases.append(dict(h_AB=ab,h_AE=ae,h_JB=jb,h_JE=je,w=w,sigma=sigma,
                              cs=compute_secrecy_rate(*gains,w,c,sigma),ber=actual,
                              energy=compute_energy_consumption(w,c),rate_upper=high,utility_upper=upper,
                              zf=compute_zero_forcing_beamformer(jb,je)))
    rate_upper,ber_lower,utility_upper,zf=compute_theoretical_bounds(*gains,c)
    failures=[]
    for w in VLCEnvironment(c).action_space:
        cs=compute_secrecy_rate(*gains,w,c);pe=compute_bob_ber(ab,jb,w,c)
        u=compute_system_utility(cs,pe,compute_energy_consumption(w,c),c)
        if cs>rate_upper+1e-12 or pe<ber_lower-1e-12 or u>utility_upper+1e-12: failures.append(w.tolist())
    data_path=ROOT/'output_figures/fig6_data.json'
    if not data_path.exists():
        raise RuntimeError('Regenerate figures first: python main.py --mode all --slots 2000')
    run=json.loads(data_path.read_text(encoding='utf-8'))
    expected_config=json.loads(json.dumps(asdict(c),default=json_value))
    if canonical_config(run['metadata']['config']) != expected_config:
        raise RuntimeError('Figure 6 configuration is stale. Regenerate with current defaults.')
    if run['metadata']['slots']<2000:
        raise RuntimeError('Figure 6 data are a preview. Regenerate with --slots 2000.')
    history=run['histories']['drl']
    comparison={'DRL_rate_slot_1400':{'paper':5.68,'computed_raw':history['secrecy_rate'][1399],
                                    'computed_EMA50':float(smooth_curve(np.asarray(history['secrecy_rate']),50)[1399])},
                'DRL_BER_slot_1200':{'paper':.0002,'computed_EMA50':float(smooth_curve(np.asarray(history['ber']),50)[1199])}}
    points=[]
    for db in range(4,22,2):
        sigma=c.noise_variance_from_snr(ab,db)
        points.append({'snr_db':db,'maximum_discrete_rate':max(compute_secrecy_rate(*gains,w,c,sigma) for w in VLCEnvironment(c).action_space)})
    result={'metadata':metadata(c), 'checks':{'BER_literal_max_error':max(errors),'global_bound_counterexamples':failures,
             'default_energy_minus_ones':compute_energy_consumption(-np.ones(4),c),
             'literal_signed_energy_minus_ones':compute_energy_consumption(-np.ones(4),replace(c,energy_model='paper_signed'))},
            'corollary':corollary_diagnostics(*gains,c), 'rate_ceiling':rate_upper,
            'paper_comparison':comparison,'snr_action_exhaustion':{'convention':c.snr_definition,'points':points},
            'published_curves_reproduced':False,
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'vlc').glob('*.py')}}
    sweep_path=ROOT/'output_figures/fig7_data.json'
    if not sweep_path.exists():
        raise RuntimeError('Figure 7 data missing. Regenerate all figures.')
    sweep=json.loads(sweep_path.read_text(encoding='utf-8'))
    if canonical_config(sweep['metadata']['config']) != expected_config or sweep['metadata']['slots'] < 2000:
        raise RuntimeError('Figure 7 configuration or slot count is stale. Regenerate all figures.')
    if [p['snr_db'] for p in sweep['points']] != list(range(4,22,2)):
        raise RuntimeError('Figure 7 must contain all nine SNR points from 4 to 20 dB.')
    for p in sweep['points']:
        assert np.isclose(p['sigma_B_sq']/c.noise_variance_from_snr(ab,p['snr_db']),1.,rtol=1e-12)
    result['full_figure7_run']={'slots_per_agent_per_point':sweep['metadata']['slots'],
        'points':len(sweep['points']),
        'snr_db':[p['snr_db'] for p in sweep['points']],
        'drl_mean_rates':[float(np.mean(p['histories']['drl']['secrecy_rate'])) for p in sweep['points']]}
    result['zero_collapse_fixed']={
        'drl_slot_1400_positive':comparison['DRL_rate_slot_1400']['computed_EMA50']>1e-6,
        'all_nine_snr_means_positive':len(sweep['points'])==9 and all(
            x>0 for x in result['full_figure7_run']['drl_mean_rates'])}
    result['saved_actions_replayed']={
        'figure6':replay_actions(run,c,gains,c.noise_power_watts),
        'figure7':[replay_actions(p,c,gains,p['sigma_B_sq']) for p in sweep['points']]}
    reference=extract_published_curves()
    if any(record['metadata']['paper_sha256'] != reference['provenance']['paper_sha256'] for record in [run,sweep]):
        raise RuntimeError('Saved runs refer to a different PDF. Regenerate the figures.')
    conformance=assess_published_targets(run,sweep,reference)
    conformance['noise_compatibility']=noise_compatibility(c,gains,VLCEnvironment(c).action_space)
    curve=reference['figure7']['secrecy_rate']['curves']['drl']
    conformance['figure7_physical_feasibility']=[]
    for db,target in zip(curve['x'],curve['y']):
        ceiling=compute_theoretical_bounds(*gains,c,c.noise_variance_from_snr(ab,db))[0]
        conformance['figure7_physical_feasibility'].append({
            'snr_db':db, 'paper_secrecy_rate':target,'current_bob_capacity_ceiling':ceiling,
            'target_within_capacity_ceiling':bool(target<=ceiling)})
    result['numerical_conformance']={key:conformance[key] for key in
        ['status','passed_comparisons','total_comparisons','numerical_targets_passed','reproduction_verified']}
    save_record(ROOT/'paper_audit/published_curve_reference.json',reference)
    save_record(ROOT/'paper_audit/numerical_conformance.json',conformance)
    plot_comparison(run,sweep,reference,ROOT/'paper_audit/paper_comparison.png')
    save_record(ROOT/'paper_audit/verification_current.json',result)
    save_record(ROOT/'paper_audit/browser_reference.json',{'cases':cases,'record':run})
    assert max(errors)<1e-12 and not failures
    assert all(result['zero_collapse_fixed'].values()), 'Zero-collapse regression detected'
    print(json.dumps({'equation_checks':'passed','paper_comparison':comparison,
                      'zero_collapse_fixed':result['zero_collapse_fixed'],
                      'figure7_mean_rates':result['full_figure7_run']['drl_mean_rates'],
                      'published_curves_reproduced':False},indent=2))
    print('Current evidence: paper_audit/verification_current.json')
    print(f"Published numerical targets: {conformance['status'].upper()} "
          f"({conformance['passed_comparisons']}/{conformance['total_comparisons']} comparisons within declared tolerances).")
    print('Detailed comparison: paper_audit/numerical_conformance.json; plot: paper_audit/paper_comparison.png')
    if not args.equations_only and not conformance['numerical_targets_passed']:
        raise SystemExit(1)


if __name__=='__main__': main()

"""Replay the alternative physical experiment; does not certify paper reproduction."""
import json
import hashlib
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from vlc import VLCConfig,VLCChannel
from vlc.secrecy import compute_secrecy_rate,compute_bob_ber,compute_energy_consumption,compute_system_utility
from vlc.bounds import compute_theoretical_bounds
from vlc.experiments import save_record,canonical_config
from simulations.sim_fig6_convergence import smooth_curve


def replay(record,config,noise):
    gains=VLCChannel(config).get_all_channel_gains()
    ab,ae,jb,je=gains
    upper,lower,utility_upper,_=compute_theoretical_bounds(*gains,config,noise)
    errors=dict(secrecy_rate=0.,ber=0.,energy=0.,utility=0.)
    observations=0
    summary={}
    for name in ['rl','drl']:
        history=record['histories'][name]
        actions=np.asarray(record['actions'][name])
        assert actions.ndim==2 and actions.shape[1]==config.num_jammers
        assert len(actions)>=2000 and all(len(v)==len(actions) for v in history.values())
        assert np.isfinite(actions).all() and (np.abs(actions)<=1).all()
        assert np.allclose(actions*config.action_lx,np.rint(actions*config.action_lx),atol=1e-12,rtol=0)
        for i,w in enumerate(actions):
            rate=compute_secrecy_rate(*gains,w,config,noise)
            ber=compute_bob_ber(ab,jb,w,config,noise)
            energy=compute_energy_consumption(w,config)
            utility=compute_system_utility(rate,ber,energy,config)
            expected=dict(secrecy_rate=rate,ber=ber,energy=energy,utility=utility)
            assert rate<=upper+1e-8 and rate>=0 and lower-1e-8<=ber<=.5 and energy>=0 and utility<=utility_upper+1e-8
            for metric,value in expected.items():
                actual=history[metric][i]
                assert np.isfinite(actual)
                errors[metric]=max(errors[metric],abs(actual-value))
            observations+=1
        summary[name]={metric:float(np.mean(values)) for metric,values in history.items()}
    assert max(errors.values())<1e-10,errors
    return {'observations_replayed':observations,'maximum_absolute_errors':errors,
            'rate_upper':upper,'ber_lower':lower,'mean_metrics':summary}


def main():
    folder=ROOT/'output_figures/physical'
    run=json.loads((folder/'fig6_data.json').read_text())
    sweep=json.loads((folder/'fig7_data.json').read_text())
    config=VLCConfig(**run['metadata']['config'])
    assert config.model=='physical' and not run['metadata']['reproduction_verified']
    assert canonical_config(run['metadata']['config'])==canonical_config(sweep['metadata']['config'])
    assert [p['snr_db'] for p in sweep['points']]==list(range(4,22,2))
    nominal=replay(run,config,config.noise_variance)
    points=[]
    ab=VLCChannel(config).get_all_channel_gains()[0]
    for point in sweep['points']:
        sigma=config.noise_variance_from_snr(ab,point['snr_db'])
        assert np.isclose(point['sigma_B_sq']/sigma,1.,rtol=1e-12,atol=0)
        points.append({'snr_db':point['snr_db'],**replay(point,config,sigma)})
    history=run['histories']['drl']
    result={'physical_consistency_passed':True,'paper_reproduction_verified':False,
            'model_interpretation':run['metadata']['model_interpretation'],
            'figure6':nominal,'figure7':points,
            'drl_checkpoints':{'rate_slot1400_raw':history['secrecy_rate'][1399],
                               'rate_slot1400_EMA50':float(smooth_curve(np.array(history['secrecy_rate']),50)[1399]),
                               'ber_slot1200_raw':history['ber'][1199],
                               'ber_slot1200_EMA50':float(smooth_curve(np.array(history['ber']),50)[1199])},
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (ROOT/'vlc').glob('*.py')}}
    save_record(ROOT/'paper_audit/physical_verification.json',result)
    total=nominal['observations_replayed']+sum(p['observations_replayed'] for p in points)
    print(json.dumps({'observations_replayed':total,'consistency_passed':True,
                      'drl_checkpoints':result['drl_checkpoints'],
                      'figure7_drl_rate_means':[p['mean_metrics']['drl']['secrecy_rate'] for p in points],
                      'paper_reproduction_verified':False},indent=2))


if __name__=='__main__':main()

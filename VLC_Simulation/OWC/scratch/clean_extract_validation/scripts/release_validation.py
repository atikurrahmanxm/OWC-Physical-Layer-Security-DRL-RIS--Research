"""Saved-policy replay and prespecified supplementary geometry checks.

Reads the existing matched-v2 study without modifying source data or training.
Supplementary transfer uses frozen nominal-trained policies and reconstructs
the oracle codebook for each geometry. It is not a retraining experiment.
"""
import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from vlc.config import VLCConfig
from vlc.ris import OpticalRISConfig
from vlc.ris_environment import RISEnvironment
from vlc.drl_fj import DRLFJAgent

DATA=ROOT/'output_figures/ris/training_budget_study_matched_v2'
OUT=ROOT/'manuscript/research_draft_v2/release_audit'
SCHEMES={'baseline':'off','fixed_ris':'fixed','joint_ris':'joint'}
METRICS=('utility','secrecy_rate','ber','energy')
GEOMETRIES={
 'nominal':{'bob':[1.8,1.6,.85],'eve':[3.2,3.4,.85]},
 'changed_positions':{'bob':[2.,3.,.85],'eve':[3.5,1.5,.85]},
 'swapped_receivers':{'bob':[3.2,3.4,.85],'eve':[1.8,1.6,.85]},
 'near_eve':{'bob':[1.8,1.6,.85],'eve':[1.9,1.7,.85]},
 'colocated':{'bob':[1.8,1.6,.85],'eve':[1.8,1.6,.85]},
}

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
    temp.replace(path)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def build_env(scheme,geometry='nominal',noise_db=0):
    cfg=VLCConfig(model='paper',energy_model='l1',cnn_m0=11,seed=42)
    g=GEOMETRIES[geometry]
    return RISEnvironment(cfg,control_mode=SCHEMES[scheme],bob_pos=np.array(g['bob']),eve_pos=np.array(g['eve']),sigma_B_sq=cfg.noise_variance*10**(noise_db/10))

def load_agent(record,env):
    cfg=VLCConfig(model='paper',energy_model='l1',cnn_m0=11,seed=record['seed'])
    agent=DRLFJAgent(env,config=cfg)
    cp=DATA/'checkpoints'/record['checkpoints']['policy_cnn']
    mp=DATA/'checkpoints'/record['checkpoints']['dnd_memory']
    model=torch.load(cp,map_location='cpu',weights_only=True)
    assert (model['scheme'],model['seed'],model['budget'],model['protocol_version'])==(record['scheme'],record['seed'],record['budget'],2)
    assert model['num_actions']==env.num_actions
    agent.cnn.load_state_dict(model['cnn_state'],strict=True)
    agent.prev_cnn.load_state_dict(model['cnn_state'],strict=True)
    memory=json.loads(mp.read_text())
    for idx,payload in memory.items():
        d=agent.dnd_dict[int(idx)]
        d.keys=[np.asarray(k,dtype=np.float32) for k in payload['keys']]
        d.values=[float(x) for x in payload['values']]
        d.revision+=1
    return agent

def replay(records,slots):
    envs={s:build_env(s) for s in SCHEMES}
    rows=[]
    for n,(path,r) in enumerate(records,1):
        start=time.perf_counter();agent=load_agent(r,envs[r['scheme']]);actual=agent.evaluate(slots)
        errors={};matched=True
        for m in METRICS:
            x=np.asarray(actual['history'][m]);expected=np.asarray(r['evaluation'][m]['values'][:slots])
            err=float(np.max(np.abs(x-expected)));errors[m]=err
            matched &= bool(np.allclose(x,expected,atol=1e-10,rtol=0))
        qs=[int(agent.env.decode_action(a)[1]) for a in actual['actions']]
        counts={str(q):int(count) for q,count in Counter(qs).items()}
        expected_counts={str(k):v for k,v in r['evaluation']['q_counts'].items()}
        first_matches=bool(np.allclose(actual['actions'][0],r['evaluation']['chosen_action'],atol=1e-12,rtol=0))
        counts_matches=counts==expected_counts if slots==r['eval_slots'] else None
        row={'run':path.name,'scheme':r['scheme'],'budget':r['budget'],'seed':r['seed'],'slots':slots,
             'metrics_match':matched,'max_absolute_errors':errors,'first_action_match':first_matches,
             'q_counts':counts,'recorded_q_counts':expected_counts,'q_counts_match':counts_matches,
             'recorded_chosen_q':r['evaluation']['chosen_q'],'actual_modal_q':int(Counter(qs).most_common(1)[0][0]),
             'metric_array_sha256':{m:hashlib.sha256(np.asarray(actual['history'][m],dtype='<f8').tobytes()).hexdigest() for m in METRICS},
             'elapsed_seconds':time.perf_counter()-start,'source_run_sha256':sha(path)}
        assert matched and first_matches and counts_matches is not False,row
        write(OUT/'replay_runs'/path.name,row);rows.append(row)
        print(f'REPLAY {n}/{len(records)} {path.stem}: PASS {slots} slots ({row["elapsed_seconds"]:.2f}s)',flush=True)
    write(OUT/'full_policy_replay.json',{'protocol':'fresh CNN+DND load, epsilon=0, empty history, no learning','records':rows,'policy_count':len(rows),'slots_per_policy':slots,'compared_metric_values':len(rows)*slots*len(METRICS),'all_match':all(r['metrics_match'] for r in rows)})
    return rows

def enumerate_geometries():
    rows=[]
    for geometry,g in GEOMETRIES.items():
        env=build_env('joint_ris',geometry)
        gains={str(q):env.evaluate_action(env.encode_action([0,0,0,0],q))['gains'] for q in range(5)}
        for noise in (-3,0,3):
            env.sigma_B_sq=env.config.noise_variance*10**(noise/10)
            grid=[env.evaluate_action(i) for i in range(env.num_actions)]
            subsets={'baseline':[r for r in grid if r['ris_index']==0],
                     'fixed_ris':[r for r in grid if r['ris_index']==1],'joint_ris':grid}
            maxima={s:{m:max(v,key=lambda r:r[m]) for m in ['utility','secrecy_rate']} for s,v in subsets.items()}
            rows.append({'geometry':geometry,'positions':g,'noise_offset_db':noise,'noise_variance_numeric':env.sigma_B_sq,'maxima':maxima,'effective_gains':gains})
            print('GRID',geometry,noise,{s:round(v['utility']['utility'],5) for s,v in maxima.items()},flush=True)
    write(OUT/'geometry_grid_sensitivity.json',{'interpretation':'Finite discrete oracle maxima, not trained performance. Noise changes are numerical sensitivity, not physical calibration.','rows':rows})
    return rows

def transfer(records,slots):
    rows=[]
    selected=[(p,r) for p,r in records if r['budget']==10000]
    for geometry,g in GEOMETRIES.items():
        if geometry=='nominal':continue
        envs={s:build_env(s,geometry) for s in SCHEMES}
        for n,(path,r) in enumerate(selected,1):
            agent=load_agent(r,envs[r['scheme']]);result=agent.evaluate(slots)
            qs=[int(agent.env.decode_action(a)[1]) for a in result['actions']]
            row={'geometry':geometry,'positions':g,'scheme':r['scheme'],'seed':r['seed'],'training_budget':r['budget'],'evaluation_slots':slots,
                 'metric_means':{m:float(np.mean(result['history'][m])) for m in METRICS},
                 'metric_values':{m:[float(x) for x in result['history'][m]] for m in METRICS},
                 'q_counts':{str(q):int(count) for q,count in Counter(qs).items()},
                 'secrecy_outage_0p1':float(np.mean(np.asarray(result['history']['secrecy_rate'])<.1)),
                 'bob_outage_1e4':float(np.mean(np.asarray(result['history']['ber'])>1e-4)),
                 'source_run_sha256':sha(path)}
            write(OUT/'transfer_runs'/f'{geometry}_{path.name}',row);rows.append(row)
            print(f'TRANSFER {geometry} {n}/{len(selected)} {path.stem}',flush=True)
    write(OUT/'frozen_policy_geometry_transfer.json',{'interpretation':'Nominal-trained frozen learner, oracle codebook reconstructed at the supplied test geometry. No retraining; not unknown-CSI robustness or mobility validation.','rows':rows})
    return rows

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['all','replay','grid','transfer'],default='all')
    parser.add_argument('--replay-slots',type=int,default=1000);parser.add_argument('--transfer-slots',type=int,default=200)
    args=parser.parse_args();torch.set_num_threads(1);OUT.mkdir(parents=True,exist_ok=True)
    records=[(p,json.loads(p.read_text())) for p in sorted((DATA/'runs').glob('*.json'))]
    assert len(records)==90
    cfg=VLCConfig(model='paper',energy_model='l1',cnn_m0=11)
    default_cfg=asdict(cfg)
    def normal(v):
        if isinstance(v,np.ndarray):return v.tolist()
        if isinstance(v,dict):return {k:normal(x) for k,x in v.items()}
        if isinstance(v,(np.integer,np.floating)):return v.item()
        return v
    # Written before outcomes: reproducible, explicit supplemental choices.
    write(OUT/'validation_protocol.json',{'date':'2026-11-18','source_script_sha256':sha(Path(__file__)),
          'geometries_fixed_before_results':GEOMETRIES,'noise_offsets_db':[-3,0,3],
          'original_study':'90 nominal matched-v2 runs; supplemental analyses do not alter original records',
          'replay_slots':args.replay_slots,'transfer_slots':args.transfer_slots,
          'effective_current_config':normal(default_cfg),'ris_config':asdict(OpticalRISConfig()),
          'provenance_limit':'These current settings reconstruct recorded checks; they do not recover the full historical uncommitted working tree.'})
    if args.phase in ('all','replay'):replay(records,args.replay_slots)
    if args.phase in ('all','grid'):enumerate_geometries()
    if args.phase in ('all','transfer'):transfer(records,args.transfer_slots)

if __name__=='__main__':main()

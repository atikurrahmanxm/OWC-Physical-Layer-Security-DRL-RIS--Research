"""Bounded fresh-process checkpoint replay, without training or file mutation.

Default checks seed 42 / 10k for all three schemes against their first 32
recorded evaluation slots. This is not an all-policy/all-slot replay claim.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from vlc.config import VLCConfig
from vlc.ris_environment import RISEnvironment
from vlc.drl_fj import DRLFJAgent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--budget',type=int,default=10000)
    parser.add_argument('--slots',type=int,default=32)
    args=parser.parse_args()
    assert 1<=args.slots<=1000
    torch.set_num_threads(1)
    data=ROOT/'output_figures/ris/training_budget_study_matched_v2'
    report=[]
    for scheme,mode in [('baseline','off'),('fixed_ris','fixed'),('joint_ris','joint')]:
        r=json.loads((data/'runs'/f'run_{scheme}_s{args.seed}_b{args.budget}.json').read_text())
        cfg=VLCConfig(energy_model='l1',cnn_m0=11,seed=args.seed)
        env=RISEnvironment(cfg,control_mode=mode)
        agent=DRLFJAgent(env)
        ckpt=torch.load(data/'checkpoints'/r['checkpoints']['policy_cnn'],map_location='cpu',weights_only=True)
        assert ckpt['scheme']==scheme and ckpt['seed']==args.seed and ckpt['budget']==args.budget
        agent.cnn.load_state_dict(ckpt['cnn_state'],strict=True)
        agent.prev_cnn.load_state_dict(ckpt['cnn_state'],strict=True)
        memory=json.loads((data/'checkpoints'/r['checkpoints']['dnd_memory']).read_text())
        for a,v in memory.items():
            d=agent.dnd_dict[int(a)]
            d.keys=[np.asarray(k,dtype=np.float32) for k in v['keys']]
            d.values=[float(x) for x in v['values']]
            d.revision+=1
        result=agent.evaluate(args.slots)
        errors={}
        for m in ['utility','secrecy_rate','ber','energy']:
            actual=np.array(result['history'][m]);expected=np.array(r['evaluation'][m]['values'][:args.slots])
            errors[m]=float(np.max(np.abs(actual-expected)))
            assert np.allclose(actual,expected,atol=1e-10,rtol=0), (scheme,m,errors[m])
        report.append(dict(scheme=scheme,seed=args.seed,budget=args.budget,slots=args.slots,max_absolute_errors=errors))
        print(scheme,'PASS',args.slots,'slots',errors,flush=True)
    output=ROOT/'manuscript/research_draft_v2/verification'/f'replay_seed{args.seed}_budget{args.budget}_slots{args.slots}.json'
    output.write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__': main()

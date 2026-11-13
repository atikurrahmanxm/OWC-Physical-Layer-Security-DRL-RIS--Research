"""Paper-baseline reduction and actual joint-controller integration checks."""
from dataclasses import replace
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import Request,urlopen
import numpy as np
import torch
from vlc import VLCConfig,VLCEnvironment,DRLFJAgent
from vlc.ris import OpticalRISConfig
from vlc.ris_environment import RISEnvironment
from app_server import start_server

ROOT=Path(__file__).resolve().parents[1]


class RISEnvironmentTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.c=VLCConfig(energy_model='paper_signed')

    def test_off_reduces_to_paper_metrics_for_every_action(self):
        base=VLCEnvironment(self.c)
        ris=RISEnvironment(self.c,control_mode='off')
        np.testing.assert_array_equal(base.action_space,ris.action_space)
        np.testing.assert_array_equal(base.reset(),ris.reset())
        for index in range(base.num_actions):
            a,ua,ia=base.step(index)
            b,ub,ib=ris.step(index)
            np.testing.assert_array_equal(a,b)
            self.assertEqual(ua,ub)
            for metric in ['secrecy_rate','ber','energy','utility']:
                self.assertEqual(ia[metric],ib[metric])

    def test_zero_reflectivity_and_disabled_ris_reduce_to_direct_channels(self):
        base=VLCEnvironment(self.c)
        _,_,expected=base.step([-.5,1.,0.,1.])
        for settings in [OpticalRISConfig(reflectivity=0.),OpticalRISConfig(enabled=False)]:
            env=RISEnvironment(self.c,settings,control_mode='joint')
            for q in range(env.num_ris_configurations):
                row=env.evaluate_action(env.encode_action([-.5,1.,0.,1.],q))
                for key in ['secrecy_rate','ber','energy','utility']:
                    self.assertEqual(row[key],expected[key])
                self.assertEqual(row['gains'],row['direct_gains'])

    def test_joint_action_encoding_is_categorical_not_a_fifth_jammer(self):
        env=RISEnvironment(self.c)
        self.assertEqual(env.action_space.shape[1],5)
        self.assertEqual(env.num_actions,625*env.num_ris_configurations)
        for q in range(env.num_ris_configurations):
            action=env.encode_action([-.5,1.,0.,1.],q)
            w,index=env.decode_action(action)
            np.testing.assert_array_equal(w,[-.5,1.,0.,1.])
            self.assertEqual(index,q)
        with self.assertRaises(ValueError):env.decode_action([0,0,0,0,.12345])
        with self.assertRaises(ValueError):env.decode_action(True)
        with self.assertRaises(ValueError):env.decode_action(-1)
        with self.assertRaises(ValueError):env.encode_action([2,0,0,0],0)

    def test_dry_evaluation_preserves_current_state_and_actions_are_replayed(self):
        env=RISEnvironment(self.c)
        before=env.reset().copy()
        action=env.encode_action([-.5,1.,0.,1.],min(1,env.num_ris_configurations-1))
        row=env.evaluate_action(action)
        np.testing.assert_array_equal(before,env.get_state())
        state,reward,info=env.step(action)
        self.assertEqual(info['secrecy_rate'],row['secrecy_rate'])
        self.assertEqual(info['gains'],row['gains'])
        self.assertEqual(reward,row['utility'])
        self.assertEqual(state[2],row['gains']['h_AB'])

    def test_original_cnn_dnd_is_preserved_when_ris_is_off(self):
        c=replace(self.c,cnn_m0=11)
        base=DRLFJAgent(VLCEnvironment(c),c)
        env=RISEnvironment(c,control_mode='off')
        ris=DRLFJAgent(env,env.config)
        self.assertEqual(base.train(24),ris.train(24))
        self.assertEqual(base.action_history,ris.action_history)

    def test_joint_cnn_records_the_full_action_without_truncation(self):
        env=RISEnvironment(self.c)
        agent=DRLFJAgent(env,env.config)
        self.assertEqual(agent.action_width,5)
        self.assertGreaterEqual(env.config.cnn_m0**2,11*9+4)
        history=agent.train(24)
        for i,action in enumerate(agent.action_history):
            self.assertEqual(len(action),5)
            row=env.evaluate_action(action)
            for metric in history:
                self.assertEqual(history[metric][i],row[metric])

    def test_qos_is_an_explicit_soft_penalty_and_keeps_paper_utility(self):
        env=RISEnvironment(self.c,qos_ber_max=.01,qos_penalty=10.)
        w=np.zeros(4);w[0]=-env.h_AB/env.h_JB[0]
        row=env.evaluate_action(env.encode_action(w,0))
        self.assertAlmostEqual(row['ber'],.75)
        self.assertFalse(row['qos_feasible'])
        self.assertAlmostEqual(row['utility'],row['base_utility']-10*(row['ber']-.01))
        with self.assertRaises(ValueError):RISEnvironment(self.c,qos_penalty=10.)
        with self.assertRaises(ValueError):RISEnvironment(VLCConfig(model='physical'))

    def test_passive_eve_does_not_change_bob_direct_channel(self):
        a=RISEnvironment(self.c,eve_pos=np.array([3.2,3.4,.85]))
        b=RISEnvironment(self.c,eve_pos=np.array([1.,1.,.85]))
        w=[-.5,1.,0.,1.]
        for q in [0,1]:
            first=a.evaluate_action(a.encode_action(w,q))
            second=b.evaluate_action(b.encode_action(w,q))
            self.assertEqual(first['gains']['h_AB'],second['gains']['h_AB'])
            self.assertEqual(first['gains']['h_JB'],second['gains']['h_JB'])

    def test_colocated_receivers_do_not_gain_secrecy_from_ris(self):
        env=RISEnvironment(self.c,eve_pos=self.c.bob_pos.copy())
        for q in range(env.num_ris_configurations):
            row=env.evaluate_action(env.encode_action([-.5,1.,0.,1.],q))
            self.assertEqual(row['gains']['h_AB'],row['gains']['h_AE'])
            self.assertEqual(row['gains']['h_JB'],row['gains']['h_JE'])
            self.assertEqual(row['secrecy_rate'],0.)

    def test_ris_http_metrics_and_training_use_the_actual_backend(self):
        server,url=start_server()
        def post(endpoint,payload):
            request=Request(url+endpoint,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
            with urlopen(request,timeout=30) as response:return json.load(response)
        try:
            row=post('api/ris/metrics',{'ris_index':0,'beamformer':[-.5,1,0,1]})
            self.assertEqual(row['selected'],row['baseline'])
            self.assertFalse(row['paper_reproduction_verified'])
            job=post('api/ris/experiment',{'slots':16,'seeds':[42],'sigma':1e-12})['job_id']
            for _ in range(400):
                with urlopen(url+'api/jobs/'+job,timeout=30) as response:status=json.load(response)
                if status['status'] in {'complete','error'}:break
                time.sleep(.05)
            self.assertEqual(status['status'],'complete',status)
            result=status['result']
            self.assertTrue(result['complete'])
            self.assertEqual(len(result['runs']),3)
            for run in result['runs']:
                self.assertEqual(run['sigma_B_sq'],1e-12)
                self.assertEqual(len(run['actions']),16)
                self.assertTrue(all(error==0 for error in run['action_replay_maximum_errors'].values()))
        finally:
            server.shutdown();server.server_close()

    def test_launcher_runs_a_real_preview_and_reports_single_seed_uncertainty(self):
        with tempfile.TemporaryDirectory() as temp:
            p=subprocess.run([sys.executable,'-B',str(ROOT/'run.py'),'--mode','ris','--slots','16','--save_dir',temp],
                             cwd=ROOT,capture_output=True,text=True,timeout=120)
            self.assertEqual(p.returncode,0,p.stderr)
            record=json.loads((Path(temp)/'ris_study_data.json').read_text())
            self.assertTrue(record['complete'])
            self.assertEqual(record['settings']['energy_models'],['paper_signed'])
            self.assertEqual(len(record['runs']),3)
            self.assertTrue(all(a['all_slots']['secrecy_rate']['ci95'] is None for a in record['aggregates']))


if __name__=='__main__':unittest.main()

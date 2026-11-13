"""Counterexamples from the paper audit, plus real-agent/service integration."""
import itertools
import json
import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import numpy as np
from scipy.special import erfc
import torch
from vlc import VLCConfig, VLCChannel, VLCEnvironment, RLFJAgent, DRLFJAgent
from vlc.secrecy import compute_bob_ber, compute_energy_consumption, compute_secrecy_rate, compute_system_utility
from vlc.bounds import compute_theoretical_bounds, compute_zero_forcing_beamformer, corollary_diagnostics
from vlc.drl_fj import DNDMemory
from vlc.experiments import diagnose_operating_point
from app_server import start_server

ROOT = Path(__file__).resolve().parents[1]


class PaperRegressionTests(unittest.TestCase):
    def setUp(self):
        self.c = VLCConfig()
        self.g = VLCChannel(self.c).get_all_channel_gains()
        torch.set_num_threads(1)

    def test_ber_keeps_negative_channel_squared(self):
        ab, _, jb, _ = self.g
        w = -np.ones(4)
        expected = .75 * erfc(np.sqrt(2*(ab+jb@w)**2/(5e-10)))
        self.assertAlmostEqual(compute_bob_ber(ab,jb,w,self.c,1e-10), expected, places=14)

    def test_signed_equation_and_l1_are_distinct(self):
        self.assertEqual(compute_energy_consumption(-np.ones(4),self.c), 4.)
        self.assertEqual(compute_energy_consumption(-np.ones(4),replace(self.c,energy_model="paper_signed")), -4.)

    def test_default_reward_does_not_pay_for_negative_weights(self):
        env=VLCEnvironment(self.c)
        _,reward,info=env.step(-np.ones(4))
        self.assertEqual(info['secrecy_rate'],0.)
        self.assertEqual(info['energy'],4.)
        self.assertLess(reward,0.)
        literal=VLCEnvironment(replace(self.c,energy_model='paper_signed'))
        self.assertGreater(literal.step(-np.ones(4))[1],0.)

    def test_snr_sweep_has_feasible_positive_rates_without_energy_credits(self):
        legacy=replace(self.c,snr_definition='electrical')
        for db in range(4,22,2):
            sigma=self.c.noise_variance_from_snr(self.g[0],db)
            d=diagnose_operating_point(VLCEnvironment(self.c,sigma_B_sq=sigma))
            self.assertGreater(d['maximum_discrete_secrecy_rate'],0.)
            self.assertLessEqual(d['maximum_discrete_secrecy_rate'],d['bob_capacity_ceiling'])
            old_sigma=legacy.noise_variance_from_snr(self.g[0],db)
            old=diagnose_operating_point(VLCEnvironment(legacy,sigma_B_sq=old_sigma))
            self.assertEqual(old['maximum_discrete_secrecy_rate'],0.)

    def test_rate_ceiling_and_low_snr_utility_tradeoff_are_disclosed(self):
        table=diagnose_operating_point(VLCEnvironment(self.c))
        self.assertAlmostEqual(table['bob_capacity_ceiling'],1.9086544954886058)
        self.assertLess(table['bob_capacity_ceiling'],5.68)
        sigma=self.c.noise_variance_from_snr(self.g[0],4)
        low=diagnose_operating_point(VLCEnvironment(self.c,sigma_B_sq=sigma))
        self.assertGreater(low['maximum_discrete_secrecy_rate'],0.)
        self.assertEqual(low['secrecy_at_maximum_discrete_utility'],0.)
        self.assertTrue(np.array_equal(low['maximum_utility_action'],np.zeros(4)))

    def test_no_eve_information_link_has_no_leakage(self):
        ab, _, jb, je = self.g
        rate = compute_secrecy_rate(ab,0.,jb,je,np.zeros(4),self.c)
        expected = .5*np.log2(1+2*ab**2*.1**2/(np.pi*np.e*self.c.noise_power_watts))
        self.assertAlmostEqual(rate,expected,places=13)

    def test_zf_matches_independently_enumerated_box_vertices(self):
        rng = np.random.default_rng(7)
        for _ in range(12):
            jb,je = rng.uniform(.01,1,(2,4))*1e-7
            vertices = []
            for free in range(4):
                other = [j for j in range(4) if j != free]
                for signs in itertools.product([-1.,1.],repeat=3):
                    w = np.zeros(4); w[other] = signs
                    w[free] = -jb[other]@w[other]/jb[free]
                    if abs(w[free]) <= 1+1e-12:
                        vertices.append(abs(je@w))
            w = compute_zero_forcing_beamformer(jb,je)
            self.assertAlmostEqual(abs(je@w)/max(vertices),1.,places=10)
            self.assertLess(abs(jb@w),1e-18)

    def test_zf_handles_collinear_and_zero_channels(self):
        self.assertTrue(np.array_equal(compute_zero_forcing_beamformer(np.ones(4),np.ones(4)),np.zeros(4)))
        self.assertTrue(np.array_equal(compute_zero_forcing_beamformer(np.zeros(4),np.ones(4)),np.ones(4)))

    def test_global_bounds_cover_every_discrete_action_both_models(self):
        ab,ae,jb,je = self.g
        for model in ["paper_signed","l1"]:
            c = replace(self.c,energy_model=model)
            high,low,upper,_ = compute_theoretical_bounds(*self.g,c)
            for w in VLCEnvironment(c).action_space:
                cs = compute_secrecy_rate(*self.g,w,c)
                pe = compute_bob_ber(ab,jb,w,c)
                u = compute_system_utility(cs,pe,compute_energy_consumption(w,c),c)
                self.assertLessEqual(cs,high+1e-12)
                self.assertGreaterEqual(pe,low-1e-12)
                self.assertLessEqual(u,upper+1e-12)

    def test_conditional_corollary_is_not_certified(self):
        d = corollary_diagnostics(*self.g,self.c)
        self.assertFalse(d['applicable'])
        self.assertFalse(d['condition20_at_target'])
        self.assertGreater(d['target_ratio'],1.)

    def test_dnd_replaces_updated_q_without_second_averaging(self):
        d = DNDMemory(); k=np.zeros(180)
        d.append_or_update(k,2.); d.append_or_update(k,4.)
        self.assertEqual(len(d),1)
        self.assertEqual(d.query(k),4.)

    def test_batched_dnd_matches_each_action_dictionary(self):
        agent = DRLFJAgent(VLCEnvironment(self.c),self.c)
        rng=np.random.default_rng(4)
        for action in [0,7,19]:
            for _ in range(4):
                agent.dnd_dict[action].append_or_update(rng.normal(size=180),rng.normal())
        key=rng.normal(size=180)
        actual=agent.estimate_all_q_values(key)
        for action in range(agent.num_actions):
            self.assertAlmostEqual(actual[action],agent.dnd_dict[action].query(key),places=12)
        agent.dnd_dict[7].append_or_update(key,9.)
        self.assertAlmostEqual(agent.estimate_all_q_values(key)[7],agent.dnd_dict[7].query(key),places=12)

    def test_named_snr_conventions(self):
        ab=self.g[0];gamma=10**1.2
        electrical=replace(self.c,snr_definition='electrical')
        self.assertAlmostEqual(electrical.noise_variance_from_snr(ab,12),ab**2/gamma,places=23)
        eq4=self.c
        sigma=eq4.noise_variance_from_snr(ab,12)
        bob_term=.5*np.log2(1+2*ab**2*.1**2/(np.pi*np.e*sigma))
        self.assertAlmostEqual(bob_term,.5*np.log2(1+gamma),places=13)

    def test_both_agents_are_deterministic_and_record_actual_actions(self):
        for cls in [RLFJAgent,DRLFJAgent]:
            a=cls(VLCEnvironment(self.c),self.c);b=cls(VLCEnvironment(self.c),self.c)
            ha,hb=a.train(24),b.train(24)
            self.assertEqual(ha,hb)
            self.assertEqual(a.action_history,b.action_history)
            self.assertEqual(len(a.action_history),24)
            for metric in ha.values(): self.assertTrue(np.isfinite(metric).all())
            if cls is DRLFJAgent: self.assertTrue(all(p.grad is None or torch.isfinite(p.grad).all() for p in a.cnn.parameters()))

    def test_action_and_noise_validation(self):
        env=VLCEnvironment(self.c)
        with self.assertRaises(ValueError): env.step([2,0,0,0])
        with self.assertRaises(ValueError): compute_bob_ber(self.g[0],self.g[2],np.zeros(4),self.c,0.)
        with self.assertRaises(ValueError): VLCConfig(cnn_m0=8)

    def test_cli_training_honors_snr_and_exports_raw_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'run.json'
            r=subprocess.run([sys.executable,'-B',str(ROOT/'run.py'),'--mode','train','--algo','rl','--slots','3','--snr','12','--snr-definition','eq4','--results',str(target)],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            data=json.loads(target.read_text())
            c=replace(self.c,snr_definition='eq4')
            self.assertAlmostEqual(data['metadata']['sigma_B_sq'],c.noise_variance_from_snr(self.g[0],12),places=23)
            self.assertEqual(len(data['actions']),3)

    def test_http_service_runs_actual_agents_and_rejects_cross_origin(self):
        server,url=start_server()
        try:
            payload=dict(slots=16,seed=42)
            req=Request(url+'api/experiment',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
            with urlopen(req,timeout=10) as response: job=json.load(response)['job_id']
            for _ in range(100):
                with urlopen(url+'api/jobs/'+job,timeout=10) as response: data=json.load(response)
                if data['status'] in ['complete','error']: break
                time.sleep(.05)
            self.assertEqual(data['status'],'complete',data)
            result=data['result']
            self.assertEqual(len(result['histories']['drl']['ber']),16)
            self.assertEqual(len(result['actions']['drl']),16)
            self.assertFalse(result['metadata']['reproduction_verified'])
            expected=DRLFJAgent(VLCEnvironment(self.c),self.c).train(16)
            self.assertEqual(result['histories']['drl'],expected)
            bad=Request(url+'api/experiment',data=b'{}',headers={'Origin':'https://example.com'})
            with self.assertRaises(HTTPError) as error: urlopen(bad,timeout=10)
            self.assertEqual(error.exception.code,403)
        finally:
            server.shutdown();server.server_close()

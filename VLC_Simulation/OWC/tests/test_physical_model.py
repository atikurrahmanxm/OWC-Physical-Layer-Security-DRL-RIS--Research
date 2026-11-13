"""Independent physical checks before training the alternative 4-PAM model."""
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import Request,urlopen
import numpy as np
from scipy.integrate import quad
from scipy.special import erfc
from scipy.stats import norm
from vlc import VLCConfig,VLCChannel,VLCEnvironment,DRLFJAgent,RLFJAgent
from vlc.physical import pam_mutual_information,pam_bit_error_rate,pam_bit_map_lower_bound
from vlc.secrecy import compute_secrecy_rate,compute_bob_ber,compute_energy_consumption
from vlc.bounds import compute_theoretical_bounds
from vlc.experiments import metadata
from app_server import start_server

ROOT=Path(__file__).resolve().parents[1]


class PhysicalModelTests(unittest.TestCase):
    def setUp(self):
        self.c=VLCConfig(model='physical')
        self.g=VLCChannel(self.c).get_all_channel_gains()

    def test_noise_power_current_units_and_modulated_snr(self):
        c=replace(self.c,receiver_resistance_ohm=50.)
        self.assertAlmostEqual(c.noise_variance/c.noise_power_watts,1/50.)
        variance=c.noise_variance_from_snr(self.g[0],12.)
        mean_square=(5/9)*(self.g[0]*c.modulation_index*c.id_bias)**2
        self.assertAlmostEqual(mean_square/variance,10**1.2)
        self.assertEqual(metadata(c)['model_interpretation']['noise_variance_unit'],'A^2')

    def test_ber_matches_independent_gray_pam_gaussian_formula(self):
        # Exact all-neighbor errors, including nonadjacent Gray transitions.
        for a in [.1,1.,3.,10.]:
            q=lambda x:.5*erfc(x/np.sqrt(2))
            expected=.75*q(a/3)+.5*q(a)-.25*q(5*a/3)
            self.assertAlmostEqual(pam_bit_error_rate(a,0.,1.),expected,places=13)
        self.assertEqual(pam_bit_error_rate(0.,1.,1.),.5)

    def test_bit_map_lower_bound_matches_independent_likelihood_decisions(self):
        rng=np.random.default_rng(102)
        a=1.1
        bits=np.array([[0,0],[0,1],[1,1],[1,0]])
        means=a*np.array([-1.,-1/3,1/3,1.])
        sent=rng.integers(4,size=300000)
        y=means[sent]+rng.normal(size=len(sent))
        likelihood=np.exp(-.5*(y[:,None]-means)**2)
        decisions=np.column_stack([likelihood[:,bits[:,b]==1].sum(axis=1)>likelihood[:,bits[:,b]==0].sum(axis=1)
                                   for b in range(2)])
        exact=pam_bit_map_lower_bound(a,1.)
        self.assertAlmostEqual(np.mean(decisions!=bits[sent]),exact,delta=.0015)
        self.assertLessEqual(exact,pam_bit_error_rate(a,0.,1.))

    def test_uniform_jamming_ber_matches_independent_waveform_monte_carlo(self):
        rng=np.random.default_rng(7701)
        bits=np.array([[0,0],[0,1],[1,1],[1,0]])
        levels=np.array([-1.,-1/3,1/3,1.])
        symbols=rng.integers(4,size=400000)
        a,j,variance=2.1,1.7,.35
        y=a*levels[symbols]+rng.uniform(-j,j,len(symbols))+rng.normal(0,np.sqrt(variance),len(symbols))
        decisions=np.digitize(y,[-2*a/3,0.,2*a/3])
        observed=np.mean(bits[symbols]!=bits[decisions])
        self.assertAlmostEqual(pam_bit_error_rate(a,j,variance),observed,delta=.0015)

    def test_mutual_information_matches_independent_awgn_integration(self):
        a=2.3
        levels=a*np.array([-1.,-1/3,1/3,1.])
        def integrand(y):
            p=norm.pdf(y-levels)
            mean=np.mean(p)
            return np.sum(np.where(p>0,p*np.log2(np.maximum(p,1e-300)/max(mean,1e-300)),0.))/4
        expected=quad(integrand,-15.,15.,epsabs=1e-10)[0]
        self.assertAlmostEqual(pam_mutual_information(a,0.,1.),expected,places=9)

    def test_quadrature_convergence_and_common_current_scaling(self):
        for a,j in [(0.1,0.),(1.,2.),(10.,30.),(100.,1000.)]:
            value=pam_mutual_information(a,j,1.)
            self.assertAlmostEqual(value,pam_mutual_information(a,j,1.,48),places=8)
            self.assertAlmostEqual(value,pam_mutual_information(a*1e-6,j*1e-6,1e-12),places=10)
            self.assertAlmostEqual(pam_bit_error_rate(a,j,1.),pam_bit_error_rate(a*1e-6,j*1e-6,1e-12),places=12)

    def test_same_channel_has_no_secrecy_and_finite_alphabet_ceiling(self):
        ab,ae,jb,je=self.g
        for w in [np.zeros(4),np.ones(4),np.array([-.5,1,0,1])]:
            self.assertEqual(compute_secrecy_rate(ab,ab,jb,jb,w,self.c),0.)
            rate=compute_secrecy_rate(*self.g,w,self.c)
            self.assertGreaterEqual(rate,0.)
            self.assertLessEqual(rate,2*self.c.symbol_rate_per_hz)
        self.assertGreater(pam_mutual_information(50.,0.,1.),1.9999)
        self.assertLess(pam_mutual_information(.001,0.,1.),1e-6)

    def test_optical_conversion_does_not_change_received_signal(self):
        other=replace(self.c,eta=2.,id_bias=None)
        gains=VLCChannel(other).get_all_channel_gains()
        w=np.array([-.5,1,0,1])
        self.assertAlmostEqual(compute_secrecy_rate(*gains,w,other),compute_secrecy_rate(*self.g,w,self.c),places=12)
        self.assertAlmostEqual(compute_bob_ber(gains[0],gains[2],w,other),compute_bob_ber(self.g[0],self.g[2],w,self.c),places=12)

    def test_optical_power_and_noise_have_expected_clean_receiver_effects(self):
        ab,_,jb,je=self.g
        no_jamming=np.zeros(4)
        high=replace(self.c,led_avg_power=2.,id_bias=None)
        baseline_ber=compute_bob_ber(ab,jb,no_jamming,self.c)
        self.assertLess(compute_bob_ber(ab,jb,no_jamming,high),baseline_ber)
        self.assertGreater(compute_bob_ber(ab,jb,no_jamming,self.c,2*self.c.noise_variance),baseline_ber)
        # With Eve's information channel absent the reported secrecy equals Bob MI.
        baseline_rate=compute_secrecy_rate(ab,0.,jb,je,no_jamming,self.c)
        self.assertGreater(compute_secrecy_rate(ab,0.,jb,je,no_jamming,high),baseline_rate)
        self.assertLess(compute_secrecy_rate(ab,0.,jb,je,no_jamming,self.c,2*self.c.noise_variance),baseline_rate)
        self.assertAlmostEqual(compute_energy_consumption(np.ones(4),high),4*self.c.max_jamming_energy)

    def test_jamming_damages_reception_and_energy_is_joules(self):
        ab,_,jb,_=self.g
        baseline=compute_bob_ber(ab,jb,np.zeros(4),self.c)
        for sign in [-1.,1.]:
            self.assertGreater(compute_bob_ber(ab,jb,sign*np.ones(4),self.c),baseline)
        c=replace(self.c,jammer_resistance_ohm=3.,slot_duration_s=.2)
        w=np.array([-.5,1,0,1])
        expected=.1**2/3*np.dot(w,w)*3*.2
        self.assertAlmostEqual(compute_energy_consumption(w,c),expected,places=14)
        self.assertEqual(compute_energy_consumption(w,c),compute_energy_consumption(-w,c))
        self.assertAlmostEqual(compute_energy_consumption(.5*w,c),expected/4)

    def test_bounds_cover_whole_action_grid(self):
        upper,lower,utility,_=compute_theoretical_bounds(*self.g,self.c)
        env=VLCEnvironment(self.c)
        for i in range(env.num_actions):
            _,reward,info=env.step(i)
            self.assertLessEqual(info['secrecy_rate'],upper+1e-9)
            self.assertGreaterEqual(info['ber'],lower-1e-9)
            self.assertLessEqual(reward,utility+1e-9)

    def test_model_rejects_mixed_conventions(self):
        for values in [dict(energy_model='paper_signed'),dict(snr_definition='eq4'),dict(id_bias=2.),dict(receiver_resistance_ohm=0.),dict(eve_noise_ratio=-1.)]:
            with self.assertRaises(ValueError): VLCConfig(model='physical',**values)
        with self.assertRaises(ValueError): VLCConfig(model='paper',receiver_resistance_ohm=50.)

    def test_http_physical_run_matches_direct_backend(self):
        import torch
        torch.set_num_threads(1)
        server,url=start_server()
        try:
            payload={'model':'physical','slots':16,'receiver_resistance_ohm':50.}
            request=Request(url+'api/experiment',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
            with urlopen(request,timeout=10) as response: job=json.load(response)['job_id']
            for _ in range(200):
                with urlopen(url+'api/jobs/'+job,timeout=10) as response: data=json.load(response)
                if data['status'] in ['complete','error']:break
                time.sleep(.05)
            self.assertEqual(data['status'],'complete',data)
            result=data['result']
            self.assertEqual(result['metadata']['config']['model'],'physical')
            c=replace(self.c,receiver_resistance_ohm=50.)
            expected=DRLFJAgent(VLCEnvironment(c),c).train(16)
            self.assertEqual(result['histories']['drl'],expected)
            self.assertTrue(all(e>=0 for e in result['histories']['drl']['energy']))
        finally:
            server.shutdown();server.server_close()

    def test_cli_launcher_exports_physical_units_and_resistance(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'physical.json'
            p=subprocess.run([sys.executable,'-B',str(ROOT/'run.py'),'--mode','train','--model','physical',
                              '--algo','rl','--slots','5','--receiver-resistance','50','--results',str(target)],
                              cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            record=json.loads(target.read_text())
            self.assertEqual(record['metadata']['config']['model'],'physical')
            self.assertAlmostEqual(record['metadata']['sigma_B_sq']/self.c.noise_power_watts,1/50.)
            self.assertEqual(len(record['actions']),5)
            self.assertEqual(record['metadata']['model_interpretation']['noise_variance_unit'],'A^2')


if __name__=='__main__':unittest.main()

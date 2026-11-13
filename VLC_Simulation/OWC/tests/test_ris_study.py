"""Statistical/reporting counterexamples for matched RIS experiments."""
import unittest
import numpy as np
from scipy.stats import t as student_t
from vlc.config import VLCConfig
from vlc.ris_experiments import estimate_uncertainty,summarize_history,aggregate_runs,run_ris_study


class RISStudyTests(unittest.TestCase):
    def test_one_seed_does_not_claim_a_zero_width_confidence_interval(self):
        estimate=estimate_uncertainty([1.3])
        self.assertEqual(estimate['mean'],1.3)
        self.assertIsNone(estimate['ci95'])
        self.assertIsNone(estimate['sample_std'])

    def test_small_sample_ci_uses_student_t_and_independent_seed_count(self):
        values=np.array([1.,2.,3.])
        estimate=estimate_uncertainty(values)
        expected_half=student_t.ppf(.975,2)/np.sqrt(3)
        np.testing.assert_allclose(estimate['ci95'],[2-expected_half,2+expected_half])
        self.assertEqual(estimate['n'],3)

    def test_training_averages_include_exploration_and_outages_are_explicit(self):
        history={'secrecy_rate':[0.,0.,2.,2.], 'ber':[.5,.5,0.,0.],
                 'energy':[4.,4.,1.,1.],'utility':[-2.,-2.,1.,1.]}
        summary=summarize_history(history,final_window=2,qos_ber_max=.01,secrecy_target=.1)
        self.assertEqual(summary['all_slots']['secrecy_rate'],1.)
        self.assertEqual(summary['final_window']['secrecy_rate'],2.)
        self.assertEqual(summary['bob_qos_outage_fraction'],.5)
        self.assertEqual(summary['secrecy_outage_fraction'],.5)
        with self.assertRaises(ValueError):summarize_history(history,final_window=0)

    def test_paired_changes_preserve_seed_pairs_and_energy_scenario_groups(self):
        runs=[]
        for energy in ['paper_signed','l1']:
            for seed in [42,43]:
                for scheme,rate in [('baseline',seed-40.),('joint_ris',seed-39.)]:
                    history={key:[rate] for key in ['secrecy_rate','ber','energy','utility']}
                    runs.append({'scenario':{'name':'nominal'},'energy_model':energy,'seed':seed,'scheme':scheme,
                                 'summary':summarize_history(history)})
        aggregates,paired=aggregate_runs(runs)
        self.assertEqual(len(aggregates),4)
        self.assertEqual(len(paired),2)
        for item in paired:
            self.assertEqual(item['seeds'],[42,43])
            self.assertEqual(item['all_slots']['secrecy_rate']['mean'],1.)
            self.assertEqual(item['all_slots']['secrecy_rate']['n'],2)

    def test_mixed_models_duplicate_seeds_and_invalid_qos_fail_before_training(self):
        with self.assertRaises(ValueError):run_ris_study(config=VLCConfig(model='physical'),slots=1)
        with self.assertRaises(ValueError):run_ris_study(seeds=[42,42],slots=1)
        with self.assertRaises(ValueError):run_ris_study(slots=1,qos_penalty=1.,qos_ber_max=None)
        with self.assertRaises(ValueError):run_ris_study(slots=1,scenarios=[{'name':'../outside','bob':[1,1,.85],'eve':[3,3,.85]}])


if __name__=='__main__':unittest.main()

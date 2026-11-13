"""Counterexamples to false numerical-reproduction success."""
import unittest
import numpy as np
from vlc import VLCConfig, VLCChannel, VLCEnvironment
from vlc.secrecy import compute_bob_ber
from paper_audit.published_targets import (
    extract_published_curves, compare_value, assess_published_targets, noise_compatibility)


class PublishedTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = extract_published_curves()

    def test_vector_reference_has_five_measured_snr_vertices(self):
        curve = self.reference['figure7']['secrecy_rate']['curves']['drl']
        self.assertEqual(curve['x'], [4., 8., 12., 16., 20.])
        self.assertAlmostEqual(curve['y'][0], 1.746, places=4)
        self.assertAlmostEqual(curve['y'][-1], 4.375, places=4)
        self.assertAlmostEqual(curve['y'][-1]/curve['y'][0]-1, 1.51, delta=.01)
        self.assertFalse(self.reference['provenance']['author_raw_data'])

    def test_vector_axes_decode_linear_and_logarithmic_metrics(self):
        curves = self.reference['figure6']
        rate = curves['secrecy_rate']['curves']['drl']
        utility = curves['utility']['curves']['drl']
        self.assertEqual(len(rate['x']), 1999)
        self.assertAlmostEqual(rate['x'][0], 1., delta=.01)
        self.assertAlmostEqual(rate['x'][-1], 1999., delta=.01)
        self.assertAlmostEqual(rate['y'][0], 3.64, delta=.01)
        self.assertAlmostEqual(utility['y'][0], 2.68, delta=.01)
        ber = self.reference['figure7']['ber']['curves']['drl']
        self.assertAlmostEqual(ber['y'][0], .0023, delta=1e-7)
        self.assertAlmostEqual(ber['y'][-1], .0001, delta=1e-10)

    def test_ber_target_checks_reject_implausibly_low_and_high_values(self):
        self.assertFalse(compare_value(4.42e-25, .0002, factor=1.25)['passed'])
        self.assertFalse(compare_value(.002, .0002, factor=1.25)['passed'])
        self.assertTrue(compare_value(.00021, .0002, factor=1.25)['passed'])

    def test_noise_inversions_round_trip_literal_equations(self):
        c = VLCConfig()
        gains = VLCChannel(c).get_all_channel_gains()
        result = noise_compatibility(c, gains, VLCEnvironment(c).action_space)
        self.assertFalse(result['rate_target_feasible_at_nominal_noise'])
        self.assertAlmostEqual(result['zero_forcing_ber_recomputed'], .0002, places=12)
        best = result['closest_single_action_noise_requirements']
        self.assertAlmostEqual(best['rate_recomputed'], 5.68, places=11)
        self.assertAlmostEqual(compute_bob_ber(gains[0],gains[2],np.array(best['action']),c,
                                             best['noise_for_ber_target']), .0002, places=12)
        self.assertGreater(best['noise_gap_db'], 50.)

    def fixture_records(self):
        # Synthetic unit fixtures only: never exported as simulation output.
        run = {'histories': {'drl': {'secrecy_rate': [5.68]*2000, 'ber': [.0002]*2000}}}
        sweep = {'points': []}
        for i, db in enumerate([4.,8.,12.,16.,20.]):
            histories = {agent: {metric: [item['curves'][agent]['y'][i]]
                                 for metric,item in self.reference['figure7'].items()}
                         for agent in ['rl','drl']}
            sweep['points'].append({'snr_db': db, 'histories': histories})
        return run, sweep

    def test_numerical_agreement_does_not_certify_unknown_author_model(self):
        run, sweep = self.fixture_records()
        result = assess_published_targets(run,sweep,self.reference)
        self.assertTrue(result['numerical_targets_passed'])
        self.assertEqual(result['passed_comparisons'],32)
        self.assertFalse(result['reproduction_verified'])

    def test_zero_rates_fail_even_if_equations_and_exports_are_valid(self):
        run, sweep = self.fixture_records()
        run['histories']['drl']['secrecy_rate'] = [0.]*2000
        result = assess_published_targets(run,sweep,self.reference)
        self.assertFalse(result['numerical_targets_passed'])
        self.assertEqual(result['status'],'fail')
        self.assertFalse(result['checkpoints']['DRL_rate_slot_1400']['passed'])


if __name__ == '__main__':
    unittest.main()

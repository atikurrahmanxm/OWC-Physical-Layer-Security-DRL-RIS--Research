"""Unit tests for the supervisor demonstration server routes and launcher."""
import json
import unittest
import urllib.request
from urllib.error import HTTPError
from app_server import start_server


class SupervisorDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = start_server()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_demo_route_returns_200_html(self):
        req = urllib.request.Request(self.url + "demo")
        with urllib.request.urlopen(req, timeout=5) as res:
            self.assertEqual(res.status, 200)
            self.assertIn("text/html", res.headers.get("Content-Type", ""))
            content = res.read().decode("utf-8")
            self.assertIn("Optical RIS + Friendly Jamming Secure VLC System", content)
            self.assertIn("Optical Geometry", content)

    def test_compact_results_json_route(self):
        req = urllib.request.Request(self.url + "compact_results.json")
        with urllib.request.urlopen(req, timeout=5) as res:
            self.assertEqual(res.status, 200)
            self.assertIn("application/json", res.headers.get("Content-Type", ""))
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("aggregates", data)
            self.assertIn("paired_seed_comparisons", data)

    def test_figures_route_returns_png(self):
        req = urllib.request.Request(self.url + "figures/fig1_training_curves.png")
        with urllib.request.urlopen(req, timeout=5) as res:
            self.assertEqual(res.status, 200)
            self.assertEqual(res.headers.get("Content-Type"), "image/png")
            data = res.read()
            self.assertGreater(len(data), 1000)

    def test_live_metrics_post(self):
        payload = {
            "bob": [1.8, 1.6, 0.85],
            "eve": [3.2, 3.4, 0.85],
            "beamformer": [-0.5, 1.0, 0.0, 1.0],
            "ris_index": 1,
            "energy_model": "l1"
        }
        req = urllib.request.Request(
            self.url + "api/ris/metrics",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertAlmostEqual(data["selected"]["reflected_gains"]["h_AB"], 6.3554634e-06, places=11)
            self.assertEqual(data["baseline"]["reflected_gains"]["h_AB"], 0.0)
            self.assertGreater(data["selected"]["secrecy_rate"], 1.8)

    def test_cross_origin_blocked(self):
        bad_req = urllib.request.Request(
            self.url + "demo",
            headers={"Origin": "https://malicious-external-site.com"}
        )
        with self.assertRaises(HTTPError) as ctx:
            urllib.request.urlopen(bad_req, timeout=5)
        self.assertEqual(ctx.exception.code, 403)


if __name__ == "__main__":
    unittest.main()


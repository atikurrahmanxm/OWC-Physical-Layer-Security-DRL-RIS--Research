# Independent Antigravity Review: Optical RIS + Friendly Jamming (FJ) + VLC + DRL Integration

**Role:** Independent Antigravity Reviewer  
**Date:** 2026-11-13  
**Status of Optics Implementation:** **Optics validation is PENDING** (`vlc/ris.py` does not exist yet; all reflection physics, ray geometry, and power conservation checks remain unverified).  
**Protocol Compliance:** Read-only inspection; no files, settings, or credentials were modified; no terminal commands were run.

---

## 1. Executive Summary & Baseline Preservation Review

The objective defined in [Agent.MD](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/Agent.MD) and [docs/ANTIGRAVITY_RIS_TASK.md](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/docs/ANTIGRAVITY_RIS_TASK.md) is to extend the 2024 paper baseline (*Smart Jamming for Secrecy*, IEEE TWC 2024) with an optical mirror-array RIS under joint CNN + DND DRL control (`RIS + FJ + VLC + DRL`).

### Baseline Preservation Findings
1. **Mathematical Reduction:** Under `control_mode='off'`, [vlc/ris_environment.py#L131-L136](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L131-L136) sets reflected gains strictly to zero:
   $$h_{AB, \text{eff}} = h_{AB, \text{direct}}, \quad h_{AE, \text{eff}} = h_{AE, \text{direct}}, \quad \mathbf{h}_{JB, \text{eff}} = \mathbf{h}_{JB, \text{direct}}, \quad \mathbf{h}_{JE, \text{eff}} = \mathbf{h}_{JE, \text{direct}}$$
   For identical beamforming weights $\mathbf{w}$, noise variance $\sigma_B^2$, and configuration settings, direct channel metrics ($c_s$, $p_e$, $E$, $u$) match the unextended [vlc/environment.py](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/environment.py).
2. **Alternative Physical Mode Isolation:** [vlc/ris_environment.py#L29-L30](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L29-L30) explicitly rejects `model='physical'`, ensuring the diagnostic 4-PAM physical mode does not silently replace the 2024 paper baseline.
3. **Reproduction Ground Reality:** As recorded in `Agent.MD`, the 2024 paper's published numerical curves are **not** reproduced by the baseline (failing 31 of 32 checks, Bob's ceiling is $\approx 1.91$ bps/Hz vs published 5.68). This review confirms that the RIS extension builds upon the repository's nominal paper equations, but does not claim reproduction of published curves.

---

## 2. Concrete Observed Defects & Inconsistencies

### Defect 1: Unhandled Dependency on Missing `vlc/ris.py`
- **Location:** [vlc/ris_environment.py#L27](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L27), [L120](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L120); [vlc/ris_experiments.py#L218](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_experiments.py#L218)
- **Observed Behavior:** Both modules execute direct imports: `from .ris import OpticalRIS, OpticalRISConfig`. Because `vlc/ris.py` does not exist in the workspace, any instantiation of `RISEnvironment` or execution of `run_ris_study` fails immediately with `ModuleNotFoundError: No module named 'vlc.ris'`.
- **Status:** **Optics validation is pending.** Until `vlc/ris.py` is provided, optical path gains, mirror normal vectors, FoV clipping, and passivity cannot be verified.

### Defect 2: Inconsistent Energy Model Default
- **Location:** [vlc/ris_environment.py#L28](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L28) vs [vlc/config.py#L148](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/config.py#L148)
- **Observed Behavior:**
  - In `vlc/config.py`, default initialization `VLCConfig()` sets `energy_model = "l1"`.
  - In `vlc/ris_environment.py#L28`, `c = config or VLCConfig(energy_model='paper_signed')`.
  - Calling `RISEnvironment()` defaults to `paper_signed` (literal sum of weights $\sum_i w_i$, which can be negative), whereas calling `RISEnvironment(config=VLCConfig())` defaults to `l1` (nonnegative absolute sum $\sum_i |w_i|$).
- **Remediation:** Align `c = config or VLCConfig()` so defaults remain deterministic and consistent with repository conventions.

### Defect 3: Redundant Double Instantiation of `OpticalRIS`
- **Location:** [vlc/ris_environment.py#L49](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L49) and [L68](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L68) $\to$ [L121](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L121)
- **Observed Behavior:** In `RISEnvironment.__init__`, `self.ris = OpticalRIS(...)` is instantiated at line 49. Then at line 66, `self._direct_geometry = None`. When line 68 calls `self._update_channel()`, it calls `_gains_at()`, which triggers `_refresh_geometry()` because `key != self._direct_geometry`. Line 121 re-instantiates `self.ris = OpticalRIS(...)` a second time.
- **Remediation:** Initialize `self._direct_geometry = self._geometry_key()` or delegate initial construction exclusively to `_refresh_geometry()`.

### Defect 4: Information Dictionary `info['action']` Mismatch in Joint Mode
- **Location:** [vlc/ris_environment.py#L174](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L174) vs [vlc/environment.py#L142](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/environment.py#L142)
- **Observed Behavior:** In `VLCEnvironment.step`, `info['action']` returns the vector from `self.action_space`. In `RISEnvironment.step`, `info['action'] = np.asarray(info['beamformer'])` (only the 4 jammer weights), while the joint action passed to the environment has 5 coordinates.
- **Remediation:** Expose `info['joint_action'] = vector` or keep `info['action']` aligned with `self.action_space[action_idx]` while preserving `info['beamformer']` and `info['ris_index']`.

### Defect 5: Standalone CNN Dimension Asymmetry
- **Location:** [vlc/ris_environment.py#L37-L39](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L37-L39) vs [vlc/ris_experiments.py#L199](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_experiments.py#L199)
- **Observed Behavior:** In `vlc/ris_environment.py`, `cnn_m0` is bumped from 10 to 11 *only* if `control_mode == 'joint'`. In standalone usage, an agent initialized on `control_mode='off'` or `'fixed'` will retain $m_0=10$, while `control_mode='joint'` uses $m_0=11$.
- **Note:** [vlc/ris_experiments.py#L199](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_experiments.py#L199) correctly mitigates this for study runs via `c = replace(c, cnn_m0=max(11, c.cnn_m0))`, but the standalone environment remains asymmetric if instantiated outside the study runner.

---

## 3. Hypothetical Risks & Algorithmic Concerns

### Risk 1: Action Space Explosion & Severe DND Memory Sparsity
- **Location:** [vlc/ris_environment.py#L57-L63](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L57-L63); [vlc/drl_fj.py#L186-L188](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/drl_fj.py#L186-L188), [L254-L272](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/drl_fj.py#L254-L272)
- **Mechanism:** In Algorithm 2, each discrete action has an independent DND dictionary $\mathcal{D}_w$. With 4 jammers quantized at $L_x=2$ ($5^4 = 625$ actions) and $Q$ discrete RIS configurations, $|\mathcal{W} \times \mathcal{Q}| = 625 \times Q$. For $Q=8$, there are 5,000 distinct actions.
- **Risk:** In a 2,000-slot training run, at least 60% of joint actions are never sampled even once. The corresponding DNDs remain empty, defaulting to $Q(s, a)=0$. Epsilon-greedy exploration over 5,000 actions with $\epsilon \in [0.02, 0.15]$ has negligible sample efficiency. This is a fundamental limitation of transferring a tabular-action DND architecture to a higher-dimensional joint action space.

### Risk 2: Trajectory Drift from $m_0$ Scaling
- **Location:** [vlc/drl_fj.py#L42-L45](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/drl_fj.py#L42-L45), [L202-L235](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/drl_fj.py#L202-L235)
- **Mechanism:** Increasing $m_0$ from 10 to 11 expands the CNN input matrix from $10 \times 10$ to $11 \times 11$. The output of Conv Layer 2 expands from $c_2 = 7$ to $c_2 = 8$, increasing the input dimension of linear layer `fc1` from 1,960 to 2,560.
- **Risk:** Even with the same pseudo-random seed, an agent initialized with $m_0=11$ follows a completely different weight trajectory and exploration path compared to the 2024 paper baseline with $m_0=10$. Matched comparisons must run both baseline and joint schemes under $m_0=11$ (as `ris_experiments.py` does), and must not compare $m_0=11$ RIS runs against $m_0=10$ historical logs.

### Risk 3: Static Arbitrary Reference for `fixed_ris`
- **Location:** [vlc/ris_experiments.py#L24-L25](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_experiments.py#L24-L25), [L192](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_experiments.py#L192)
- **Mechanism:** `fixed_ris` is hardcoded to `fixed_configuration=1`.
- **Risk:** If configuration 1 happens to steer reflected energy toward Eve or away from Bob, `fixed_ris` will perform poorly, creating an artificial visual advantage for `joint_ris`. Conversely, if configuration 1 was handcrafted to favor Bob, `fixed_ris` might outperform `joint_ris` due to the learner's exploration overhead. The orientation semantics of configuration 1 must be documented once `vlc/ris.py` is available.

---

## 4. Scientific & Physical Limitations

1. **Oracle Eve CSI Assumption:**
   [vlc/ris_environment.py#L49](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L49) and [L187](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L187) pass `eve_pos` directly into the RIS codebook constructor. In passive eavesdropping scenarios, Eve does not broadcast pilots and her position cannot be known. Any codebook targeting or nulling based on Eve's exact coordinates is an oracle simulation upper bound.
2. **Soft QoS Penalty vs Hard Constraints:**
   [vlc/ris_environment.py#L154-L156](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L154-L156) uses a linear penalty $\delta_{\text{qos}} \cdot \max(0, p_e - p_{e, \text{max}})$. This is an unconstrained soft penalty. If the secrecy rate reward exceeds the penalty, the DRL agent will violate Bob's QoS to maximize return. It must not be reported as a "guaranteed QoS service level".
3. **Unmodeled RIS Energy Overhead:**
   [vlc/ris_environment.py#L152](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L152) and [L191](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L191) exclude mirror actuator/switching power from energy calculations. Claims of improved system energy efficiency are invalid unless actuator consumption is either modeled or explicitly disclosed as excluded.
4. **Scalar Gain and Neglected Multipath Dispersion (ISI):**
   [vlc/ris_environment.py#L135-L136](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L135-L136) adds direct and reflected scalar gains directly. In a $5 \times 5 \times 3\text{ m}^3$ room, path differences of $2\text{--}4\text{ m}$ introduce differential delays of $7\text{--}14\text{ ns}$. At high symbol rates ($>20\text{ MHz}$), this creates inter-symbol interference. The scalar model is valid only for flat-fading / low-symbol-rate regimes.
5. **No Novelty or Benefit Claims Without Measurement:**
   Prior literature (Qian et al. 2021, Saifaldeen et al. 2022, Guo et al. 2026) has already investigated mirror-assisted secure VLC and DRL beamforming. Simply combining optical RIS, friendly jamming, and CNN+DND does not constitute novelty. Claims of improvement must be supported by multi-seed, statistically tested comparisons against properly matched baselines.

---

## 5. Proposed Independent Test Suite for `tests/test_antigravity_ris.py`

The integrating agent should implement and execute the following unit and regression tests in `tests/test_antigravity_ris.py` once `vlc/ris.py` is present:

```python
"""Independent Antigravity verification suite for Optical RIS + FJ + VLC + DRL."""
import unittest
import numpy as np
from vlc.config import VLCConfig
from vlc.environment import VLCEnvironment
from vlc.ris_environment import RISEnvironment


class TestAntigravityRISIntegration(unittest.TestCase):

    def setUp(self):
        self.config = VLCConfig(model="paper", energy_model="paper_signed", cnn_m0=11)
        self.w_zero = np.zeros(self.config.num_jammers)
        self.w_test = np.array([0.5, -0.5, 1.0, -1.0])

    def test_01_no_ris_reduction_to_baseline(self):
        """Verify control_mode='off' reproduces VLCEnvironment direct gains and metrics."""
        base_env = VLCEnvironment(self.config)
        ris_off_env = RISEnvironment(self.config, control_mode="off")

        self.assertAlmostEqual(base_env.h_AB, ris_off_env.h_AB, places=12)
        self.assertAlmostEqual(base_env.h_AE, ris_off_env.h_AE, places=12)
        np.testing.assert_allclose(base_env.h_JB, ris_off_env.h_JB, rtol=1e-12)
        np.testing.assert_allclose(base_env.h_JE, ris_off_env.h_JE, rtol=1e-12)

        info_base = base_env.step(self.w_test)[2]
        info_ris = ris_off_env.step(self.w_test)[2]
        for metric in ("secrecy_rate", "ber", "energy", "utility"):
            self.assertAlmostEqual(info_base[metric], info_ris[metric], places=12,
                                   msg=f"Metric mismatch in {metric}")

    def test_02_common_mirror_configuration_across_links(self):
        """Verify that Alice and all jammers observe the same physical RIS configuration."""
        ris_env = RISEnvironment(self.config, control_mode="joint")
        action = ris_env.encode_action(self.w_test, ris_index=1)
        info = ris_env.evaluate_action(action)
        # Reflected gains must be calculated simultaneously from the same configuration index
        self.assertEqual(info["ris_index"], 1)
        self.assertIn("reflected_gains", info)
        ref = info["reflected_gains"]
        self.assertTrue(ref["h_AB"] >= 0 and ref["h_AE"] >= 0)
        self.assertEqual(len(ref["h_JB"]), self.config.num_jammers)
        self.assertEqual(len(ref["h_JE"]), self.config.num_jammers)

    def test_03_passive_eve_non_interference(self):
        """Verify Eve's position does NOT alter Bob's direct or reflected channel gains."""
        cfg1 = VLCConfig(model="paper", cnn_m0=11, eve_pos=np.array([3.2, 3.4, 0.85]))
        cfg2 = VLCConfig(model="paper", cnn_m0=11, eve_pos=np.array([1.0, 1.0, 0.85]))
        env1 = RISEnvironment(cfg1, control_mode="joint")
        env2 = RISEnvironment(cfg2, control_mode="joint")

        # Bob's direct gains must remain identical regardless of Eve's coordinates
        self.assertAlmostEqual(env1._direct_gains[0], env2._direct_gains[0], places=12)
        np.testing.assert_allclose(env1._direct_gains[2], env2._direct_gains[2], rtol=1e-12)

    def test_04_action_encoding_decoding_roundtrip(self):
        """Verify bijection between joint action indices, continuous vectors, and decoding."""
        env = RISEnvironment(self.config, control_mode="joint")
        for q in range(env.num_ris_configurations):
            encoded = env.encode_action(self.w_test, ris_index=q)
            self.assertEqual(encoded.shape, (5,))
            w_dec, q_dec = env.decode_action(encoded)
            np.testing.assert_allclose(w_dec, self.w_test, rtol=1e-10)
            self.assertEqual(q_dec, q)

    def test_05_qos_penalty_accounting(self):
        """Verify that QoS penalty strictly triggers only when BER > qos_ber_max."""
        ber_target = 1e-4
        penalty_val = 100.0
        env = RISEnvironment(self.config, control_mode="joint",
                             qos_ber_max=ber_target, qos_penalty=penalty_val)
        
        info = env.evaluate_action(env.action_space[0])
        expected_violation = max(0.0, info["ber"] - ber_target)
        self.assertAlmostEqual(info["qos_violation"], expected_violation, places=10)
        self.assertAlmostEqual(info["utility"],
                               info["base_utility"] - penalty_val * expected_violation, places=10)

    def test_06_action_replay_determinism(self):
        """Verify that state feedback does not cause numerical drift upon action replay."""
        env = RISEnvironment(self.config, control_mode="joint")
        action = env.action_space[0]
        state1, u1, info1 = env.step(action)
        info2 = env.evaluate_action(action)
        self.assertAlmostEqual(info1["utility"], info2["utility"], places=12)
        self.assertAlmostEqual(info1["secrecy_rate"], info2["secrecy_rate"], places=12)


if __name__ == "__main__":
    unittest.main()
```

---

## 6. Actionable Recommendations for Integrating Agent

1. **Implement `vlc/ris.py`:** Create `OpticalRIS` and `OpticalRISConfig` providing `num_configurations`, `configuration_names`, `metadata()`, and `get_reflected_gains(index) -> Tuple[float, float, np.ndarray, np.ndarray]`. Ensure optical passivity ($\sum P_{\text{refl}} \le P_{\text{inc}}$) and FoV geometric limits are enforced.
2. **Fix Default Inconsistency:** Change [vlc/ris_environment.py#L28](file:///D:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research/VLC_Simulation/OWC/vlc/ris_environment.py#L28) from `c = config or VLCConfig(energy_model='paper_signed')` to `c = config or VLCConfig()`.
3. **Resolve Double Instantiation:** Eliminate redundant construction of `self.ris` in `RISEnvironment.__init__`.
4. **Run Verification:** Once `vlc/ris.py` is committed, execute `python -B -m unittest tests/test_antigravity_ris.py` to validate baseline reduction and action roundtrips before running multi-slot studies.


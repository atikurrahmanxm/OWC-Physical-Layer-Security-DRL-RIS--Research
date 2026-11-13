# RIS + friendly jamming + VLC + DRL: research and validation notes

Review date: 2026-11-13, Asia/Calcutta. This is a research planning note, not a novelty certificate or a claim of publication readiness.

## Scope retained from the user

The baseline is the system in the supplied 2024 paper, *Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication*, DOI [10.1109/TWC.2024.3458046](https://doi.org/10.1109/TWC.2024.3458046). Add an optical mirror-array RIS and jointly control its configuration and the friendly-jamming weights. The separate finite-alphabet `physical` mode is not the baseline for this extension.

The local PDF's received-signal structure, amplitude constraints and Section VI parameters were inspected. Existing unresolved energy/SNR interpretations must remain explicit and identical across compared schemes. A comparison against this implementation is not automatically a numerical reproduction of the published figures.

## Verified prior work and overlap

### Qian et al., 2021

*Secure Visible Light Communications via Intelligent Reflecting Surfaces*, Lei Qian, Xuefen Chi, Linlin Zhao and Anas Chaaban, [author-submitted arXiv record](https://arxiv.org/abs/2101.12390).

The author abstract describes mirror-array VLC secrecy, orientation optimization, a reflected-spot reformulation and particle-swarm optimization. Thus optical steering toward Bob while limiting Eve leakage is established prior work. A new paper needs a more specific, tested contribution than adding a mirror array.

### Saifaldeen et al., 2022

*DRL-Based IRS-Assisted Secure Visible Light Communications*, Danya A. Saifaldeen, Bekir S. Ciftler, Mohamed M. Abdallah and Khalid A. Qaraqe, IEEE Photonics Journal 14(6), DOI [10.1109/JPHOT.2022.3178852](https://doi.org/10.1109/JPHOT.2022.3178852). Primary institutional source: [HBKU publication record and abstract](https://elmi.hbku.edu.qa/en/publications/drl-based-irs-assisted-secure-visible-light-communications/).

Its abstract explicitly describes joint beamforming-weight and mirror-orientation control using DDPG, adaptation to user mobility, and a mirror-arrangement/complexity tradeoff. Therefore neither joint RIS/beamforming control nor using DRL for secure mirror-assisted VLC is new by itself. Replacing DDPG with CNN+DND needs measured justification rather than an algorithm-name novelty claim.

### Guo et al., 2026: mandatory close-work check

*RIS-Aided Physical Layer Security for Visible Light Communication Systems*, Dongqin Guo, Gang Xin, Qi Wu and Jian Zhang, IEEE Photonics Journal 18(1), pp. 1-6, DOI [10.1109/JPHOT.2026.3651843](https://doi.org/10.1109/JPHOT.2026.3651843), [publisher document 11340672](https://ieeexplore.ieee.org/document/11340672/).

Title, authors, venue, issue and February 2026 publication metadata were verified from the [publisher-deposited Crossref record](https://api.crossref.org/works/10.1109/JPHOT.2026.3651843). The IEEE full text was inaccessible in this review environment. Technical details indexed elsewhere suggest close overlap with RIS and jamming, but this note does not treat those secondary descriptions as a verified technical comparison. Obtain the primary full text and compare its threat model, jamming origin, optics, constraints and optimization before making a novelty statement.

This short review is not exhaustive. Search for newer optical RIS/FJ, robust-CSI, constrained learning and secure VLC work before submission. Verify bibliographic details from publishers or author/institutional manuscripts.

## Candidate contribution to test, not yet established

A defensible research question is:

> Under the 2024 friendly-jamming VLC system, can a bounded optical-RIS codebook and CNN+DND joint controller improve secrecy while satisfying a declared Bob QoS target, at useful control/training cost and under explicitly modeled Eve-location uncertainty?

Potential contribution dimensions are the specific friendly-jamming/RIS coordination, constraint handling, sample efficiency, finite-action codebook scaling, or robustness. Choose only the dimensions actually implemented and supported by results. A favorable stationary single-seed simulation establishes none of these broadly.

## Minimal mathematical extension

```text
h_AB_eff(q) = h_AB_direct + h_AB_RIS(q)
h_AE_eff(q) = h_AE_direct + h_AE_RIS(q)
h_JB_eff(q) = h_JB_direct + h_JB_RIS(q)
h_JE_eff(q) = h_JE_direct + h_JE_RIS(q)

y_B = h_AB_eff(q)*x + (h_JB_eff(q)^T*w)*j + n_B
y_E = h_AE_eff(q)*x + (h_JE_eff(q)^T*w)*j + n_E
action = [w, q]
```

All source-to-RIS links must use the same physical mirror normals for a selected configuration. A surface cannot independently choose favorable coefficients for each receiver/source. Keep gain units, LED aggregation and reflection area accounting consistent. Scalar DC gains assume path delays are negligible at the symbol rate; this does not validate a dispersive/ISI case.

## Explicit assumptions required in every experiment

- Mirror geometry, finite area, placement, reflectivity, orientation limits, receiver aperture/FoV and visibility.
- Reflection model and numerical approximation; finite-area/subdivision and intercepted-power checks. Point-ray image geometry alone is not a proof of finite-aperture power conservation.
- Surface grouping/codebook construction, including which transmitter and target informed each orientation. An Eve-focused or location-aware codebook uses Eve information and must be labeled accordingly.
- Direct and reflected Alice/jammer paths, flat-channel approximation, and any path excluded by actual geometry.
- Known/estimated Bob and Eve information; perfect Eve CSI is an oracle simulation assumption, not a passive-Eve detector.
- Chosen printed signed-energy or L1 interpretation, SNR conversion, seed and channel-motion process. Carry these choices across all comparisons.
- QoS threshold and penalty/constraint, if any. A finite soft penalty does not guarantee constraint satisfaction.
- Passive Eve initially. Blockage or active jamming is an additional declared scenario; Eve's mere presence must not create arbitrary Bob interference.
- RIS controller energy and update delay, if excluded, disclosed as excluded. Equal LED power alone does not establish equal total-system energy.

## Tests and fair experiment matrix

1. RIS disabled, zero area and zero reflectivity reproduce direct channel gains and original metrics at the same jammer action. Distinguish this metric-level identity from differences in random learning trajectories caused by larger action sets.
2. Test geometric reflection law, surface visibility, receiver FoV, orientation bounds, finite area and passive-power limits independently of reward optimization.
3. Use a common surface configuration for Alice and all jammers, even when it helps Eve or hurts Bob. Retain adverse outcomes.
4. Compare at least no RIS + DRL-FJ, fixed RIS + DRL-FJ and joint RIS/FJ + DRL, at matched channel/scenario/seed, slots, power and interpretation choices. Add no-jamming and channel-nulling references where appropriate.
5. Include an exhaustive codebook/action-grid reference for small problems. Label it a finite-grid reference, not a continuous global optimum. If used to initialize learning, disclose that privileged optimization and use it equally in baselines.
6. Preserve per-slot raw observations, joint actions, effective gains, base reward and any QoS penalty. Recompute saved metrics from saved actions and geometry.
7. Report training means including exploration separately from greedy post-training evaluation. Also report Bob BER, Bob-outage fraction, secrecy-outage fraction and feasibility. Secrecy targets and QoS thresholds must be declared before selecting favorable results.
8. Use paired seeds/scenarios and report the number of independent seeds. Do not infer a confidence interval over seeds from thousands of correlated slots. For one seed, report one-seed results without invented error bars.
9. Measure runtime, action count, model size and control overhead. A larger action space may make a superficially stronger model harder to learn within equal slots.
10. Test Eve positions near Bob, poor RIS placement and imperfect location/CSI. An inability to meet both objectives is a research result, not a reason to adjust the plot.

## Ten-day work plan and submission boundary

The requested ten-day interval is treated as an engineering/research sprint from 2026-11-13 toward a **submission-readiness decision on 2026-11-23**. Peer-reviewed publication or acceptance within that period cannot be guaranteed. If evidence is weak, reduce the claims or extend validation rather than submitting unsupported results.

| Date | Work and evidence required |
|---|---|
| Nov 13 | Freeze baseline configuration/assumptions; implement and independently test optical paths and no-RIS reduction; capture closest-work bibliography. |
| Nov 14 | Complete joint action/state integration, raw exports, QoS reporting and independent action replay; run smoke tests. |
| Nov 15 | Pilot matched ablations; identify action-space learning failures and infeasible scenarios; freeze primary metrics and scenario split. |
| Nov 16 | Run multi-seed stationary experiments and codebook/area sensitivity with recorded compute budgets. |
| Nov 17 | Evaluate mobility or CSI uncertainty only if implemented correctly; otherwise keep a narrower stationary claim. |
| Nov 18 | Reproduce key cases independently, inspect power/geometry convergence, verify every plotted result from raw records. |
| Nov 19 | Complete primary full-text closest-work comparison, choose a supported contribution and prepare tables/figures. |
| Nov 20 | Draft model, assumptions, algorithm changes, complexity, experimental protocol and limitations. |
| Nov 21 | Draft results/related work; run numerical and citation consistency review; release-reproduce representative figures. |
| Nov 22 | Independent manuscript/code review, resolve discrepancies, select an appropriate venue and inspect its requirements. |
| Nov 23 | Submission-readiness decision. Submit only with coauthor approval, substantiated claims, ethical authorship and venue-compliant materials. |

This schedule is a plan, not completed evidence. No manuscripts have been submitted and no external messages have been sent by this review task.

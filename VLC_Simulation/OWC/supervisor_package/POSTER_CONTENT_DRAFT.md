# Final-year project poster — content draft

Presentation: 14 November 2026, 9:00 AM onwards; Audi 1, Block C.

Status: Content prepared from existing project evidence. Apply the institution's shared template once supplied. Student names/rolls, guide, department and institution remain required; do not invent them.

## Proposed title

**Optical RIS-Assisted Secure VLC Using Friendly Jamming and Deep Reinforcement Learning**

## Author block — fill before printing

Students: [Names and roll numbers]  
Project guide: [Name]  
Department: [Department]  
Institution: [Institution]

## Problem statement

Indoor visible light communication broadcasts optical signals that can be received by an eavesdropper. Friendly jamming can protect confidentiality but can also interfere with the legitimate receiver. We investigate whether a controllable optical mirror array can improve this secrecy–reliability trade-off.

## Objectives

- Extend a 2024 VLC friendly-jamming baseline with a finite optical RIS.
- Jointly select jammer weights and RIS configuration using CNN/DND reinforcement learning.
- Compare no RIS, fixed RIS and joint control under matched simulations.
- Measure secrecy, Bob BER, cost and failure cases honestly.

## System architecture — diagram specification

Alice LED → Bob and Eve via direct optical channels. Alice and four friendly-jammer fixtures also illuminate a six-mirror wall-mounted RIS. One shared mirror configuration affects all source–receiver links. The DRL controller selects four jammer weights plus one RIS configuration. Receiver metrics feed the reward/learning loop.

Use a clean architecture diagram plus one cropped 3D demo screenshot; label the screenshot “Simulation visualization; animated paths are illustrative.” Render arrows for actual model components without suggesting automatic Eve detection or guaranteed decoding failure.

## Methodology

1. Compute direct Lambertian and finite specular RIS channel gains with receiver FoV and optical-power bounds.
2. Form effective channels by adding direct and reflected gains.
3. Use CNN + per-action DND control with 625 jammer vectors and five RIS configurations: 3,125 joint actions.
4. Train for 2,000 slots and evaluate separately for 1,000 frozen greedy slots across 10 independent seeds in the nominal L1 study.
5. Compare paired seed differences and report 95% confidence intervals. Static repeated slots are not independent samples.

## Equations — typeset mathematically in final poster

Effective channel: h_eff(q) = h_direct + h_RIS(q).

Joint action: a_t = [w_1,w_2,w_3,w_4,q_tilde].

Primary utility: r_t = c_s(t) − 3.5 p_e(t) − 0.4 E(t).

Here E is the selected model-defined jammer cost, not measured total hardware energy. The primary poster comparison uses the explicitly labeled nonnegative L1 cost interpretation, which differs from the literal signed-energy expression.

## Implementation

- Python / NumPy / PyTorch backend: finite mirror optics, FJ environment and CNN/DND learner.
- Interactive local browser demo: 3D room, mirror configurations, receiver presets, live backend metrics and recorded-action replay.
- Recorded raw histories/actions, reproducibility metadata and scientific figures.
- Latest independently executed full suite in this conversation: 94 passing tests before the latest build changes; latest subsequent focused demo check: five passing integration tests. Rerun before putting an unqualified current-test badge on the final poster.

## Main results — nominal L1, frozen evaluation

| Scheme | Mean secrecy (bps/Hz) | 95% CI across 10 seeds |
|---|---:|---:|
| No RIS + FJ + DRL | 1.3205 | [1.2289, 1.4122] |
| Fixed RIS + FJ + DRL | 1.4978 | [1.3184, 1.6772] |
| Joint RIS + FJ + DRL | 1.4565 | [1.3199, 1.5930] |

Fixed RIS versus baseline: +0.1773 bps/Hz (+13.4% sample-mean increase); paired 95% CI [+0.0378,+0.3167]. Joint versus baseline: +0.1359 bps/Hz; paired CI [−0.0440,+0.3158], so joint superiority is not established. Do not claim fixed versus joint statistical equivalence.

All schemes have zero modeled frozen evaluation outages at this nominal static operating point. Do not claim a joint outage advantage using training statistics. Tested near-Bob finite grid and colocated scenario yield zero secrecy; this is not a universal proximity threshold.

Use supervisor_package/figures/fig2_frozen_evaluation_secrecy and fig3_paired_differences (PNG/PDF) as the principal evidence. A paired-difference plot is preferable to unsupported “best algorithm” branding.

## Key contributions — implementation/evaluation claims

- Integrated a finite specular optical RIS with the VLC/FJ baseline.
- Implemented joint jammer/RIS actions in a CNN/DND controller.
- Delivered an interactive backend-linked 3D demonstration and reproducible matched evaluation.
- Quantified fixed-RIS benefit, joint-control uncertainty and adverse geometry cases.

These are project deliverables, not a claim of first-ever research novelty. Literature includes prior optical RIS and secure VLC/DRL work.

## Limitations and next steps

Static geometry and oracle Eve-position information; no body-blockage or multipath-ISI model; RIS actuation energy excluded. Exact numerical reproduction of the original paper is unresolved. Next: uncertain Eve geometry and sample-efficient joint control, selected after guide feedback.

## Reference footer

2024 baseline: Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication. DOI: 10.1109/TWC.2024.3458046. Keep any additional poster references accurate and concise.

## 60-second presentation script — Bangla

“আমাদের project হলো optical RIS-assisted secure VLC। Alice থেকে Bob-এর data transmission Eve intercept করতে পারে। Friendly jamming Eve-কে বাধা দিতে পারে, কিন্তু Bob-এরও ক্ষতি করতে পারে। তাই আমরা ২০২৪ system model-এর ওপর ছয়-mirror RIS যোগ করেছি এবং jammer weights ও RIS configuration-এর joint DRL control implement করেছি। এখানে live 3D simulation ও backend-computed channel changes দেখানো হচ্ছে। দশটি seed-এর nominal study-তে Fixed RIS baseline-এর তুলনায় secrecy rate বাড়িয়েছে। Joint control implement হয়েছে, তবে তার superiority এখনো statistically established নয়। আমরা limitation ও near-Bob failure case-ও report করেছি। পরের কাজ uncertain Eve geometry ও improved joint-control learning।”

## Before leaving for the venue

- Apply the official poster template and check required size/orientation; do not assume A0/A1.
- Fill and proofread every member's name/roll, guide, department and institution.
- Export print-ready PDF with readable equations, labels, citations and graphs; inspect the actual PDF.
- Take the PDF and original editable poster on laptop plus a second local copy.
- Rehearse the local demo and keep saved screenshots/figures available if the live service fails.
- Ensure all group members attend, per the notice. Ask the organizer about physical printing/display requirements if unspecified.

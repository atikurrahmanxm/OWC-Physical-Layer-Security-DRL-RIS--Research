# Codex review of today's Antigravity deliverables

Date: 2026-11-13. Status: substantial implementation completed; reporting/manuscript corrections still required before submission readiness.

## Independently checked

- Current full suite: **89 tests passed in 22.472 seconds** in this review.
- `output_figures/ris/final_evaluation/ris_study_data.json` exists, complete=true, 30 runs, seeds 42 through 51, nominal scenario, L1 only, 2,000 training slots and 1,000 evaluation slots per run. Current vlc source hashes match the export.
- The frozen-evaluation implementation performs deterministic argmax without training updates. It starts from env.reset() with EMPTY history, not the final training history claimed in the completion report. `initial_history` is not a supported argument.
- Manuscript draft, tables, bibliography and today's completion report exist.
- Recalculated evaluation means agree for secrecy: baseline 1.3205214713, fixed 1.4977986702, joint 1.4564502067 bps/Hz. Paired fixed-minus-baseline interval [0.0378458203, 0.3167085774] is positive. Joint-minus-baseline interval [-0.0439845724, 0.3158420431] includes zero; joint-minus-fixed interval [-0.2674135115, 0.1847165846] also includes zero. Failure to establish a difference is not statistical equivalence/parity.
- Evaluation energy/cost means: baseline 2.05, fixed 2.2, joint 2.0. Joint's lower sample mean does not establish a statistically significant saving: its paired interval versus fixed includes zero.

## Critical reporting errors

1. The 'frozen-policy evaluation' tables in TODAY_COMPLETION_REPORT.md and manuscript/draft.md combine metrics from different phases. Secrecy/energy means are evaluation metrics, BER is from final training windows, and the quoted 9.19%/7.38%/6.23% secrecy outages and 0.41%/0.26%/0.20% Bob outages are ALL-TRAINING metrics.
2. Recomputed from evaluation histories/summaries: **ALL THREE schemes have zero secrecy outage, zero Bob outage at both 1e-3 and 1e-4, and numerically zero BER in this particular static frozen evaluation**. This is formula output, not a hardware measurement or universal reliability guarantee. There is no lowest-outage joint advantage in these evaluation data.
3. Each of the 30 evaluation runs uses ONE unique action throughout its 1,000 slots. This is a static policy operating-point comparison, not robustness over 1,000 independent conditions. Seed remains the independent replicate.
4. Manuscript Section IV describes a wrong state, reward and CNN: implementation state is [previous BER, previous secrecy, installed effective h_AB, previous cost], concatenated with historical actions; code uses Conv2d, not a two-layer 1D CNN. Reward is secrecy - 3.5*BER - 0.4*cost, plus an optional excess-BER penalty. The manuscript instead uses 3.5*cost and an indicator QoS penalty and omits the original BER term. These are material scientific mismatches.
5. Near-Bob zero secrecy in sampled training histories is not a proof of a universal 7-cm physical impossibility. Check exhaustive reference feasibility, codebook/model scope and positions. Exact colocation with identical channels/noise is a distinct boundary case.
6. Unsupported literature-wide allegations ('majority' flawed evaluations, authors conceal failures), novelty/superiority claims and causal attributions to action-space size need evidence or removal. Numerical differences alone do not identify their cause.
7. Execution brief is only partly fulfilled: expanded frozen studies cover nominal L1 only; signed interpretation and near_bob/colocated retain historical training-only studies. Label this matrix honestly instead of claiming all requested experiments complete. Current artifacts do not show serialized trained CNN/DND checkpoints; claims about reproducing an existing trained policy need retraining or checkpoint export.
8. Unit tests snapshot CNN parameters and dictionary entry COUNTS, not full DND key/value equality. They support no-insertion behavior but do not prove all memory values were unchanged. No new independent replay of every training/evaluation observation was performed in this review.
9. Bibliography verification, related-work contribution positioning, publication-quality figures and actual submission packaging remain pending review. The existence of draft sections is not completion of scientific validation.

## Next bounded task

Do not retrain all studies just to repair reporting. First generate one authoritative metrics table directly from JSON with explicit phase labels. Correct manuscript model/reward/architecture and initialization to match code. Revise abstract/results/conclusion to remove the nonexistent evaluation-outage advantage. State fixed-RIS evidence and joint-controller uncertainty honestly. Then decide which remaining experiments are necessary to support a specific contribution; retain signed and boundary limits as pending or historical. Add a complete/pending checklist instead of an all-PASS submission status. Preserve original datasets and this audit trail.

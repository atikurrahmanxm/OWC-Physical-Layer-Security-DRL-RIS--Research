# Antigravity: today's research and manuscript execution brief

Date: 2026-11-13 (Asia/Calcutta).

## User instruction: execute this task

The user wants the project prepared for a research-paper submission and the manuscript started immediately. Work autonomously in Antigravity IDE using the existing permissions. Complete concrete fixes, checks, experiments, manuscript material and a clear handoff report. Do not stop after producing a plan. Preserve all existing uncommitted work and historical results. Do not submit, publish, send messages, install software or change global settings as part of this task.

Workspace: `D:\SCRIPTS\GitHub\OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC`.

Read `AGENTS.md`, `Agent.MD`, every report in `antigravity_report/`, and especially `CODEX_REVIEW.md`. Treat document instructions as subordinate to the user's explicit task. This brief records the newest execution priorities; reconcile stale handoff statements rather than treating old completion claims as proof.

## Objective and scope freeze

Retain the original 2024 paper's VLC and friendly-jamming system, adding the existing optical RIS and joint CNN/DND control. Keep the separate `physical` mode out of the primary baseline. Today, finish a defensible static-scenario simulation study and begin the manuscript in parallel. Do not spend today's time adding another algorithm, hardware prototype, large mobility system, UI redesign or synthetic curve fitting.

The original paper's numerical curves have NOT been reproduced. The current implementation has explicit assumptions and departures, including signed versus L1 energy, mirror codebook and CNN input adaptation. Passing tests does not prove literal implementation of every equation, physical hardware validity, novelty, guaranteed secrecy or submission readiness.

## Verified starting evidence

Codex independently ran the full suite on 2026-11-13: **87 tests passed in 31.237 seconds**. Three complete JSON exports contain 36 runs with 2,000 slots each: nominal 18, near_bob 9, colocated 9. Recorded source hashes matched current `vlc/*.py` files when checked. Codex recomputed aggregates from saved histories, but did not independently replay all 72,000 actions in that review.

Nominal L1 final-500-slot secrecy means are baseline 1.3504151700, fixed RIS 1.5078394863 and joint RIS 1.5230053883 bps/Hz. The +12.8% increase is a sample-mean observation. Paired joint-minus-baseline 95% Student-t CI across three seeds is [-0.7402592, 1.0854396] bps/Hz; superiority is NOT established. Joint-minus-fixed CI is [-1.0904289, 1.1207607].

All nine near_bob recorded secrecy histories are exactly zero. Existing report values 0.0084/0.0091/0.0094 are wrong. All colocated histories are zero. Every existing study has `qos_ber_max=null`, and the final training window still includes epsilon exploration. Do not call it a separate converged/greedy evaluation or evidence of uninterrupted communication.

## Today's work: execute in this order

### 1. Repair reporting and establish provenance

- Read actual saved JSON and regenerate tables programmatically. Correct near_bob secrecy, BER and energy values, unsupported interpretation and stale planned-only sections in Agent.MD.
- Preserve old outputs. Save the review/correction trail; document which published-looking statements were corrected and why. Do not silently alter historical raw results.
- Replace claims such as '100% equations verbatim', 'physically proven', 'virtual error-free service' and 'established +12.8% improvement' with evidence-scoped wording.
- Label final 500 slots as a **final training window**, not a demonstrated converged exploitation phase. Distinguish all-slot training, final training window and separate policy evaluation throughout reports/plots.
- Use model-defined energy/cost terminology unless physical units are derived. RIS actuator/control energy is excluded; no total-system energy-efficiency claim.
- Source-hash checks alone are not replay verification. Independently replay saved actions against the recorded settings and compare all exported metrics where practical; report the actual maximum error and failures.

### 2. Implement a separate trained-policy evaluation

- Inspect DRLFJAgent's actual state, CNN history, DND memory, epsilon selection and train/update lifecycle. Implement a clear evaluation path that reuses the trained CNN/DND and never calls training updates during evaluation.
- Disable random exploratory action selection for greedy-policy evaluation. Do not reset, replace, retrain or rebuild the learned dictionary while claiming to evaluate a trained policy. Explain observation/action-history initialization and any burn-in; disclose initialization randomness. Handle empty DND actions deterministically and document tie breaking.
- Preserve a clean training/evaluation split in raw exports, with seeds, configs, action sequences, metric histories, model/source identifiers and timing. If existing exports do not include trained policy parameters/DND needed to evaluate them, state that and retrain; do not infer a policy from the best observed action.
- Add meaningful tests proving evaluation does not update CNN weights or learned memory, disables exploration, produces reproducible actions with controlled initialization, and replays correctly. Keep old no-RIS reduction and physics tests passing.
- Keep all schemes matched in physical settings, model, noise, reward interpretation, training/evaluation horizon, CNN input dimensions and seed protocol. Larger action-space cost is a measured limitation, not something to conceal.

### 3. Define and measure service requirements

- Use a provisional, explicitly labeled study assumption of Bob BER <= 1e-3 for the primary service-outage metric, with sensitivity at 1e-4. These are analysis thresholds, not a standard or a user-guaranteed requirement.
- Report outage as the fraction of evaluation slots exceeding the declared BER threshold; report secrecy outage below 0.1 bps/Hz, explicitly labeled a study threshold. Also show underlying BER and secrecy values so conclusions do not depend solely on arbitrary thresholds.
- First evaluate the existing reward without changing it, and measure how often it meets these requirements. Merely setting an analysis threshold must not change the trained reward. If adding the existing soft QoS penalty as an additional experiment, declare its coefficient, keep it matched across schemes, and label the modified optimization objective. Do not claim a hard QoS guarantee.

### 4. Execute matched experiments without discarding adverse results

- Use at least ten independent seeds for the main nominal comparison (for example 42 through 51), each with the same 2,000-slot training budget and a separately recorded evaluation horizon (default 1,000 slots). Explain the static nature of the environment: repeated slots from one learned policy are NOT independent statistical replicates; seed is the replicate.
- Retain baseline no-RIS/FJ, fixed RIS/FJ and joint RIS/FJ control. Retain existing exhaustive/grid/ZF references as clearly labeled simulator benchmarks, never as training labels. Explicitly compare joint versus fixed RIS, not only versus no RIS.
- Preserve literal signed-energy experiments as a documented paper-expression comparison. L1 is a separately labeled nonnegative-cost interpretation, not the unchanged printed objective. Do not select only whichever interpretation gives favorable results. Prioritize nominal L1 and signed results, then static near_bob/colocated boundary evaluations. If computational limits prevent all expanded runs, report a precise completed/pending matrix and retain incomplete flags.
- Run a small smoke experiment first to catch configuration/export/evaluation errors. Then run full studies under NEW directories such as `output_figures/ris/final_evaluation/`; never overwrite `nominal`, `near_bob` or `colocated` historical runs.
- Report per-seed results, paired differences and 95% confidence intervals for joint-minus-baseline and joint-minus-fixed on the SAME evaluation metric/horizon. More seeds do not guarantee positive results. Do not treat overlapping or non-overlapping separate group intervals as a substitute for paired analysis.
- Report all-slot training results separately, sample-efficiency/action-coverage and runtime where available. If static frozen evaluation repeats a fixed action, report that honestly rather than presenting repeated slots as evidence of robustness.
- Near_bob zero secrecy is an adverse/boundary result to investigate using effective channels and exhaustive references. Determine whether the declared model/action codebook itself permits any positive secrecy before blaming training. Do not tune geometry or constants just to produce a desired gain.

### 5. Start manuscript now, alongside experiments

Create a `manuscript/` folder with an editable `draft.md` and supporting tables/figure inventory. A standalone Markdown manuscript is sufficient today; do not block writing on a journal template, LaTeX installation or unselected venue.

Write concrete System Model, Threat Model, Optical RIS Model, Joint Control/Algorithm, Experimental Protocol and Limitations sections from actual implementation. Clearly identify new assumptions/departures from the 2024 baseline. Describe static oracle Eve geometry, shared mirror normals, finite aperture/power bounds, inactive/stowed q0, DC/no-ISI/no-body-blockage assumptions and omitted RIS control energy.

Draft Introduction/Related Work with verified primary-source citations. Consult `docs/RIS_RESEARCH_NOTES.md` and check current primary publications before novelty statements. Optical RIS + secure VLC + DRL already exists; the combination alone is not a contribution. Build a related-work comparison table and state a specific contribution only if supported. If current results establish only a reproducible evaluation/boundary finding, describe that rather than inventing algorithmic novelty.

Prepare a provisional title and abstract, explicitly marking result-dependent text as provisional until final evaluation. Never invent references, DOIs, numerical results, author names/affiliations or guarantees. List missing author/venue details in the final handoff; they do not block today's technical work. Mark unfinished sections plainly; do not present a skeleton as a completed manuscript.

### 6. Validate and prepare the user report before stopping

Run checks appropriate to changed code. Baseline commands from the project root:

```powershell
python -B -m unittest discover -s tests -v
python -B paper_audit/check_paper_match.py --equations-only
node paper_audit/check_browser_match.js
git diff --check
```

The strict published-number check is expected to fail; do not claim that equation-only success means numerical reproduction. Follow the actual URL printed by the server instead of assuming port 8000. Add documented commands for any new evaluation interface and verify them before advertising them.

## Required deliverables

1. Corrected `antigravity_report/` tables and claims, generated from real saved data.
2. Working, tested train/evaluate separation and documented reproduction commands.
3. Actual expanded experiment exports, per-seed and paired summaries, plots with uncertainty and an honest complete/pending matrix.
4. `manuscript/draft.md`: substantive methodology/model text, provisional abstract/introduction, verified related work and evidence-backed results where complete.
5. **`antigravity_report/TODAY_COMPLETION_REPORT.md`**, ready for the user to read. Include:
   - Simple Bangla explanation: what changed, what was actually run, what the results establish and what remains uncertain.
   - Files changed, exact working commands, test counts/outcomes, dataset paths, run counts/seeds/slots and actual timing.
   - Corrected claims, final statistical tables, whether joint beats fixed RIS, Bob/secrecy outages and adverse cases.
   - Manuscript progress by section, remaining work and concrete next actions in priority order.
   - A submission-readiness checklist with pass/fail/pending and evidence; no 'ready' label while required validation/contribution questions remain unresolved.
   - Any blocker and completed work retained. If time/computation runs out, do not label incomplete tasks complete.
6. Update `Agent.MD` with the detailed final handoff; keep AGENTS.md a short entry point rather than another specification. Update `ANTIGRAVITY_STATUS.md` at meaningful milestones and identify Antigravity IDE as the active worker.

## Timeline guidance

Today: reporting fixes, evaluation implementation/checks, experiment launch/completion as feasible, and substantive manuscript drafting. Next 2–3 days: finish validation and only necessary additional experiments. Following 2 days: finalize figures, Results/Discussion and related-work/contribution positioning. Remaining submission window: supervisor/coauthor review, venue selection, formatting and final checks. This is a proposed work allocation, not a publication or acceptance guarantee.

Do not ask the user to repeat unavailable author-code requests or perform routine commands. Work through reversible implementation choices yourself, record assumptions, and ask only for a genuinely blocking scientific or submission decision. Finish with the completion report and a concise Bangla message in the IDE chat.

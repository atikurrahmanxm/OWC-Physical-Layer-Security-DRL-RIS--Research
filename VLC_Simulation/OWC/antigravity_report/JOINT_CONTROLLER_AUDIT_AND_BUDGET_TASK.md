# Antigravity execution task: understand joint control before expanding the study

Date: 2026-11-17, Asia/Calcutta.

## User-authorized objective

The user agrees to investigate why joint RIS/FJ DRL has not outperformed fixed RIS, then run a controlled training-budget comparison. Execute this in Antigravity IDE. Begin with saved-data analysis; do not immediately launch long runs or redesign the algorithm. Deliver actual findings, scripts, tests and a report. Keep manuscript, poster and UI work out of this task.

Read AGENTS.md and Agent.MD first, followed by the actual source and relevant audit reports. Older 'planned/not implemented' handoff sections are historical and conflict with current code. Preserve all user changes, especially the edited poster and English guide, all historical results and current research model. Do not reset, commit, push, publish, install packages, change global settings or send external messages as part of this task.

## Scientific question

In the nominal L1 study, frozen-evaluation secrecy means are approximately 1.3205 (baseline), 1.4978 (fixed RIS) and 1.4565 (joint), across seeds 42–51. Joint superiority is not established. Determine what the recorded actions and feasible references reveal; then test whether increased training changes the result under matched conditions. Larger action space is a plausible explanation, not an established cause. It must not be assumed as the answer.

## Stage A — inspect and audit existing data first

Use the complete study exports under `output_figures/ris/final_evaluation/` and `changed_positions/`; retain the signed/near-Bob/colocated historical studies as separate settings, never pool them. Ensure Git LFS JSON is materialized before parsing. Check `complete`, run identities, seeds, configs, source hashes, history/action lengths and phase labels. If evidence is missing or mismatched, record that before making claims.

Create a reproducible analysis script under `scripts/` that reads existing artifacts without changing them. Save NEW outputs under `output_figures/ris/joint_controller_audit/`. Report at least:

1. **Action coverage:** unique full joint actions sampled, fraction of available actions sampled, counts over time, repeated-action concentration, weight-vector coverage and per-q visit counts. Compare fixed/no-RIS coverage on their respective 625-action spaces. Training observations are not a direct log of epsilon decisions: do not infer exact random/greedy choices without instrumentation.
2. **RIS selections:** q distributions for all training slots, final 500 training slots and frozen evaluation; switching frequency, per-seed breakdown and any tendency to remain off/neutral or choose inferior patterns. Report discrete q from observations/encoding consistently. A correlation between q and performance is not a counterfactual causal estimate.
3. **Per-action performance:** recorded secrecy, BER, original cost and utility; best observed reward/rate; final/frozen selected actions and their metrics. Distinguish secrecy-optimal from reward-optimal: the controller optimizes utility, not secrecy alone.
4. **Reference gaps:** inspect `discrete_reference` fields in each run and independently recompute representative references using RISEnvironment for the same geometry, energy interpretation, noise and optional QoS settings. Compare achieved utility to exact finite-grid maximum utility; secrecy to maximum secrecy only as a separately labeled target. Reference enumeration is NOT a continuous global optimum and must NOT be fed to training.
5. **Fixed-action feasibility:** evaluate the fixed-RIS controller's final w,q=1 action in the joint environment with identical settings and show it is feasible and yields the same metrics. Because the joint action space contains q=1, its exact-grid maximum utility should be at least the fixed-q maximum. Assert/test this invariant; if it fails, investigate model/config mismatches before any long run.
6. **Paired comparisons:** recompute same-seed differences and 95% seed-level intervals for evaluation utility, secrecy and jammer cost, not only secrecy. Report Bob/secrecy outage thresholds explicitly. Static repeated slots are not independent statistical replicates. No difference is not equivalence.
7. **Algorithm diagnostics:** inspect actual CNN/DND update, empty-dictionary behavior, argmax ties, Gaussian normalization and input/history scaling for possible issues. Saved actions cannot prove what every unsaved Q-value or CNN state was. Do not claim to inspect missing trained checkpoints. If new runs need DND occupancy/epsilon decision/learning-loss instrumentation, add minimal passive logging consistently across schemes and document it.

Save `supervisor_package/JOINT_CONTROLLER_AUDIT.md` with traceable tables, actual config and provenance, representative action examples, reference gaps and clearly separated observations/hypotheses. State whether apparent underperformance concerns reward, secrecy, or both. If a real bug is found, write a meaningful regression test, fix it with documented scope and keep old results labeled pre-fix. Do not silently compare pre-fix and post-fix studies as matched runs.

## Stage B — controlled budget experiment

After Stage A, implement a small dedicated runner (suggested `simulations/sim_training_budget_study.py`) using existing study infrastructure. Predeclare its config in a JSON/YAML/Markdown manifest before full execution.

Primary matrix:

- Scenario: existing nominal room and receiver coordinates, unchanged RIS geometry/codebook.
- Model: `paper`; primary interpretation: explicit `energy_model=l1`. Preserve literal signed energy as a separate interpretation, not the same reward. This task is a budget experiment, not another author-curve fitting exercise.
- Schemes: no RIS/FJ DRL, fixed q=1 RIS/FJ DRL and joint RIS/FJ DRL.
- Seeds: 42–51 for ALL schemes and budgets.
- Training budgets: 2,000, 5,000 and 10,000 slots.
- Frozen evaluation: 1,000 slots for each budget checkpoint, epsilon-free/no updates, explicit fresh-episode history initialization.
- Same architecture/input side, physical power/noise, reward coefficients, action quantization and seed protocol across matched comparisons. Reward remains secrecy −3.5*BER −0.4*cost, optional QoS penalty off in this primary matrix. Analyze provisional Bob outage at BER >1e-3 and >1e-4, secrecy outage at rate <0.1; do not change the reward just to meet these thresholds.

Choose and document ONE consistent budget protocol: independent training from seed initialization for each budget, or checkpoints from one training trajectory. Independent runs are simplest to interpret. Checkpoint evaluation must not mutate the ongoing training environment, RNG state, history, replay buffers, network mode or memory: use a true independent evaluation copy/checkpoint and test state invariance if choosing that optimization. Existing `evaluate()` resets the shared environment, so do not insert it mid-training and assume continuation is unchanged.

Do not reuse historical 2,000-slot data unless you verify identical source/settings/protocol and explicitly label reuse; otherwise run a fresh matched baseline. Do not retrain only joint while presenting fixed historical runs as a fully matched new matrix. Training budget means all schemes get that many slots; also report wall-clock time because computational cost differs.

First run a tiny smoke matrix using separate output paths to validate phase separation, per-seed identity, action replay, export and restart behavior. Then execute full runs under NEW `output_figures/ris/training_budget_study/` subdirectories. Keep `complete=false` until the declared matrix is finished. Preserve completed-run checkpoints and support restart without duplication; validate existing settings/source identity before skipping completed work. Do not overwrite historical experiments or lose finished runs when interrupted.

Export per-run training and evaluation raw metrics/actions, direct/reflected/effective gains or reproducible references to them, minimal action/DND diagnostics, timing and source/config hashes. Serialize trained CNN, DND and required preprocessing/config state if feasible using a documented local format, with a meaningful round-trip evaluation test; do not claim replayed histories alone can reconstruct a trained policy.

## Stage C — compare and report

Produce machine-generated tables and standalone PNG/PDF scientific plots:

- Frozen utility and secrecy versus training budget, with individual seeds and seed-level uncertainty.
- Paired joint-minus-fixed and joint-minus-no-RIS differences at each budget.
- Exact finite-grid utility gap versus budget, separately from secrecy-rate gap.
- Action coverage, q selection and runtime/sample-efficiency summaries.
- BER and declared outage metrics without interpreting float underflow as hardware reliability.

Report adverse and null results. If joint still does not beat fixed, say so. Do not keep changing seeds/hyperparameters or extending training until significance appears. Multiple budgets/comparisons are exploratory unless a primary comparison/multiplicity method is declared; label unadjusted 95% intervals appropriately. The declared primary question can be the nominal L1 10,000-slot joint-minus-fixed evaluation utility difference, with secrecy and shorter budgets secondary; state this before looking at new results.

Use the audit and experiment to recommend a bounded next research step: more useful action structure, investigation of learning behavior, robustness tests, or an honest comparative-evaluation framing. Do not claim algorithmic novelty just from combining existing components.

## Completion and user communication

Update ANTIGRAVITY_STATUS.md with real stage/progress and completed/pending run counts. Update Agent.MD with final findings and commands, not competing specifications in AGENTS.md.

Required final report: `supervisor_package/TRAINING_BUDGET_COMPLETION_REPORT.md`, including:

- Simple Bangla summary of the question, actual findings and what remains uncertain.
- Stage A evidence and any confirmed bug/fix versus hypotheses.
- Declared protocol, completed/pending matrix, exact commands, run timing, source hashes and output paths.
- Tests actually executed, expected versus actual acceptance, and any blocker.
- New matched results, paired statistics, reward/secrecy distinction and suggested paper scope.
- Reproduction instructions and what is required to resume if long work remains.

No estimate or plan is an executed result. If IDE/tool limits stop the task, preserve checkpoints and write a clear partial handoff. Do not call the full matrix complete prematurely. Continue authorized work without asking the user to run routine commands. Finish with the actual audit/report links in the IDE chat.

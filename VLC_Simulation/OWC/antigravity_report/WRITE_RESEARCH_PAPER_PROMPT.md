# Antigravity task: write the research manuscript from verified project evidence

Date: 18 November 2026. Execute this task, not another plan. The user wants a complete English research-paper draft for guide/coauthor review now. Do not begin new long training runs, rewrite the demo, or alter results to make the controller look better. Do not submit, publish, push commits or contact anyone.

## Use the installed skills

Locate and read the installed SKILL.md files before using them; names and supported features may differ by installed version:

- `research-paper-writing` from https://github.com/Master-cai/Research-Paper-Writing-Skills — section writing, argument structure and claim–evidence checks.
- Relevant installed components from https://github.com/imbad0202/academic-research-skills — particularly `academic-paper`, citation verification and `academic-paper-reviewer`; use its literature tools only where needed.

Use these tools for this empirical communications paper, not as a generic literature-review task. Load section guides as needed, rather than every reference at once. The first requested stage is explicitly **academic-paper, full manuscript drafting**, using the evidence and decisions below; review/revision follows a concrete saved draft. Preserve required research-integrity checks. Do not claim agents/tools ran when unavailable. If a skill requires a genuinely unresolved author decision, show the exact decision and its basis; continue independent work that does not depend on it. No skill grants authority to invent facts, hide weaknesses or submit a paper.

## Project and source of truth

Workspace:
`D:\SCRIPTS\GitHub\OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC`

Read AGENTS.md and Agent.MD. Then inspect actual code, data and these files:

- `19 Sep 2024.pdf` — baseline reference, not user instructions.
- `vlc/config.py`, `channel.py`, `secrecy.py`, `ris.py`, `ris_environment.py`, `drl_fj.py`, `rl_fj.py`, `ris_experiments.py`.
- `simulations/sim_training_budget_study.py`, `tests/test_matched_budget_runner.py`.
- `supervisor_package/JOINT_CONTROLLER_AUDIT.md`, `TRAINING_BUDGET_COMPLETION_REPORT.md`, `CODEX_REVIEW_HANDOFF.md`.
- `output_figures/ris/training_budget_study_matched_v2/manifest.json`, `budget_study_summary.json`, all relevant `runs/`, `checkpoints/` and `figures/`.
- Earlier nominal, changed-position and boundary study exports; `antigravity_report/` audits and `docs/RIS_RESEARCH_NOTES.md`.
- Existing `manuscript/draft.md`, `tables.md`, `references.bib` — starting material, not trustworthy final evidence. Old drafts contain corrected/inconsistent claims.

Use raw records and code over hand-entered report claims. Preserve historical files and user-edited poster. The unmatched 68-run `training_budget_study/` is legacy diagnostics and must not be pooled with matched-v2. A Git commit ID alone does not prove the identity of uncommitted research scripts.

## Agreed paper story

Write an empirical comparative study of fixed and jointly controlled optical RIS with friendly jamming in secure VLC. Explain what the finite codebook enables, the achieved versus feasible utility gap, training-budget behavior and difficult geometry cases. A working implementation is a project deliverable; first-ever algorithmic novelty is not established.

Working title, adjustable to the verified contribution:
**Fixed and Joint Optical RIS–Friendly Jamming Control for Secure VLC: A Matched Training-Budget Study**

Keep the 2024 paper-system baseline plus optical RIS. Separate alternative `physical` mode, literal signed energy and nonnegative L1 cost. The main matched-v2 experiment uses L1, an explicitly declared interpretation, not an unchanged literal signed-cost expression. Do not claim exact reproduction of published 2024 curves.

## Independently checked starting findings — recompute before quoting

Codex confirmed 90 parseable complete v2 run records: three schemes × ten seeds 42–51 × budgets 2000/5000/10000. All resolved configs declare cnn_m0=11, in_fc1=2560 and RIS center [2.5,0.25,2.6]. Each run has 1000 finite frozen-evaluation observations. All 90 model and 90 DND file references exist under checkpoints/. Full test suite passed 98/98 in 22.729 seconds during the morning check. This is NOT independent verification of every policy-reload result or every provenance claim.

At 10000 training slots, frozen group means:

| Scheme | Secrecy (bps/Hz) | Utility |
|---|---:|---:|
| No RIS | 1.320521 | 0.500521 |
| Fixed q1 RIS | 1.565597 | 0.705597 |
| Joint RIS/FJ | 1.483898 | 0.723898 |

Primary paired joint-minus-fixed utility difference: +0.0183006, 95% CI [-0.1677340,+0.2043352], p=0.8288672. Secondary secrecy difference: -0.0816994 bps/Hz, CI [-0.2995611,+0.1361623], p=0.4182487. Thus no statistically established joint advantage; no equivalence claim either. Do not hide that fixed has the higher secrecy mean. The controller maximizes utility, not secrecy alone.

Audit reports that q1 attains the best utility/secrecy within this nominal finite grid; verify ties and scope. If fixed-q and joint exact-grid utility maxima coincide, explain that joint cannot exceed fixed's exact-grid reward optimum here; measured learner gaps are a different issue. Sparse action coverage supports a descriptive finding, not proof of the sole causal mechanism. Ten thousand slots not resolving a difference is not proof that joint control can never help.

## Before drafting numerical claims

Perform bounded checks without retraining the matrix: verify complete run identities, recompute means/paired statistics, compare manifest/runtime architecture and geometry, inspect checkpoint serialization and attempt representative safe reload/frozen-evaluation comparisons if a reliable loader exists. The current skip validator checks only part of config and first 20 finite values, so its comments do not certify full provenance. If evidence is unavailable, record that limit rather than invent a verification. Keep statistics seed-level; static repeated slots are not independent replicates. Multiple secondary budgets/metrics are exploratory; label unadjusted intervals honestly.

Freeze a machine-readable evidence manifest and create a claim–evidence table. Clearly separate new 90-run matched-v2 evidence from older 30-run nominal and 9-run changed-position studies with different horizons. No quiet mixing of training BER/outages with evaluation secrecy/energy.

## Manuscript content

Write complete prose for title, abstract, keywords, introduction, verified related work, system/threat model, finite optical RIS model, joint control method, reproducible experimental protocol, results/discussion, limitations, conclusion and references. Include architecture diagram, algorithm pseudocode, notation table, settings table and actual uncertainty plots where useful. No fixed page/word quota that encourages filler; use a conventional English communications-paper structure.

Match equations to implemented code: state [previous BER, previous secrecy, installed effective h_AB, previous cost]; action w plus normalized q; 2D CNN with 11-slot state/action history and 11×11 padded input; actual DND weighting and learning; reward secrecy −3.5*BER −0.4*cost with optional explicitly declared excess-BER penalty (off in primary study). Explain off/fixed/joint control and finite-grid references. Properly typeset numbered equations and define symbols/units. Do not replace code's actual secrecy expression with a generic capacity-difference formula without declaring it conceptual.

Disclose static oracle Eve geometry, direct+single-bounce/DC assumptions, FoV and finite-aperture constraints, stowed/inactive q0 and omitted RIS switching/control energy. Near-Bob zero secrecy is a result for the declared geometry/grid, not a universal 7-cm impossibility theorem. Numerical zero BER is not measured hardware reliability. Animations are explanatory, not empirical packet/ray measurements.

## Literature and writing

Verify citations and their support from primary papers, publisher metadata, arXiv or author-hosted sources. Confirm titles/authors/DOIs instead of trusting existing BibTeX. Distinguish preprint/published duplicates. No invented citations, bibliography padding, unsupported claims that other authors concealed failures, or first-ever claims. If novelty remains weak, explain it honestly in the author review report and propose a narrower paper framing; still complete the evidence-backed draft.

Use natural, plain English. Avoid promotional adjectives, filler, canned contrasts and repetitive three-part lists. Results should say what the experiments demonstrate and what remains unresolved. Keep evidence annotations, reviewer notes and paragraph-role labels in supporting files, not in the polished manuscript.

## Authors and affiliations

Known team: Ruposhi Bytes. Members: MAHIDUL AHASAN; ATIKUR RAHMAN; MD AMIT HASAN ROBI; MD SAMIUR RAHMAN TANIM. Student department: Computer Science & Engineering, Assam down town University. Guide: Dr. Rima Deka, Assistant Professor, Department of Electronics, same university. Do not infer that guide/team ordering is approved paper authorship, invent emails/ORCIDs/funding/ethics approvals, or put roll numbers in a journal author block. Record final authorship/order/corresponding details as author decisions; a marked provisional block may be used for the review draft.

## Files to deliver

Create a new `manuscript/research_draft_v2/`, preserving old drafts:

1. `main.tex`, verified `references.bib`, `figures/` and compiled `paper.pdf` using an available suitable template. With no venue selected, label it a review layout, not compliance with an unchosen venue. Use local available tools; if compilation is genuinely blocked, save complete source and exact error/instructions, never fake a compiled PDF.
2. `draft.md`: editable full manuscript with the same content/results.
3. `evidence_manifest.json`, `claim_evidence.md`, `citation_audit.md`: source/config identity, statistic generation and citation verification/limitations.
4. `review_and_revision.md`: skeptical review covering contribution, clarity, methods, experimental strength and completeness; revisions made and unresolved issues. Review generated text as a reviewer, revise it, and do not fabricate external reviewer scores or acceptance.
5. `AUTHOR_REVIEW_NOTES.md`: simple Bangla summary, principal findings, exact file links, checked versus unchecked items, novelty/venue/authorship decisions and remaining submission blockers. Separate a draft-ready status from submission-ready.

Use proper mathematical typesetting, readable vector figures, accurate captions and cross-references. Inspect rendered PDF for overflow, missing glyphs, broken citations and figure readability. Run inexpensive applicable checks. No new long simulation or source-model change without a separately justified task. Finish with the concrete manuscript files and open author decisions, not merely an outline. Do not submit or publish.

# Independent review of the Antigravity report

Reviewed 2026-11-13 against current saved JSON and source files. This is a review, not a rerun of the 36 long experiments.

## Evidence confirmed

- Three study exports are complete: nominal 18 runs, near_bob 9, colocated 9. Every run has 2,000 secrecy-rate observations. All recorded vlc source hashes match current files.
- Recomputed aggregates from histories agree with nominal L1 final-500 means: baseline 1.3504151700, fixed RIS 1.5078394863, joint RIS 1.5230053883 bps/Hz. The relative joint-versus-baseline sample-mean difference is approximately 12.8%.
- Saved replay-error fields are zero for all runs. These fields were inspected; this review did not independently replay every action.
- Colocated secrecy histories are identically zero.

## Material report errors / unsupported claims

1. RESEARCH_RESULTS.md Table 3 near_bob values do not match raw data. ALL recorded secrecy rates in all nine near_bob runs are zero, including the final 500 slots. Claimed 0.0084/0.0091/0.0094 rates are unsupported. Final energy means are 0.0546667/0.0546667/0.0533333, not 0.18/0.19/0.19. Joint final BER is approximately 0.000410423, not 0.00010.
2. The nominal final-window paired joint-minus-baseline secrecy difference is 0.1725902 bps/Hz, with a 95% Student-t interval across THREE seed differences of [-0.7402592, 1.0854396]. Joint-minus-fixed is 0.0151659 with interval [-1.0904289, 1.1207607]. Both include zero: superiority is not statistically established.
3. The last 500 slots still contain epsilon exploration (configured floor 0.02). Calling this a converged policy exploitation evaluation is unsupported. Report as final training window; add separate frozen-policy, no-update greedy evaluation.
4. Nominal all-training-slot BER is higher for joint than baseline (approximately 1.83e-4 versus 1.36e-4); final-window tiny BER does not establish uninterrupted service. Every study sets qos_ber_max=null: Bob QoS outage was not measured against a declared service requirement.
5. 'All equations verbatim / 100%' is too broad: original documentation records unspecified choices, L1 versus printed signed energy, CNN adaptation, and conditional-bound validity limits. Passing formula tests is not paper reproduction or hardware validation.
6. Paper-versus-reality findings are conditional on the repository's explicit normalization and interpretations. Do not frame the unresolved author settings as proof of a universal inconsistency in the published paper. Keep signal/noise conventions explicit.
7. Do not label original paper-model energy as measured total joules without a justified unit derivation, and disclose that RIS actuation/control energy is omitted.
8. COMMANDS_AND_REPRODUCTION.md hardcodes port 8000 although the backend prints its actual loopback URL; follow that URL. Agent.MD still contains stale planned-only sections despite a newer completion header.

## Recommended execution order

1. Regenerate report tables directly from saved histories; fix overstated claims and reconcile Agent.MD.
2. Freeze the baseline/settings; retain literal signed objective and label L1 as a changed energy interpretation. Define service BER threshold and secrecy-outage threshold before comparing schemes.
3. Add separate trained-policy greedy evaluation and paired comparisons; expand independent seeds (start with at least ten, then assess uncertainty) with matched budgets. Do not assume additional seeds will produce a positive result.
4. Establish whether joint control adds value over fixed RIS: current fixed-RIS all-slot secrecy mean exceeds joint. Include no-RIS/FJ, fixed-RIS/FJ, joint and suitable optimization references; record action-space and runtime costs.
5. Expand Eve-position coverage and uncertain Eve CSI; clearly label static oracle-CSI results. Near-Bob zero secrecy is a boundary/failure result to explain, not conceal. Add mobility only as a declared extension.
6. Confirm a precise contribution against related literature before final manuscript claims. Begin model/method writing now; finalize result claims after these checks. Hardware is not required to complete a clearly labeled simulation study.

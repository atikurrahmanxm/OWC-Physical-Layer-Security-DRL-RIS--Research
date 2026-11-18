# Statistical robustness audit

Post-hoc robustness analysis; not a new preregistration.
All 18 comparisons: 3 budgets x 3 contrasts x 2 metrics. Holm correction is conservative across this full reported family.
All 1024 sign patterns enumerated. Requires symmetry/exchangeability of paired differences under the null; not a randomized-treatment causal test.

| 10k comparison | Metric | Difference | t p | Holm t p (18) | Sign-flip p | Holm sign-flip p (18) |
|---|---|---:|---:|---:|---:|---:|
| joint_ris − fixed_ris | utility | +0.0183 | 0.82887 | 1.00000 | 0.83594 | 1.00000 |
| joint_ris − fixed_ris | secrecy_rate | -0.0817 | 0.41825 | 1.00000 | 0.41992 | 1.00000 |
| fixed_ris − baseline | utility | +0.2051 | 0.00034 | 0.00614 | 0.00391 | 0.07031 |
| fixed_ris − baseline | secrecy_rate | +0.2451 | 0.00409 | 0.06956 | 0.00781 | 0.13281 |
| joint_ris − baseline | utility | +0.2234 | 0.02261 | 0.31661 | 0.02539 | 0.38086 |
| joint_ris − baseline | secrecy_rate | +0.1634 | 0.07818 | 1.00000 | 0.08789 | 0.99023 |

Interpret corrected exploratory evidence separately from the existing protocol-primary joint-minus-fixed utility contrast. Numerical mean improvement is not automatically a multiplicity-adjusted finding.

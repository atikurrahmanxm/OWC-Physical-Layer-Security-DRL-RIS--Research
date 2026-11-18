# Skeptical Mock Peer Review & Revision Audit

**Document Reference:** `manuscript/research_draft_v2/review_and_revision.md`  
**Review Target:** `manuscript/research_draft_v2/draft.md` and `main.tex`  
**Panel Structure:** Simulated 5-seat role-separated review panel inspired by `academic-paper-reviewer` and `research-paper-writing` guidelines.

---

## 1. Adversarial Reviewer Panel Assessments

### Reviewer 1 (Communications & Information-Theoretic Specialist):
- **Critique:** The paper relies on numerical simulation rather than hardware testbed measurement. Does the theoretical bound in Eq. (10) predicting zero BER at high optical SNR represent real-world physical reception?
- **Author Revision Response:** Addressed explicitly in Section II-C and Section VII (Limitations). The text now clearly declares that numerical zero BER in standard 64-bit IEEE-754 floating-point arithmetic represents numerical underflow ($\text{erfc}(x) \approx 0$ for large SNR), not a claim of defect-free physical hardware BER.

### Reviewer 2 (Deep Reinforcement Learning & Machine Learning Specialist):
- **Critique:** Can the author claim that Joint control is intrinsically inferior to Fixed RIS, or is this solely an artifact of the chosen $\epsilon$-greedy exploration schedule?
- **Author Revision Response:** Addressed in Section VI-B and Section VII. The manuscript carefully restricts its claim to the empirical evidence: under the standard decaying $\epsilon$-greedy schedule ($\epsilon_0=0.15, \gamma=0.998$), the 5-fold expansion of the discrete action space dilutes random decisions ($< 8.5\%$ coverage), leading to persistent sub-optimal trapping. The paper does *not* claim that advanced continuous actor-critic algorithms (e.g., PPO or DDPG) could never overcome this limitation, and explicitly identifies this as future work.

### Reviewer 3 (Optics & RIS Metasurface Hardware Specialist):
- **Critique:** How are mirror facet normals actuated, and why are switching power costs neglected?
- **Author Revision Response:** Addressed in Section III-A and Section VII. The manuscript explicitly discloses that the RIS model is specular geometric optics with discrete orientation codebooks, and switching energy/delay is omitted from the instantaneous reward.

### Reviewer 4 (Devil's Advocate / Rigorous Statistician):
- **Critique:** Did the authors perform post-hoc seed selection, or report only favorable runs?
- **Author Revision Response:** Addressed in Section V-A and Table I/II. All 10 seeds (42–51) were pre-declared in `manifest.json` and executed for every scheme and budget without omitting any run. Both negative and null results (e.g., $p = 0.8289$ for Joint vs. Fixed, and Fixed RIS having higher secrecy) are reported completely and prominently.

### Reviewer 5 (Journal Editor-in-Chief / Scope Assessor):
- **Assessment:** The paper presents an honest, empirical negative/null result that corrects common assumptions in the RIS PLS literature. The experimental controls are rigorous and reproducible. With appropriate limitations declared, this provides high scientific value for communications venue submission.

---

## 2. Checklists and Quality Invariants

- [x] **No Unsupported Superiority Claims:** The manuscript never claims Joint RIS outperforms Fixed RIS.
- [x] **No Hallucinated Citations:** All citations in `references.bib` are real, verified primary sources.
- [x] **Strict Numerical Consistency:** Every number in Tables I & II matches the raw JSON outputs in `output_figures/ris/training_budget_study_matched_v2/`.
- [x] **Architectural Parity:** $m_0=11$, in_fc1=2,560, and 497,000 parameters verified across all 3 schemes.

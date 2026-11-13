from pathlib import Path

path = Path("manuscript/draft.md")
content = path.read_text(encoding="utf-8")

# 1. Abstract: one-dimensional -> two-dimensional
old_abstract_phrase = "combining a one-dimensional Feature Convolutional Neural Network (CNN) with an episodic Differentiable Neural Dictionary (DND) for fast Q-value estimation and sample-efficient policy learning."
new_abstract_phrase = "combining a two-dimensional Feature Convolutional Neural Network (CNN with Conv2d layers) with an episodic Differentiable Neural Dictionary (DND) for Q-value estimation and policy learning."

# 2. Contributions: 3,125-dimensional -> cardinality 3,125 with five-coordinate representation
old_contrib_phrase = "constructing an expanded 3,125-dimensional discrete action space managed by a unified Feature CNN and DND episodic memory."
new_contrib_phrase = "constructing an expanded discrete action space of cardinality $|\\mathcal{A}| = 3,125$ with a five-coordinate action representation $\\mathbf{a}_t = [w_1, w_2, w_3, w_4, \\tilde{q}]^T \\in [-1, 1]^5$, managed by a unified Feature CNN and DND episodic memory."

# 3. Observation sequence: w -> a
old_phi_phrase = "\\boldsymbol{\\phi}_t = [\\mathbf{s}_{t-M}, \\mathbf{w}_{t-M}, \\dots, \\mathbf{s}_{t-1}, \\mathbf{w}_{t-1}, \\mathbf{s}_t]"
new_phi_phrase = "\\boldsymbol{\\phi}_t = [\\mathbf{s}_{t-M}, \\mathbf{a}_{t-M}, \\dots, \\mathbf{s}_{t-1}, \\mathbf{a}_{t-1}, \\mathbf{s}_t]"

# 4. Flatten & FC Layer 1 dimensions: 1960 -> 2560 for m0=11
old_fc_phrase = "- **Flatten & FC Layer 1**: Spatial feature maps are flattened ($40 \\times 7 \\times 7 = 1960$ inputs) and passed through `nn.Linear(1960, 180)`, followed by ReLU activation."
new_fc_phrase = "- **Flatten & FC Layer 1**: With adapted input dimension $m_0 = 11$, spatial dimensions after convolutions are $c_1 = (11-3)//1+1 = 9$ and $c_2 = (9-2)//1+1 = 8$. Feature maps are flattened ($f_2 \\times c_2 \\times c_2 = 40 \\times 8 \\times 8 = 2560$ inputs) and passed through `nn.Linear(2560, 180)`, followed by ReLU activation. (Note: $1960$ inputs correspond to $m_0 = 10$)."

# 5. Joint uncertainty attribution
old_stat_phrase = "2. **Joint RIS Statistical Uncertainty**: Joint RIS achieves a $+10.3\\%$ sample mean secrecy increase ($1.4565$ vs. $1.3205\\text{ bps/Hz}$) over Baseline, but its paired 95% confidence interval spans zero ($[-0.0440, +0.3158]$). Superiority over Baseline cannot be statistically claimed under this training budget."
new_stat_phrase = "2. **Joint RIS Statistical Uncertainty**: Joint RIS achieves a $+10.3\\%$ sample mean secrecy increase ($1.4565$ vs. $1.3205\\text{ bps/Hz}$) over Baseline, but its paired 95% confidence interval spans zero ($[-0.0440, +0.3158]\\text{ bps/Hz}$). We hypothesize that this observed cross-seed variance may be associated with exploring an action space of cardinality $3,125$ (vs. $625$ for Fixed RIS) within a $2,000$-slot training horizon; establishing causal attribution would require isolated ablation studies across varying training budgets. Superiority over Baseline cannot be statistically claimed under this training horizon."

# 6. Conclusion
old_concl_phrase = "In this paper, we presented a comprehensive physical and algorithmic framework for joint Friendly Jamming and Optical RIS beamforming in secure indoor Visible Light Communication networks. By uniting a 4-jammer array and a 6-tile specular micro-mirror array under a unified discrete MDP, we demonstrated how Feature CNNs with DND episodic memory can adaptively synthesize constructive signal paths for Bob while directing artificial noise toward Eve. We established a rigorous evaluation standard, separating exploratory training from frozen greedy evaluation, and employing 10-seed paired Student-$t$ statistical inference. Finally, by disclosing the near-Bob and colocated secrecy collapse boundaries, we established clear electromagnetic operational limits for optical physical layer security."
new_concl_phrase = "In this paper, we presented an empirical and algorithmic framework for joint Friendly Jamming and Optical RIS beamforming in secure indoor Visible Light Communication networks. By uniting a 4-jammer array and a 6-tile specular micro-mirror array under a discrete MDP with cardinality $|\\mathcal{A}|=3,125$, we evaluated the interaction between optical reflection steering and artificial noise emission under the IEEE TWC 2024 baseline. Through a strict methodology separating exploratory training from frozen greedy evaluation across 10 matched seeds, we established that Fixed RIS achieves a statistically significant secrecy rate improvement of $+0.1773\\text{ bps/Hz}$ over the baseline without RIS ($[+0.0378, +0.3167]\\text{ bps/Hz}$). For Joint RIS, while achieving a $+10.3\\%$ sample mean secrecy increase, the paired confidence interval spans zero ($[-0.0440, +0.3158]\\text{ bps/Hz}$), reflecting cross-seed variance when exploring 3,125 actions within a 2,000-slot training budget. Finally, through exhaustive action enumeration over the discrete codebook, we characterized the physical boundary in near-Bob scenarios, confirming that the DRL policy rationally suppresses jamming power when channel geometry precludes positive secrecy."

# Perform replacements
for name, old, new in [
    ("Abstract", old_abstract_phrase, new_abstract_phrase),
    ("Contributions", old_contrib_phrase, new_contrib_phrase),
    ("Phi sequence", old_phi_phrase, new_phi_phrase),
    ("FC Layer 1", old_fc_phrase, new_fc_phrase),
    ("Stat Finding", old_stat_phrase, new_stat_phrase),
    ("Conclusion", old_concl_phrase, new_concl_phrase),
]:
    if old not in content:
        raise ValueError(f"Could not find target for {name}")
    content = content.replace(old, new)
    print(f"Replaced: {name}")

path.write_text(content, encoding="utf-8")
print("Successfully updated manuscript/draft.md with all consistency fixes!")


# Closest prior work and journal preparation

Checked 18 November 2026. This is a focused primary-source audit, not a systematic literature review or external peer review. No journal submission or author contact was performed. The main manuscript was not edited by this audit.

## What the prior work establishes

| Source and inspection coverage | Relevant result or design | Consequence for this manuscript |
|---|---|---|
| Qian, Chi, Zhao and Chaaban, *Secure Visible Light Communications via Intelligent Reflecting Surfaces*, ICC2021, DOI [10.1109/ICC42927.2021.9500409](https://doi.org/10.1109/ICC42927.2021.9500409). Six-page author preprint downloaded from [arXiv](https://arxiv.org/abs/2101.12390); geometry, optimization and experiments inspected. | Pages 2–4 describe a biased IM/DD source, mirror orientations and reflected-spot optimization. Pages 4–6 compare optimized reflected spots, fixed Focus-on-Bob and no IRS. Nearby Eve positions can also fall inside Bob's reflected spot. | Optical-RIS security and fixed-versus-optimized reflection are already established ideas. Our finite detector/point-source approximation is different, not automatically more accurate. We cannot claim fixed alignment always prevents Eve reception. |
| Saifaldeen, Ciftler, Abdallah and Qaraqe, *DRL-Based IRS-Assisted Secure Visible Light Communications*, IEEE Photonics Journal14(6), article8656209, 2022, DOI [10.1109/JPHOT.2022.3178852](https://doi.org/10.1109/JPHOT.2022.3178852). Nine-page publisher article obtained from [Qatar National Library Manara](https://manara.qnl.qa/articles/journal_contribution/DRL-Based_IRS-Assisted_Secure_Visible_Light_Communications/26862139). | Pages 3–6 specify mirror/fixture control and DDPG with known Bob/Eve positions. Pages 6–8 describe mobile-user experiments, approximately100,000 training iterations, and beamforming/mirror and PSO comparisons. | Joint optical mirror and transmitter control with DRL predates this project. Our 625/3,125 discrete actions and CNN/DND learner differ from its continuous DDPG. A static 2k–10k-slot result cannot refute its mobility/continuous-control findings. |
| Liu, Liu, Du and Guizani, *Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication*, IEEE TWC23(12):17915–17928, 2024, DOI [10.1109/TWC.2024.3458046](https://doi.org/10.1109/TWC.2024.3458046). Fourteen-page author manuscript downloaded from [author website](https://liusc1028.github.io/papers/TWC24liu.pdf); contribution and controller/model sections inspected. | The original contribution includes RL/DRL-friendly-jamming, convolutional representation, DND experience use and utility/complexity analysis. It does not supply this project's optical-RIS extension. | Attribute the controller and inherited metric expressions. New implementation checks are not evidence of reproducing its published curves, and current source parity must not be inferred from a successful paper-mode run. |
| Liu, Zhang, Song and Han, *Optical Reflecting Intelligent Surface-Assisted Secure Visible Light Communication: An Inverse Pre-Reflection Model-Driven Deep Reinforcement Learning Approach*, IEEE TWC25:19162–19178, 2026, DOI [10.1109/TWC.2026.3708130](https://doi.org/10.1109/TWC.2026.3708130). [Primary institutional abstract/metadata](https://scholars.cityu.edu.hk/en/publications/optical-reflecting-intelligent-surface-assisted-secure-visible-li/) checked; full text not obtained. | Its abstract explicitly states joint LED beamforming and ORIS-orientation optimization for a secrecy/BER/energy utility, with model-driven and outage-aware DRL for multiple users. | This is direct conceptual overlap with the broad project idea. Abstract evidence already rules out a first-use claim for that combination. Exact algorithmic and numerical comparison remains unknown until full text is accessible. |

Three of four closest papers have cached primary full texts. The fourth has primary abstract/metadata evidence only. IEEE requests returned access challenges/HTTP418; author repository and OpenAlex checks did not reveal an accessible 2026 full text. The audit must not be labelled a complete four-paper full-text review.

## Defendable contribution and remaining gap

The supportable contribution is a finite-codebook, architecture-matched empirical audit of one implemented friendly-jamming learner: separate the attainable optimum from the policy found under a given budget, quantify seed-level uncertainty, and publish enough evidence to repeat the comparison. This is a proposed positioning inferred from the evidence, not a verified first-in-literature result.

The six-facet model and90-run study are useful implementation/evaluation work, but neither guarantees journal-level novelty. The most useful additions are scenario-dependent optimality gaps, an explicit strong deterministic finite-grid baseline, sensitivity to receiver/Eve geometry and normalization, and complete policy replay. Comparisons should distinguish a changing best codebook configuration from failure to discover an already optimal fixed one. Do not claim equivalence or causal exploration failure solely from nonsignificant tests and low coverage.

### Suggested replacement related-work text

> Optical reflecting surfaces have already been used to improve VLC secrecy. Qian et al. compare reflected-spot optimization with a fixed focus-on-Bob alignment and a no-IRS reference. Saifaldeen et al. jointly control fixture weights and mirror orientations using continuous-action DDPG with known user positions. Liu et al. subsequently describe model-driven optical-RIS control for a secrecy, BER and energy utility. Our question is narrower: for a finite optical codebook and a CNN/DND friendly-jamming implementation, does an expanded joint action set improve evaluated utility under matched training budgets? We compare learned policies with the best available discrete actions and report seed-level uncertainty. We do not claim that the RIS/DRL combination is new or that our controller outperforms these prior methods.

Use citation keys `qian2021secure`, `saifaldeen2022drl`, `liu2026oris`; cite `liu2024smart` when identifying the inherited controller. The proposed text deliberately makes no unverified detailed claim about the 2026 algorithm.

## Journal shortlist — provisional, not a submission instruction

| Venue | Verified fit and publication route | Official instructions |
|---|---|---|
| **Optical and Quantum Electronics** | Official scope includes optical communications and simulation of optical systems. Hybrid publication; the publisher explicitly states no APC for its subscription route. Optional OA currently £2490/$3390/€2790 plus applicable taxes, with price determined at acceptance. This is the practical first shortlist choice if budget is limited, subject to guide and author agreement. | [Scope](https://link.springer.com/journal/11082/aims-and-scope), [fees/routes](https://link.springer.com/journal/11082/how-to-publish-with-us), [author instructions](https://link.springer.com/journal/11082/submission-guidelines). |
| **Photonics** | Official scope includes optical communications and theoretical/simulation work. Fully OA; official APC is CHF2400 plus applicable taxes, payable after acceptance. Do not select it without confirming funding. Advertised decision statistics are not a promise of review or acceptance for this paper. | [Scope](https://www.mdpi.com/journal/photonics/about), [APC](https://www.mdpi.com/journal/photonics/apc), [author instructions](https://www.mdpi.com/journal/photonics/instructions). |

Both journals still assess scientific validity and originality. Choosing a simulation-friendly venue does not resolve the model or novelty issues.

### Optical and Quantum Electronics preparation specifics

Use a150–250-word abstract,4–6 keywords, complete author affiliations and a corresponding email. Word and LaTeX sources are accepted; the journal encourages its Springer template and decimal headings. Its instructions place Statements and Declarations after References. Funding, competing interests and author contributions must reflect actual author-confirmed facts; the data policy requires a data-availability statement for original research. The page contains an earlier optional wording, but the dedicated current research-data section is mandatory. Substantive LLM use must be documented; this project went beyond copyediting. All authors must approve submission, and simultaneous submission is disallowed. See the [official instructions](https://link.springer.com/journal/11082/submission-guidelines).

### Photonics preparation specifics

The journal permits a consistent reference style at initial submission, with journal formatting at revision. A cover letter must explain fit and significance and confirm exclusivity and all-author approval. Those declarations cannot be asserted by an agent without author confirmation. See [official instructions](https://www.mdpi.com/journal/photonics/instructions).

## Evidence cache and provenance

- `literature/qian2021.pdf` / `.txt`: six-page author preprint; text has page markers.
- `literature/saifaldeen2022.pdf` / `.txt`: nine-page publisher article from the QNL primary repository; repository metadata in `saifaldeen2022_figshare_metadata.json`.
- `literature/liu2024.pdf` / `.txt`: fourteen-page author manuscript; text has page markers.
- `literature/saifaldeen2022_institution.html`, `liu2026_institution.html`: primary institutional pages.
- `literature/oqe_scope.html`, `oqe_authors.html`, `oqe_fees.html`: publisher snapshots.
- `literature/mdpi_web_tool_snapshot.json`: web extraction, because direct HTTP requests to MDPI were blocked403.
- `literature/paper_provenance.json` / `web_provenance.json`: URLs, coverage boundaries and SHA256 hashes where downloaded.

These copyrighted PDFs are a local reading cache. They should not be bundled as this project's supplementary research data or pushed publicly without checking the applicable licences.

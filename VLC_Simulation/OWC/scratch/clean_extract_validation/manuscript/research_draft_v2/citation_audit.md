# Citation audit — revised 18 November 2026

This replaces the previous blanket verification claim. The original files are preserved in `../archive_antigravity_2026_11_18/`.

## Retained bibliography

Six entries were checked against DOI registration metadata from the Crossref API. Responses are cached in `verification/`. Titles, author lists, venues, volumes/issues where supplied, years, pages, and DOIs in `references.bib` are generated from those records. The seventh entry was checked against the primary PMLR publication page.

| Key | Primary metadata source | Scope of use |
|---|---|---|
| liu2024smart | https://doi.org/10.1109/TWC.2024.3458046 | Existing baseline and its controller; local paper also available |
| pathak2015visible | https://doi.org/10.1109/COMST.2015.2476474 | General VLC background |
| bloch2008wireless | https://doi.org/10.1109/TIT.2008.921908 | Physical-layer security background |
| qian2021secure | https://doi.org/10.1109/ICC42927.2021.9500409 | Mirror-array secure VLC; author abstract also checked at https://arxiv.org/abs/2101.12390 |
| saifaldeen2022drl | https://doi.org/10.1109/JPHOT.2022.3178852 | Existence of prior DRL/IRS secure VLC; institutional abstract at https://elmi.hbku.edu.qa/en/publications/drl-based-irs-assisted-secure-visible-light-communications/ |
| liu2026oris | https://doi.org/10.1109/TWC.2026.3708130 | Prior model-driven optical-RIS/DRL study; institutional abstract at https://scholars.cityu.edu.hk/en/publications/optical-reflecting-intelligent-surface-assisted-secure-visible-li/ |
| pritzel2017neural | https://proceedings.mlr.press/v70/pritzel17a.html | Neural episodic control background |

Metadata verification is not full-text methodological verification. The prior RIS studies are cited for their stated topic/approach; no numerical superiority comparison with them is made. This was a targeted literature check, not a systematic or exhaustive novelty search.

## Errors corrected or removed

- The 2024 baseline pages were corrected from 18942–18955 to 17915–17928.
- The Pathak survey title was corrected to “Visible Light Communication, Networking, and Sensing: A Survey, Potential and Challenges.”
- The Pritzel author list now includes the full surname Puigdomènech Badia.
- The old Barros entry's DOI `10.1109/ISIT.2006.261612` resolves in Crossref to “Random Binary Fingerprinting Codes for Arbitrarily Sized Coalitions,” not the cited secrecy-capacity paper. That entry was removed; its cached response remains as audit evidence.
- The three old DOIs `10.1109/COMST.2020.2971719`, `10.1109/COMST.2022.3168249`, and `10.1109/MVT.2021.3113880` returned HTTP 404 from Crossref on this check. Their claimed bibliography records were not established and were removed. A failed lookup alone is not proof that no related publication exists.
- The unused Nature DQN citation was removed. Its valid metadata cache is retained but it is not in the final bibliography.

Before submission, authors should read the closest prior RIS papers in full and confirm venue-specific reference requirements.

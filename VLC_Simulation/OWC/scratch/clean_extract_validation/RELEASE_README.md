# Local research reproducibility package

This archive contains the project's code, completed matched-v2 run records, supplementary
diagnostics, evidence logs, and manuscript artifacts. It is not a journal acceptance,
an external deposit, or a replacement for author approval.

## What is included

- The 90 raw architecture-matched paper-mode runs and protocol manifest.
- Recorded whole-90-policy replay evidence (1,000 frozen slots per saved policy).
- Geometry/noise finite-grid sensitivity, zero-shot frozen-policy transfer, and statistical robustness.
- Nine calibrated current-domain 4-PAM/RIS grid files and summary. These are a separate
  diagnostic, not a substitute training dataset or reproduction of the 2024 paper.
- Final manuscript PDF, editable Word, LaTeX, figures, analysis and build scripts.
- Guide handoff and cover-letter draft; these still require author-confirmed facts.

## Saved checkpoints

The 180 saved CNN/DND files are EXCLUDED to keep this archive small. Their expected relative paths, sizes and SHA256 hashes are in RELEASE_CHECKPOINT_INVENTORY.json. Recover those exact artifacts from the authors to rerun saved-policy replay. Recorded full replay logs remain included. Do not call this default archive a self-contained saved-policy rerun bundle.

To make the larger archive from the full local project:

```powershell
python -B scripts/package_research_release.py --include-checkpoints
```

The package manifest records actual included-file hashes. Historical source hashes,
current code identity and previously uncommitted execution state are distinct facts;
the package cannot retroactively establish the original working tree.

## Reproduction

Extract into a clean directory and run commands from that directory. Dependencies
are not vendored. Install `requirements.txt` and `RELEASE_BUILD_REQUIREMENTS.txt`
in a Python environment first, or provision them on an offline machine in advance.
No network is needed for the numerical analyses once dependencies and data exist.
The six published-curve tests require a separately obtained 19 Sep 2024.pdf at
the extracted project root. Discovery skips those tests when the PDF is absent.

```powershell
python -m pip install -r requirements.txt -r RELEASE_BUILD_REQUIREMENTS.txt
python -B -m unittest discover -s tests -v
python -B scripts/release_statistics.py
python -B scripts/run_calibrated_ris_diagnostic.py
```

With the saved checkpoints restored or included:

```powershell
python -B scripts/release_validation.py --phase all
python -B scripts/assemble_release_evidence.py
```

`release_validation.py` replays the 90 saved policies and computes supplementary
geometry analyses; it does not train. Raw outputs and their manifests remain the
reference for claims. Regenerating a diagnostic is separate from historical training.

Build commands from the full project:

```powershell
python -B scripts/create_manuscript_system_figures.py
python -B scripts/build_manuscript_sources.py
python -B scripts/build_manuscript_docx.py
python -B scripts/revise_manuscript_evidence.py
.\.tools\tectonic\tectonic.exe --keep-logs --keep-intermediates manuscript/research_draft_v2/main.tex
python -B scripts/validate_manuscript_build.py
```

Local compiler executables are deliberately not included. Reinstall official
Pandoc/Tectonic into `.tools/`, or compile the LaTeX using an installed TeX distribution.
Word builds use Pandoc and python-docx. The included PDF/Word do not require these tools
to read. Consult the manuscript's author notes for build order and current requirements.

## Author and release decisions

Only the four students are manuscript authors. Dr. Rima Deka is Project Guide.
The corresponding author and all co-authors must confirm affiliations, author order,
contributions, funding/conflicts, AI-use disclosure, exclusivity, and final submission
approval. These declarations are not inferred by this package. A local ZIP is not a
public DOI. The guide selects the journal and approves any publication fee or upload.

Credentials, local tools, Git metadata, unrelated backups, and cached third-party
papers/HTML are excluded. The simple credential pattern scan is an additional guard,
not a guarantee that every possible secret representation can be detected.

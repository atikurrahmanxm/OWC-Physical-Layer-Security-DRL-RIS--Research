"""Prepare a local reproducibility ZIP; never upload or run experiments.

Default excludes trained CNN/DND files but inventories their SHA256 hashes.
Use --include-checkpoints for a larger self-contained policy-replay archive.
Run only after validation, calibrated diagnostics and final manuscript builds.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'manuscript/research_draft_v2'
AUDIT = PAPER / 'release_audit'
STUDY = ROOT / 'output_figures/ris/training_budget_study_matched_v2'
CALIBRATED = ROOT / 'output_figures/ris/calibrated_diagnostic_v1'
TEXT_SUFFIXES = {'.py', '.md', '.json', '.txt', '.log', '.html', '.js', '.toml', '.yaml', '.yml', '.csl'}
DENIED_PARTS = {'.git', '.tools', '.agents', '__pycache__', 'literature', 'anti_backup', 'scratch'}
SECRET_PATTERNS = [
    re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}'),
    re.compile(rb'github_pat_[A-Za-z0-9_]{30,}'),
    re.compile(rb'sk-(?:proj-)?[A-Za-z0-9_-]{24,}'),
    re.compile(rb'AKIA[0-9A-Z]{16}'),
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
]


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def permitted(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    lower = path.name.lower()
    return not (
        path.is_symlink()
        or any(part.lower() in DENIED_PARTS for part in rel.parts)
        or lower.startswith('.env')
        or lower.endswith(('.pem', '.key', '.pfx', '.p12'))
        or any(word in lower for word in ('credentials', 'service-account', 'service_account'))
        or lower == 'baseline_extracted.txt'
    )


def scan_credentials(path: Path) -> None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    tail = b''
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            sample = tail + chunk
            if any(pattern.search(sample) for pattern in SECRET_PATTERNS):
                # Never print a suspected credential or surrounding file text.
                raise ValueError(f'Possible credential in {relative(path)}; review it before packaging.')
            tail = sample[-512:]


def required_inputs() -> tuple[list[Path], list[dict], list[Path]]:
    required = [
        ROOT/'requirements.txt', ROOT/'Agent.MD', ROOT/'AGENTS.md',
        PAPER/'main.pdf', PAPER/'main.docx', PAPER/'main.tex', PAPER/'references.bib',
        PAPER/'main.bbl', PAPER/'BUILD_VALIDATION.json', PAPER/'verified_results.json',
        PAPER/'evidence_manifest.json', PAPER/'results_rows.tex', PAPER/'paired_rows.tex',
        PAPER/'release_statistics_rows.tex', PAPER/'release_geometry_rows.tex', PAPER/'release_calibrated_rows.tex',
        AUDIT/'full_policy_replay.json', AUDIT/'geometry_grid_sensitivity.json',
        AUDIT/'frozen_policy_geometry_transfer.json', AUDIT/'statistical_robustness.json',
        AUDIT/'release_evidence_summary.json', AUDIT/'validation_protocol.json',
        AUDIT/'GUIDE_SUBMISSION_HANDOFF.md', AUDIT/'COVER_LETTER_DRAFT.md',
        AUDIT/'ANTIGRAVITY_UNIT_TESTS.log', AUDIT/'ANTIGRAVITY_TEST_STATUS.md',
        STUDY/'manifest.json', CALIBRATED/'diagnostic_summary.json',
    ]
    required += [PAPER/'figures'/f'{stem}.{ext}' for stem in (
        'fig_system_model', 'fig_control_workflow', 'fig1_budget_convergence',
        'fig2_budget_paired_differences', 'fig3_budget_coverage_and_q',
        'fig4_computational_scaling', 'fig_release_geometry_transfer', 'fig_release_calibrated'
    ) for ext in ('pdf', 'png')]
    missing = [relative(p) for p in required if not p.is_file() or p.stat().st_size == 0]
    if missing:
        raise ValueError('Required final outputs are missing or empty:\n' + '\n'.join(missing))

    records = []
    runs = sorted((STUDY/'runs').glob('run_*.json'))
    expected = {(scheme, seed, budget) for scheme in ('baseline', 'fixed_ris', 'joint_ris')
                for seed in range(42, 52) for budget in (2000, 5000, 10000)}
    if len(runs) != 90:
        raise ValueError(f'Expected 90 raw matched-v2 runs; found {len(runs)}.')
    observed = set()
    for path in runs:
        record = read_json(path)
        key = (record['scheme'], record['seed'], record['budget'])
        if key in observed or not record.get('complete') or record.get('protocol_version') != 2:
            raise ValueError(f'Duplicate, incomplete or non-v2 record: {relative(path)}')
        observed.add(key)
        records.append(record)
    if observed != expected:
        raise ValueError('Raw run identities do not match the complete prespecified 90-run matrix.')

    replay = read_json(AUDIT/'full_policy_replay.json')
    if replay.get('policy_count') != 90 or replay.get('slots_per_policy') != 1000 or not replay.get('all_match'):
        raise ValueError('Whole-90-policy, 1000-slot matching replay has not been recorded as complete.')
    replay_rows = replay.get('records', [])
    if len(replay_rows) != 90 or not all(r.get('metrics_match') and r.get('first_action_match')
                                       and r.get('q_counts_match') for r in replay_rows):
        raise ValueError('Replay summary does not contain 90 passing metric/action/configuration records.')
    replay_files = [AUDIT/'replay_runs'/path.name for path in runs]
    if any(not p.is_file() for p in replay_files):
        raise ValueError('One or more per-policy replay logs are missing.')

    calibrated = read_json(CALIBRATED/'diagnostic_summary.json')
    results = calibrated.get('results', [])
    if len(results) != 9:
        raise ValueError('Expected nine completed calibrated diagnostic cases.')
    grids = []
    for row in results:
        filename = row.get('raw_grid_file', '')
        if not filename or Path(filename).name != filename or Path(filename).suffix != '.npz':
            raise ValueError('Diagnostic summary contains an invalid grid filename.')
        grids.append(CALIBRATED/filename)
    if len(set(grids)) != 9 or any(not p.is_file() or not p.stat().st_size for p in grids):
        raise ValueError('Nine distinct nonempty calibrated NPZ grids are required.')
    return required + runs + replay_files + grids, records, grids


def select_files(required: list[Path]) -> list[Path]:
    selected = set(required)
    selected.update(ROOT/name for name in ('supervisor_package/compact_results.json', 'supervisor_package/figures/fig1_training_curves.png'))
    # Explicit code/data roots avoid copying unrelated backups or personal files.
    for directory in ('vlc', 'simulations', 'scripts', 'tests', 'paper_audit'):
        selected.update(p for p in (ROOT/directory).rglob('*.py') if permitted(p))
    for name in ('README.md', 'RUN.md', 'PHYSICAL_MODEL.md', 'PAPER_REPRODUCTION.md',
                 'run.py', 'main.py', 'app_server.py', 'app_desktop.py',
                 'launch_supervisor_demo.py', 'index.html', 'ris.html',
                 'supervisor_demo.html', 'visualizer.html', 'supervisor_results.json'):
        if (ROOT/name).is_file():
            selected.add(ROOT/name)
    for p in (ROOT/'scripts').glob('*.js'):
        if permitted(p): selected.add(p)
    selected.update(p for p in PAPER.iterdir()
                    if p.is_file() and p.suffix.lower() in {'.md', '.tex', '.bib', '.json', '.bbl', '.log', '.pdf', '.docx'})
    selected.update(p for p in (PAPER/'figures').iterdir()
                    if p.is_file() and p.suffix.lower() in {'.pdf', '.png', '.svg'})
    selected.update(p for p in AUDIT.rglob('*')
                    if p.is_file() and permitted(p) and p.suffix.lower() in {'.md', '.json', '.log', '.tex'})
    # Bibliography metadata and CSL are build inputs, not cached article full texts.
    selected.update(p for p in (PAPER/'verification').glob('*')
                    if p.is_file() and p.suffix.lower() in {'.json', '.csl'})
    for p in selected:
        if not permitted(p):
            raise ValueError(f'A prohibited or symlinked input was selected: {relative(p)}')
    return sorted(selected, key=relative)


def checkpoint_inventory(records: list[dict], included: bool) -> list[dict]:
    inventory = []
    checkpoint_dir = (STUDY/'checkpoints').resolve()
    seen = set()
    for record in records:
        for kind, name in record['checkpoints'].items():
            if Path(name).name != name:
                raise ValueError('Checkpoint records must contain basenames, not external paths.')
            path = checkpoint_dir/name
            if path.is_symlink() or path.resolve().parent != checkpoint_dir or not path.is_file():
                raise ValueError(f'Checkpoint missing or unsafe: {name}')
            if path in seen:
                raise ValueError(f'Checkpoint unexpectedly shared by multiple run records: {name}')
            seen.add(path)
            inventory.append(dict(path=relative(path), kind=kind, bytes=path.stat().st_size,
                                  sha256=sha256(path), included_in_zip=included,
                                  scheme=record['scheme'], seed=record['seed'], budget=record['budget']))
    if len(inventory) != 180:
        raise ValueError(f'Expected 180 CNN/DND checkpoint files; found {len(inventory)}.')
    return inventory


def readme(checkpoints_included: bool) -> str:
    policy = ('The 180 saved CNN/DND files ARE included. Whole-policy replay can be rerun locally.'
              if checkpoints_included else
              'The 180 saved CNN/DND files are EXCLUDED to keep this archive small. Their expected '
              'relative paths, sizes and SHA256 hashes are in RELEASE_CHECKPOINT_INVENTORY.json. '
              'Recover those exact artifacts from the authors to rerun saved-policy replay. '
              'Recorded full replay logs remain included. Do not call this default archive a '
              'self-contained saved-policy rerun bundle.')
    return f'''# Local research reproducibility package

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

{policy}

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
.\\.tools\\tectonic\\tectonic.exe --keep-logs --keep-intermediates manuscript/research_draft_v2/main.tex
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
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--include-checkpoints', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'research_release')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing package archive')
    args = parser.parse_args()
    required, records, _ = required_inputs()
    selected = select_files(required)
    checkpoints = checkpoint_inventory(records, args.include_checkpoints)
    if args.include_checkpoints:
        selected += [ROOT/row['path'] for row in checkpoints]
    selected = sorted(set(selected), key=relative)
    for path in selected:
        scan_credentials(path)
    files = [dict(path=relative(p), bytes=p.stat().st_size, sha256=sha256(p)) for p in selected]
    generated = {
        'RELEASE_README.md': readme(args.include_checkpoints).encode('utf-8'),
        'RELEASE_BUILD_REQUIREMENTS.txt': b'pymupdf>=1.24\nPillow>=10.0\n',
        'RELEASE_CHECKPOINT_INVENTORY.json': json.dumps(checkpoints, indent=2).encode('utf-8'),
    }
    files += [dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
              for name, data in generated.items()]
    replay = read_json(AUDIT/'full_policy_replay.json')
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(), package_kind='local reproducibility ZIP',
                    include_checkpoints=args.include_checkpoints, included_file_count=len(files),
                    included_uncompressed_bytes=sum(row['bytes'] for row in files),
                    checkpoint_count=len(checkpoints),
                    checkpoint_uncompressed_bytes=sum(row['bytes'] for row in checkpoints),
                    recorded_replay=dict(policy_count=replay['policy_count'], slots_per_policy=replay['slots_per_policy'],
                                         all_match=replay['all_match'], compared_metric_values=replay.get('compared_metric_values')),
                    python_version=sys.version, files=files,
                    self_hash_note='The manifest is not self-hashed; the ZIP SHA256 is written beside the ZIP.',
                    excluded=['credentials and private keys', '.tools', '.git', 'third-party full-text/HTML reading cache',
                              'unrelated backups', 'saved checkpoints unless --include-checkpoints'])
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    name = 'RIS_FJ_VLC_DRL_reproducibility' + ('_with_checkpoints' if args.include_checkpoints else '')
    archive = output/(name+'.zip')
    if archive.exists():
        if args.overwrite:
            archive.unlink()
        else:
            raise FileExistsError(f'Refusing to overwrite an existing package: {archive}')
    temporary = output/(name+'.zip.tmp')
    if temporary.exists():
        temporary.unlink()
    manifest_bytes = json.dumps(manifest, indent=2).encode('utf-8')
    with zipfile.ZipFile(temporary, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as zipped:
        for path, row in zip(selected, files[:len(selected)]):
            zipped.write(path, row['path'])
            if sha256(path) != row['sha256']:
                raise RuntimeError(f'Input changed while packaging: {row["path"]}; temporary archive retained for inspection.')
        for filename, content in generated.items():
            zipped.writestr(filename, content)
        zipped.writestr('RELEASE_PACKAGE_MANIFEST.json', manifest_bytes)
    temporary.replace(archive)
    (output/'RELEASE_PACKAGE_MANIFEST.json').write_bytes(manifest_bytes)
    (output/(name+'.zip.sha256')).write_text(sha256(archive)+'  '+archive.name+'\n', encoding='utf-8')
    print(f'Created {archive} ({archive.stat().st_size:,} bytes); {len(files)} inventoried files.')
    print('No upload performed. Author/guide submission declarations still require confirmation.')


if __name__ == '__main__':
    main()

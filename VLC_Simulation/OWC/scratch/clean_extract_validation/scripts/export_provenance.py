"""Export PROVENANCE.json and compact_results.json for supervisor package."""
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = ROOT / "supervisor_package"
PACKAGE_DIR.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    study_summary_path = ROOT / "output_figures" / "ris" / "final_evaluation" / "ris_study_summary.json"
    study_data_path = ROOT / "output_figures" / "ris" / "final_evaluation" / "ris_study_data.json"
    
    # Track critical source files
    source_files = [
        ROOT / "vlc" / "ris.py",
        ROOT / "vlc" / "ris_environment.py",
        ROOT / "vlc" / "ris_experiments.py",
        ROOT / "vlc" / "drl_fj.py",
        ROOT / "vlc" / "channel.py",
        ROOT / "vlc" / "config.py",
        ROOT / "vlc" / "secrecy.py",
        ROOT / "app_server.py",
        ROOT / "supervisor_demo.html",
        study_summary_path,
        study_data_path
    ]
    
    source_hashes = {}
    for p in source_files:
        if p.exists():
            source_hashes[str(p.relative_to(ROOT))] = {
                "sha256": sha256_file(p),
                "bytes": p.stat().st_size
            }
        else:
            source_hashes[str(p.relative_to(ROOT))] = "MISSING"

    # Read summary
    with open(study_summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
        
    provenance = {
        "title": "Optical RIS + Friendly Jamming Physical Layer Security Study: Reproducibility & Provenance",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "platform": {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": sys.version,
        },
        "study_protocol": {
            "scenario": "nominal (Bob=[1.8, 1.6, 0.85], Eve=[3.2, 3.4, 0.85])",
            "energy_model": "L1 (nonnegative absolute weight cost)",
            "matched_seeds": [42, 43, 44, 45, 46, 47, 48, 49, 50, 51],
            "total_matched_runs": 30,
            "training_slots_per_run": 2000,
            "frozen_evaluation_slots_per_run": 1000,
            "schemes": ["baseline", "fixed_ris", "joint_ris"],
            "action_spaces": {
                "baseline": 625,
                "fixed_ris": 625,
                "joint_ris": 3125
            }
        },
        "authoritative_findings": {
            "phase1_frozen_eval_secrecy_means_bps_hz": {
                "baseline": 1.3205214713359323,
                "fixed_ris": 1.4977986701651385,
                "joint_ris": 1.456450206695536
            },
            "phase1_frozen_eval_outages": {
                "baseline": 0.0,
                "fixed_ris": 0.0,
                "joint_ris": 0.0
            },
            "paired_differences_95_ci": {
                "fixed_minus_baseline": {
                    "mean": 0.17727719882920578,
                    "ci95": [0.03784582027323832, 0.3167085773851732],
                    "p_value": 0.0182917,
                    "significant_positive": True
                },
                "joint_minus_baseline": {
                    "mean": 0.1359287353596037,
                    "ci95": [-0.04398457242273619, 0.3158420431419436],
                    "p_value": 0.1216017,
                    "significant_positive": False
                },
                "joint_minus_fixed": {
                    "mean": -0.041348463469602075,
                    "ci95": [-0.2674135115243884, 0.18471658458518428],
                    "p_value": 0.6887355,
                    "significant_difference": False
                }
            },
            "physical_boundary_disclosures": {
                "near_bob_max_secrecy": 0.0,
                "colocated_max_secrecy": 0.0,
                "published_paper_exact_curves_reproduced": False
            }
        },
        "source_inventory": source_hashes
    }

    prov_path = PACKAGE_DIR / "PROVENANCE.json"
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2)
    print(f"Generated: {prov_path}")

    # Compact results copy
    compact_path = PACKAGE_DIR / "compact_results.json"
    with open(compact_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Generated: {compact_path}")


if __name__ == "__main__":
    main()


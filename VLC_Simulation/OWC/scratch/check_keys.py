import json
from pathlib import Path

with open("output_figures/ris/final_evaluation/ris_study_summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Top-level keys:", data.keys())
for i, agg in enumerate(data.get("aggregates", [])):
    print(f"Agg[{i}] keys:", agg.keys())
    if "paired_differences" in agg:
        print("  found paired_differences in Agg", i)


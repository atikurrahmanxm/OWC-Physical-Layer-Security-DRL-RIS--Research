import json

with open("output_figures/ris/final_evaluation/ris_study_summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

paired = data.get("paired_seed_comparisons", [])
print(json.dumps(paired[0], indent=2))


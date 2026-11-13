import json

with open("output_figures/ris/final_evaluation/ris_study_summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

paired = data.get("paired_seed_comparisons", [])
print("paired_seed_comparisons count:", len(paired))
for p in paired:
    print(f"\nScenario: {p.get('scenario')}, Energy: {p.get('energy_model')}")
    for window in ["evaluation", "final_window", "all_slots"]:
        print(f"\n--- WINDOW: {window} ---")
        w_data = p.get(window, {})
        for comp, vals in w_data.items():
            sec = vals.get("secrecy_rate", {})
            ber = vals.get("ber", {})
            en = vals.get("energy", {})
            print(f"  {comp}:")
            print(f"    Secrecy Rate: mean={sec.get('mean'):+.6f}, std={sec.get('sample_std'):.6f}, 95% CI={sec.get('ci95')}, method={sec.get('ci_method')}")
            print(f"    Bob BER:      mean={ber.get('mean'):+.6e}, 95% CI={ber.get('ci95')}")
            print(f"    Energy:       mean={en.get('mean'):+.6f}, 95% CI={en.get('ci95')}")


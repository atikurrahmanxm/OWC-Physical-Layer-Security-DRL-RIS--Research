import json

with open("output_figures/ris/final_evaluation/ris_study_summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("="*80)
print("10-SEED MATCHED STUDY RESULTS (output_figures/ris/final_evaluation/)")
print("="*80)

print("\n--- SCHEME AGGREGATES ---")
for agg in data.get("aggregates", []):
    scheme = agg["scheme"]
    print(f"\nScheme: {scheme.upper()}")
    for window in ["evaluation", "final_window", "all_slots"]:
        w = agg.get(window, {})
        sec = w.get("secrecy_rate", {})
        ber = w.get("ber", {})
        en = w.get("energy", {})
        print(f"  [{window:12s}] Secrecy: {sec.get('mean'):.6f} (std={sec.get('sample_std'):.6f}, 95% CI=[{sec.get('ci95')[0]:.4f}, {sec.get('ci95')[1]:.4f}])")
        print(f"                 BER:     {ber.get('mean'):.6e}")
        print(f"                 Energy:  {en.get('mean'):.6f} (std={en.get('sample_std'):.6f})")
    
    qos1e3 = agg.get("bob_qos_outage_1e3", {})
    qos1e4 = agg.get("bob_qos_outage_1e4", {})
    sec_out = agg.get("secrecy_outage", {})
    print(f"  [Outages]      Bob BER > 1e-3: {qos1e3.get('mean'):.4f}, Bob BER > 1e-4: {qos1e4.get('mean'):.4f}, Secrecy < 0.1: {sec_out.get('mean'):.4f}")

print("\n" + "="*80)
print("PAIRED SEED COMPARISONS (N=10 seeds: 42..51)")
print("="*80)
for p in data.get("paired_seed_comparisons", []):
    comp = p["comparison"]
    print(f"\nComparison: >>> {comp.upper()} <<<")
    for window in ["evaluation", "final_window", "all_slots"]:
        w = p.get(window, {})
        sec = w.get("secrecy_rate", {})
        ber = w.get("ber", {})
        en = w.get("energy", {})
        print(f"  [{window:12s}] d(Secrecy): {sec.get('mean'):+.6f} bps/Hz (std={sec.get('sample_std'):.6f}, 95% CI=[{sec.get('ci95')[0]:+.4f}, {sec.get('ci95')[1]:+.4f}])")
        print(f"                 d(BER):     {ber.get('mean'):+.6e}")
        print(f"                 d(Energy):  {en.get('mean'):+.6f}")


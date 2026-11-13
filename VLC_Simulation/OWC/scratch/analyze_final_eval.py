import json
from pathlib import Path

def analyze(json_path):
    p = Path(json_path)
    if not p.exists():
        print(f"File {json_path} does not exist yet.")
        return
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    aggs = data.get("aggregates", [])
    print(f"Elapsed seconds: {data.get('elapsed_seconds'):.1f} s (~{data.get('elapsed_seconds')/60:.1f} min)")
    print(f"Complete: {data.get('complete')}")
    print(f"Total aggregates items: {len(aggs)}")
    
    for item in aggs:
        if "scheme" in item:
            scheme = item.get("scheme")
            scenario = item.get("scenario")
            energy_model = item.get("energy_model")
            print(f"\n==================== SCHEME: {scheme} ({scenario}, {energy_model}) ====================")
            all_s = item.get("all_slots", {})
            fw = item.get("final_window", {})
            ev = item.get("evaluation", {})
            
            print(f"--- ALL SLOTS (2,000 slots, includes warmup/exploration) ---")
            sec = all_s.get("secrecy_rate", {})
            ber = all_s.get("ber", {})
            en = all_s.get("energy", {})
            print(f"  Secrecy Rate: {sec.get('mean'):.6f} bps/Hz (std={sec.get('sample_std'):.6f}, 95% CI={sec.get('ci95')})")
            print(f"  Bob BER:      {ber.get('mean'):.6e} (std={ber.get('sample_std'):.6e})")
            print(f"  Energy Cost:  {en.get('mean'):.6f} (std={en.get('sample_std'):.6f})")

            print(f"--- FINAL TRAINING WINDOW (last 500 slots, eps=0.02) ---")
            sec_fw = fw.get("secrecy_rate", {})
            ber_fw = fw.get("ber", {})
            en_fw = fw.get("energy", {})
            print(f"  Secrecy Rate: {sec_fw.get('mean'):.6f} bps/Hz (std={sec_fw.get('sample_std'):.6f}, 95% CI={sec_fw.get('ci95')})")
            print(f"  Bob BER:      {ber_fw.get('mean'):.6e}")
            print(f"  Energy Cost:  {en_fw.get('mean'):.6f}")

            print(f"--- FROZEN GREEDY EVALUATION (1,000 slots, eps=0, zero updates) ---")
            sec_ev = ev.get("secrecy_rate", {})
            ber_ev = ev.get("ber", {})
            en_ev = ev.get("energy", {})
            print(f"  Secrecy Rate: {sec_ev.get('mean'):.6f} bps/Hz (std={sec_ev.get('sample_std'):.6f}, 95% CI={sec_ev.get('ci95')})")
            print(f"  Bob BER:      {ber_ev.get('mean'):.6e}")
            print(f"  Energy Cost:  {en_ev.get('mean'):.6f}")

            qos1e3 = item.get("bob_qos_outage_1e3", {})
            qos1e4 = item.get("bob_qos_outage_1e4", {})
            sec_out = item.get("secrecy_outage", {})
            print(f"--- OUTAGE FRACTIONS ---")
            print(f"  Bob QoS Outage (>1e-3): {qos1e3.get('mean')}")
            print(f"  Bob QoS Outage (>1e-4): {qos1e4.get('mean')}")
            print(f"  Secrecy Outage (<0.1):  {sec_out.get('mean')}")

        if "paired_differences" in item:
            paired = item.get("paired_differences", {})
            print(f"\n==================== PAIRED DIFFERENCES ({item.get('scenario')}, {item.get('energy_model')}) ====================")
            for window in ["evaluation", "final_window", "all_slots"]:
                print(f"\n--- Window: {window} ---")
                w_paired = paired.get(window, {})
                for comp, c_data in w_paired.items():
                    sec = c_data.get("secrecy_rate", {})
                    ber = c_data.get("ber", {})
                    en = c_data.get("energy", {})
                    print(f"  Comparison [{comp}]:")
                    print(f"    d(Secrecy Rate): {sec.get('mean'):+.6f} bps/Hz (std={sec.get('sample_std'):.6f}, 95% CI={sec.get('ci95')})")
                    print(f"    d(Bob BER):      {ber.get('mean'):+.6e}")
                    print(f"    d(Energy):       {en.get('mean'):+.6f}")

if __name__ == "__main__":
    analyze("output_figures/ris/final_evaluation/ris_study_summary.json")

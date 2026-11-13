import json
import scipy.stats as stats

with open('output_figures/ris/final_evaluation/ris_study_summary.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for p in d['paired_seed_comparisons']:
    r = p['evaluation']['secrecy_rate']
    mean = r['mean']
    se = r['standard_error']
    t_stat = mean / se
    p_val = 2 * (1 - stats.t.cdf(abs(t_stat), r['n'] - 1))
    print(f"{p['comparison']}: mean={mean:.8f}, se={se:.8f}, t={t_stat:.6f}, p={p_val:.7f}")


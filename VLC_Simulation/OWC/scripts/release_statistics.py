"""Post-hoc paired statistical sensitivity checks on the completed raw study.

Run through Antigravity for this release. No training or raw-file mutation.
"""
import itertools
import json
from pathlib import Path
import numpy as np
from scipy import stats

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'output_figures/ris/training_budget_study_matched_v2/runs'
OUT=ROOT/'manuscript/research_draft_v2/release_audit'

def holm(values):
    values=np.asarray(values,float)
    order=np.argsort(values)
    corrected=np.minimum(1,np.maximum.accumulate(values[order]*(len(values)-np.arange(len(values)))))
    result=np.empty(len(values));result[order]=corrected
    return result.tolist()

def main():
    OUT.mkdir(exist_ok=True)
    records=[json.loads(p.read_text()) for p in sorted(DATA.glob('*.json'))]
    indexed={(r['budget'],r['scheme'],r['seed']):r for r in records}
    assert len(indexed)==90
    signs=np.array(list(itertools.product([-1.,1.],repeat=10)))
    rows=[]
    for budget in (2000,5000,10000):
        for numerator,denominator in [('joint_ris','fixed_ris'),('fixed_ris','baseline'),('joint_ris','baseline')]:
            for metric in ('utility','secrecy_rate'):
                differences=np.array([indexed[budget,numerator,s]['evaluation'][metric]['mean']-indexed[budget,denominator,s]['evaluation'][metric]['mean'] for s in range(42,52)])
                mean=float(differences.mean());se=float(stats.sem(differences))
                ci=stats.t.interval(.95,9,loc=mean,scale=se)
                p=float(stats.ttest_1samp(differences,0).pvalue)
                flip=float(np.mean(np.abs(signs@differences)>=abs(differences.sum())-1e-12))
                rows.append(dict(budget=budget,numerator=numerator,denominator=denominator,metric=metric,mean_difference=mean,standard_error=se,ci95=list(map(float,ci)),t_p=p,sign_flip_p=flip,seed_differences=differences.tolist()))
    assert len(rows)==18
    for row,tp,fp in zip(rows,holm([r['t_p'] for r in rows]),holm([r['sign_flip_p'] for r in rows])):
        row['holm_t_p_18']=tp;row['holm_sign_flip_p_18']=fp
    metadata=dict(analysis_kind='Post-hoc robustness analysis; not a new preregistration.',replicates='Ten matched seed means per contrast; evaluation slots are not independent replicates.',family='All 18 comparisons: 3 budgets x 3 contrasts x 2 metrics. Holm correction is conservative across this full reported family.',sign_flip_assumption='All 1024 sign patterns enumerated. Requires symmetry/exchangeability of paired differences under the null; not a randomized-treatment causal test.',rows=rows)
    (OUT/'statistical_robustness.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    lines=['# Statistical robustness audit','',metadata['analysis_kind'],metadata['family'],metadata['sign_flip_assumption'],'','| 10k comparison | Metric | Difference | t p | Holm t p (18) | Sign-flip p | Holm sign-flip p (18) |','|---|---|---:|---:|---:|---:|---:|']
    for r in rows:
        if r['budget']==10000:
            lines.append(f"| {r['numerator']} − {r['denominator']} | {r['metric']} | {r['mean_difference']:+.4f} | {r['t_p']:.5f} | {r['holm_t_p_18']:.5f} | {r['sign_flip_p']:.5f} | {r['holm_sign_flip_p_18']:.5f} |")
    lines+=['','Interpret corrected exploratory evidence separately from the existing protocol-primary joint-minus-fixed utility contrast. Numerical mean improvement is not automatically a multiplicity-adjusted finding.']
    (OUT/'STATISTICAL_ROBUSTNESS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Completed: 18 paired contrasts, 1024 sign patterns each, two full-family Holm sensitivity corrections.')
    for r in rows:
        if r['budget']==10000: print(r['numerator'],r['denominator'],r['metric'],'Holm t p=',round(r['holm_t_p_18'],6),'sign-flip=',round(r['sign_flip_p'],6))

if __name__=='__main__': main()

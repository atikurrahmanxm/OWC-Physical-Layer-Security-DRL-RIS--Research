"""Rebuild manuscript tables, figures and evidence from existing v2 run files.

No training is performed. Run from the OWC project root.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / 'manuscript/research_draft_v2'
DATA = ROOT / 'output_figures/ris/training_budget_study_matched_v2'
SCHEMES = ['baseline', 'fixed_ris', 'joint_ris']
LABELS = ['No RIS', 'Fixed RIS', 'Joint RIS/FJ']
BUDGETS = [2000, 5000, 10000]

def describe(x):
    x = np.asarray(x, dtype=float)
    se = stats.sem(x)
    ci = stats.t.interval(.95, len(x)-1, loc=x.mean(), scale=se) if se else (x.mean(), x.mean())
    return dict(mean=float(x.mean()), se=float(se), ci95=list(map(float, ci)))

def main():
    OUT.mkdir(exist_ok=True)
    paths = sorted((DATA/'runs').glob('*.json'))
    records = [json.loads(p.read_text()) for p in paths]
    assert len(records) == 90
    indexed = {(r['budget'], r['scheme'], r['seed']): r for r in records}
    assert len(indexed) == 90
    for b in BUDGETS:
        for s in SCHEMES:
            for seed in range(42, 52):
                r = indexed[b,s,seed]
                assert r['complete'] and r['protocol_version'] == 2
                assert r['config']['cnn_m0'] == 11
                assert r['config']['energy_model'] == 'l1'
                for metric in ['utility','secrecy_rate','energy','ber']:
                    x = np.asarray(r['evaluation'][metric]['values'])
                    assert len(x) == 1000 and np.isfinite(x).all()
                    assert np.isclose(x.mean(), r['evaluation'][metric]['mean'], atol=1e-12)
    results = []
    for b in BUDGETS:
        for s in SCHEMES:
            rr = [indexed[b,s,k] for k in range(42,52)]
            row = dict(budget=b, scheme=s)
            for m in ['utility','secrecy_rate','energy','ber']:
                row[m] = describe([r['evaluation'][m]['mean'] for r in rr])
            row['training_seconds'] = describe([r['training']['wall_clock_seconds'] for r in rr])
            row['unique_actions'] = describe([r['training']['unique_actions_visited'] for r in rr])
            row['coverage_percent'] = row['unique_actions']['mean'] / (3125 if s=='joint_ris' else 625)*100
            row['chosen_q'] = [int(min(r['evaluation']['q_counts'], key=lambda q: (-r['evaluation']['q_counts'][q], int(q)))) for r in rr]
            row['bob_outage_1e4'] = describe([r['evaluation']['bob_outage_1e4'] for r in rr])
            results.append(row)
    contrasts = []
    for b in BUDGETS:
        for a,c in [('joint_ris','fixed_ris'),('fixed_ris','baseline'),('joint_ris','baseline')]:
            row = dict(budget=b, numerator=a, denominator=c)
            for m in ['utility','secrecy_rate']:
                x = [indexed[b,a,k]['evaluation'][m]['mean']-indexed[b,c,k]['evaluation'][m]['mean'] for k in range(42,52)]
                row[m] = describe(x)
                row[m]['p'] = float(stats.ttest_1samp(x,0).pvalue)
            contrasts.append(row)
    from vlc.config import VLCConfig
    from vlc.ris_environment import RISEnvironment
    env = RISEnvironment(VLCConfig(energy_model='l1',cnn_m0=11))
    grid = [env.evaluate_action(i) for i in range(env.num_actions)]
    maxima = {m: max(grid, key=lambda r:r[m]) for m in ['utility','secrecy_rate']}
    fixed = RISEnvironment(VLCConfig(energy_model='l1',cnn_m0=11),control_mode='fixed')
    for i,w in enumerate(fixed.action_space):
        reference=fixed.evaluate_action(i)
        joint=env.evaluate_action(env.encode_action(w,1))
        for m in ['utility','secrecy_rate','ber','energy']:
            assert np.isclose(reference[m],joint[m],atol=1e-12,rtol=0)
    # Evaluate the manuscript's displayed formulas independently over the grid.
    from scipy.special import erfc
    for r in grid:
        g=r['gains']; w=np.asarray(r['beamformer']); b=np.dot(g['h_JB'],w)
        ej=abs(np.dot(g['h_JE'],w)); ae=g['h_AE']; ab=g['h_AB']; cfg=env.config
        a=cfg.modulation_index*cfg.id_bias
        bob=.5*np.log2(1+2*ab**2*a**2/(np.pi*np.e*(cfg.noise_variance+2*b**2*a**2)))
        leak=min(np.log2(ae/ej)+ej/ae*np.log2(np.sqrt(np.e)),ae/ej*np.log2(np.sqrt(np.e))) if ae and ej else 0
        rate=bob if ae==0 else (max(0,bob-leak) if ej else 0)
        ber=.75*erfc(np.sqrt(2*cfg.led_avg_power*(ab+b)**2/(5*cfg.noise_variance)))
        assert np.isclose(rate,r['secrecy_rate'],atol=1e-12,rtol=0)
        assert np.isclose(ber,r['ber'],atol=1e-12,rtol=0)
    (OUT/'verified_results.json').write_text(json.dumps(dict(aggregates=results, contrasts=contrasts, finite_grid_maxima=maxima),indent=2),encoding='utf-8')
    rows=[]
    for r in results:
        u,cs=r['utility'],r['secrecy_rate']
        rows.append(f"{r['budget']:,} & {LABELS[SCHEMES.index(r['scheme'])]} & ${u['mean']:.4f} \\pm {u['se']:.4f}$ & ${cs['mean']:.4f} \\pm {cs['se']:.4f}$ & {r['coverage_percent']:.2f} & {r['training_seconds']['mean']:.1f} \\\\")
    (OUT/'results_rows.tex').write_text('\n'.join(rows)+'\n\\bottomrule\n',encoding='utf-8')
    rows=[]
    for r in contrasts:
        if r['budget'] != 10000: continue
        for m,label in [('utility','$U$'),('secrecy_rate','$R_s$')]:
            v=r[m]; a=LABELS[SCHEMES.index(r['numerator'])]; c=LABELS[SCHEMES.index(r['denominator'])]
            rows.append(f"{a} $-$ {c} & {label} & ${v['mean']:+.4f}$ & $[{v['ci95'][0]:+.4f}, {v['ci95'][1]:+.4f}]$ & {v['p']:.5f} \\\\")
    (OUT/'paired_rows.tex').write_text('\n'.join(rows)+'\n\\bottomrule\n',encoding='utf-8')
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    colors=['#777777','#1976a3','#d37620']
    def save(fig,name):
        fig.tight_layout()
        for ext in ['png','pdf']: fig.savefig(OUT/'figures'/f'{name}.{ext}',dpi=220,bbox_inches='tight')
        plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(7.0,2.65))
    for ax,m,label in zip(axes,['utility','secrecy_rate'],['Evaluation utility','Secrecy metric (bps/Hz)']):
        for s,l,c in zip(SCHEMES,LABELS,colors):
            rr=[r for r in results if r['scheme']==s]
            ax.errorbar(BUDGETS,[r[m]['mean'] for r in rr],yerr=[stats.t.ppf(.975,9)*r[m]['se'] for r in rr],marker='o',capsize=3,label=l,color=c)
        ax.set(xlabel='Training slots',ylabel=label,xticks=BUDGETS);ax.grid(alpha=.18)
    axes[0].legend(fontsize=7)
    save(fig,'fig1_budget_convergence')
    fig,axes=plt.subplots(1,2,figsize=(7,2.65))
    for ax,m,label in zip(axes,['utility','secrecy_rate'],['Joint minus fixed utility','Joint minus fixed secrecy (bps/Hz)']):
        rr=[r for r in contrasts if r['numerator']=='joint_ris' and r['denominator']=='fixed_ris']
        ax.errorbar(BUDGETS,[r[m]['mean'] for r in rr],yerr=[stats.t.ppf(.975,9)*r[m]['se'] for r in rr],marker='o',capsize=3,color=colors[2]);ax.axhline(0,color='gray',lw=.8);ax.set(xlabel='Training slots',ylabel=label,xticks=BUDGETS);ax.grid(alpha=.18)
    save(fig,'fig2_budget_paired_differences')
    fig,axes=plt.subplots(1,2,figsize=(7,2.65))
    for s,l,c in zip(SCHEMES,LABELS,colors):
        rr=[r for r in results if r['scheme']==s];axes[0].plot(BUDGETS,[r['coverage_percent'] for r in rr],'-o',label=l,color=c)
    axes[0].set(xlabel='Training slots',ylabel='Distinct actions visited (%)',xticks=BUDGETS);axes[0].legend(fontsize=7)
    bottom=np.zeros(3)
    for q in range(5):
        counts=np.array([r['chosen_q'].count(q) for r in results if r['scheme']=='joint_ris']);axes[1].bar(range(3),counts,bottom=bottom,label=f'q={q}');bottom+=counts
    axes[1].set(xticks=range(3),xticklabels=['2,000','5,000','10,000'],xlabel='Training slots',ylabel='Joint evaluation modal q (seeds)',ylim=(0,10));axes[1].legend(fontsize=7,ncol=5,loc='upper center',bbox_to_anchor=(.5,1.18),frameon=False)
    save(fig,'fig3_budget_coverage_and_q')
    fig,ax=plt.subplots(figsize=(3.5,2.5))
    for s,l,c in zip(SCHEMES,LABELS,colors):
        rr=[r for r in results if r['scheme']==s];ax.plot(BUDGETS,[r['training_seconds']['mean'] for r in rr],'-o',label=l,color=c)
    ax.set(xlabel='Training slots',ylabel='Recorded elapsed training time (s)',xticks=BUDGETS);ax.legend(fontsize=7)
    save(fig,'fig4_computational_scaling')
    checkpoints=[]
    for r in records:
        for name in r['checkpoints'].values():
            p=DATA/'checkpoints'/name
            assert p.is_file() and p.stat().st_size>0
            checkpoints.append(p)
    inputs = paths+checkpoints+[DATA/'manifest.json']+[ROOT/f for f in ['vlc/secrecy.py','vlc/ris.py','vlc/ris_environment.py','vlc/channel.py','vlc/config.py','vlc/drl_fj.py','vlc/physical.py','simulations/sim_training_budget_study.py']]
    inputs += [OUT/'main.tex',OUT/'references.bib']
    inputs += [OUT/f for f in ['results_rows.tex','paired_rows.tex','release_statistics_rows.tex','release_geometry_rows.tex','release_calibrated_rows.tex']]
    inputs += list((OUT/'figures').glob('*.pdf'))+list((OUT/'verification').glob('*.json'))
    inputs += [ROOT/'scripts'/name for name in [
        'revise_manuscript_evidence.py','build_manuscript_sources.py','audit_saved_policy_replay.py',
        'create_manuscript_system_figures.py','build_manuscript_docx.py','validate_manuscript_build.py',
        'release_statistics.py','release_validation.py','run_calibrated_ris_diagnostic.py',
        'assemble_release_evidence.py','package_research_release.py'
    ]]
    audit = OUT/'release_audit'
    inputs += [audit/name for name in [
        'statistical_robustness.json','full_policy_replay.json','geometry_grid_sensitivity.json',
        'frozen_policy_geometry_transfer.json','release_evidence_summary.json','validation_protocol.json',
        'ANTIGRAVITY_UNIT_TESTS.log','ANTIGRAVITY_STATISTICS.log','ANTIGRAVITY_VALIDATION.log','ANTIGRAVITY_CALIBRATED.log'
    ] if (audit/name).exists()]
    calibrated_dir = ROOT/'output_figures/ris/calibrated_diagnostic_v1'
    if (calibrated_dir/'diagnostic_summary.json').exists():
        inputs.append(calibrated_dir/'diagnostic_summary.json')
        inputs += sorted(calibrated_dir.glob('*.npz'))
    if (OUT/'main.docx').exists(): inputs.append(OUT/'main.docx')
    manifest = dict(checked_date='2026-11-18',description='Current-file SHA256; source hashes do not establish the exact uncommitted source state used in historical runs.',files=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in inputs])
    (OUT/'evidence_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Validated 90 run records and 180 checkpoint files; formula checks: 3125 actions; fixed-action inclusion: 625 actions. No training.')
    for r in contrasts:
        if r['budget']==10000: print(r['numerator'],r['denominator'],{m:round(r[m]['p'],6) for m in ['utility','secrecy_rate']})
    print('Grid maxima:',{m:(v['ris_index'],round(v[m],8)) for m,v in maxima.items()})

if __name__ == '__main__': main()

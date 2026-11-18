"""Assemble completed Antigravity results into manuscript tables and figures.

No simulation, training or statistical testing is performed here. Missing or
incomplete upstream evidence is an error, not a reason to fill in results.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/research_draft_v2'
AUDIT=OUT/'release_audit'
SCHEMES=['baseline','fixed_ris','joint_ris']
LABELS=['No RIS','Fixed RIS','Joint RIS/FJ']
GEOS=['nominal','changed_positions','swapped_receivers','near_eve','colocated']
NAMES=['Nominal','Changed positions','Swapped receivers','Nearby Eve','Colocated']

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def main():
    replay=read(AUDIT/'full_policy_replay.json')
    grid=read(AUDIT/'geometry_grid_sensitivity.json')['rows']
    transfer=read(AUDIT/'frozen_policy_geometry_transfer.json')['rows']
    stats=read(AUDIT/'statistical_robustness.json')['rows']
    calibrated=read(ROOT/'output_figures/ris/calibrated_diagnostic_v1/diagnostic_summary.json')
    assert replay['policy_count']==90 and replay['slots_per_policy']==1000 and replay['all_match']
    assert len(grid)==15 and len(transfer)==120 and len(stats)==18 and len(calibrated['results'])==9
    rows=[]
    for r in stats:
        if r['budget']!=10000:continue
        label={'joint_ris':'Joint','fixed_ris':'Fixed','baseline':'None'}
        comparison=label[r['numerator']]+' $-$ '+label[r['denominator']]
        metric='$U$' if r['metric']=='utility' else '$R_s$'
        rows.append(f"{comparison} & {metric} & {r['t_p']:.5f} & {r['holm_t_p_18']:.5f} & {r['sign_flip_p']:.5f} & {r['holm_sign_flip_p_18']:.5f} \\\\")
    (OUT/'release_statistics_rows.tex').write_text('\n'.join(rows)+'\n\\bottomrule\n',encoding='utf-8')
    nominal=read(OUT/'verified_results.json')['aggregates']
    combined=[]
    for geo in GEOS:
        for scheme in SCHEMES:
            if geo=='nominal':
                r=next(x for x in nominal if x['budget']==10000 and x['scheme']==scheme)
                utility=r['utility']['mean'];se=r['utility']['se'];secrecy=r['secrecy_rate']['mean']
            else:
                rr=[x for x in transfer if x['geometry']==geo and x['scheme']==scheme]
                assert len(rr)==10 and all(x['evaluation_slots']==200 for x in rr)
                uu=np.array([x['metric_means']['utility'] for x in rr]);utility=float(uu.mean());se=float(uu.std(ddof=1)/np.sqrt(10))
                secrecy=float(np.mean([x['metric_means']['secrecy_rate'] for x in rr]))
            oracle=next(x for x in grid if x['geometry']==geo and x['noise_offset_db']==0)['maxima'][scheme]
            upper=oracle['utility']['utility']
            combined.append(dict(geometry=geo,scheme=scheme,utility=utility,se=se,secrecy=secrecy,oracle_utility=upper,gap=upper-utility))
    rows=[]
    for geo,name in zip(GEOS,NAMES):
        r=next(x for x in grid if x['geometry']==geo and x['noise_offset_db']==0)
        maxima=r['maxima']
        rows.append(f"{name} & {maxima['baseline']['utility']['utility']:.4f} & {maxima['fixed_ris']['utility']['utility']:.4f} & {maxima['joint_ris']['utility']['utility']:.4f} & {maxima['joint_ris']['utility']['ris_index']} \\\\")
    (OUT/'release_geometry_rows.tex').write_text('\n'.join(rows)+'\n\\bottomrule\n',encoding='utf-8')
    rows=[]
    for r in calibrated['results']:
        values=[]
        for scheme in ['no_ris','fixed_ris_q1','joint_ris_oracle']:
            v=r['schemes'][scheme]['maximum_secrecy_subject_to_bob_ber']
            values.append('--' if v is None else f"{v['secrecy_difference_bits_per_use']:.4f}")
        name={'nominal':'Nominal','changed_positions':'Changed','colocated':'Colocated'}[r['scenario']]
        rows.append(f"{name} & {r['reference_snr_db']:g} & "+' & '.join(values)+' \\\\')
    (OUT/'release_calibrated_rows.tex').write_text('\n'.join(rows)+'\n\\bottomrule\n',encoding='utf-8')
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    colors=['#777777','#1976a3','#d37620']
    def save(fig,name):
        fig.tight_layout()
        for ext in ['png','pdf']:fig.savefig(OUT/'figures'/f'{name}.{ext}',dpi=230,bbox_inches='tight')
        plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(7.2,3.25))
    for scheme,label,c in zip(SCHEMES,LABELS,colors):
        rr=[next(x for x in combined if x['geometry']==g and x['scheme']==scheme) for g in GEOS]
        axes[0].errorbar(range(5),[r['utility'] for r in rr],yerr=[r['se'] for r in rr],marker='o',capsize=3,label=label,color=c)
        axes[1].plot(range(5),[r['gap'] for r in rr],'-o',label=label,color=c)
    for ax in axes:
        ax.set_xticks(range(5),['Nominal','Changed','Swapped','Near Eve','Colocated'],rotation=25,ha='right');ax.grid(alpha=.15)
    axes[0].set_ylabel('Frozen policy utility (mean ± SE)');axes[0].legend(fontsize=7)
    axes[1].set_ylabel('Same-action-set oracle utility minus mean')
    save(fig,'fig_release_geometry_transfer')
    fig,axes=plt.subplots(1,3,figsize=(7.2,2.9),sharey=True)
    for ax,scenario,title in zip(axes,['nominal','changed_positions','colocated'],['Nominal','Changed positions','Colocated']):
        rr=sorted([x for x in calibrated['results'] if x['scenario']==scenario],key=lambda x:x['reference_snr_db'])
        for scheme,label,c in zip(['no_ris','fixed_ris_q1','joint_ris_oracle'],LABELS,colors):
            y=[]
            for r in rr:
                v=r['schemes'][scheme]['maximum_secrecy_subject_to_bob_ber']
                y.append(np.nan if v is None else v['secrecy_difference_bits_per_use'])
            ax.plot([r['reference_snr_db'] for r in rr],y,'-o',color=c,label=label)
        ax.set(title=title,xlabel='Reference SNR (dB)',xticks=[10,20,30]);ax.grid(alpha=.15)
    axes[0].set_ylabel('QoS-feasible oracle MI difference (bits/use)');axes[0].legend(fontsize=6.5)
    save(fig,'fig_release_calibrated')
    summary=dict(replayed_policies=90,compared_metric_values=replay['compared_metric_values'],geometry_grid_cases=len(grid),geometry_action_evaluations=len(grid)*3125,transfer_cases=len(transfer),transfer_slots=len(transfer)*200,calibrated_cases=9,calibrated_action_evaluations=9*3125,transfer_summary=combined,calibrated_results=calibrated['results'])
    (AUDIT/'release_evidence_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('Assembled completed evidence, three tables and two figures. No training.')

if __name__=='__main__':main()

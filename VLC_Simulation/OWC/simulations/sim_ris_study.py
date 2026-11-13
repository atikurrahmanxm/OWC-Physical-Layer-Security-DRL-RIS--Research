"""CLI and honest plots for the matched RIS + FJ + VLC + DRL experiment."""
import argparse
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from vlc.config import VLCConfig
from vlc.ris_experiments import run_ris_study,predefined_scenarios,SCHEMES


def plot_ris_study(record,output_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from simulations.sim_fig6_convergence import smooth_curve
    if not record.get('complete'):
        raise ValueError('Refuse to plot a partial study as completed results')
    folder=Path(output_dir);folder.mkdir(parents=True,exist_ok=True)
    keys=sorted({(r['scenario']['name'],r['energy_model']) for r in record['runs']})
    paths=[]
    labels={'secrecy_rate':'Secrecy rate (bps/Hz)','ber':'Bob BER','utility':'Policy reward'}
    colors={'baseline':'tab:blue','fixed_ris':'tab:green','joint_ris':'tab:red'}
    for scenario,energy in keys:
        selected=[r for r in record['runs'] if r['scenario']['name']==scenario and r['energy_model']==energy]
        fig,axes=plt.subplots(2,3,figsize=(14,8),constrained_layout=True)
        for column,(metric,label) in enumerate(labels.items()):
            ax=axes[0,column]
            for scheme in SCHEMES:
                rows=[r for r in selected if r['scheme']==scheme]
                if not rows:continue
                values=np.array([smooth_curve(np.asarray(r['history'][metric]),50) for r in rows])
                mean=values.mean(axis=0)
                if metric=='ber':mean=np.maximum(mean,1e-12)
                ax.plot(np.arange(1,len(mean)+1),mean,color=colors[scheme],label=SCHEMES[scheme]['label'])
            if metric=='ber':ax.set_yscale('log')
            ax.set_xlabel('Training slot (EMA50 display only)');ax.set_ylabel(label);ax.grid(alpha=.3)
            if column==0:ax.legend(fontsize=8)
            ax=axes[1,column]
            aggregates=[a for a in record['aggregates'] if a['scenario']==scenario and a['energy_model']==energy]
            for i,scheme in enumerate(SCHEMES):
                item=next((a for a in aggregates if a['scheme']==scheme),None)
                if item is None:continue
                estimate=item['all_slots'][metric]
                value=estimate['mean']
                if metric=='ber':value=max(value,1e-12)
                errors=None
                if estimate['ci95'] is not None:
                    lower,upper=estimate['ci95']
                    if metric=='ber':lower=max(lower,1e-12)
                    errors=np.array([[max(0.,value-lower)],[max(0.,upper-value)]])
                ax.bar(i,value,color=colors[scheme],yerr=errors,capsize=4)
            if metric=='ber':ax.set_yscale('log')
            ax.set_xticks(range(3),['No RIS','Fixed RIS','Joint RIS'])
            ax.set_ylabel(label);ax.set_title('All training slots; seed-level 95% t-CI when n > 1',fontsize=9)
            ax.grid(axis='y',alpha=.3)
        n=len({r['seed'] for r in selected})
        fig.suptitle(f"Optical RIS extension | {scenario} | energy={energy} | {n} seed(s)\n"
                     'Paper equations with explicit baseline assumptions; no published-curve reproduction claim')
        path=folder/f'ris_comparison_{scenario}_{energy}.png'
        fig.savefig(path,dpi=170);plt.close(fig);paths.append(str(path))
    return paths


def simulate_ris_study(**kwargs):
    record=run_ris_study(**kwargs)
    plot_ris_study(record,kwargs.get('output_dir','output_figures/ris'))
    return record


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--slots',type=int,default=2000)
    parser.add_argument('--seeds',type=int,nargs='+',default=[42])
    parser.add_argument('--energy-model',choices=['paper_signed','l1','both'],default='paper_signed')
    parser.add_argument('--output',default='output_figures/ris')
    parser.add_argument('--scenarios',nargs='+',choices=['nominal','near_bob','colocated','all'],default=['nominal'])
    parser.add_argument('--snr',type=float,default=None)
    parser.add_argument('--snr-definition',choices=['eq4','electrical','pam'],default='eq4')
    parser.add_argument('--qos-ber-max',type=float,default=None)
    parser.add_argument('--qos-penalty',type=float,default=0.)
    parser.add_argument('--secrecy-target',type=float,default=.1)
    parser.add_argument('--final-window',type=int,default=500)
    parser.add_argument('--fixed-configuration',type=int,default=1)
    parser.add_argument('--skip-exhaustive',action='store_true')
    args=parser.parse_args(argv)
    config=VLCConfig(model='paper',energy_model='paper_signed' if args.energy_model=='both' else args.energy_model,
                     snr_definition=args.snr_definition)
    selected=predefined_scenarios(config)
    if 'all' not in args.scenarios:selected=[s for s in selected if s['name'] in args.scenarios]
    for scenario in selected:scenario['snr_db']=args.snr
    record=simulate_ris_study(config=config,slots=args.slots,seeds=args.seeds,scenarios=selected,
        energy_models=['paper_signed','l1'] if args.energy_model=='both' else None,
        output_dir=args.output,fixed_configuration=args.fixed_configuration,
        qos_ber_max=args.qos_ber_max,qos_penalty=args.qos_penalty,secrecy_target=args.secrecy_target,
        final_window=args.final_window,include_exhaustive=not args.skip_exhaustive)
    print(f"Completed {len(record['runs'])} matched runs. Raw results: {Path(args.output)/'ris_study_data.json'}")
    return record


if __name__=='__main__':main()

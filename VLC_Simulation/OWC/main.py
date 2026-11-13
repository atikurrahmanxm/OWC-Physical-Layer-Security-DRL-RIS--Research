"""Unified entry point for the paper-based VLC model and reproducible experiments."""
import argparse
import json
import sys
import unittest
from pathlib import Path
import numpy as np
import torch
from vlc.config import VLCConfig
from vlc.channel import VLCChannel
from vlc.environment import VLCEnvironment
from vlc.rl_fj import RLFJAgent
from vlc.drl_fj import DRLFJAgent
from vlc.bounds import compute_zero_forcing_beamformer, compute_theoretical_bounds, corollary_diagnostics
from vlc.secrecy import compute_secrecy_rate, compute_bob_ber, compute_energy_consumption, compute_system_utility
from vlc.experiments import metadata, save_record, run_learning_experiment

ROOT_DIR = Path(__file__).resolve().parent


def evaluate_custom_scenario(bob_x, bob_y, bob_z, eve_x, eve_y, eve_z,
                             snr_db=None, delta1=3.5, delta2=.4,
                             config=None, slots=2000, save_path=None):
    c = config or VLCConfig(delta1=delta1, delta2=delta2)
    bob, eve = np.array([bob_x,bob_y,bob_z]), np.array([eve_x,eve_y,eve_z])
    gains = VLCChannel(c).get_all_channel_gains(bob,eve)
    ab, ae, jb, je = gains
    sigma = c.noise_variance if snr_db is None else c.noise_variance_from_snr(ab,snr_db)
    print(f"Running {c.model} model: both agents, {slots} slots, seed={c.seed}; energy={c.energy_model}; SNR={c.snr_definition}",flush=True)
    record = run_learning_experiment(c,bob,eve,sigma,slots)
    rows = {}
    for name,w in [("No jamming",np.zeros(c.num_jammers)),("Exact zero-forcing",compute_zero_forcing_beamformer(jb,je))]:
        cs = compute_secrecy_rate(*gains,w,c,sigma)
        pe = compute_bob_ber(ab,jb,w,c,sigma)
        energy = compute_energy_consumption(w,c)
        rows[name] = dict(secrecy_rate=cs,ber=pe,energy=energy,utility=compute_system_utility(cs,pe,energy,c))
    for name in ["rl","drl"]:
        rows[name] = {metric:float(np.mean(values)) for metric,values in record["histories"][name].items()}
    print(f"Bob: {bob.tolist()}; Eve: {eve.tolist()}; noise={sigma:.8e}")
    print("Method                     Secrecy (bps/Hz)     BER          Energy       Utility")
    for name,row in rows.items():
        print(f"{name:26} {row['secrecy_rate']:12.6f} {row['ber']:13.5e} {row['energy']:10.5f} {row['utility']:12.6f}")
    cs,pe,u,_ = compute_theoretical_bounds(*gains,c,sigma)
    print(f"Independent global bounds: secrecy <= {cs:.6f}; BER >= {pe:.5e}; utility <= {u:.6f} (not jointly attainable).")
    print("Corollary 1: " + record["corollary"]["reason"])
    print("Published curves remain unverified; see PAPER_REPRODUCTION.md.")
    record["summary"] = rows
    if save_path:
        save_record(save_path,record)
        print(f"Raw results: {save_path}")
    return record


def run_unit_tests():
    suite = unittest.defaultTestLoader.discover(str(ROOT_DIR/"tests"),top_level_dir=str(ROOT_DIR))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.testsRun == 0 or not result.wasSuccessful():
        raise SystemExit(1)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=["eval","fig","train","test","all","gui","app","desktop","ris"],default="eval")
    p.add_argument("--model",choices=["paper","physical"],default="paper")
    p.add_argument("--receiver-resistance",type=float,default=1.,help="Ohms: physical current-noise variance=P_noise/R")
    p.add_argument("--jammer-resistance",type=float,default=1.,help="Ohms: physical AC jamming energy=E[j^2]*R*duration")
    p.add_argument("--slot-duration",type=float,default=1.,help="Seconds per slot for physical energy")
    p.add_argument("--noise-dbm",type=float,default=-98.79)
    p.add_argument("--eta",type=float,default=1.,help="Optical W/A, bias derived from P_T/eta")
    p.add_argument("--bob",nargs=3,type=float,default=[1.8,1.6,.85])
    p.add_argument("--eve",nargs=3,type=float,default=[3.2,3.4,.85])
    p.add_argument("--snr",type=float,default=None,help="Omit for Table I noise")
    p.add_argument("--snr-definition",choices=["electrical","eq4","pam","modulated"],default=None,help="Default: eq4 for paper, mean modulated current SNR for physical")
    p.add_argument("--energy-model",choices=["paper_signed","l1","electrical"],default=None,help="Default: l1 for paper, AC electrical joules for physical")
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--delta1",type=float,default=3.5)
    p.add_argument("--delta2",type=float,default=.4)
    p.add_argument("--slots",type=int,default=2000)
    p.add_argument("--grid_res",type=int,default=25)
    p.add_argument("--save_dir",default=None)
    p.add_argument("--results",default=None,help="Raw JSON destination for evaluation/training")
    p.add_argument("--fig",choices=["5","6","7","all"],default="all")
    p.add_argument("--algo",choices=["rl","drl"],default="drl")
    p.add_argument('--seeds',type=int,nargs='+',default=None,help='Independent RIS study seeds; defaults to --seed')
    p.add_argument('--ris-scenarios',nargs='+',choices=['nominal','near_bob','colocated','all'],default=['nominal'])
    p.add_argument('--ris-energy-sensitivity',action='store_true',help='Compare signed and L1 energy with matched settings')
    p.add_argument('--ris-reflectivity',type=float,default=.85)
    p.add_argument('--ris-center',type=float,nargs=3,default=[2.5,.25,2.6])
    p.add_argument('--ris-width',type=float,default=1.)
    p.add_argument('--ris-height',type=float,default=.5)
    p.add_argument('--ris-rows',type=int,default=2)
    p.add_argument('--ris-cols',type=int,default=3)
    p.add_argument('--qos-ber-max',type=float,default=None)
    p.add_argument('--qos-penalty',type=float,default=0.)
    p.add_argument('--secrecy-target',type=float,default=.1)
    a = p.parse_args(argv)
    if a.slots < 1:
        p.error("--slots must be positive")
    a.save_dir=a.save_dir or ('output_figures/ris' if a.mode=='ris' else "output_figures/physical" if a.model == "physical" else "output_figures")
    if a.mode=='ris':
        if a.model!='paper':
            p.error('The agreed RIS extension uses the original paper-mode equations')
        if a.energy_model is None:
            a.energy_model='paper_signed'
    if a.model == "physical" and a.mode in ["gui","app","desktop"]:
        p.error("Physical mode is available through CLI experiments and the Python API; the dashboard displays paper-equation physics.")
    try:
        c = VLCConfig(model=a.model,receiver_resistance_ohm=a.receiver_resistance,
                      jammer_resistance_ohm=a.jammer_resistance,slot_duration_s=a.slot_duration,
                      noise_power_dbm=a.noise_dbm,eta=a.eta,
                      seed=a.seed,delta1=a.delta1,delta2=a.delta2,energy_model=a.energy_model,snr_definition=a.snr_definition,bob_pos=np.asarray(a.bob),eve_pos=np.asarray(a.eve))
    except ValueError as error:
        p.error(str(error))
    torch.set_num_threads(1)
    if a.mode=='ris':
        from vlc.ris import OpticalRISConfig
        from vlc.ris_experiments import predefined_scenarios
        from simulations.sim_ris_study import simulate_ris_study
        scenarios=predefined_scenarios(c)
        if 'all' not in a.ris_scenarios:
            scenarios=[s for s in scenarios if s['name'] in a.ris_scenarios]
        for scenario in scenarios:scenario['snr_db']=a.snr
        ris_config=OpticalRISConfig(panel_center=tuple(a.ris_center),panel_width_m=a.ris_width,
            panel_height_m=a.ris_height,rows=a.ris_rows,cols=a.ris_cols,reflectivity=a.ris_reflectivity)
        simulate_ris_study(config=c,ris_config=ris_config,slots=a.slots,seeds=a.seeds or [a.seed],
            scenarios=scenarios,energy_models=['paper_signed','l1'] if a.ris_energy_sensitivity else None,
            output_dir=a.save_dir,qos_ber_max=a.qos_ber_max,qos_penalty=a.qos_penalty,secrecy_target=a.secrecy_target)
    elif a.mode == "test":
        run_unit_tests()
    elif a.mode in ["app","desktop"]:
        from app_desktop import launch_desktop_app
        launch_desktop_app()
    elif a.mode == "gui":
        from app_server import serve
        serve(open_browser=True)
    elif a.mode == "eval":
        evaluate_custom_scenario(*a.bob,*a.eve,snr_db=a.snr,config=c,slots=a.slots,
                                 save_path=a.results or str(Path(a.save_dir)/"evaluation.json"))
    elif a.mode == "train":
        bob,eve = np.array(a.bob),np.array(a.eve)
        ab = VLCChannel(c).get_all_channel_gains(bob,eve)[0]
        sigma = c.noise_variance if a.snr is None else c.noise_variance_from_snr(ab,a.snr)
        env = VLCEnvironment(c,bob,eve,sigma_B_sq=sigma)
        agent = RLFJAgent(env,c) if a.algo == "rl" else DRLFJAgent(env,c)
        history = agent.train(a.slots)
        target = a.results or str(Path(a.save_dir)/f"training_{a.algo}.json")
        save_record(target,{"metadata":metadata(c,slots=a.slots,bob=bob,eve=eve,sigma_B_sq=sigma),"history":history,"actions":agent.action_history})
        print(f"Completed {a.algo}, {a.slots} slots. Raw data: {target}")
        print({k:v[-1] for k,v in history.items()})
    else:
        from simulations.sim_fig5_spatial import simulate_fig5
        from simulations.sim_fig6_convergence import simulate_fig6
        from simulations.sim_fig7_snr import simulate_fig7
        from simulations.run_all import run_all
        if a.mode == "all" or a.fig == "all":
            run_all(a.save_dir,a.slots,a.grid_res,config=c)
        elif a.fig == "5":
            simulate_fig5(a.grid_res,a.save_dir,config=c)
        elif a.fig == "6":
            simulate_fig6(a.slots,a.save_dir,seed=a.seed,config=c)
        else:
            simulate_fig7(num_slots=a.slots,save_dir=a.save_dir,seed=a.seed,config=c)


if __name__ == "__main__":
    main()

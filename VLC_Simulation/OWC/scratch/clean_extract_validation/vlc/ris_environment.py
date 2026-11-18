"""Paper-system environment extended only by optical RIS effective channels.

The discrete joint action consists of four FJ weights and one normalized
codebook coordinate. Physical mirror normals are recorded in RIS metadata;
the coordinate itself is not a beam weight, phase or additional transmitter.
"""
from dataclasses import replace
import math
import numpy as np
from .config import VLCConfig
from .environment import VLCEnvironment
from .secrecy import (compute_secrecy_rate,compute_bob_ber,
                      compute_energy_consumption,compute_system_utility)


def gain_record(gains):
    ab,ae,jb,je=gains
    return {'h_AB':float(ab),'h_AE':float(ae),
            'h_JB':np.asarray(jb,dtype=float).tolist(),
            'h_JE':np.asarray(je,dtype=float).tolist()}


class RISEnvironment(VLCEnvironment):
    def __init__(self,config=None,ris_config=None,bob_pos=None,eve_pos=None,
                 sigma_B_sq=None,control_mode='joint',fixed_configuration=1,
                 qos_ber_max=None,qos_penalty=0.):
        from .ris import OpticalRIS,OpticalRISConfig
        c=config or VLCConfig(energy_model='paper_signed')
        if c.model!='paper':
            raise ValueError('The agreed RIS extension uses model=paper; physical mode is a separate experiment')
        if control_mode not in {'joint','fixed','off'}:
            raise ValueError('control_mode must be joint, fixed or off')
        if qos_ber_max is not None and (not np.isfinite(qos_ber_max) or not 0<qos_ber_max<=.75):
            raise ValueError('Bob BER target must lie in (0,0.75]')
        if not np.isfinite(qos_penalty) or qos_penalty<0 or (qos_penalty>0 and qos_ber_max is None):
            raise ValueError('QoS penalty must be nonnegative and requires an explicit BER target')
        required=c.sliding_window_m*(4+c.num_jammers+1)+4
        if control_mode=='joint' and c.cnn_m0**2<required:
            c=replace(c,cnn_m0=math.ceil(math.sqrt(required)))
        if sigma_B_sq is not None and (not np.isfinite(sigma_B_sq) or sigma_B_sq<=0):
            raise ValueError('Noise variance must be finite and positive')
        self.control_mode=control_mode
        self.qos_ber_max=qos_ber_max
        self.qos_penalty=float(qos_penalty)
        self.ris_config=ris_config or OpticalRISConfig()
        self._ris_ready=False
        self._current_ris_index=0
        super().__init__(c,bob_pos,eve_pos,sigma_B_sq)
        self.ris=OpticalRIS(c,self.ris_config,bob_pos=self.bob_pos,eve_pos=self.eve_pos)
        self.num_ris_configurations=int(self.ris.num_configurations)
        if self.num_ris_configurations<1:
            raise ValueError('RIS codebook must include the disabled configuration at index zero')
        if control_mode=='fixed' and (isinstance(fixed_configuration,bool) or not isinstance(fixed_configuration,(int,np.integer)) or not 0<=fixed_configuration<self.num_ris_configurations):
            raise ValueError('Fixed RIS configuration is outside the codebook')
        self.fixed_configuration=int(fixed_configuration) if control_mode=='fixed' else 0
        self.fj_action_space=self.action_space.copy()
        if control_mode=='joint':
            chunks=[]
            for q in range(self.num_ris_configurations):
                column=np.full((len(self.fj_action_space),1),self._encode_index(q))
                chunks.append(np.concatenate([self.fj_action_space,column],axis=1))
            self.action_space=np.concatenate(chunks,axis=0)
        self.num_actions=len(self.action_space)
        self._ris_ready=True
        self._gain_cache={}
        self._direct_gains=self.channel_model.get_all_channel_gains(self.bob_pos,self.eve_pos)
        self._direct_geometry=self._geometry_key()
        self._current_ris_index=self.fixed_configuration if control_mode=='fixed' else 0
        self._update_channel()

    def _encode_index(self,index):
        return 0. if self.num_ris_configurations==1 else 2.*index/(self.num_ris_configurations-1)-1.

    def encode_action(self,beamformer,ris_index):
        w=np.asarray(beamformer,dtype=float)
        if w.shape!=(self.config.num_jammers,) or not np.isfinite(w).all() or (np.abs(w)>1).any():
            raise ValueError('One finite weight in [-1,1] is required per jammer')
        if isinstance(ris_index,bool) or not isinstance(ris_index,(int,np.integer)) or not 0<=ris_index<self.num_ris_configurations:
            raise ValueError('RIS index is outside the codebook')
        if self.control_mode!='joint':
            expected=self.fixed_configuration if self.control_mode=='fixed' else 0
            if ris_index!=expected:
                raise ValueError('The selected configuration is not available in this control mode')
            return w.copy()
        return np.r_[w,self._encode_index(int(ris_index))]

    def decode_action(self,action):
        if isinstance(action,bool):
            raise ValueError('A boolean is not an action index')
        if isinstance(action,(int,np.integer)):
            if not 0<=action<self.num_actions:
                raise ValueError('Action index is outside the discrete action space')
            vector=self.action_space[int(action)]
        else:
            vector=np.asarray(action,dtype=float)
        width=self.config.num_jammers+(self.control_mode=='joint')
        if vector.shape!=(width,) or not np.isfinite(vector).all() or (np.abs(vector)>1).any():
            raise ValueError(f'Action must have {width} finite coordinates in [-1,1]')
        w=vector[:self.config.num_jammers].copy()
        if self.control_mode=='joint':
            index=0 if self.num_ris_configurations==1 else int(round((vector[-1]+1)*(self.num_ris_configurations-1)/2))
            if abs(float(vector[-1])-self._encode_index(index))>1e-10:
                raise ValueError('RIS coordinate does not encode a discrete configuration')
        else:
            index=self.fixed_configuration if self.control_mode=='fixed' else 0
        return w,index

    def _geometry_key(self):
        return tuple(np.r_[self.bob_pos,self.eve_pos,self.config.alice_pos,
                            self.config.jammer_positions.ravel(),self.config.phi_half_deg,
                            self.config.fov_deg,self.config.n0,self.config.detector_area,
                            self.config.pd_responsivity,self.config.eta,self.config.num_leds_per_fixture])

    def _refresh_geometry(self):
        key=self._geometry_key()
        if key==self._direct_geometry:
            return
        self._direct_gains=self.channel_model.get_all_channel_gains(self.bob_pos,self.eve_pos)
        # Codebook geometry is explicitly reconstructed if receiver locations
        # are changed. Published studies initially use stationary scenarios.
        from .ris import OpticalRIS
        self.ris=OpticalRIS(self.config,self.ris_config,bob_pos=self.bob_pos,eve_pos=self.eve_pos)
        if int(self.ris.num_configurations)!=self.num_ris_configurations:
            raise ValueError('Changing geometry must not change the RIS codebook size')
        self._gain_cache={}
        self._direct_geometry=key

    def _gains_at(self,index):
        self._refresh_geometry()
        if index not in self._gain_cache:
            direct=self._direct_gains
            if self.control_mode=='off' or index==0:
                reflected=(0.,0.,np.zeros(self.config.num_jammers),np.zeros(self.config.num_jammers))
            else:
                reflected=self.ris.get_reflected_gains(index)
            effective=tuple(np.asarray(a)+np.asarray(b) for a,b in zip(direct,reflected))
            effective=(float(effective[0]),float(effective[1]),effective[2],effective[3])
            self._gain_cache[index]=(effective,reflected)
        return self._gain_cache[index]

    def _update_channel(self):
        if not getattr(self,'_ris_ready',False):
            return super()._update_channel()
        gains,_=self._gains_at(self._current_ris_index)
        self.h_AB,self.h_AE,self.h_JB,self.h_JE=gains

    def evaluate_action(self,action):
        w,index=self.decode_action(action)
        gains,reflected=self._gains_at(index)
        ab,ae,jb,je=gains
        cs=compute_secrecy_rate(*gains,w,self.config,self.sigma_B_sq)
        pe=compute_bob_ber(ab,jb,w,self.config,self.sigma_B_sq)
        energy=compute_energy_consumption(w,self.config)
        base=compute_system_utility(cs,pe,energy,self.config)
        violation=0. if self.qos_ber_max is None else max(0.,pe-self.qos_ber_max)
        return {'secrecy_rate':cs,'ber':pe,'energy':energy,
                'utility':base-self.qos_penalty*violation,'base_utility':base,
                'qos_violation':violation,'qos_feasible':bool(self.qos_ber_max is None or pe<=self.qos_ber_max),
                'beamformer':w.tolist(),'ris_index':index,'gains':gain_record(gains),
                'direct_gains':gain_record(self._direct_gains),'reflected_gains':gain_record(reflected)}

    def reset(self):
        self._current_ris_index=self.fixed_configuration if self.control_mode=='fixed' else 0
        return super().reset()

    def step(self,action):
        info=self.evaluate_action(action)
        self._current_ris_index=info['ris_index']
        self._update_channel()
        self.current_step+=1
        self.prev_pe=info['ber']
        self.prev_cs=info['secrecy_rate']
        self.prev_energy=info['energy']
        info['step']=self.current_step
        info['action']=self.encode_action(info['beamformer'],info['ris_index'])
        return self.get_state(),info['utility'],info

    def ris_metadata(self):
        self._refresh_geometry()
        return {**self.ris.metadata(),'control_mode':self.control_mode,
                'fixed_configuration':self.fixed_configuration,
                'num_ris_configurations':self.num_ris_configurations,
                'configuration_names':list(self.ris.configuration_names),
                'action_layout':{'beamformer_coordinates':self.config.num_jammers,
                                 'ris_coordinate':'normalized codebook index in [-1,1]' if self.control_mode=='joint' else None},
                'observation_layout':['previous_ber','previous_secrecy_rate','currently_installed_effective_h_AB','previous_energy'],
                'cnn_input_side':self.config.cnn_m0,
                'CSI_assumption':'Scenario geometry known exactly; codebook target positions are oracle simulation inputs',
                'channel_assumption':'Single-bounce scalar optical gains; no RIS delay/ISI or blockage added',
                'qos':{'ber_max':self.qos_ber_max,'penalty':self.qos_penalty,
                       'kind':'soft excess-BER penalty, not a hard service guarantee'},
                'RIS_energy':'Control/switching energy not included in the original paper utility; no total-energy gain claim'}

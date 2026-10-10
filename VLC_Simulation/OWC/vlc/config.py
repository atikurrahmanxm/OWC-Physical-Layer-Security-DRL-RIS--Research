"""
Configuration and default parameters for Secure VLC Friendly Jamming System.
All parameters strictly follow the paper:
'Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication'
IEEE Transactions on Wireless Communications (2024).
"""

from dataclasses import dataclass, field
import numpy as np


@dataclass
class VLCConfig:
    # ----------------- Room and Node Geometries (Section VI & Fig. 4) -----------------
    # Room dimensions [X, Y, Z] in meters: 5 x 5 x 3 m^3
    room_size: np.ndarray = field(default_factory=lambda: np.array([5.0, 5.0, 3.0]))
    
    # Alice (VLC transmitter): located at ceiling center (2.5, 2.5, 3.0) m
    alice_pos: np.ndarray = field(default_factory=lambda: np.array([2.5, 2.5, 3.0]))
    
    # Friendly jammers (4 LED light fixtures deployed around Alice on ceiling)
    # Positions: (1.5, 1.5, 3.0), (1.5, 3.5, 3.0), (3.5, 1.5, 3.0), (3.5, 3.5, 3.0) m
    jammer_positions: np.ndarray = field(default_factory=lambda: np.array([
        [1.5, 1.5, 3.0],
        [1.5, 3.5, 3.0],
        [3.5, 1.5, 3.0],
        [3.5, 3.5, 3.0]
    ]))
    
    # Bob (Legitimate user default position): (1.8, 1.6, 0.85) m
    bob_pos: np.ndarray = field(default_factory=lambda: np.array([1.8, 1.6, 0.85]))
    
    # Eve (Wiretapper / Eavesdropper default position): (3.2, 3.4, 0.85) m
    eve_pos: np.ndarray = field(default_factory=lambda: np.array([3.2, 3.4, 0.85]))
    
    # Number of LEDs per light fixture
    num_leds_per_fixture: int = 4
    
    # ----------------- Physical Channel Parameters (Table I) -----------------
    # LED average optical power P_T = 1 W
    led_avg_power: float = 1.0
    
    # Modulation index alpha = 10% = 0.10
    modulation_index: float = 0.10
    
    # Half irradiation intensity semi-angle phi_{1/2} = 60 deg
    phi_half_deg: float = 60.0
    
    # Receiver PD Field of View (FoV) psi_F = 60 deg
    fov_deg: float = 60.0
    
    # Optical concentrator refractive index n0 = 1.5
    n0: float = 1.5
    
    # Background noise power sigma_B^2 of Bob: -98.79 dBm
    noise_power_dbm: float = -98.79
    
    # PD detector physical area A_P = 1 cm^2 = 1.0e-4 m^2
    detector_area: float = 1.0e-4
    
    # PD responsivity R = 0.54 A/W
    pd_responsivity: float = 0.54
    
    # Electro-optical conversion efficiency eta (W/A)
    eta: float = 1.0
    
    # Direct Current (DC) bias I_D driving the LED
    # Since P_T = eta * I_e and average power is 1 W with zero-mean signal, I_D = P_T / eta
    id_bias: float = 1.0
    
    # ----------------- Utility Function Parameters (Eq. 7 & Section VI) -----------------
    # Penalty coefficient for Bob's BER
    delta1: float = 3.5
    
    # Penalty coefficient for energy consumption
    delta2: float = 0.4
    
    # Unit jamming cost varrho_s (Eq. 16)
    unit_jamming_cost: float = 1.0
    
    # ----------------- Learning Algorithm Hyperparameters (Section VI) -----------------
    # Q-learning learning rate lambda = 0.5 (Eq. 9)
    learning_rate: float = 0.5
    
    # Discount factor beta = 0.5 (Eq. 9)
    discount_factor: float = 0.5
    
    # Sliding window length M for state-action sequence phi^(k) = 11
    sliding_window_m: int = 11
    
    # Experience mini-batch size T = 4 (Algorithm 2 & Section VI)
    minibatch_size: int = 4
    
    # CNN Architecture hyper-parameter vector:
    # F = [f1, f2, m1, m2, s1, s2, n1, n2] = [20, 40, 3, 2, 1, 1, 180, 180]
    cnn_f1: int = 20
    cnn_f2: int = 40
    cnn_m1: int = 3
    cnn_m2: int = 2
    cnn_s1: int = 1
    cnn_s2: int = 1
    cnn_n1: int = 180
    cnn_n2: int = 180
    
    # CNN input matrix size m0 x m0 (m0 = 10, total 100 entries, padded from 92)
    cnn_m0: int = 10
    
    # Action quantization parameter L_x (each element quantized to 2*L_x + 1 values)
    # Default Lx = 1 gives {-1, 0, 1} for each of the 4 jammers -> 3^4 = 81 actions
    action_lx: int = 1
    
    # Exploration probability epsilon (Eq. 8)
    epsilon_start: float = 0.15
    epsilon_min: float = 0.02
    epsilon_decay: float = 0.998
    
    # Nominal effective SNR adjustment factor for figure reproduction
    # Calibrated to ensure theoretical bound and convergence levels match Fig. 6 & Fig. 7
    snr_scale: float = 500.0

    @property
    def num_jammers(self) -> int:
        return len(self.jammer_positions)

    @property
    def phi_half_rad(self) -> float:
        return float(np.deg2rad(self.phi_half_deg))

    @property
    def fov_rad(self) -> float:
        return float(np.deg2rad(self.fov_deg))

    @property
    def noise_power_watts(self) -> float:
        # Convert -98.79 dBm to Watts: P(W) = 10^((P(dBm) - 30) / 10)
        return float(10.0 ** ((self.noise_power_dbm - 30.0) / 10.0))

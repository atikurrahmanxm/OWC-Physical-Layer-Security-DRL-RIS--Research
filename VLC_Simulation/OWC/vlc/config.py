"""
Configuration and default parameters for Secure VLC Friendly Jamming System.
Table I values and Section VI hyperparameters follow the paper.
Additional numerical choices are explicit assumptions, not author-provided settings.
'Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication'
IEEE Transactions on Wireless Communications (2024).
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class VLCConfig:
    # paper: printed rate/BER equations; physical: one explicit 4-PAM channel.
    model: str = "paper"
    receiver_resistance_ohm: float = 1.0
    jammer_resistance_ohm: float = 1.0
    slot_duration_s: float = 1.0
    symbol_rate_per_hz: float = 1.0
    eve_noise_ratio: float = 1.0
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
    id_bias: Optional[float] = None
    
    # ----------------- Utility Function Parameters (Eq. 7 & Section VI) -----------------
    # Penalty coefficient for Bob's BER
    delta1: float = 3.5
    
    # Penalty coefficient for energy consumption
    delta2: float = 0.4
    
    # Unit jamming cost varrho_s (Eq. 16)
    unit_jamming_cost: float = 1.0

    # Nonnegative amplitude cost: a phase/sign change cannot generate energy.
    # This interprets the ambiguous printed Eq. (16); paper_signed is opt-in.
    energy_model: Optional[str] = None
    # SNR is the interference-free SINR inside Eq. (4). The author's Figure 7
    # normalization is unspecified; electrical retains the old convention.
    snr_definition: Optional[str] = None
    seed: int = 42
    cnn_learning_rate: float = 1e-2
    dnd_match_threshold: float = 0.0
    
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
    # Lx = 2 gives {-1.0, -0.5, 0.0, 0.5, 1.0} for each of the 4 jammers -> 5^4 = 625 actions
    action_lx: int = 2
    
    # Exploration probability epsilon (Eq. 8)
    epsilon_start: float = 0.15
    epsilon_min: float = 0.02
    epsilon_decay: float = 0.998

    def __post_init__(self):
        for name in ('room_size','alice_pos','bob_pos','eve_pos','jammer_positions'):
            value=np.asarray(getattr(self,name),dtype=float)
            if not np.all(np.isfinite(value)) or (value.shape != (3,) if name != 'jammer_positions' else
                    value.ndim != 2 or value.shape[1] != 3 or len(value) == 0):
                raise ValueError(f"Invalid {name} geometry")
            setattr(self,name,value)
        if not np.isfinite(self.noise_power_dbm):
            raise ValueError("Noise power in dBm must be finite")
        if self.model not in {"paper", "physical"}:
            raise ValueError("model must be paper or physical")
        if self.energy_model is None:
            self.energy_model = "electrical" if self.model == "physical" else "l1"
        if self.snr_definition is None:
            self.snr_definition = "modulated" if self.model == "physical" else "eq4"
        if not np.isfinite(self.eta) or self.eta <= 0:
            raise ValueError("eta must be finite and positive")
        if self.id_bias is None:
            self.id_bias = self.led_avg_power / self.eta
        if not isinstance(self.seed, int) or not 0 <= self.seed < 2**32:
            raise ValueError("seed must be an unsigned 32-bit integer")
        if not np.all(np.isfinite([self.delta1, self.delta2, self.unit_jamming_cost, self.dnd_match_threshold])):
            raise ValueError("Penalties and DND threshold must be finite")
        if self.dnd_match_threshold < 0:
            raise ValueError("DND match threshold must be nonnegative")
        if not 0 <= self.epsilon_min <= self.epsilon_start <= 1 or not 0 < self.epsilon_decay <= 1:
            raise ValueError("Invalid epsilon schedule")
        if self.energy_model not in {"paper_signed", "l1", "electrical"}:
            raise ValueError("energy_model must be paper_signed, l1 or electrical")
        if self.snr_definition not in {"electrical", "eq4", "pam", "modulated"}:
            raise ValueError("Unknown SNR definition")
        if self.model == "physical" and (self.energy_model != "electrical" or self.snr_definition != "modulated"):
            raise ValueError("physical model requires electrical energy and modulated SNR")
        if self.model == "paper" and self.energy_model == "electrical":
            raise ValueError("electrical energy is available with model=physical")
        if self.model == "paper" and (self.receiver_resistance_ohm != 1. or self.jammer_resistance_ohm != 1. or self.slot_duration_s != 1.):
            raise ValueError("Resistance and slot-duration conversions require model=physical; paper mode retains the legacy convention")
        for name in ("receiver_resistance_ohm", "jammer_resistance_ohm", "slot_duration_s", "symbol_rate_per_hz", "eve_noise_ratio"):
            if not np.isfinite(getattr(self, name)) or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.model == "physical" and (not np.isclose(self.eta*self.id_bias,self.led_avg_power,rtol=1e-12,atol=0) or self.unit_jamming_cost != 1.):
            raise ValueError("physical model requires eta*I_D=P_T and unit_jamming_cost=1; use delta2 for cost per joule")
        if self.action_lx < 1 or not isinstance(self.action_lx, int):
            raise ValueError("action_lx must be a positive integer")
        if not 0 < self.fov_deg < 90 or not 0 < self.phi_half_deg < 90:
            raise ValueError("FoV and LED semi-angle must be between 0 and 90 degrees")
        for name in ("led_avg_power", "eta", "id_bias", "detector_area", "pd_responsivity", "cnn_learning_rate"):
            if not np.isfinite(getattr(self, name)) or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not 0 < self.modulation_index <= 1:
            raise ValueError("modulation_index must be in (0, 1]")
        if self.delta1 < 0 or self.delta2 < 0 or self.unit_jamming_cost < 0:
            raise ValueError("Utility penalties and unit cost must be nonnegative")
        if self.sliding_window_m < 1 or self.minibatch_size < 1:
            raise ValueError("Sliding window and batch size must be positive")
        if self.cnn_m0**2 < self.sliding_window_m * (4 + self.num_jammers) + 4:
            raise ValueError("CNN input is too small for the state-action sequence")

    def noise_variance_from_snr(self, h_AB: float, snr_db: float) -> float:
        """Explicit assumptions: electrical=P_T*h**2/noise; eq4=Bob SINR
        inside Eq. (4); pam=squared interference-free erfc argument in Eq. (14);
        modulated=mean-square received 4-PAM current divided by current variance.
        None is claimed to be the authors' undocumented Figure 7 convention.
        """
        if h_AB <= 0 or not np.isfinite(snr_db):
            raise ValueError("An SNR override requires a positive Bob link and finite dB")
        if self.snr_definition == "electrical":
            signal = self.led_avg_power * h_AB**2
        elif self.snr_definition == "eq4":
            signal = 2 * h_AB**2 * self.modulation_index**2 * self.id_bias**2 / (np.pi * np.e)
        elif self.snr_definition == "pam":
            signal = 2 * self.led_avg_power * h_AB**2 / 5
        else:
            # Mean-square current of equiprobable levels {-A,-A/3,A/3,A}.
            signal = (5./9.) * (h_AB*self.modulation_index*self.id_bias)**2
        variance = float(signal / 10.0**(snr_db / 10.0))
        if not np.isfinite(variance) or variance <= 0:
            raise ValueError("SNR results in a nonpositive or nonfinite variance")
        return variance

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

    @property
    def noise_variance(self) -> float:
        """Physical mode: sampled receiver-current variance [A^2], P_noise/R.
        Paper mode retains the legacy numeric use of the Table I watt value.
        """
        return self.noise_power_watts / self.receiver_resistance_ohm if self.model == "physical" else self.noise_power_watts

    @property
    def max_jamming_energy(self) -> float:
        if self.model == "physical":
            return self.num_jammers * (self.modulation_index*self.id_bias)**2/3 * self.jammer_resistance_ohm*self.slot_duration_s
        return self.num_jammers*self.unit_jamming_cost

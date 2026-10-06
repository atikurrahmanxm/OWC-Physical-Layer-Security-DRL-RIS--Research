"""
Simulation Configuration and Physical Parameters.
Aligned with IEEE TWC (Sep 2024) paper:
"Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication"
and extended with Optical Reconfigurable Intelligent Surface (O-RIS).
"""

import numpy as np

class Config:
    # ----------------- Indoor Room Geometry -----------------
    ROOM_X = 5.0  # Length (m)
    ROOM_Y = 5.0  # Width (m)
    ROOM_Z = 3.0  # Height (m)

    # ----------------- Transmitter (Alice) -----------------
    # Commercial indoor LED ceiling luminaire array (400 lux standard)
    ALICE_POS = np.array([2.5, 2.5, 3.0])
    NUM_ALICE_LEDS = 80  # 80 LED chips per luminaire fixture for indoor room
    P_OPT_ALICE = 1.0    # Average optical power (W) per LED
    ID_BIAS = 1.0        # DC bias current (A)
    MODULATION_INDEX_ALPHA = 0.10  # 10%
    SEMI_ANGLE_HALF = np.deg2rad(60.0)  # phi_1/2 = 60 deg -> Lambertian m = 1
    ETA_EO = 1.0         # Electro-optical conversion efficiency (W/A)

    # ----------------- Friendly Jammers -----------------
    NUM_JAMMERS = 4
    JAMMER_POSITIONS = np.array([
        [1.25, 1.25, 3.0],
        [1.25, 3.75, 3.0],
        [3.75, 1.25, 3.0],
        [3.75, 3.75, 3.0]
    ])
    UNIT_JAMMING_COST = 0.1  # \varrho_s

    # ----------------- Receivers (Bob & Eve) -----------------
    DEFAULT_BOB_POS = np.array([1.8, 1.6, 0.85])   # User terminal (m)
    DEFAULT_EVE_POS = np.array([3.2, 3.4, 0.85])   # Eavesdropper (m)
    RECEIVER_HEIGHT = 0.85                         # Desk height (m)

    # Photodiode (PD) parameters (Wide-angle reception for indoor VLC)
    PD_AREA = 1.0e-4           # 1 cm^2 = 1e-4 m^2
    PD_FOV = np.deg2rad(75.0)  # FOV = 75 deg (wide-angle acceptance)
    PD_RESPONSIVITY = 0.54     # R = 0.54 A/W
    REFRACTIVE_INDEX_N0 = 1.5  # n0 = 1.5
    OPTICAL_FILTER_GAIN = 1.0  # Ts = 1.0

    # Noise powers (-98.79 dBm)
    NOISE_POWER_BOB = 10 ** ((-98.79 - 30.0) / 10.0)
    NOISE_POWER_EVE = 10 ** ((-98.79 - 30.0) / 10.0)

    # ----------------- Optical RIS (O-RIS) Parameters -----------------
    # Mounted on upper side wall (y = 5.0 m, z = 2.6 m) facing interior [0, -1, 0]
    RIS_CENTER = np.array([2.5, 5.0, 2.6])
    RIS_NORMAL = np.array([0.0, -1.0, 0.0])
    RIS_NUM_ELEMENTS_X = 4
    RIS_NUM_ELEMENTS_Z = 4
    RIS_TOTAL_ELEMENTS = RIS_NUM_ELEMENTS_X * RIS_NUM_ELEMENTS_Z  # 16 elements (can scale to 64)
    RIS_TOTAL_AREA = 0.25 * 0.25  # 0.0625 m^2
    RIS_ELEMENT_AREA = RIS_TOTAL_AREA / RIS_TOTAL_ELEMENTS
    RIS_REFLECTIVITY = 0.90       # 90% optical reflection efficiency
    RIS_ELEMENT_POWER = 0.02      # 20 mW per active RIS element control circuit
    RIS_DIVERGENCE_ANGLE = np.deg2rad(10.0)  # 10 deg narrow reflected pencil cone

    # ----------------- Modulation & PLS Metrics -----------------
    PAM_ORDER = 4  # 4-PAM
    DELTA_1 = 3.5  # BER weight in utility u(k)
    DELTA_2 = 0.4  # Energy consumption weight in utility u(k)

    # ----------------- Reinforcement Learning Parameters -----------------
    LEARNING_RATE_LAMBDA = 0.5
    DISCOUNT_FACTOR_BETA = 0.5
    EPSILON_START = 0.8
    EPSILON_END = 0.05
    EPSILON_DECAY = 0.998
    WINDOW_SIZE_M = 11      # Sliding history window size M = 11
    BATCH_SIZE_T = 4        # Experience mini-batch size T = 4
    MEMORY_CAPACITY = 2000

    # Jammer Action Quantization (from paper: 2*Lx + 1 values)
    LX = 2                  # w_i in {-1, -0.5, 0, 0.5, 1}
    ACTION_WEIGHTS_1D = np.linspace(-1.0, 1.0, 2 * LX + 1)

    # CNN Feature Extractor Hyperparameters F = [f1, f2, m1, m2, s1, s2, n1, n2]
    CNN_F1 = 20
    CNN_F2 = 40
    CNN_M1 = 3
    CNN_M2 = 2
    CNN_S1 = 1
    CNN_S2 = 1
    CNN_N1 = 180
    CNN_N2 = 180

    # Simulation Defaults
    DEFAULT_TIME_SLOTS = 2000
    RANDOM_SEED = 42

# Manuscript Supporting Tables

This document contains formatted Markdown tables for the manuscript on Joint Friendly Jamming and Optical Reconfigurable Intelligent Surface for Physical Layer Security in Visible Light Communication.

---

## Table I: Related Work Comparison Matrix

| Reference | Channel & Optics | Secrecy Mechanism | Optimization / Learning Method | Discrete / Continuous | QoS & Verification Protocol | Adverse / Boundary Analysis Disclosed |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Qian et al. (2021)** | Optical Mirror RIS, Snell Reflection | RIS Phase/Tilt Steering | Particle Swarm Optimization (PSO) | Continuous Orientations | Numerical Secrecy Rate | No (Assumes separated Eve) |
| **Saifaldeen et al. (2022)** | Optical IRS, Specular Reflection | Joint Beamforming & IRS | Deep Deterministic Policy Gradient (DDPG) | Continuous Actions | Secrecy Rate under Mobility | No |
| **Liu et al. (2024)** | Ceiling Direct LoS VLC | 4 Ceiling Friendly Jammers | Feature CNN + Differentiable Neural Dictionary (DND) | Discrete Jamming ($5^4=625$) | 4-PAM BER, Continuous Secrecy Rate (Eq. 4) | Infeasible cases not characterized |
| **Guo et al. (2026)** | Optical RIS + VLC | RIS-aided Jamming / Beamforming | Analytical / Convex Relaxation | Continuous / Discrete | Secrecy Capacity bounds | Partial |
| **This Work** | Optical Mirror RIS + Direct LoS VLC | **Joint 4-FJ & RIS Mirror Array** | **Joint Feature CNN + Episodic DND** | **Unified Discrete ($5^4 \times 5 = 3125$)** | **Frozen Greedy Evaluation ($\epsilon=0$), Bob $\text{BER} \le 10^{-3}$, 10-seed paired Student-$t$ CIs** | **Full Disclosure (Near-Bob \& Colocated $R_s = 0$, Exploration Penalty)** |

---

## Table II: Simulation & Optical Parameters (Baseline & RIS Extension)

| Parameter | Symbol | Value | Unit | Basis / Origin |
| :--- | :--- | :--- | :--- | :--- |
| Room Dimensions | $L \times W \times H$ | $5.0 \times 5.0 \times 3.0$ | $\text{m}$ | Table I (Liu et al., 2024) |
| Alice (Transmitter) Position | $\mathbf{p}_A$ | $(2.5, 2.5, 3.0)$ | $\text{m}$ | Table I (Liu et al., 2024) |
| Jammer Positions | $\mathbf{p}_{J_1}, \dots, \mathbf{p}_{J_4}$ | $(1.5, 1.5, 3.0), (1.5, 3.5, 3.0), (3.5, 1.5, 3.0), (3.5, 3.5, 3.0)$ | $\text{m}$ | Table I (Liu et al., 2024) |
| Nominal Bob Position | $\mathbf{p}_B$ | $(1.8, 1.6, 0.85)$ | $\text{m}$ | Table I (Liu et al., 2024) |
| Nominal Eve Position | $\mathbf{p}_E$ | $(3.2, 3.4, 0.85)$ | $\text{m}$ | Table I (Liu et al., 2024) |
| Near-Bob Eve Position | $\mathbf{p}_{E,\text{near}}$ | $(1.85, 1.65, 0.85)$ | $\text{m}$ | Adverse Boundary Study ($\sim 7\text{ cm}$ separation) |
| Colocated Eve Position | $\mathbf{p}_{E,\text{colo}}$ | $(1.8, 1.6, 0.85)$ | $\text{m}$ | Theoretical Wiretap Bound ($0\text{ cm}$ separation) |
| Semi-angle at Half Power | $\Phi_{1/2}$ | $60$ | $\text{deg}$ | Table I (Liu et al., 2024) |
| Lambertian Order | $m$ | $1.0$ | dimensionless | $-\ln 2 / \ln(\cos \Phi_{1/2})$ |
| Receiver Field of View (FoV) | $\Psi_c$ | $60$ | $\text{deg}$ | Table I (Liu et al., 2024) |
| Photodetector Physical Area | $A_{det}$ | $1.0 \times 10^{-4}$ | $\text{m}^2$ ($1.0\text{ cm}^2$) | Table I (Liu et al., 2024) |
| Optical Filter Gain | $T_s(\psi)$ | $1.0$ | dimensionless | Table I (Liu et al., 2024) |
| Refractive Index | $n_{lens}$ | $1.5$ | dimensionless | Table I (Liu et al., 2024) |
| Optical Concentrator Gain | $g(\psi)$ | $n_{lens}^2 / \sin^2(\Psi_c) = 3.0$ | dimensionless | For $0 \le \psi \le \Psi_c$ |
| Photodetector Responsivity | $R_{pd}$ | $0.54$ | $\text{A/W}$ | Table I (Liu et al., 2024) |
| Optical-to-Electrical Slope | $\eta$ | $1.0$ | $\text{W/A}$ | Table I (Liu et al., 2024) |
| LEDs per Luminaire | $N_{LED}$ | $4$ | dimensionless | Table I (Liu et al., 2024) |
| Noise Power Spectral Density | $\sigma^2$ | $1.3213 \times 10^{-13}$ ($-98.79\text{ dBm}$) | $\text{W}$ | Table I (Liu et al., 2024) |
| RIS Panel Center | $\mathbf{p}_{\text{RIS}}$ | $(2.5, 0.25, 2.6)$ | $\text{m}$ | North Wall High Mount |
| RIS Dimensions | $W_{\text{RIS}} \times H_{\text{RIS}}$ | $1.0 \times 0.5$ | $\text{m}$ | Total Area $0.5\text{ m}^2$ |
| RIS Tile Array Layout | $N_{\text{rows}} \times N_{\text{cols}}$ | $2 \times 3 = 6$ tiles | dimensionless | Specular Mirror Tiles |
| Individual Tile Dimensions | $w_{\text{tile}} \times h_{\text{tile}}$ | $0.333 \times 0.25$ | $\text{m}$ | Subdivided Mirror Surface |
| RIS Mirror Reflectivity | $\rho$ | $0.85$ | dimensionless | Aluminum/Dielectric Mirror |
| Jammer Weight Levels | $\mathcal{W}_k$ | $\{0.0, 0.25, 0.50, 0.75, 1.0\}$ | dimensionless | 5 levels per jammer ($5^4 = 625$) |
| RIS Orientation Codebook | $\mathcal{Q}$ | $\{q_0, q_1, q_2, q_3, q_4\}$ | dimensionless | 5 discrete aimed normal sets |
| Total Joint Action Space | $|\mathcal{A}|$ | $5^4 \times 5 = 3,125$ | dimensionless | Joint $(\mathbf{w}, q)$ combinations |
| DRL Feature CNN | Architecture | Conv2d ($m_1=3, f_1=20$) $\to$ Conv2d ($m_2=2, f_2=40$) $\to$ Flatten ($2560$) $\to$ FC ($180 \times 180$) | Table I (Liu et al., 2024), adapted with $m_0=11$ |
| Sliding Observation Window | $M$ | $11$ slots | Table I (Liu et al., 2024) |
| DND Match Threshold | $\delta$ | $0.0$ | Exact $L_2$ state-key matching |
| Learning Rate ($\alpha$), Discount ($\gamma$) | $\alpha, \gamma$ | $0.5, 0.5$ | Table I (Liu et al., 2024) |
| Exploration Epsilon | $\epsilon_{\text{start}}, \epsilon_{\text{min}}, \lambda_{\epsilon}$ | $0.15 \to 0.02$, decay $0.998$ | Training only; $\epsilon=0$ during evaluation |
| Training Horizon | $T_{\text{train}}$ | $2,000$ | slots | Per seed |
| Evaluation Horizon | $T_{\text{eval}}$ | $1,000$ | slots | Frozen policy, $\epsilon=0$, zero updates |

---

## Table III: RIS Codebook Configurations ($\mathcal{Q}$)

| Code | Label | Aiming Vector / Optimization Target | Functional Role in Wiretap Channel |
| :---: | :--- | :--- | :--- |
| $q_0$ | Stowed / Neutral | Mirror normal fixed to room inward normal $[0, 1, 0]^T$ | Flat specular reflection without directional concentration |
| $q_1$ | Bob-Centric | Focuses Alice transmitter path directly onto Bob | Maximizes direct signal power at legitimate receiver ($h_{AB}$) |
| $q_2$ | Eve-Centric | Focuses jammer centroid path directly onto Eve | Maximizes artificial noise power at eavesdropper ($h_{JE}$) |
| $q_3$ | Compromise / Min-Leak | Angle bisector maximizing Bob channel while steering away from Eve | Balances signal enhancement with eavesdropper leakage minimization |
| $q_4$ | Targeted Jammer | Focuses nearest jammer fixture directly onto Eve | Concentrates localized jamming energy into eavesdropper field |


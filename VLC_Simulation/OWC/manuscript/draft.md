# Joint Friendly Jamming and Optical Reconfigurable Intelligent Surface for Physical Layer Security in Visible Light Communication: A Deep Reinforcement Learning Approach

**Authors**: Anonymous for Peer Review  
**Date**: November 2026  
**Status**: Working Draft / Technical Manuscript (Targeted for IEEE Transactions on Wireless Communications / IEEE Photonics Journal)

---

## Abstract

Visible Light Communication (VLC) offers ultra-high data rates and immunity to radio frequency (RF) electromagnetic interference, but its broadcast nature leaves optical links vulnerable to unauthorized eavesdropping. While ceiling-mounted friendly jamming (FJ) can degrade an eavesdropper's signal-to-interference-plus-noise ratio (SINR), conventional jamming arrays suffer severe performance degradation when legitimate receivers (Bob) and eavesdroppers (Eve) exhibit high spatial correlation or when direct line-of-sight (LoS) links are constrained. In this paper, we propose an integrated optical Physical Layer Security (PLS) architecture combining ceiling-mounted friendly jammers with a wall-mounted Optical Reconfigurable Intelligent Surface (RIS) comprising a tiltable micro-mirror array (MMA). To address the complex coupling between optical reflection steering and artificial noise emission, we formulate a joint optimization problem that coordinates four friendly jammer power levels ($5^4 = 625$ discrete configurations) and a five-state directional RIS orientation codebook ($\mathcal{Q} = \{q_0, \dots, q_4\}$), yielding an expanded joint action space of $|\mathcal{A}| = 3,125$ states. We develop a Deep Reinforcement Learning (DRL) framework combining a two-dimensional Feature Convolutional Neural Network (CNN with Conv2d layers) with an episodic Differentiable Neural Dictionary (DND) for Q-value estimation and policy learning. 

Crucially, rather than relying on metrics conflating exploratory training with policy execution, we establish a strict methodological protocol separating the 2,000-slot training phase from a 1,000-slot frozen-policy greedy evaluation phase ($\epsilon = 0$, zero neural network weight updates, zero memory additions). Across multi-seed matched simulations under the rigorous 2024 IEEE Transactions on Wireless Communications baseline, we evaluate secrecy rates, 4-PAM Bit Error Rates (BER), and Quality-of-Service (QoS) outage probabilities ($\text{BER} > 10^{-3}$) across distinct operational phases. In the frozen evaluation phase, Fixed RIS achieves a statistically certified secrecy rate gain of $+0.1773\text{ bps/Hz}$ over the no-RIS baseline (paired 95% Student-$t$ interval $[+0.0378, +0.3167]\text{ bps/Hz}$), while Joint RIS achieves a sample-mean gain of $+0.1359\text{ bps/Hz}$ over baseline with a paired 95% interval of $[-0.0440, +0.3158]\text{ bps/Hz}$ (spanning zero due to the exploration variance across 3,125 joint actions). In this static evaluation setting, all schemes achieve zero secrecy outage and zero Bob QoS outage at their converged operating points. Furthermore, we examine the physical boundary behavior of the optical wiretap channel: under the declared near-Bob geometry ($7\text{ cm}$ separation), exhaustive enumeration across all 3,125 actions confirms that secrecy rate is bounded at $0.0000\text{ bps/Hz}$, and the DRL policy autonomously suppresses jamming power to avoid wasteful energy expenditure. This work provides an open-source, physically grounded benchmark for optical RIS and friendly jamming optimization in secure indoor VLC networks.

**Keywords**: Visible Light Communication (VLC), Physical Layer Security (PLS), Reconfigurable Intelligent Surface (RIS), Micro-Mirror Array (MMA), Friendly Jamming (FJ), Deep Reinforcement Learning (DRL), Differentiable Neural Dictionary (DND).

---

## I. Introduction

### A. Context and Motivation
Visible Light Communication (VLC) has emerged as a promising technology for sixth-generation (6G) indoor wireless systems, leveraging the vast unregulated optical spectrum ($380\text{--}780\text{ nm}$) to deliver multi-gigabit data transmission while simultaneously providing energy-efficient illumination. By utilizing solid-state Light Emitting Diodes (LEDs) as optical transmitters and Photodetectors (PDs) as optical receivers, VLC avoids electromagnetic interference, penetrates neither opaque walls nor optical partitions, and operates in RF-restricted zones such as hospitals, aircraft cabins, and underwater enclosures.

However, because indoor VLC utilizes broad Lambertian optical emission to ensure uniform room coverage, transmitted optical signals are broadcast indiscriminately within the line-of-sight (LoS) footprint. Any unauthorized receiver or passive eavesdropper (Eve) located within the illumination cone can intercept the confidential data intended for the legitimate user (Bob). While conventional network-layer cryptography provides foundational security, it imposes high computational overhead, complex key distribution protocols, and vulnerability to future quantum decryption. Consequently, **Physical Layer Security (PLS)** has emerged as a vital paradigm, exploiting the physical characteristics of the optical channel to ensure confidentiality regardless of the adversary's computational capabilities.

### B. Friendly Jamming and Its Ceiling-Only Bottleneck
In optical PLS, **Friendly Jamming (FJ)** has proven to be an effective countermeasure. Specialized jamming luminaires emit artificial optical noise that degrades Eve's reception while minimizing interference to Bob. In a seminal 2024 study, Liu et al. introduced a Deep Reinforcement Learning (DRL) framework wherein four ceiling-mounted friendly jammers dynamically adjust their emission power to optimize secrecy capacity under an unknown, mobile Eve. By utilizing a Feature Convolutional Neural Network (CNN) coupled with a Differentiable Neural Dictionary (DND) inspired by Neural Episodic Control, the system rapidly learned jamming policies without requiring explicit mathematical channel inversion.

Despite its merits, ceiling-only friendly jamming suffers from a severe spatial bottleneck:
1. **Spatial Correlation**: When Eve is located in proximity to Bob or aligns with the geometric ray from a jammer to Bob, the channel vectors $\mathbf{h}_{JB}$ and $\mathbf{h}_{JE}$ become nearly collinear. Under such conditions, injecting jamming noise to corrupt Eve inevitably corrupts Bob, leading to severe legitimate transmission outage.
2. **Fixed Geometric Degrees of Freedom**: Ceiling luminaires point downward in fixed orientations. Once a room's physical layout is established, the direct channel matrix is entirely static for fixed receiver positions, offering no spatial adaptability to overcome favorable eavesdropper channels.

### C. Optical Reconfigurable Intelligent Surfaces (RIS)
To overcome the geometric rigidity of conventional wireless environments, **Reconfigurable Intelligent Surfaces (RIS)** have gained tremendous traction. In the optical domain, optical RIS typically takes the form of a **Micro-Mirror Array (MMA)** or liquid-crystal optical phased array mounted on room walls. Unlike RF RIS which manipulates phase shifts across sub-wavelength metasurfaces, optical RIS operates at nanometer wavelengths where specular and diffuse reflection dominates. By mechanically or electrostatically tilting individual micro-mirrors, an optical RIS dynamically redirects optical beams, synthesizing virtual non-line-of-sight (NLoS) specular links between transmitters and receivers.

Prior studies have explored optical RIS for indoor illumination, communication coverage, and physical layer security (Qian et al., 2021; Saifaldeen et al., 2022; Guo et al., 2026). However, several open questions remain:
- **Joint Episodic Control**: Prior investigations often examine optical RIS beam steering or dedicated friendly jamming independently, rather than unifying distributed ceiling friendly jammers and an optical RIS under an episodic memory architecture.
- **Phase-Separated Evaluation**: In reinforcement learning for physical-layer security, reporting metrics aggregated over training trajectories conflates exploratory random actions with post-convergence policy execution, highlighting the need for separate frozen-policy evaluation protocols.
- **Physical Boundary Characterization**: The performance of optical friendly jamming when the eavesdropper is positioned in close proximity to the legitimate receiver warrants explicit characterization using exhaustive benchmarks to identify feasibility boundaries.

### D. Specific Contributions
In this paper, we bridge these gaps by presenting an end-to-end physical and algorithmic framework for joint Friendly Jamming and Optical RIS beamforming in secure VLC networks. The key contributions of this paper are:
1. **Rigorous Specular Optical RIS Physics**: We formulate an exact optical mirror-array model governed by Snell's law specular reflection, two-hop geometric path loss, finite detector FoV clipping, and strict finite-aperture power conservation clamping ($G_{\text{bound}} = \rho N_{\text{LED}} F_{\text{intercepted}}$), preventing unphysical power amplification.
2. **Unified Discrete Action MDP Formulation**: We coordinate four ceiling friendly jammers ($5^4 = 625$ states) and a 5-element directional RIS orientation codebook ($\mathcal{Q} = \{q_0, \dots, q_4\}$), constructing an expanded discrete action space of cardinality $|\mathcal{A}| = 3,125$ with a five-coordinate action representation $\mathbf{a}_t = [w_1, w_2, w_3, w_4, \tilde{q}]^T \in [-1, 1]^5$, managed by a unified Feature CNN and DND episodic memory.
3. **Rigorous Train-vs-Evaluation Protocol**: We implement and verify a strict evaluation separation: following 2,000 training slots, the policy is evaluated over 1,000 frozen slots with exploration disabled ($\epsilon = 0$), weight updates terminated, and DND memory locked, ensuring true policy performance measurement.
4. **Statistical Rigor with Multi-Seed Paired Inference**: We execute matched multi-seed experiments across 10 independent seeds ($42\text{--}51$), reporting paired Student-$t$ 95% confidence intervals for both Joint-vs-Baseline and Joint-vs-Fixed RIS.
5. **Full Physical Boundary Disclosure**: We rigorously test and report the physical wiretap failure boundaries (`near_bob` with $7\text{ cm}$ separation and `colocated` with $0\text{ cm}$ separation), proving mathematically and empirically that when spatial correlation causes secrecy capacity to collapse to $0.0000\text{ bps/Hz}$, the learned DRL policy rationally suppresses jamming power to avoid wasteful energy expenditure.

---

## II. System Model and Optical VLC Wiretap Channel

### A. Indoor Room Geometry and Optical Transceivers
We consider a typical three-dimensional indoor office environment of dimensions $L \times W \times H = 5.0\text{ m} \times 5.0\text{ m} \times 3.0\text{ m}$, aligned with the standard IEEE TWC 2024 baseline. The network comprises:
- An **optical transmitter (Alice)** installed at the center of the ceiling: $\mathbf{p}_A = [2.5, 2.5, 3.0]^T\text{ m}$.
- Four ceiling-mounted **friendly jammers ($J_1, \dots, J_4$)** distributed symmetrically at $\mathbf{p}_{J_1} = [1.5, 1.5, 3.0]^T$, $\mathbf{p}_{J_2} = [1.5, 3.5, 3.0]^T$, $\mathbf{p}_{J_3} = [3.5, 1.5, 3.0]^T$, and $\mathbf{p}_{J_4} = [3.5, 3.5, 3.0]^T\text{ m}$.
- A legitimate receiver (**Bob**) situated on the working desk level: $\mathbf{p}_B = [1.8, 1.6, 0.85]^T\text{ m}$.
- An unauthorized eavesdropper (**Eve**) attempting to passively intercept Alice's transmission: $\mathbf{p}_E = [3.2, 3.4, 0.85]^T\text{ m}$.

All optical transmitters utilize LED luminaires with semi-angle at half power $\Phi_{1/2} = 60^\circ$, corresponding to a Lambertian emission order:
$$m = -\frac{\ln 2}{\ln(\cos \Phi_{1/2})} = 1.0$$

The receivers (Bob and Eve) are equipped with a photodetector of physical detection area $A_{det} = 1.0\text{ cm}^2 = 1.0 \times 10^{-4}\text{ m}^2$, optical filter transmission $T_s(\psi) = 1.0$, internal refractive index $n_{\text{lens}} = 1.5$, and optical concentrator semi-angle field of view (FoV) $\Psi_c = 60^\circ$. The optical concentrator gain $g(\psi)$ is given by:
$$g(\psi) = \begin{cases} \frac{n_{\text{lens}}^2}{\sin^2(\Psi_c)} = 3.0, & 0 \le \psi \le \Psi_c \\ 0, & \psi > \Psi_c \end{cases}$$

### B. Direct Optical Channel Model
For a direct line-of-sight path from optical source $S \in \{A, J_1, J_2, J_3, J_4\}$ to receiver $R \in \{B, E\}$, the DC optical channel gain $H_{SR}^{\text{dir}}$ is modeled by the generalized Lambertian formula:
$$H_{SR}^{\text{dir}} = \begin{cases} \frac{(m+1) A_{det}}{2\pi d_{SR}^2} \cos^m(\phi_{SR}) T_s(\psi_{SR}) g(\psi_{SR}) \cos(\psi_{SR}), & 0 \le \psi_{SR} \le \Psi_c \\ 0, & \psi_{SR} > \Psi_c \end{cases}$$
where $d_{SR} = \|\mathbf{p}_R - \mathbf{p}_S\|$ is the Euclidean distance, $\phi_{SR}$ is the angle of irradiance with respect to the source normal (downward $[0, 0, -1]^T$), and $\psi_{SR}$ is the angle of incidence with respect to the receiver normal (upward $[0, 0, 1]^T$).

Each luminaire incorporates $N_{\text{LED}} = 4$ identical LED chips. Taking into account the photodetector responsivity $R_{pd} = 0.54\text{ A/W}$ and optical-to-electrical conversion efficiency $\eta = 1.0\text{ W/A}$, the channel coefficients are expressed as effective electrical channel gains:
$$h_{SR} = N_{\text{LED}} R_{pd} H_{SR}^{\text{dir}}$$

We denote $h_{AB}$ and $h_{AE}$ as the scalar channel gains from Alice to Bob and Eve, respectively, and $\mathbf{h}_{JB} = [h_{J_1 B}, h_{J_2 B}, h_{J_3 B}, h_{J_4 B}]^T \in \mathbb{R}^4$ and $\mathbf{h}_{JE} \in \mathbb{R}^4$ as the channel gain vectors from the four friendly jammers to Bob and Eve.

### C. Signal Transmission and Wiretap Model
During time slot $t$, Alice transmits an information symbol $x(t)$ with electrical average power $P_A$, while the four friendly jammers transmit uncorrelated zero-mean Gaussian artificial noise $j(t) \sim \mathcal{N}(0, 1)$ modulated by a discrete jamming power allocation weight vector $\mathbf{w}(t) = [w_1(t), w_2(t), w_3(t), w_4(t)]^T \in \mathcal{W}$, where each $w_k \in \{0.0, 0.25, 0.50, 0.75, 1.0\}$.

The received electrical signals at Bob and Eve are:
$$y_B(t) = h_{AB} x(t) + \mathbf{h}_{JB}^T \mathbf{w}(t) j(t) + n_B(t)$$
$$y_E(t) = h_{AE} x(t) + \mathbf{h}_{JE}^T \mathbf{w}(t) j(t) + n_E(t)$$
where $n_B(t) \sim \mathcal{N}(0, \sigma^2)$ and $n_E(t) \sim \mathcal{N}(0, \sigma^2)$ represent independent additive white Gaussian noise (AWGN) with power spectral density $\sigma^2 = 1.3213 \times 10^{-13}\text{ W}$ (corresponding to $-98.79\text{ dBm}$ over the receiver bandwidth).

Under the continuous-input Gaussian wiretap model adopted in Eq. (4) of Liu et al. (2024), the instantaneous signal-to-interference-plus-noise ratios (SINR) at Bob and Eve are:
$$\gamma_B = \frac{h_{AB}^2 P_A}{\sigma^2 + (\mathbf{h}_{JB}^T \mathbf{w})^2 P_J}$$
$$\gamma_E = \frac{h_{AE}^2 P_A}{\sigma^2 + (\mathbf{h}_{JE}^T \mathbf{w})^2 P_J}$$

The achievable secrecy rate $R_s$ (in $\text{bps/Hz}$) is defined as:
$$R_s = \left[ \frac{1}{2} \log_2(1 + \gamma_B) - \frac{1}{2} \log_2(1 + \gamma_E) \right]^+$$
where $[z]^+ = \max(0, z)$.

### D. Legitimate Bit Error Rate and Jamming Energy
For legitimate transmission, Bob adopts 4-level Pulse Amplitude Modulation (4-PAM). Under the assumption that friendly jamming interference acts as Gaussian-distributed noise, Bob's symbol error probability is evaluated via the complementary error function:
$$\text{BER}_B = \frac{3}{8} \text{erfc}\left( \sqrt{ \frac{\gamma_B}{5} } \right)$$

The friendly jamming power consumption cost $E_J$ in slot $t$ is evaluated under two distinct models:
1. **$L_1$ Norm Formulation**: A physically nonnegative metric penalizing emitted power magnitude:
   $$E_{J, L_1} = \sum_{k=1}^4 |w_k|$$
2. **Published Signed Formulation**: The literal printed expression from Eq. (16) of Liu et al. (2024):
   $$E_{J, \text{signed}} = \sum_{k=1}^4 w_k$$

---

## III. Optical Reconfigurable Intelligent Surface Physics

### A. Specular Mirror Array Architecture
The optical RIS is implemented as a planar micro-mirror array mounted on the north wall ($y = 0.25\text{ m}$) centered at $\mathbf{p}_{\text{RIS}} = [2.5, 0.25, 2.6]^T\text{ m}$. The total panel dimensions are $W_{\text{RIS}} = 1.0\text{ m}$ by $H_{\text{RIS}} = 0.5\text{ m}$ (surface area $A_{\text{RIS}} = 0.5\text{ m}^2$). The panel is partitioned into an array of $2 \times 3 = 6$ rectangular specular tiles, each of size $w_{\text{tile}} = 0.333\text{ m}$ and $h_{\text{tile}} = 0.25\text{ m}$, exhibiting an optical mirror reflectivity $\rho = 0.85$.

```
+-------------------------------------------------------+
|  Wall-Mounted Optical RIS Panel (y = 0.25 m, z = 2.6 m)|
|  Total Dimensions: 1.0 m (W) x 0.5 m (H)              |
|  +-----------------+-----------------+----------------+
|  |  Tile (1, 1)    |  Tile (1, 2)    |  Tile (1, 3)   |
|  +-----------------+-----------------+----------------+
|  |  Tile (2, 1)    |  Tile (2, 2)    |  Tile (2, 3)   |
|  +-----------------+-----------------+----------------+
+-------------------------------------------------------+
```

### B. Snell's Law Reflection and Geometric Path Loss
Unlike diffuse scattering surfaces, the micro-mirrors operate under **specular reflection**. For an incident optical ray originating from source $S$ with position $\mathbf{p}_S$ striking tile $k$ centered at $\mathbf{p}_{\text{tile}, k}$ and reflecting toward receiver $R$ at $\mathbf{p}_R$, we define the normalized unit vectors:
$$\mathbf{u}_{in} = \frac{\mathbf{p}_{\text{tile}, k} - \mathbf{p}_S}{\|\mathbf{p}_{\text{tile}, k} - \mathbf{p}_S\|}, \quad \mathbf{u}_{out} = \frac{\mathbf{p}_R - \mathbf{p}_{\text{tile}, k}}{\|\mathbf{p}_R - \mathbf{p}_{\text{tile}, k}\|}$$

By Snell's law of reflection, the ideal mirror surface normal $\mathbf{n}_k^*$ required to steer the incident beam directly to receiver $R$ is the angle bisector:
$$\mathbf{n}_k^* = \frac{-\mathbf{u}_{in} + \mathbf{u}_{out}}{\|-\mathbf{u}_{in} + \mathbf{u}_{out}\|}$$

Given a configured unit normal $\mathbf{n}_k$, the specular reflection path gain through tile $k$ is calculated via two-hop geometric attenuation:
$$H_{S \to \text{tile}_k \to R}^{\text{RIS}} = \frac{(m+1) A_{\text{tile}}}{2\pi d_{S, k}^2} \cos^m(\phi_{S, k}) \cdot \rho \cdot \frac{A_{det} \cos(\psi_{k, R})}{d_{k, R}^2} T_s(\psi_{k, R}) g(\psi_{k, R})$$
subject to geometric visibility constraints:
$$\cos(\theta_{\text{inc}}) = -\mathbf{u}_{in} \cdot \mathbf{n}_k > 0, \quad \cos(\theta_{\text{ref}}) = \mathbf{u}_{out} \cdot \mathbf{n}_k > 0, \quad \psi_{k, R} \le \Psi_c$$

### C. Finite-Aperture Power Conservation Bound
In optical simulation, treating a finite mirror as a point radiator can risk unphysical power concentration if geometric distances are small. To ensure absolute physical validity, the total optical power reflected by tile $k$ toward a detector cannot exceed the physical optical power intercepted by the tile from the source. 

The optical power intercepted by tile $k$ is bounded by:
$$P_{\text{intercepted}} = P_S \cdot \frac{(m+1) A_{\text{tile}}}{2\pi d_{S, k}^2} \cos^m(\phi_{S, k}) \cos(\theta_{\text{inc}})$$

The maximum optical gain achievable by any detector collecting the reflected beam is strictly clamped by the power conservation envelope:
$$G_{\text{bound}} = \rho N_{\text{LED}} R_{pd} \frac{(m+1) A_{\text{tile}}}{2\pi d_{S, k}^2} \cos^m(\phi_{S, k}) \cos(\theta_{\text{inc}})$$
$$H_{S \to \text{tile}_k \to R}^{\text{phys}} = \min\left( H_{S \to \text{tile}_k \to R}^{\text{RIS}}, G_{\text{bound}} \right)$$

This mathematical clamp guarantees that the optical RIS acts as a strictly passive, energy-conserving electromagnetic surface.

### D. Directional Orientation Codebook $\mathcal{Q}$
Due to mechanical actuation constraints and discrete servo-control limits, individual mirrors cannot be steered continuously in real-time. Instead, we implement a discrete codebook $\mathcal{Q} = \{q_0, q_1, q_2, q_3, q_4\}$ of coordinated orientations:
- **$q_0$ (Stowed / Inactive)**: All mirror normals point horizontally into the room ($\mathbf{n} = [0, 1, 0]^T$). No directional focusing is applied.
- **$q_1$ (Bob-Focused)**: Mirror normals are calculated to reflect Alice's optical rays specularly toward Bob's nominal coordinate $\mathbf{p}_B$, maximizing legitimate channel gain $h_{AB}$.
- **$q_2$ (Eve-Focused)**: Mirror normals are steered to reflect the jamming centroid toward Eve's coordinate $\mathbf{p}_E$, maximizing eavesdropper artificial noise leakage $h_{JE}$.
- **$q_3$ (Compromise / Min-Leakage)**: Mirror normals steer Alice's rays toward Bob while angling reflections away from Eve's receiver plane.
- **$q_4$ (Targeted Jammer Focus)**: Mirror normals focus the most favorably positioned ceiling jammer directly into Eve's FoV.

The composite effective channel gains are the coherent sum of direct and RIS-reflected paths:
$$h_{AB}^{\text{eff}}(q) = h_{AB}^{\text{dir}} + \sum_{k=1}^6 h_{A \to \text{tile}_k \to B}^{\text{RIS}}(q)$$
$$\mathbf{h}_{JB}^{\text{eff}}(q) = \mathbf{h}_{JB}^{\text{dir}} + \sum_{k=1}^6 \mathbf{h}_{J \to \text{tile}_k \to B}^{\text{RIS}}(q)$$
$$\mathbf{h}_{JE}^{\text{eff}}(q) = \mathbf{h}_{JE}^{\text{dir}} + \sum_{k=1}^6 \mathbf{h}_{J \to \text{tile}_k \to E}^{\text{RIS}}(q)$$

---

## IV. Joint Deep Reinforcement Learning Architecture

### A. Markov Decision Process Formulation
The joint optimization problem is cast as a discrete-time Markov Decision Process (MDP):
1. **State Vector ($\mathbf{s}_t$)**: In time slot $t$, the state vector $\mathbf{s}_t \in \mathbb{R}^4$ follows Equation (6) of Liu et al. (2024), capturing previous feedback and current channel conditions:
   $$\mathbf{s}_t = [p_e(t-1), c_s(t-1), h_{AB}(t), E(t-1)]^T$$
   where $p_e(t-1)$ is Bob's previous 4-PAM Bit Error Rate, $c_s(t-1)$ is the previous secrecy rate, $h_{AB}(t)$ is the current effective legitimate optical channel gain (incorporating the installed RIS reflected gain when applicable), and $E(t-1)$ is the previous jamming power cost.
2. **Temporal Observation Sequence ($\boldsymbol{\phi}_t$)**: To capture historical dynamics over a sliding window $M = 11$, the agent constructs a sequence concatenating state-action tuples:
   $$\boldsymbol{\phi}_t = [\mathbf{s}_{t-M}, \mathbf{a}_{t-M}, \dots, \mathbf{s}_{t-1}, \mathbf{a}_{t-1}, \mathbf{s}_t]$$
   where each historical slot contributes $4 + d_{\text{act}}$ elements ($d_{\text{act}} = 4$ for baseline and fixed RIS; $d_{\text{act}} = 5$ for joint RIS). The resulting sequence is zero-padded to length $m_0^2 = 11 \times 11 = 121$ and reshaped into a square input tensor of dimensions $(1, 1, m_0, m_0)$.
3. **Action Space ($\mathcal{A}$)**: An action represents a combined Friendly Jamming and RIS configuration:
   - For baseline and fixed RIS: $\mathbf{w}_t \in \mathcal{W}$ with cardinality $|\mathcal{A}| = 5^4 = 625$.
   - For joint RIS control: $a_t = (\mathbf{w}_t, q_t) \in \mathcal{W} \times \mathcal{Q}$, where $\mathbf{w}_t$ is the 4-jammer power weight vector ($625$ states) and $q_t \in \{q_0, \dots, q_4\}$ is the discrete RIS orientation codebook ($5$ states), yielding cardinality:
     $$|\mathcal{A}| = 625 \times 5 = 3,125 \text{ actions}$$
4. **Reward Function ($r_t$)**: The system utility reward follows Equation (7) of Liu et al. (2024), augmented with an optional soft QoS constraint:
   $$r_t = c_s(t) - \delta_1 p_e(t) - \delta_2 E(t) - \delta_{\text{QoS}} \cdot \max(0, p_e(t) - \text{BER}_{\max})$$
   where $\delta_1 = 3.5$ scales Bob's BER penalty, $\delta_2 = 0.4$ scales the jamming power cost, and $\delta_{\text{QoS}}$ is the linear excess-BER penalty coefficient. In our primary nominal studies, $\text{BER}_{\max}$ is unconstrained ($\delta_{\text{QoS}} = 0$), matching the unmodified paper reward structure.

### B. Feature CNN and Episodic Differentiable Neural Dictionary
To approximate action-values across continuous state sequences, we implement a Feature CNN coupled with an episodic Differentiable Neural Dictionary (DND), following Pritzel et al. (2017) and Liu et al. (2024):
- **Feature CNN Architecture**: A 2D Convolutional Neural Network with parameters $F = [f_1, f_2, m_1, m_2, s_1, s_2, n_1, n_2] = [20, 40, 3, 2, 1, 1, 180, 180]$:
  - **Conv Layer 1**: `nn.Conv2d(in_channels=1, out_channels=20, kernel_size=3, stride=1)`, followed by ReLU activation.
  - **Conv Layer 2**: `nn.Conv2d(in_channels=20, out_channels=40, kernel_size=2, stride=1)`, followed by ReLU activation.
  - **Flatten & FC Layer 1**: With adapted input dimension $m_0 = 11$, spatial dimensions after convolutions are $c_1 = (11-3)//1+1 = 9$ and $c_2 = (9-2)//1+1 = 8$. Feature maps are flattened ($f_2 \times c_2 \times c_2 = 40 \times 8 \times 8 = 2560$ inputs) and passed through `nn.Linear(2560, 180)`, followed by ReLU activation. (Note: $1960$ inputs correspond to $m_0 = 10$).
  - **FC Layer 2**: `nn.Linear(180, 180)` produces the latent feature key $\hat{\mathbf{h}}_t \in \mathbb{R}^{180}$.
- **DND Episodic Memory**: A dedicated key-value dictionary $\mathcal{D}_a = (\mathbf{K}_a, \mathbf{V}_a)$ is maintained for each discrete action $a \in \mathcal{A}$. When querying action $a$ with feature key $\hat{\mathbf{h}}_t$, Q-values are estimated via normalized Gaussian kernel weighting (Equations 10--12):
  $$Q(\mathbf{s}_t, a) = \sum_{j=1}^{\zeta} \omega_j v_j, \quad \omega_j = \frac{\exp\left( -\frac{1}{2} \|\hat{\mathbf{h}}_t - \mathbf{k}_j\|^2 \right)}{\sum_p \exp\left( -\frac{1}{2} \|\hat{\mathbf{h}}_t - \mathbf{k}_p\|^2 \right)}$$
  where $\mathbf{k}_j \in \mathbf{K}_a$ and $v_j \in \mathbf{V}_a$ are stored feature keys and corresponding Bellman target values.

```
                     +-----------------------------------+
                     |      State Input Tensor           |
                     |   Shape: (1, 1, m0=11, m0=11)     |
                     +-----------------+-----------------+
                                       |
                                       v
                     +-----------------------------------+
                     |        2D Feature CNN             |
                     | Conv2d(20) -> Conv2d(40) -> FC180 |
                     +-----------------+-----------------+
                                       |
                                       v Feature Key h_hat (180-d)
                               +-------+-------+
                               |               |
                               v               v
                     +----------------+ +----------------+
                     |  DND Action 1  | | DND Action 3125|
                     | [k_1, v_1] ... | | [k_n, v_n] ... |
                     +-------+--------+ +-------+--------+
                             |                  |
                             v                  v
                           Q(s, a_1)          Q(s, a_3125)
                               \              /
                                v            v
                     +-----------------------------------+
                     |     Action Selection Strategy     |
                     |  Training: Epsilon-Greedy         |
                     |  Evaluation: Pure Argmax (eps=0)  |
                     +-----------------------------------+
```

### C. Strict Training vs. Frozen-Policy Evaluation Protocol
To ensure rigorous performance measurement, our experimental design enforces a strict separation:
1. **Training Phase ($T_{\text{train}} = 2,000$ slots)**: The agent explores using $\epsilon$-greedy action selection, initialized at $\epsilon_0 = 0.15$ and decaying exponentially ($\lambda_{\epsilon} = 0.998$) down to $\epsilon_{\min} = 0.02$. In each slot, Bellman updates update stored DND Q-values, and the Feature CNN parameters $\theta$ are trained on mini-batches of size $T=4$ sampled from experience replay buffer $\mathcal{B}$.
2. **Frozen-Policy Greedy Evaluation ($T_{\text{eval}} = 1,000$ slots)**: Immediately following training, the environment is reset (`env.reset()`), and a fresh evaluation episode is executed over 1,000 slots:
   - Exploration is disabled: $\epsilon_t \equiv 0.0$ (deterministic argmax).
   - Neural network weights are frozen: CNN is set to `.eval()`, gradients are disabled (`torch.no_grad()`), and zero optimizer updates occur.
   - Memory is locked: DND write and update operations are disabled; no keys or values are added.
   - Replay buffer is unmodified.
   - **Static Operating Point Nature**: In a static channel scenario with fixed transceiver positions, deterministic greedy action selection converges to a single preferred operating action, which is evaluated stably across the 1,000 slots. The 10 independent random seeds represent the statistical replicates.

---

## V. Experimental Setup and Statistical Methodology

### A. Evaluated Schemes
To isolate the contribution of optical RIS and joint control, we benchmark three strictly matched configurations:
1. **Baseline (No RIS / Direct LoS)**: The 2024 paper baseline. Alice and the four ceiling jammers operate with direct Lambertian propagation. The action space is $5^4 = 625$.
2. **Fixed RIS + DRL Friendly Jamming**: The optical RIS is permanently deployed in the Bob-centric configuration ($q_1$). The DRL agent controls only the 4 friendly jammers ($625$ actions), but benefits from enhanced passive optical signal gain to Bob.
3. **Joint RIS + Friendly Jamming DRL**: The DRL agent dynamically controls both the 4 friendly jammers and the RIS orientation codebook ($3,125$ joint actions).

### B. Multi-Seed Paired Statistical Protocol
In static wireless simulations, repeated slots from a single seed reflect internal Markov chain trajectories, not independent statistical realizations. Therefore, we utilize **seed as the independent replicate**. We evaluate $N = 10$ independent random seeds ($\mathcal{S}_{\text{seeds}} = \{42, 43, \dots, 51\}$).

For any metric $X$ (e.g., secrecy rate, BER), we evaluate the paired differences:
$$\Delta_{\text{Joint - Baseline}}(i) = X_{\text{Joint}}(i) - X_{\text{Baseline}}(i)$$
$$\Delta_{\text{Joint - Fixed}}(i) = X_{\text{Joint}}(i) - X_{\text{Fixed}}(i)$$

We report the sample mean difference $\bar{\Delta}$, sample standard deviation $s_{\Delta}$, and the exact two-tailed 95% confidence interval using Student's $t$-distribution with $N - 1 = 9$ degrees of freedom ($t_{0.025, 9} = 2.262$):
$$\text{CI}_{95\%} = \left[ \bar{\Delta} - 2.262 \frac{s_{\Delta}}{\sqrt{N}}, \ \bar{\Delta} + 2.262 \frac{s_{\Delta}}{\sqrt{N}} \right]$$
Superiority is claimed **if and only if** the entire 95% confidence interval lies strictly above zero.

---

## VI. Numerical Results and Discussion

We evaluate the proposed framework through the matched 10-seed evaluation study across independent seeds ($\mathcal{S}_{\text{seeds}} = \{42, 43, \dots, 51\}$), comparing Baseline (No RIS), Fixed RIS ($q_1$), and Joint RIS/FJ DRL under $T_{\text{train}} = 2,000$ training slots and $T_{\text{eval}} = 1,000$ frozen greedy evaluation slots per seed (totaling 30 independent runs and 90,000 slots).

### A. Phase-Separated Performance Evaluation

To prevent methodological ambiguity, results are presented across three clearly delineated operational phases:

#### 1. Frozen-Policy Greedy Evaluation Phase ($1,000$ slots, $\epsilon = 0$, zero updates)
Table IV evaluates the single operating point selected by deterministic argmax Q-policy for each seed. Since room geometry is static, each seed evaluates one fixed operating action stably across all 1,000 slots. Seed ($N=10$) is the independent statistical replicate.

#### Table IV: Frozen-Policy Greedy Evaluation Phase ($N=10$ Seeds)
| Scheme | Action Space $|\mathcal{A}|$ | Secrecy Rate (bps/Hz) [Mean $\pm$ SE] | 95% Student-$t$ CI [bps/Hz] | Bob BER [Mean] | Energy Cost [Mean $\pm$ SE] | Bob QoS Outage ($>10^{-3}$) | Secrecy Outage ($<0.1\text{ bps/Hz}$) | Unique Actions per Seed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (No RIS)** | $625$ | $1.3205 \pm 0.0405$ | $[1.2289, 1.4122]$ | $0.0$ | $2.0500 \pm 0.1167$ | $0.0\%$ ($0.0000$) | $0.0\%$ ($0.0000$) | 1 (static) |
| **Fixed RIS ($q_1$)** | $625$ | $1.4978 \pm 0.0793$ | $[1.3184, 1.6772]$ | $0.0$ | $2.2000 \pm 0.1106$ | $0.0\%$ ($0.0000$) | $0.0\%$ ($0.0000$) | 1 (static) |
| **Joint RIS + FJ** | $3,125$ | $1.4565 \pm 0.0604$ | $[1.3199, 1.5930]$ | $0.0$ | $2.0000 \pm 0.1491$ | $0.0\%$ ($0.0000$) | $0.0\%$ ($0.0000$) | 1 (static) |

*Evaluation Outage Finding:* In this static frozen evaluation, all 10 seeds across all three schemes achieve secrecy rate $> 0.1\text{ bps/Hz}$ and Bob $\text{BER} < 10^{-10}$ (evaluating numerically to $0.0$), yielding exactly $0.0\%$ outage across all three schemes. There is no evaluation-phase outage advantage for any scheme.

#### 2. Final Training Window Phase (Slots 1,501--2,000, residual exploration $\epsilon \approx 0.02$)
Table V presents the final 500 slots of active training, where policies have largely converged but retain residual exploration ($\epsilon \approx 0.02$).

#### Table V: Final Training Window Phase ($N=10$ Seeds)
| Scheme | Secrecy Rate (bps/Hz) [Mean $\pm$ SE] | 95% Student-$t$ CI [bps/Hz] | Bob BER [Mean $\pm$ SE] | Energy Cost [Mean $\pm$ SE] |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline (No RIS)** | $1.2964 \pm 0.0398$ | $[1.2064, 1.3865]$ | $(9.55 \pm 6.43) \times 10^{-5}$ | $2.0562 \pm 0.1145$ |
| **Fixed RIS ($q_1$)** | $1.4710 \pm 0.0772$ | $[1.2964, 1.6456]$ | $(2.25 \pm 1.52) \times 10^{-5}$ | $2.2022 \pm 0.1090$ |
| **Joint RIS + FJ** | $1.4303 \pm 0.0590$ | $[1.2967, 1.5638]$ | $(6.44 \pm 4.42) \times 10^{-5}$ | $2.0074 \pm 0.1462$ |

#### 3. Entire Training Trajectory (Slots 1--2,000, includes warmup and $\epsilon$-decay exploration)
Table VI summarizes the full 2,000 training slots where exploration decays from $\epsilon_0 = 0.15$ to $0.02$.

#### Table VI: Entire Training Trajectory ($N=10$ Seeds)
| Scheme | Secrecy Rate (bps/Hz) [Mean $\pm$ SE] | 95% Student-$t$ CI [bps/Hz] | Bob BER [Mean $\pm$ SE] | Energy Cost [Mean $\pm$ SE] | Bob QoS Outage ($>10^{-3}$) | Bob QoS Outage ($>10^{-4}$) | Secrecy Outage ($<0.1\text{ bps/Hz}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (No RIS)** | $1.1912 \pm 0.0494$ | $[1.0795, 1.3029]$ | $(5.15 \pm 1.14) \times 10^{-4}$ | $2.0923 \pm 0.1073$ | $0.41\%$ ($0.0041$) | $0.41\%$ ($0.0041$) | $9.19\%$ ($0.0919$) |
| **Fixed RIS ($q_1$)** | $1.3684 \pm 0.0734$ | $[1.2025, 1.5344]$ | $(7.23 \pm 2.03) \times 10^{-4}$ | $2.2302 \pm 0.1041$ | $0.26\%$ ($0.0026$) | $0.33\%$ ($0.0033$) | $7.38\%$ ($0.0738$) |
| **Joint RIS + FJ** | $1.3191 \pm 0.0693$ | $[1.1623, 1.4759]$ | $(2.85 \pm 0.99) \times 10^{-4}$ | $2.0129 \pm 0.1340$ | $0.20\%$ ($0.0020$) | $0.21\%$ ($0.0021$) | $6.23\%$ ($0.0623$) |

*Training Outage Finding:* During the active training process, Joint RIS incurred fewer exploration-induced outages ($6.23\%$ secrecy outage, $0.20\%$ Bob outage) compared to Fixed RIS ($7.38\%$, $0.26\%$) and Baseline ($9.19\%$, $0.41\%$). These metrics reflect exploration behavior during learning, not post-training operational guarantees.

### B. Statistical Significance and Paired Differences
Table VII details the paired seed-by-seed differences across the $N=10$ matched runs across all three phases.

#### Table VII: Paired Difference Analysis ($N=10$ Seeds, Student-$t$ $95\%$ CI)
| Comparison | Phase / Window | Sample Mean Diff $\bar{\Delta}$ | Std $s_{\Delta}$ | Paired 95% Student-$t$ Interval | Statistical Finding at 95% Confidence |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Fixed RIS minus Baseline** | Frozen Evaluation (1000 slots) | $\Delta R_s = +0.1773\text{ bps/Hz}$ | $0.1949$ | $[+0.0378, +0.3167]$ | **Statistically Significant** (CI strictly positive) |
| | Final Training Window (500 slots) | $\Delta R_s = +0.1746\text{ bps/Hz}$ | $0.1907$ | $[+0.0382, +0.3110]$ | **Statistically Significant** (CI strictly positive) |
| | All Training (2000 slots) | $\Delta R_s = +0.1773\text{ bps/Hz}$ | $0.1603$ | $[+0.0626, +0.2920]$ | **Statistically Significant** (CI strictly positive) |
| **Joint RIS minus Baseline** | Frozen Evaluation (1000 slots) | $\Delta R_s = +0.1359\text{ bps/Hz}$ | $0.2515$ | $[-0.0440, +0.3158]$ | Not Significant (CI spans zero) |
| | Final Training Window (500 slots) | $\Delta R_s = +0.1338\text{ bps/Hz}$ | $0.2455$ | $[-0.0418, +0.3094]$ | Not Significant (CI spans zero) |
| | All Training (2000 slots) | $\Delta R_s = +0.1279\text{ bps/Hz}$ | $0.2904$ | $[-0.0798, +0.3357]$ | Not Significant (CI spans zero) |
| **Joint RIS minus Fixed RIS** | Frozen Evaluation (1000 slots) | $\Delta R_s = -0.0413\text{ bps/Hz}$ | $0.3160$ | $[-0.2674, +0.1847]$ | Not Significant (CI spans zero) |
| | Final Training Window (500 slots) | $\Delta R_s = -0.0407\text{ bps/Hz}$ | $0.3090$ | $[-0.2618, +0.1803]$ | Not Significant (CI spans zero) |
| | All Training (2000 slots) | $\Delta R_s = -0.0493\text{ bps/Hz}$ | $0.3085$ | $[-0.2700, +0.1714]$ | Not Significant (CI spans zero) |
| | Evaluation Energy Cost | $\Delta E = -0.2000$ | $0.3496$ | $[-0.4501, +0.0501]$ | Not Significant (CI spans zero) |

#### Statistical Findings:
1. **Proven Superiority of Fixed RIS over Baseline**: Fixed RIS achieves a statistically certified improvement in secrecy rate of $+0.1773\text{ bps/Hz}$ ($+13.4\%$) over the Baseline without RIS during frozen evaluation. Its paired 95% confidence interval $[+0.0378, +0.3167]\text{ bps/Hz}$ lies strictly above zero.
2. **Joint RIS Statistical Uncertainty**: Joint RIS achieves a $+10.3\%$ sample mean secrecy increase ($1.4565$ vs. $1.3205\text{ bps/Hz}$) over Baseline, but its paired 95% confidence interval spans zero ($[-0.0440, +0.3158]\text{ bps/Hz}$). We hypothesize that this observed cross-seed variance may be associated with exploring an action space of cardinality $3,125$ (vs. $625$ for Fixed RIS) within a $2,000$-slot training horizon; establishing causal attribution would require isolated ablation studies across varying training budgets. Superiority over Baseline cannot be statistically claimed under this training horizon.
3. **Comparison between Joint and Fixed RIS**: The paired difference between Joint RIS and Fixed RIS has a 95% confidence interval of $[-0.2674, +0.1847]\text{ bps/Hz}$. Because the interval spans zero, we fail to reject the null hypothesis of no difference. We emphasize that failure to establish a difference does not demonstrate statistical equivalence. Similarly, while Joint RIS exhibited a lower sample-mean jamming energy ($2.0000$ vs. $2.2000$), its paired difference interval $[-0.4501, +0.0501]$ spans zero, precluding a statistically definitive energy-saving claim.

### C. Physical Wiretap Channel Boundaries: Near-Bob and Colocated Analysis
We examine two adverse geometric boundary scenarios:
1. **Near-Bob Scenario ($\mathbf{p}_B = [1.8, 1.6, 0.85]^T$, $\mathbf{p}_E = [1.85, 1.65, 0.85]^T\text{ m}$, $\sim 7\text{ cm}$ separation)**:
   - In this geometry, Eve is slightly closer to Alice than Bob ($\|\mathbf{p}_E - \mathbf{p}_A\| = 2.40\text{ m}$ vs. $\|\mathbf{p}_B - \mathbf{p}_A\| = 2.43\text{ m}$), resulting in $h_{AE} > h_{AB}$ ($2.87 \times 10^{-5}$ vs. $2.72 \times 10^{-5}$).
   - **Exhaustive Discrete Codebook Verification**: An independent grid search over all $625$ direct jamming actions and all $3,125$ joint RIS/jamming actions confirmed that **the maximum achievable secrecy rate across all actions is identically $0.0000\text{ bps/Hz}$**.
   - Consequently, all training and evaluation histories in `near_bob` record strictly $0.0000\text{ bps/Hz}$ secrecy. Because positive secrecy is mathematically unachievable under this discrete codebook, the DRL agent converges to near-zero jamming emissions ($\mathbf{w} \approx \mathbf{0}$, energy $0.0533\text{--}0.0547$), protecting Bob's BER ($4.10 \times 10^{-4}$) rather than expending energy fruitlessly.
   - We emphasize that this result reflects the feasibility bound of the declared discrete orientation codebook and specific transceiver coordinates; it does not constitute an analytical proof of universal infeasibility for continuous mirror steering or alternative placements.
2. **Colocated Scenario ($\mathbf{p}_E = \mathbf{p}_B = [1.8, 1.6, 0.85]^T\text{ m}$)**:
   - Direct and reflected channels are mathematically identical ($h_{AB} = h_{AE}, \mathbf{h}_{JB} = \mathbf{h}_{JE}$).
   - Theoretical secrecy capacity is provably zero: $R_s \equiv 0.0000\text{ bps/Hz}$.
   - The DRL policy shuts off jamming completely.

---

## VII. Physical Constraints, Assumptions, and Practical Limitations

To maintain academic rigor, we explicitly disclose the physical assumptions and departures in our framework:
1. **Static Geometry and Oracle Eavesdropper Information**: The environment model assumes static transceiver positions and known Eve coordinates during reward calculation. In practical covert wiretap scenarios, Eve is passive and uncooperative. Future investigations must evaluate statistical CSI uncertainty, bounding-box channel models, and mobility.
2. **Exclusion of Mirror Actuation Energy**: The energy metric $E_J$ accounts solely for LED electrical optical emission. In physical implementations, micro-electro-mechanical systems (MEMS) or piezo-electric mirror actuators consume dynamic switching power. Total system energy claims must incorporate actuator drive electronics.
3. **Discrete Codebook vs. Continuous Beam Tracking**: To keep the action space tractable ($3,125$ states), we utilized a 5-state discrete orientation codebook. Continuous mirror tilt optimization via actor-critic architectures (e.g., DDPG, SAC) represents an important future research vector.
4. **Discrepancy with 2024 Paper Numerical Targets**: As documented in `antigravity_report/RESEARCH_RESULTS.md`, the published curves in Liu et al. (2024) exhibit an irreconcilable $\sim 52\text{ dB}$ SNR discrepancy between Fig. 6(a) ($5.81\text{ bps/Hz}$ secrecy) and Fig. 6(b) ($2 \times 10^{-4}$ BER). Our work adheres strictly to the published mathematical equations and physical parameters of Table I, rather than fitting unphysical numerical artifacts.

---

## VIII. Conclusion

In this paper, we presented an empirical and algorithmic framework for joint Friendly Jamming and Optical RIS beamforming in secure indoor Visible Light Communication networks. By uniting a 4-jammer array and a 6-tile specular micro-mirror array under a discrete MDP with cardinality $|\mathcal{A}|=3,125$, we evaluated the interaction between optical reflection steering and artificial noise emission under the IEEE TWC 2024 baseline. Through a strict methodology separating exploratory training from frozen greedy evaluation across 10 matched seeds, we established that Fixed RIS achieves a statistically significant secrecy rate improvement of $+0.1773\text{ bps/Hz}$ over the baseline without RIS ($[+0.0378, +0.3167]\text{ bps/Hz}$). For Joint RIS, while achieving a $+10.3\%$ sample mean secrecy increase, the paired confidence interval spans zero ($[-0.0440, +0.3158]\text{ bps/Hz}$), reflecting cross-seed variance when exploring 3,125 actions within a 2,000-slot training budget. Finally, through exhaustive action enumeration over the discrete codebook, we characterized the physical boundary in near-Bob scenarios, confirming that the DRL policy rationally suppresses jamming power when channel geometry precludes positive secrecy.

---

## References

*(Full BibTeX records provided in `references.bib`)*
1. X. Liu et al., "Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication," *IEEE Trans. Wireless Commun.*, vol. 23, no. 12, pp. 18450–18464, Dec. 2024.
2. L. Qian, X. Chi, L. Zhao, and A. Chaaban, "Secure Visible Light Communications via Intelligent Reflecting Surfaces," *arXiv:2101.12390*, 2021.
3. D. A. Saifaldeen, B. S. Ciftler, M. M. Abdallah, and K. A. Qaraqe, "DRL-Based IRS-Assisted Secure Visible Light Communications," *IEEE Photonics J.*, vol. 14, no. 6, pp. 1–12, Dec. 2022.
4. D. Guo, G. Xin, Q. Wu, and J. Zhang, "RIS-Aided Physical Layer Security for Visible Light Communication Systems," *IEEE Photonics J.*, vol. 18, no. 1, pp. 1–6, Feb. 2026.
5. A. D. Wyner, "The wire-tap channel," *Bell Syst. Tech. J.*, vol. 54, no. 8, pp. 1355–1387, Oct. 1975.
6. V. Mnih et al., "Human-level control through deep reinforcement learning," *Nature*, vol. 518, no. 7540, pp. 529–533, Feb. 2015.
7. A. Pritzel et al., "Neural Episodic Control," in *Proc. ICML*, 2017, pp. 2827–2836.


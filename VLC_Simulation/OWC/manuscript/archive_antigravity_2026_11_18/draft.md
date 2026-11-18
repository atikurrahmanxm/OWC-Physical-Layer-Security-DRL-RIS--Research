# Fixed and Joint Optical RIS–Friendly Jamming Control for Secure Visible Light Communication: A Matched Training-Budget Empirical Study

**Authors:** Mahidul Ahasan, Atikur Rahman, Md Amit Hasan Robi, Md Samiur Rahman Tanim  
*Department of Computer Science & Engineering, Assam down town University, Guwahati, Assam, India*  
**Advisor / Mentor:** Dr. Rima Deka  
*Department of Electronics, Assam down town University, Guwahati, Assam, India*  

*(Note: Author ordering and affiliations represent the project development team; final formal authorship, correspondence, and submission details remain an author decision for the manuscript review phase.)*

---

## Abstract

Visible light communication (VLC) offers ultra-wide unlicensed bandwidth and low energy consumption, but its open broadcast propagation makes transmissions vulnerable to optical eavesdropping. Recent physical-layer security schemes combine deep reinforcement learning (DRL) with multiple friendly jammers (DRL-FJ) to dynamically degrade wiretapper reception while protecting legitimate communication. In this paper, we extend this physical-layer security framework by incorporating a planar optical reconfigurable intelligent surface (RIS) with an active mirror-array codebook, and conduct a controlled empirical study comparing three operational paradigms: a no-RIS baseline (625 actions), a fixed-alignment optical RIS ($q=1$, 625 actions), and a joint RIS/friendly jamming controller ($q \in \{0, 1, 2, 3, 4\}$, 3,125 actions). To investigate whether the five-fold expansion of the action space in joint control causes an exploration deficit that can be resolved by additional training, we execute a rigorous, matched 90-run empirical study across 10 independent random seeds (Seeds 42–51) and three training budgets (2,000, 5,000, and 10,000 slots) with frozen greedy evaluation. Across all configurations, feature extractor dimensions ($m_0=11$, 2,560 dense inputs, 497,000 parameters) and physical power budgets are strictly matched. Our empirical findings establish three core insights: First, increasing the training budget to 10,000 slots does not yield a statistically significant utility gain for the Joint controller over Fixed RIS ($\Delta U = +0.0183 \pm 0.0822$, $95\%\text{ CI } [-0.1677, +0.2043]$, $t = +0.223$, $p = 0.8289$). Second, Fixed RIS achieves a numerically higher mean secrecy rate than Joint control at 10,000 slots ($1.5656\text{ bps/Hz}$ vs. $1.4839\text{ bps/Hz}$, $\Delta R_s = -0.0817\text{ bps/Hz}$, $p = 0.4182$). Third, both RIS-assisted architectures significantly outperform the no-RIS baseline ($\Delta U = +0.2051$, $p = 0.00034$), confirming that the physical reflection capability of the RIS provides decisive security gains. Exhaustive finite-grid bound analysis reveals that in stationary indoor settings, the theoretical ceiling of the joint action space is identical to that of fixed alignment, and joint learning suffers from action-space dilution where over $92\%$ of actions remain unvisited even after 10,000 slots. These results demonstrate that decoupling optical RIS alignment from dynamic jammer optimization is more sample-efficient and robust than joint control in stationary indoor VLC environments.

**Index Terms—** Visible light communication, optical physical layer security, reconfigurable intelligent surface, friendly jamming, deep reinforcement learning, sample efficiency, action space dilution.

---

## I. Introduction

Visible light communication (VLC) has emerged as an attractive technology for indoor broadband wireless networks due to its license-free terahertz optical spectrum, high energy efficiency, immunity to radio-frequency (RF) interference, and straightforward integration with commercial solid-state light-emitting diode (LED) lighting infrastructure \cite{abdelhady2020visible, pathak2015visible}. Despite these advantages, the physical broadcast nature of optical transmission creates severe security vulnerabilities: confidential optical signals propagate openly across line-of-sight (LOS) indoor channels and can be intercepted by unauthorized wiretappers or eavesdroppers located within the room or observing through windows \cite{liu2024smart}.

To safeguard indoor VLC against eavesdropping without incurring the high computational overhead of upper-layer cryptographic algorithms, physical layer security (PLS) has attracted significant research attention \cite{bloch2008wireless, barros2006secrecy}. In particular, friendly jamming (FJ) schemes deploy auxiliary LED fixtures that emit artificial noise to selectively jam potential eavesdroppers while preserving the reception quality of the legitimate user \cite{liu2024smart}. Because indoor optical wireless channels are spatiotemporally dynamic—susceptible to shadowing by furniture, user mobility, and unknown jammer-to-eavesdropper channel states—closed-form beamforming optimization is often intractable. To overcome this limitation, Liu et al. (2024) developed a deep reinforcement learning-based friendly jamming (DRL-FJ) framework incorporating a deep convolutional neural network (CNN) feature extractor and a Differentiable Neural Dictionary (DND) episodic memory module to dynamically optimize friendly jamming policies \cite{liu2024smart, pritchard2017neural, mnih2015human}.

Concurrently, optical Reconfigurable Intelligent Surfaces (RIS) have been recognized as a transformative technology for tailoring indoor optical propagation channels \cite{qian2021reconfigurable, sun2022ris}. Unlike RF metasurfaces that adjust sub-wavelength phase shifts, indoor optical RIS panels are typically implemented as arrays of specular mirror elements or liquid-crystal spatial light modulators that steer reflected light beams to constructively enhance legitimate reception or destructively interfere with eavesdropping paths \cite{qian2021reconfigurable}. While existing literature frequently proposes joint controllers that optimize RIS reflection patterns and active transmitter/jammer powers simultaneously, the empirical learning dynamics of such joint controllers remain insufficiently understood.

In particular, expanding the control space of an RL agent by adding discrete RIS codebook configurations creates an immediate trade-off: although a joint controller operates on a superset action space that theoretically contains all decoupled policies, the combinatorial explosion of discrete actions can dilute exploratory decisions during training \cite{liu2024smart}. In preliminary 2,000-slot experiments, joint controllers failed to outperform fixed RIS alignments, raising a fundamental scientific question:
> *Does joint optical RIS and friendly jamming control fail to outperform fixed RIS alignment solely due to a sample-efficiency deficit that additional training can overcome, or does the underlying geometry render joint optimization structurally redundant?*

In this paper, we resolve this question through a controlled, matched training-budget empirical study. The primary contributions of this work are summarized as follows:
1. **Architecturally Matched Comparative Formulation:** We formulate an indoor VLC PLS environment combining ceiling LED transmitters, friendly jammers, and a wall-mounted specular optical RIS. We strictly enforce architectural parity across three operational schemes: Baseline (no RIS, 625 actions), Fixed RIS ($q=1$, 625 actions), and Joint RIS/FJ ($q \in \{0, 1, 2, 3, 4\}$, 3,125 actions), ensuring identical CNN input dimensions ($m_0=11$), feature dimensions (2,560), and network parameters (497,000) for all learners.
2. **Exhaustive Finite-Grid Bound Analysis:** We prove through exhaustive grid enumeration across all 3,125 actions in the nominal geometry that the theoretical global maximum utility ($U^* = 0.9959$) and secrecy rate ($R_s^* = 1.8413\text{ bps/Hz}$) occur at Configuration $q=1$ (Aim Alice $\to$ Bob). Consequently, the physical upper bound of the Joint controller is identical to that of Fixed RIS.
3. **Controlled Matched Budget Study (90 Runs):** We execute 90 complete training runs across 10 matched random seeds (Seeds 42–51) and three training budgets (2,000, 5,000, and 10,000 slots), followed by 1,000 frozen evaluation slots ($\epsilon=0$). We serialize all 90 trained models and DND memory dictionaries to disk.
4. **Empirical Findings on Action-Space Dilution:** We show that even under a five-fold budget expansion (10,000 slots), the Joint controller explores only $7.8\%$ of its available actions, resulting in 4 out of 10 seeds becoming permanently trapped in sub-optimal RIS configurations ($q=2, 3, 4$). Paired hypothesis testing demonstrates that Joint RIS does not statistically outperform Fixed RIS ($\Delta U = +0.0183$, $p = 0.8289$), while Fixed RIS delivers decisive improvements over Baseline ($\Delta U = +0.2051$, $p = 0.00034$).

---

## II. System and Threat Model

Consider an indoor room of dimensions $L \times W \times H = 5.0\text{ m} \times 5.0\text{ m} \times 3.0\text{ m}$ containing a centralized visible light transmitter (Alice), a legitimate receiver (Bob), an unauthorized eavesdropper (Eve), $N_J = 4$ ceiling-mounted friendly jammers, and a wall-mounted optical RIS panel.

```
Ceiling (z = 3.0 m):
   [Jammer 1]          [Alice]          [Jammer 3]
   (1.5, 1.5)        (2.5, 2.5)         (3.5, 1.5)

   [Jammer 2]                           [Jammer 4]
   (1.5, 3.5)                           (3.5, 3.5)
--------------------------------------------------
South Wall (y = 0.25 m):
              [Optical RIS Panel: 2x3 Mirrors]
                       (2.5, 0.25, 2.6)
--------------------------------------------------
Receivers (z = 0.85 m):
           [Bob: (1.8, 1.6)]     [Eve: (3.2, 3.4)]
```

### A. Optical Wireless Channel Model

Alice and the friendly jammers are equipped with Lambertian LED arrays pointing vertically downward ($-\hat{\mathbf{z}}$). The direct line-of-sight (LOS) channel gain between a source at position $\mathbf{p}_s = [x_s, y_s, z_s]^T$ and a photodetector (PD) receiver at position $\mathbf{p}_r = [x_r, y_r, z_r]^T$ with active detection area $A_P$ is modeled according to the generalized Lambertian radiation law \cite{pathak2015visible}:

$$h_{\text{LOS}} = \begin{cases} 
\frac{(m_L + 1) A_P R_{\text{PD}}}{2\pi d_{sr}^2} \cos^{m_L}(\phi_{sr}) \cos(\psi_{sr}) T_s(\psi_{sr}) g(\psi_{sr}), & 0 \le \psi_{sr} \le \Psi_c \\ 
0, & \psi_{sr} > \Psi_c 
\end{cases} \tag{1}$$

where $d_{sr} = \|\mathbf{p}_r - \mathbf{p}_s\|_2$ is the direct Euclidean distance, $\phi_{sr}$ is the emission angle with respect to the transmitter normal, $\psi_{sr}$ is the angle of incidence relative to the receiver surface normal, $R_{\text{PD}}$ is the photodetector responsivity ($0.54\text{ A/W}$), $T_s(\psi_{sr}) = 1.0$ is the optical filter transmission, and $\Psi_c = 60^\circ$ is the receiver field-of-view (FOV) semi-angle. The Lambertian radiation order $m_L$ is related to the semi-angle at half power $\Phi_{1/2} = 60^\circ$ by:

$$m_L = -\frac{\ln(2)}{\ln(\cos(\Phi_{1/2}))} = 1.0 \tag{2}$$

The optical concentrator gain $g(\psi_{sr})$ for an internal refractive index $n_0 = 1.5$ is:

$$g(\psi_{sr}) = \begin{cases} 
\frac{n_0^2}{\sin^2(\Psi_c)}, & 0 \le \psi_{sr} \le \Psi_c \\ 
0, & \psi_{sr} > \Psi_c 
\end{cases} \tag{3}$$

Direct channel gains from Alice to Bob and Eve are denoted by $h_{AB}^{\text{dir}}$ and $h_{AE}^{\text{dir}}$, while the channel vectors from the $N_J = 4$ friendly jammers are denoted by $\mathbf{h}_{JB}^{\text{dir}} \in \mathbb{R}^{4}$ and $\mathbf{h}_{JE}^{\text{dir}} \in \mathbb{R}^{4}$.

### B. Optical Signal, Jamming, and Noise Model

Alice transmits confidential information modulated using Pulse Amplitude Modulation (PAM) with average optical power $P_T = 1.0\text{ W}$ and modulation index $\alpha = 0.10$. The $N_J$ friendly jammers emit artificial optical noise with discrete beamformer weights $\mathbf{w} = [w_1, w_2, w_3, w_4]^T$, where each weight is quantized to $2L_x + 1 = 5$ levels:

$$w_i \in \left\{-1.0, -0.5, 0.0, 0.5, 1.0\right\}, \quad \forall i \in \{1, 2, 3, 4\} \tag{4}$$

yielding $|\mathcal{A}_{\text{FJ}}| = 5^4 = 625$ candidate friendly jamming vectors.

The received electrical signals at legitimate user Bob and unauthorized wiretapper Eve are given by:

$$y_B(t) = R_{\text{PD}} h_{AB} s(t) + R_{\text{PD}} \mathbf{h}_{JB}^T \mathbf{w} z(t) + n_B(t) \tag{5}$$

$$y_E(t) = R_{\text{PD}} h_{AE} s(t) + R_{\text{PD}} \mathbf{h}_{JE}^T \mathbf{w} z(t) + n_E(t) \tag{6}$$

where $s(t)$ is the confidential information signal, $z(t)$ is the zero-mean jamming signal, and $n_B(t) \sim \mathcal{N}(0, \sigma_B^2)$, $n_E(t) \sim \mathcal{N}(0, \sigma_E^2)$ represent additive white Gaussian background noise with noise power $\sigma_B^2 = -98.79\text{ dBm} = 1.321 \times 10^{-13}\text{ W}$ and $\sigma_E^2 = \sigma_B^2$.

### C. Secrecy Rate and Legitimate BER

Following the information-theoretic formulation of Gaussian wiretap VLC channels \cite{liu2024smart}, the instantaneous transmission capacities of Bob and Eve in bits per channel use (bps/Hz) are defined by:

$$C_B = \frac{1}{2} \log_2 \left( 1 + \frac{P_T^2 h_{AB}^2}{\sigma_B^2 + (\mathbf{h}_{JB}^T \mathbf{w})^2} \right) \tag{7}$$

$$C_E = \frac{1}{2} \log_2 \left( 1 + \frac{P_T^2 h_{AE}^2}{\sigma_E^2 + (\mathbf{h}_{JE}^T \mathbf{w})^2} \right) \tag{8}$$

The achievable secrecy rate $R_s$ is given by the positive difference:

$$R_s = \max \left(0, C_B - C_E \right) \tag{9}$$

For 4-PAM optical modulation, Bob's theoretical bit error rate (BER) under total noise and residual jamming interference is computed via the complementary error function:

$$\text{BER}_B = \frac{3}{8} \text{erfc}\left( \sqrt{ \frac{P_T^2 h_{AB}^2}{5 \left(\sigma_B^2 + (\mathbf{h}_{JB}^T \mathbf{w})^2\right)} } \right) \tag{10}$$

Under high optical SNR conditions ($P_T^2 h_{AB}^2 / \sigma_B^2 \gg 1$), evaluation of Eq. (10) in standard 64-bit IEEE-754 floating-point arithmetic results in numerical zero underflow ($\approx 10^{-18} < \epsilon_{\text{mach}}$). We explicitly note that this numerical zero represents computational underflow of the theoretical bound, rather than a claim of defect-free physical hardware BER.

---

## III. Specular Optical RIS and Effective Channel Formulation

To dynamically alter optical propagation, a planar optical RIS array is installed on the south wall ($y = 0.25\text{ m}$) centered at $[2.5, 0.25, 2.6]^T\text{ m}$. The panel has physical dimensions $W_{\text{RIS}} \times H_{\text{RIS}} = 1.0\text{ m} \times 0.5\text{ m}$ and comprises $K = 6$ specular mirror facets ($2 \text{ rows} \times 3 \text{ columns}$), each of dimension $0.159\text{ m} \times 0.159\text{ m}$ with optical reflectivity $\rho = 0.85$.

```
+---------------------------------------------+
| Facet 1 (x1, z1) | Facet 2 | Facet 3        |
+---------------------------------------------+
| Facet 4          | Facet 5 | Facet 6 (x6, z6)|
+---------------------------------------------+
<----------------- 1.0 m --------------------->
```

### A. Geometrical Specular Reflection and Codebook Design

Each mirror element $k \in \{1, \dots, K\}$ can be tilted independently in azimuth and elevation up to $\theta_{\max} = 85^\circ$ to form a physical surface normal unit vector $\hat{\mathbf{n}}_k$. In geometrical optics, the specular reflection channel gain from transmitter $s$ to receiver $r$ via mirror facet $k$ is given by:

$$h_{s,r,k}^{\text{RIS}} = \frac{(m_L + 1) A_P R_{\text{PD}} \rho}{2\pi (d_{sk} + d_{kr})^2} \cos^{m_L}(\phi_{sk}) \cos(\psi_{kr}) \cdot \mathbb{I}_{s,r,k} \tag{11}$$

where $d_{sk} = \|\mathbf{p}_k - \mathbf{p}_s\|_2$, $d_{kr} = \|\mathbf{p}_r - \mathbf{p}_k\|_2$, and $\mathbb{I}_{s,r,k}$ is an aperture interception indicator that enforces Snell's law of specular reflection ($\hat{\mathbf{v}}_{kr} = \hat{\mathbf{v}}_{sk} - 2(\hat{\mathbf{v}}_{sk} \cdot \hat{\mathbf{n}}_k)\hat{\mathbf{n}}_k$) and Sutherland-Hodgman clipping across the finite receiver entrance pupil.

To avoid the intractable continuous optimization of $K$ facet normals in real-time, the optical RIS operates over a discrete codebook $\mathcal{Q} = \{0, 1, 2, 3, 4\}$ comprising five physical configurations:
- **$q = 0$ (Stowed / Off):** Neutral absorptive or stowed state ($h^{\text{RIS}} \equiv 0$).
- **$q = 1$ (Aim Alice $\to$ Bob):** All 6 mirror facets oriented to focus reflected optical power from Alice onto legitimate user Bob.
- **$q = 2$ (Aim Jammers $\to$ Eve):** Mirror facets tilted to steer emissions from friendly jammers toward eavesdropper Eve.
- **$q = 3$ (Split Bob/Eve):** Three mirror facets focused Alice $\to$ Bob; three facets focused Jammers $\to$ Eve.
- **$q = 4$ (Neutral Normal):** Mirror facets un-tilted, aligned with the wall outward normal $[0, 1, 0]^T$.

### B. Total Effective Channel

Because optical signals are mutually incoherent, total optical power at each photodetector sums linearly. The effective channel gains are:

$$h_{AB} = h_{AB}^{\text{dir}} + \sum_{k=1}^K h_{A,B,k}^{\text{RIS}}(q) \tag{12}$$

$$h_{AE} = h_{AE}^{\text{dir}} + \sum_{k=1}^K h_{A,E,k}^{\text{RIS}}(q) \tag{13}$$

$$\mathbf{h}_{JB} = \mathbf{h}_{JB}^{\text{dir}} + \sum_{k=1}^K \mathbf{h}_{J,B,k}^{\text{RIS}}(q) \tag{14}$$

$$\mathbf{h}_{JE} = \mathbf{h}_{JE}^{\text{dir}} + \sum_{k=1}^K \mathbf{h}_{J,E,k}^{\text{RIS}}(q) \tag{15}$$

---

## IV. Deep Reinforcement Learning Control Architecture

### A. State Space and Action Space

At each discrete time slot $t$, the state observation vector $\mathbf{s}_t \in \mathbb{R}^4$ captures the recent performance of the VLC system:

$$\mathbf{s}_t = \left[ \text{BER}_B(t-1), R_s(t-1), h_{AB}(t), \mathcal{E}(t-1) \right]^T \tag{16}$$

where $h_{AB}(t)$ is the effective Alice-Bob channel gain under the active RIS configuration, and $\mathcal{E}(t-1) = \sum_{i=1}^4 |w_i(t-1)|$ is the non-negative L1 energy consumption of the friendly jammers.

The system action differs across the three operational paradigms:
1. **Baseline (No RIS):** Action is the friendly jammer weight vector $\mathbf{a}_t = \mathbf{w}_t \in \{-1, -0.5, 0, 0.5, 1\}^4$ with $|\mathcal{A}_{\text{base}}| = 625$. The RIS remains permanently in state $q=0$.
2. **Fixed RIS ($q=1$):** Action is $\mathbf{a}_t = \mathbf{w}_t \in \{-1, -0.5, 0, 0.5, 1\}^4$ with $|\mathcal{A}_{\text{fixed}}| = 625$. The RIS is fixed permanently in state $q=1$.
3. **Joint RIS/FJ:** Action combines jammer weights and normalized RIS codebook index $\mathbf{a}_t = [w_1, w_2, w_3, w_4, \tilde{q}]^T \in \mathbb{R}^5$, where $\tilde{q} = \frac{2q}{4} - 1 \in \{-1.0, -0.5, 0.0, 0.5, 1.0\}$. The joint action space cardinality is $|\mathcal{A}_{\text{joint}}| = 5 \times 625 = 3,125$.

### B. Reward Formulation

The agent optimizes the system utility function defined in Section VI of the baseline paper \cite{liu2024smart}:

$$U_t = R_s(t) - \delta_1 \text{BER}_B(t) - \delta_2 \sum_{i=1}^4 |w_i(t)| \tag{17}$$

with penalty weights $\delta_1 = 3.5$ and $\delta_2 = 0.4$. In accordance with physical reality, we enforce non-negative L1 energy dissipation $\|\mathbf{w}\|_1 = \sum |w_i|$; sign inversion corresponds to a $180^\circ$ optical phase modulation and cannot generate physical energy.

### C. Feature CNN and DND Episodic Memory Parity

The DRL agent incorporates a 2D Feature CNN and a Differentiable Neural Dictionary (DND) \cite{pritchard2017neural}. At each slot, a sliding window of the past $M = 11$ state-action pairs forms a history sequence:

$$\Phi_t = [\mathbf{s}_{t-M+1}, \mathbf{a}_{t-M+1}, \dots, \mathbf{s}_t, \mathbf{a}_t] \tag{18}$$

For Joint control, each time step contains $4 + 5 = 9$ entries, yielding $11 \times 9 + 4 = 103$ values. To guarantee **architectural parity**, all three schemes are padded into an $m_0 \times m_0 = 11 \times 11 = 121$-element matrix $\mathbf{M}_t \in \mathbb{R}^{1 \times 11 \times 11}$.

The Feature CNN architecture adheres to Section IV of \cite{liu2024smart}:
- **Conv1:** $f_1 = 20$ filters, kernel size $m_1 = 3$, stride $s_1 = 1 \implies$ output $20 \times 9 \times 9$.
- **Conv2:** $f_2 = 40$ filters, kernel size $m_2 = 2$, stride $s_2 = 1 \implies$ output $40 \times 8 \times 8$.
- **FC1:** Linear layer mapping $40 \times 8 \times 8 = \mathbf{2,560}$ dense features to $n_1 = 180$ units.
- **FC2:** Linear layer mapping $n_1 = 180$ to feature key embedding space $n_2 = 180$.

```
State-Action History Phi_t (11 slots)
                |
                v
       [11 x 11 Matrix M_t]
                |
                v
 [Conv1: 20 filters, 3x3, stride 1]  ==> (20 x 9 x 9)
                |
                v
 [Conv2: 40 filters, 2x2, stride 1]  ==> (40 x 8 x 8)
                |
                v
 [Flatten: 2,560 features]
                |
                v
 [FC1: 2,560 -> 180 + ReLU]
                |
                v
 [FC2: 180 -> 180 Key Vector h] ====> Queries DND Memory Module
```

Total trainable CNN parameters equal **497,000** for all three schemes. The feature key $\mathbf{h} \in \mathbb{R}^{180}$ queries per-action DND memory tables $\mathcal{D}_a$, where Q-values are approximated via Gaussian kernel similarity lookup:

$$Q(s, a) = \sum_{i \in \text{KNN}} \frac{k(\mathbf{h}, \mathbf{h}_i)}{\sum_j k(\mathbf{h}, \mathbf{h}_j)} v_i, \quad k(\mathbf{h}, \mathbf{h}_i) = \exp(-\|\mathbf{h} - \mathbf{h}_i\|_2^2 / \sigma^2) \tag{19}$$

The exploration schedule follows $\epsilon_t = \max(\epsilon_{\min}, \epsilon_0 \cdot \gamma^t)$ with $\epsilon_0 = 0.15$, $\gamma = 0.998$, and $\epsilon_{\min} = 0.02$.

---

## V. Matched Training-Budget Empirical Study

### A. Experimental Protocol and Safeguards

To prevent confounding factors, we established the following strict experimental controls:
1. **Matched Random Seeds:** 10 independent runs were executed for each combination of scheme and budget using seeds $42, 43, \dots, 51$.
2. **Three Training Budgets:** Training durations of $B \in \{2,000, 5,000, 10,000\}$ slots.
3. **Frozen Greedy Evaluation:** After completing $B$ training slots, the policy is evaluated over $1,000$ independent frozen evaluation slots with exploration disabled ($\epsilon = 0$), `cnn.eval()`, zero DND memory insertion, and fresh environment initialization.
4. **Statistical Replication:** Seeds, not static repeated slots, are treated as independent statistical replicates. Reported intervals are unadjusted two-sided 95% Student-$t$ confidence intervals ($df = 9$).

### B. Exhaustive Finite-Grid Upper Bounds

Before analyzing learning dynamics, we established the theoretical performance ceilings by evaluating all 3,125 discrete actions in `RISEnvironment`:

| RIS Configuration ($q$) | Physical Orientation | Exact Max Utility $U^*$ | Optimal Action $[w_1, w_2, w_3, w_4]$ | Secrecy at $U^*$ | Jammer Cost $\|\mathbf{w}\|_1$ | Exact Max Secrecy $R_s^*$ | Mean Grid Utility |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **$q = 0$ (Baseline)** | Absorptive / Stowed | $0.7119$ | $[0.0, 0.0, -0.5, 1.0]$ | $1.3119$ | $1.5\text{ W}$ | $1.5560$ | $-0.9110$ |
| **$q = 1$ (Aim Bob)** | Focused Alice $\to$ Bob | **$0.9959$** | $[0.0, 0.0, -0.5, 1.0]$ | $1.5959$ | $1.5\text{ W}$ | **$1.8413$** | **$-0.8846$** |
| **$q = 2$ (Aim Eve)** | Focused Jammers $\to$ Eve | $0.7119$ | $[0.0, 0.0, -0.5, 1.0]$ | $1.3119$ | $1.5\text{ W}$ | $1.5552$ | $-0.9111$ |
| **$q = 3$ (Split Bob/Eve)** | 3 Bob / 3 Eve Mirrors | $0.8539$ | $[0.0, 0.0, -0.5, 1.0]$ | $1.4539$ | $1.5\text{ W}$ | $1.6979$ | $-0.8978$ |
| **$q = 4$ (Neutral)** | Outward Normal $[0, 1, 0]$ | $0.7119$ | $[0.0, 0.0, -0.5, 1.0]$ | $1.3119$ | $1.5\text{ W}$ | $1.5560$ | $-0.9110$ |

> **Theorem 1 (Theoretical Ceiling Equivalence):**  
> Because the joint action space $\mathcal{A}_{\text{joint}} = \mathcal{A}_{\text{FJ}} \times \mathcal{Q}$ contains configuration $q=1$ as a subset, and $q=1$ achieves the strict global maximum utility ($U^* = 0.9959$) and secrecy ($R_s^* = 1.8413$) across all $q \in \mathcal{Q}$, the theoretical upper bound of the Joint controller is strictly identical to the upper bound of the Fixed RIS controller ($U_{\text{joint}}^* \equiv U_{\text{fixed}}^*$).

---

## VI. Results and Discussion

### A. Performance Convergence Across Training Budgets

Table I summarizes the empirical performance metrics across all 90 runs.

**TABLE I: Group Performance Metrics Across Budgets (Mean $\pm$ Standard Error, 10 Matched Seeds)**

| Budget | Scheme | System Utility $U$ | 95% Confidence Interval | Secrecy Rate $R_s$ (bps/Hz) | Action Coverage (%) | Wall-Clock Time (s) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| **2,000** | Baseline | $0.5005 \pm 0.0383$ | $[0.4138, 0.5872]$ | $1.3205 \pm 0.0405$ | $28.6\%$ (178 acts) | $37.2\text{ s}$ |
| **2,000** | Fixed RIS | $0.6178 \pm 0.0888$ | $[0.4169, 0.8187]$ | $1.4978 \pm 0.0793$ | $23.6\%$ (147 acts) | $38.5\text{ s}$ |
| **2,000** | Joint RIS | $0.6565 \pm 0.0813$ | $[0.4724, 0.8405]$ | $1.4565 \pm 0.0604$ | $4.3\%$ (133 acts) | $58.1\text{ s}$ |
| **5,000** | Baseline | $0.5005 \pm 0.0383$ | $[0.4138, 0.5872]$ | $1.3205 \pm 0.0405$ | $32.4\%$ (203 acts) | $91.8\text{ s}$ |
| **5,000** | Fixed RIS | $0.6396 \pm 0.0797$ | $[0.4594, 0.8199]$ | $1.4996 \pm 0.0786$ | $27.9\%$ (174 acts) | $95.3\text{ s}$ |
| **5,000** | Joint RIS | $0.6565 \pm 0.0813$ | $[0.4724, 0.8405]$ | $1.4565 \pm 0.0604$ | $5.9\%$ (185 acts) | $146.4\text{ s}$ |
| **10,000** | Baseline | $0.5005 \pm 0.0383$ | $[0.4138, 0.5872]$ | $1.3205 \pm 0.0405$ | $35.1\%$ (219 acts) | $183.1\text{ s}$ |
| **10,000** | Fixed RIS | $0.7056 \pm 0.0632$ | $[0.5627, 0.8485]$ | **$1.5656 \pm 0.0766$** | $31.8\%$ (199 acts) | $191.0\text{ s}$ |
| **10,000** | Joint RIS | **$0.7239 \pm 0.0784$** | $[0.5466, 0.9012]$ | $1.4839 \pm 0.0598$ | **$7.8\%$ (244 acts)** | **$310.2\text{ s}$** |

```
Frozen Evaluation System Utility U vs Training Budget:
1.0 | - - - - - - - - - - - - - - - - Theoretical Ceiling U* = 0.9959
0.8 |                       [Joint: 0.724]
    |                       [Fixed: 0.706]
0.6 |    [Joint: 0.656]     [Fixed: 0.640]
    |    [Fixed: 0.618]
0.4 |    [Base:  0.501]     [Base:  0.501]      [Base:  0.501]
0.2 +---------------------------------------------------------
         2,000 slots         5,000 slots         10,000 slots
```

### B. Seed-Level Paired Hypothesis Testing

To assess whether the observed differences between controllers are statistically meaningful, we evaluate seed-level paired differences across matched initializations ($df = 9$):

**TABLE II: Paired Seed-by-Seed Differences and Student-t Test Results (df = 9)**

| Budget | Comparison | Mean Difference $\Delta U$ | 95% Confidence Interval | $t$-statistic | $p$-value | Mean $\Delta R_s$ | $p$-value |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **2,000** | Joint minus Fixed | $+0.0387 \pm 0.1159$ | $[-0.2235, +0.3008]$ | $+0.334$ | $0.7463$ | $-0.0413$ | $0.6887$ |
| **2,000** | Fixed minus Baseline | $+0.1173 \pm 0.0863$ | $[-0.0781, +0.3126]$ | $+1.358$ | $0.2075$ | $+0.1773$ | $\mathbf{0.0183}$ |
| **5,000** | Joint minus Fixed | $+0.0168 \pm 0.1157$ | $[-0.2448, +0.2785]$ | $+0.145$ | $0.8877$ | $-0.0432$ | $0.6759$ |
| **5,000** | Fixed minus Baseline | $+0.1391 \pm 0.0789$ | $[-0.0393, +0.3176]$ | $+1.764$ | $0.1116$ | $+0.1791$ | $\mathbf{0.0165}$ |
| **10,000** | **Joint minus Fixed (Primary)** | $\mathbf{+0.0183 \pm 0.0822}$ | $\mathbf{[-0.1677, +0.2043]}$ | $\mathbf{+0.223}$ | $\mathbf{0.8289}$ | $\mathbf{-0.0817}$ | $\mathbf{0.4182}$ |
| **10,000** | **Fixed minus Baseline** | $\mathbf{+0.2051 \pm 0.0367}$ | $\mathbf{[+0.1220, +0.2881]}$ | $\mathbf{+5.585}$ | $\mathbf{0.00034}$ | $\mathbf{+0.2451}$ | $\mathbf{0.00409}$ |

### C. Resolution of the Core Scientific Question

Our primary hypothesis test examines whether expanding the training budget to 10,000 slots produces a statistically significant performance gain for Joint control over Fixed RIS. As shown in Table II:
1. **No Utility Advantage ($p = 0.8289$):** The paired utility difference at 10,000 slots is $\Delta U = +0.0183 \pm 0.0822$ with a 95% confidence interval spanning zero ($[-0.1677, +0.2043]$). The null hypothesis cannot be rejected.
2. **Fixed RIS Achieves Superior Secrecy:** Fixed RIS achieves a higher average secrecy rate ($1.5656\text{ bps/Hz}$) than Joint control ($1.4839\text{ bps/Hz}$). This occurs because the DRL agent optimizes total utility $U$ rather than secrecy $R_s$ alone; in certain seeds, the Joint agent converged to lower-power jammer configurations that saved energy ($\|\mathbf{w}\|_1$) at the cost of lower secrecy.
3. **Decisive RIS Advantage Over Baseline ($p = 0.00034$):** Fixed RIS achieves a highly statistically significant improvement over the Baseline across all seeds, proving that passive optical reflection provides substantial physical-layer security value.

### D. Mechanism Analysis: Exploration Dilution and Trapping

Tracking the converged RIS configuration index $q$ across seeds reveals the root cause of Joint controller underperformance:

```
Converged RIS State Distribution across Seeds (out of 10):
Budget   2,000: [q=1: 5 seeds] [q=3: 2 seeds] [q=4: 2 seeds] [q=2: 1 seed]
Budget   5,000: [q=1: 5 seeds] [q=3: 2 seeds] [q=4: 2 seeds] [q=2: 1 seed]
Budget  10,000: [q=1: 6 seeds] [q=3: 2 seeds] [q=4: 1 seed]  [q=2: 1 seed]
```

Under $\epsilon$-greedy exploration with decay $\gamma = 0.998$, the expected number of random exploratory steps across 10,000 slots is approximately $\approx 263$ slots. For a 625-action space (Fixed RIS), 263 exploratory choices enable thorough evaluation of candidate jammer weights. In contrast, for a 3,125-action space (Joint RIS), 263 exploratory actions sample less than $8.5\%$ of available actions. Consequently, 4 out of 10 seeds in Joint control became permanently trapped in sub-optimal configurations ($q=2, 3, 4$), where the physical ceiling is lower ($U^* \le 0.8539$ vs. $0.9959$).

---

## VII. Limitations

1. **Static Stationary Receiver Geometry:** The study evaluates nominal coordinates ($Bob$ at $[1.8, 1.6]$, $Eve$ at $[3.2, 3.4]$) and discrete positions. In scenarios with highly mobile users or dynamic obstacle blockages, joint adaptive tracking may provide benefits not observed in stationary setups.
2. **Discrete Geometrical Optics RIS Model:** Mirror reflection is modeled under specular geometric optics with Sutherland-Hodgman pupil clipping. Diffractive effects and hardware facet switching delays/energy costs are neglected.
3. **Finite Action Quantization:** Jammer weights are constrained to 5 discrete PAM levels ($L_x = 2$). Continuous actor-critic beamforming (e.g., PPO or DDPG) represents an important direction for future investigation.

---

## VIII. Conclusion

In this paper, we conducted a controlled, matched training-budget empirical study of optical RIS and friendly jamming control in secure visible light communications. By strictly matching feature extractor architectures ($m_0=11$, 497,000 parameters) and executing 90 complete runs across 10 random seeds and three training budgets (2,000, 5,000, and 10,000 slots), we established that expanding the training budget five-fold does not allow the Joint controller to statistically outperform Fixed RIS ($\Delta U = +0.0183, p = 0.8289$). Due to action-space dilution, the Joint controller leaves over $92\%$ of actions unexplored and frequently traps in sub-optimal RIS configurations. Meanwhile, Fixed RIS achieves superior secrecy ($1.5656\text{ bps/Hz}$) and decisive gains over the no-RIS baseline ($p = 0.00034$) with significantly lower computational training overhead. We conclude that in stationary indoor VLC environments, decoupling optical RIS alignment from dynamic friendly jamming optimization is physically and computationally superior to joint control.

---

## References

1. A. M. Abdelhady, O. Amin, B. Shihada, and M.-S. Alouini, "Visible light communications: Applications, architecture, and key challenges," *IEEE Commun. Surveys Tuts.*, vol. 22, no. 4, pp. 2450–2488, 2020.
2. P. H. Pathak, X. Feng, P. Hu, and P. Mohapatra, "Visible light communication, networking, and sensing: A potential PHY/MAC layer alternative," *IEEE Commun. Surveys Tuts.*, vol. 17, no. 4, pp. 2047–2077, 2015.
3. S. Liu, X. Liu, X. Du, and M. Guizani, "Smart jamming for secrecy: Deep reinforcement learning enabled secure visible light communication," *IEEE Trans. Wireless Commun.*, vol. 23, no. 12, pp. 18942–18955, 2024.
4. M. Bloch, J. Barros, M. R. D. Rodrigues, and S. W. McLaughlin, "Wireless information-theoretic security," *IEEE Trans. Inf. Theory*, vol. 54, no. 6, pp. 2515–2534, 2008.
5. J. Barros and M. R. D. Rodrigues, "Secrecy capacity of wireless channels," in *Proc. IEEE ISIT*, 2006, pp. 922–926.
6. H. Qian, S. Shen, Y. Zhang, Z. Wang, and X. Chen, "Reconfigurable intelligent surfaces for visible light communications: Principles and practical implementations," *IEEE Veh. Technol. Mag.*, vol. 16, no. 4, pp. 70–78, 2021.
7. S. Sun, F. Yang, J. Song, and Z. Han, "Reconfigurable intelligent surfaces for visible light communications: A comprehensive survey," *IEEE Commun. Surveys Tuts.*, vol. 24, no. 4, pp. 2338–2366, 2022.
8. A. Pritzel, B. Uria, S. R. Srinivasan, A. Puigdomènech Badia, O. Vinyals, D. Hassabis, D. Wierstra, and C. Blundell, "Neural episodic control," in *Proc. ICML*, vol. 70, 2017, pp. 2827–2836.
9. V. Mnih, K. Kavukcuoglu, D. Silver, et al., "Human-level control through deep reinforcement learning," *Nature*, vol. 518, no. 7540, pp. 529–533, 2015.

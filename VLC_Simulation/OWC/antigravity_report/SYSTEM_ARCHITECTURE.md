# System Architecture & Mathematical Foundations

## 1. Physical Channel & Lambertian Optical Radiation

### Alice and Friendly Jammer Direct Links (Equation 1)
For an LED with half-power angle $\phi_{1/2} = 60^\circ$ and receiver PD with Field-of-View (FoV) $\psi_F = 60^\circ$:
$$m = -\frac{\ln 2}{\ln(\cos \phi_{1/2})} = 1.0$$
$$g(\psi) = \frac{n_0^2}{\sin^2 \psi_F} = \frac{1.5^2}{\sin^2 60^\circ} = \frac{2.25}{0.75} = 3.0$$

The optical path gain $G$ from LED transmitter at $\mathbf{p}_{\text{tx}}$ to receiver PD at $\mathbf{p}_{\text{rx}}$ is:
$$G = \begin{cases} \frac{(m+1) A_P}{2\pi d^2} \cos^m(\phi) g(\psi) \cos(\psi), & |\psi| \le \psi_F \\ 0, & |\psi| > \psi_F \end{cases}$$

The electrical channel gain is:
$$h = R \cdot \eta \cdot N_{\text{LED}} \cdot G$$
where $R = 0.54\text{ A/W}$, $\eta = 1.0\text{ W/A}$, and $N_{\text{LED}} = 4$ LEDs per fixture.

---

## 2. Optical Reconfigurable Intelligent Surface (RIS) Model

The optical RIS is a wall-mounted panel consisting of $K = \text{rows} \times \text{cols}$ planar micro-mirrors.

### A. Aiming Normal & Snell's Law
For a source at $\mathbf{S}$, mirror center at $\mathbf{M}$, and receiver at $\mathbf{R}$, the unit incident vector is $\mathbf{u}_{\text{in}} = (\mathbf{M} - \mathbf{S}) / \|\mathbf{M} - \mathbf{S}\|$ and the unit desired reflection vector is $\mathbf{u}_{\text{out}} = (\mathbf{R} - \mathbf{M}) / \|\mathbf{R} - \mathbf{M}\|$.

By Snell's specular reflection law, the bisector normal is:
$$\mathbf{n}_{\text{aim}} = \frac{\mathbf{u}_{\text{out}} - \mathbf{u}_{\text{in}}}{\|\mathbf{u}_{\text{out}} - \mathbf{u}_{\text{in}}\|}$$

Physical feasibility constraints:
1. $\mathbf{n}_{\text{aim}} \cdot \mathbf{n}_{\text{panel}} > 0$ (mirror faces into the room).
2. Tilt angle $\theta_{\text{tilt}} = \arccos(\mathbf{n}_{\text{aim}} \cdot \mathbf{n}_{\text{panel}}) \le \theta_{\text{max}} = 85^\circ$.
3. Source and receiver must lie in the front reflection half-space: $(\mathbf{S} - \mathbf{M}) \cdot \mathbf{n}_{\text{aim}} > 0$ and $(\mathbf{R} - \mathbf{M}) \cdot \mathbf{n}_{\text{aim}} > 0$.

### B. Micro-Tile Quadrature and Conservation
Each tile is subdivided into coplanar quadrature elements. The intercepted power fraction of tile $k$ is bounded by:
$$F_{\text{intercepted}} = \int_{\text{tile}} \frac{(m+1)}{2\pi d_1^2} \cos^m(\phi_1) \cos(\theta_{\text{inc}}) \, dA$$
The reflected optical gain received by PD area $A_P$ at distance $d_2$ is strictly bounded by:
$$G_{\text{RIS}, k} \le \rho \cdot N_{\text{LED}} \cdot F_{\text{intercepted}}$$
where $\rho = 0.85$ is the mirror reflectivity.

### C. Effective Channels
$$\begin{aligned}
h_{AB}^{\text{eff}}(\mathbf{q}) &= h_{AB}^{\text{direct}} + h_{AB}^{\text{RIS}}(\mathbf{q}) \\
h_{AE}^{\text{eff}}(\mathbf{q}) &= h_{AE}^{\text{direct}} + h_{AE}^{\text{RIS}}(\mathbf{q}) \\
\mathbf{h}_{JB}^{\text{eff}}(\mathbf{q}) &= \mathbf{h}_{JB}^{\text{direct}} + \mathbf{h}_{JB}^{\text{RIS}}(\mathbf{q}) \\
\mathbf{h}_{JE}^{\text{eff}}(\mathbf{q}) &= \mathbf{h}_{JE}^{\text{direct}} + \mathbf{h}_{JE}^{\text{RIS}}(\mathbf{q})
\end{aligned}$$

---

## 3. Deep Reinforcement Learning (DRL-FJ) Architecture

### A. State-Action Sequence (Equation 6 & Section IV)
The temporal state sequence stacks history over sliding window $M = 11$:
$$\phi^{(k)} = \left[ \mathbf{s}^{(k-M)}, \mathbf{a}^{(k-M)}, \dots, \mathbf{s}^{(k-1)}, \mathbf{a}^{(k-1)}, \mathbf{s}^{(k)} \right]$$
* State vector: $\mathbf{s}^{(k)} = \left[ p_e^{(k-1)}, c_s^{(k-1)}, h_{AB}^{(k)}, E^{(k-1)} \right]$ (length 4).
* Action vector: $\mathbf{a}^{(k)} = [w_1, w_2, w_3, w_4, q]$ (length 5 in joint RIS mode).
* Total sequence length is $11 \times 9 + 4 = 103$, padded to $11 \times 11 = 121$ ($m_0 = 11$).

### B. Feature CNN ($F = [20, 40, 3, 2, 1, 1, 180, 180]$)
1. **Input:** Matrix of size $m_0 \times m_0 = 11 \times 11$.
2. **Conv Layer 1:** $f_1 = 20$ filters of size $m_1 = 3 \times 3$, stride $s_1 = 1$, followed by ReLU.  
   Output spatial dimension: $c_1 = (11 - 3)/1 + 1 = 9$. Feature map: $20 \times 9 \times 9$.
3. **Conv Layer 2:** $f_2 = 40$ filters of size $m_2 = 2 \times 2$, stride $s_2 = 1$, followed by ReLU.  
   Output spatial dimension: $c_2 = (9 - 2)/1 + 1 = 8$. Feature map: $40 \times 8 \times 8 = 2560$.
4. **FC Layer 1:** Linear $(2560 \to n_1 = 180)$ + ReLU.
5. **FC Layer 2:** Linear $(180 \to n_2 = 180)$. Outputs key $\hat{\mathbf{h}} \in \mathbb{R}^{180}$.

### C. Differentiable Neural Dictionary (DND) Memory Module
For each discrete action $\mathbf{a} \in \mathcal{W}$, a dictionary $\mathcal{D}_{\mathbf{a}} = (\mathbf{K}_{\mathbf{a}}, \mathbf{V}_{\mathbf{a}})$ stores keys $\mathbf{h}_j$ and values $v_j$.
$$\text{Ker}(\hat{\mathbf{h}}, \mathbf{h}_j) = \exp\left(-\frac{1}{2}\|\hat{\mathbf{h}} - \mathbf{h}_j\|_2^2\right)$$
$$\omega_j = \frac{\text{Ker}(\hat{\mathbf{h}}, \mathbf{h}_j)}{\sum_{p=1}^\zeta \text{Ker}(\hat{\mathbf{h}}, \mathbf{h}_p)}, \quad Q(\mathbf{s}, \mathbf{a}) = \sum_{j=1}^\zeta \omega_j v_j$$

### D. CNN Loss & Stochastic Gradient Descent (Equation 13)
$$\mathcal{L}(\theta) = \frac{1}{T}\sum_{t=1}^T \left( u^{(t)} - Q(\phi^{(t)}, \mathbf{a}^{(t)}; \theta) + \beta \max_{\mathbf{a}'} Q(\phi^{(t+1)}, \mathbf{a}'; \theta^{(k-1)}) \right)^2$$
Minimized via SGD with learning rate $\eta = 0.01$ and mini-batch size $T = 4$.


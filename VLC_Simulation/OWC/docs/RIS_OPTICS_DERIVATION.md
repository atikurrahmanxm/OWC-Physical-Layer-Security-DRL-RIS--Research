# Mathematical and Physical Derivation: Finite-Area Planar Optical RIS for Visible Light Communications

## 1. Executive Summary and Scope

This document provides the mathematical derivation and physical formulation for the finite-area planar optical Reconfigurable Intelligent Surface (RIS) implemented in `vlc/ris.py` and tested in `tests/test_ris_optics.py`.

The optical RIS module extends the 2024 research baseline (*"Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication"*, IEEE TWC 2024) to the joint **RIS + FJ + VLC + DRL** architecture agreed upon in `Agent.MD`.

### Key Modeling Principles
1. **Incoherent IM/DD Optical Propagation**:
   Visible light communication relies on intensity modulation with direct detection (IM/DD). The transmitted information and jamming signals modulate the instantaneous optical power of the LEDs, and the photodiode (PD) detector produces a photocurrent proportional to the intercepted optical power. Consequently, optical channels are **real-valued, non-negative scalar power gains**. RF complex phase shifts, array steering vectors, and wave interference models do not apply to incoherent wideband LED emission.
2. **Direct Current (DC) / Geometric Optics Approximation**:
   In the modeled indoor scenario (room $5 \times 5 \times 3\text{ m}$), propagation path delays for direct and reflected paths are on the order of $\Delta d / c \approx (1\text{ to }3\text{ m}) / (3 \times 10^8\text{ m/s}) \approx 3.3\text{ to }10\text{ ns}$. At modulation bandwidths and symbol rates well below $100\text{ MHz}$, delay dispersion and inter-symbol interference (ISI) are negligible. The scalar channel gain model assumes instantaneous optical power superposition.
3. **Finite Planar Specular Mirror Elements**:
   The RIS consists of an array of micro-mirrors / planar specular reflective tiles. Unlike an ideal continuous reflector or point-source mirror, each tile has finite physical dimensions, rotation-clearance constraints, and a bounded surface area.
4. **Finite Receiver Entrance Aperture Clipping**:
   Rather than treating the receiver as an infinitesimal point or using a binary center-ray hit/miss heuristic (which overcounts arbitrarily small mirrors), the model projects the specular cone of each mirror from its virtual source onto the receiver plane and clips this projected convex polygon against the finite effective entrance aperture of the optical concentrator using the Sutherland-Hodgman algorithm.
5. **Strict Optical Power Conservation**:
   The optical power delivered to any receiver through a reflective tile cannot exceed the total optical power intercepted by that tile multiplied by its surface reflectivity $\rho$. This conservation law is enforced via numerical Gauss-Legendre quadrature integration of source irradiance across the mirror surface.

---

## 2. Geometry and Panel Coordinate System

### 2.1 Room and Coordinate Axes
The room is modeled in Cartesian coordinates $[X, Y, Z]$ with dimensions $5.0 \times 5.0 \times 3.0\text{ m}$:
- Ceiling plane: $Z = 3.0\text{ m}$.
- Floor plane: $Z = 0.0\text{ m}$.
- Desk / receiver horizontal plane: $Z = 0.85\text{ m}$.
- Alice (ceiling transmitter): $\mathbf{p}_A = [2.5, 2.5, 3.0]\text{ m}$.
- Friendly jammers (4 ceiling fixtures):
  $\mathbf{p}_{J0} = [1.5, 1.5, 3.0]$, $\mathbf{p}_{J1} = [1.5, 3.5, 3.0]$, $\mathbf{p}_{J2} = [3.5, 1.5, 3.0]$, $\mathbf{p}_{J3} = [3.5, 3.5, 3.0]\text{ m}$.
- Bob (legitimate receiver nominal): $\mathbf{p}_B = [1.8, 1.6, 0.85]\text{ m}$.
- Eve (eavesdropper nominal): $\mathbf{p}_E = [3.2, 3.4, 0.85]\text{ m}$.

### 2.2 Panel Location and Wall Standoff
The optical RIS panel is mounted on the wall along the $X-Z$ plane at nominal center:
$$\mathbf{c}_{\text{panel}} = [x_c, y_c, z_c] = [2.5, 0.25, 2.6]\text{ m}.$$
- The nominal plane is parallel to $X-Z$ at $Y = 0.25\text{ m}$.
- The nominal inward-facing surface normal is:
  $$\hat{\mathbf{n}}_0 = [0.0, 1.0, 0.0] \quad (+Y\text{ direction, facing into the room}).$$
- The $0.25\text{ m}$ standoff from the $Y = 0.0\text{ m}$ wall provides mechanical clearance for mirror rotations inside the room boundaries.

### 2.3 Grid Partitioning and Tile Clearance
The panel has bounding dimensions:
- Width along $X$: $W = 1.0\text{ m}$.
- Height along $Z$: $H = 0.5\text{ m}$.
- Bounding area: $A_{\text{bounding}} = W \cdot H = 0.50\text{ m}^2$.
- Grid: $R = 2$ rows, $C = 3$ columns ($N = R \cdot C = 6$ tiles).

Grid pitches:
$$p_x = \frac{W}{C} = \frac{1.0}{3} \approx 0.3333\text{ m}, \quad p_z = \frac{H}{R} = \frac{0.5}{2} = 0.2500\text{ m}.$$

To prevent mechanical collision between adjacent tiles under maximum 3D rotation, each square tile has a rotation-clearance diameter:
$$D = 0.90 \cdot \min(p_x, p_z) = 0.90 \cdot 0.2500\text{ m} = 0.2250\text{ m}.$$

The side length $s$ of each square tile inscribed in this clearance circle is:
$$s = \frac{D}{\sqrt{2}} = \frac{0.2250}{\sqrt{2}} \approx 0.1591\text{ m} \quad (\approx 15.91\text{ cm}).$$

The reflecting area per tile is:
$$A_{\text{tile}} = s^2 = \frac{D^2}{2} \approx 0.02531\text{ m}^2.$$

The total actual reflecting area is:
$$A_{\text{actual}} = N \cdot A_{\text{tile}} = 6 \cdot 0.02531 \approx 0.15188\text{ m}^2.$$
Notice that $A_{\text{actual}} \approx 0.1519\text{ m}^2 < A_{\text{bounding}} = 0.50\text{ m}^2$. The difference represents structural framing, mechanical gimbals, and rotational clearance gaps.

Tile centers $\mathbf{M}_{r, c}$ for $r \in \{0, \dots, R-1\}$ and $c \in \{0, \dots, C-1\}$:
$$\mathbf{M}_{r, c} = \left[ x_c - \frac{W}{2} + \left(c + \frac{1}{2}\right) p_x, \; y_c, \; z_c - \frac{H}{2} + \left(r + \frac{1}{2}\right) p_z \right].$$

---

## 3. Kinematics, Orthonormal Basis, and Normal Aiming

### 3.1 Orthonormal Tile Basis via Rodrigues' Rotation
In the un-tilted state ($\hat{\mathbf{n}} = \hat{\mathbf{n}}_0 = [0, 1, 0]$), the tile's local tangent vectors are:
$$\hat{\mathbf{u}}_0 = [1.0, 0.0, 0.0] \quad (\text{horizontal / width}), \quad \hat{\mathbf{v}}_0 = [0.0, 0.0, 1.0] \quad (\text{vertical / height}).$$

When the mirror tilts to a target unit normal $\hat{\mathbf{n}}$, the local axes rotate accordingly. Let:
$$\mathbf{k} = \hat{\mathbf{n}}_0 \times \hat{\mathbf{n}}, \quad s_k = \|\mathbf{k}\| = \sin\theta, \quad c_k = \hat{\mathbf{n}}_0 \cdot \hat{\mathbf{n}} = \cos\theta.$$

If $s_k < 10^{-12}$:
- If $c_k > 0$: $\hat{\mathbf{u}} = \hat{\mathbf{u}}_0$, $\hat{\mathbf{v}} = \hat{\mathbf{v}}_0$.
- If $c_k \le 0$: $\hat{\mathbf{u}} = -\hat{\mathbf{u}}_0$, $\hat{\mathbf{v}} = \hat{\mathbf{v}}_0$.

Otherwise, with unit rotation axis $\hat{\mathbf{k}} = \mathbf{k} / s_k$, any vector $\mathbf{w}$ is rotated by Rodrigues' formula:
$$R(\mathbf{w}) = \mathbf{w} \cos\theta + (\hat{\mathbf{k}} \times \mathbf{w}) \sin\theta + \hat{\mathbf{k}} (\hat{\mathbf{k}} \cdot \mathbf{w}) (1 - \cos\theta).$$
Applying $R$ to $\hat{\mathbf{u}}_0$ and $\hat{\mathbf{v}}_0$, followed by Gram-Schmidt re-orthogonalization against $\hat{\mathbf{n}}$, yields the orthonormal frame $(\hat{\mathbf{u}}, \hat{\mathbf{v}}, \hat{\mathbf{n}})$.

The four corners of the square tile centered at $\mathbf{M}$ are:
$$\mathbf{V}_0 = \mathbf{M} - \frac{s}{2} \hat{\mathbf{u}} - \frac{s}{2} \hat{\mathbf{v}}, \quad \mathbf{V}_1 = \mathbf{M} + \frac{s}{2} \hat{\mathbf{u}} - \frac{s}{2} \hat{\mathbf{v}},$$
$$\mathbf{V}_2 = \mathbf{M} + \frac{s}{2} \hat{\mathbf{u}} + \frac{s}{2} \hat{\mathbf{v}}, \quad \mathbf{V}_3 = \mathbf{M} - \frac{s}{2} \hat{\mathbf{u}} + \frac{s}{2} \hat{\mathbf{v}}.$$

### 3.2 Ideal Specular Aiming and Spherical Cap Tilt Constraint
To aim a tile from source $\mathbf{S}$ through mirror center $\mathbf{M}$ to receiver $\mathbf{R}$, the ideal specular normal bisects the incident and reflected directions:
$$\hat{\mathbf{v}}_S = \frac{\mathbf{S} - \mathbf{M}}{\|\mathbf{S} - \mathbf{M}\|}, \quad \hat{\mathbf{v}}_R = \frac{\mathbf{R} - \mathbf{M}}{\|\mathbf{R} - \mathbf{M}\|}, \quad \hat{\mathbf{n}}_{\text{ideal}} = \frac{\hat{\mathbf{v}}_S + \hat{\mathbf{v}}_R}{\|\hat{\mathbf{v}}_S + \hat{\mathbf{v}}_R\|}.$$

The actuator mechanical tilt limit is $\theta_{\max} = 85.0^\circ$. Let $\theta = \arccos(\hat{\mathbf{n}}_{\text{ideal}} \cdot \hat{\mathbf{n}}_0)$. If $\theta > \theta_{\max}$, the normal is projected onto the boundary of the spherical cap around $\hat{\mathbf{n}}_0$:
$$\mathbf{n}_{\perp} = \hat{\mathbf{n}}_{\text{ideal}} - (\hat{\mathbf{n}}_{\text{ideal}} \cdot \hat{\mathbf{n}}_0) \hat{\mathbf{n}}_0, \quad \hat{\mathbf{u}}_{\perp} = \frac{\mathbf{n}_{\perp}}{\|\mathbf{n}_{\perp}\|},$$
$$\hat{\mathbf{n}}_{\text{constrained}} = \cos(\theta_{\max}) \hat{\mathbf{n}}_0 + \sin(\theta_{\max}) \hat{\mathbf{u}}_{\perp}.$$

---

## 4. Image-Source Projection and Finite Aperture Clipping

### 4.1 Reflecting Halfspace Check
A specular reflection is physically valid only when both the source $\mathbf{S}$ and receiver $\mathbf{R}$ reside on the active reflecting side of the mirror plane:
$$\hat{\mathbf{n}} \cdot (\mathbf{S} - \mathbf{M}) > 0 \quad \text{and} \quad \hat{\mathbf{n}} \cdot (\mathbf{R} - \mathbf{M}) > 0.$$
If either quantity is $\le 0$, the path is blocked by the mirror substrate, yielding exact zero gain.

### 4.2 Virtual Source and Reflected LED Optical Axis
The mirror plane has equation $\hat{\mathbf{n}} \cdot (\mathbf{x} - \mathbf{M}) = 0$. The virtual image source $\mathbf{S}'$ is:
$$\mathbf{S}' = \mathbf{S} - 2 [\hat{\mathbf{n}} \cdot (\mathbf{S} - \mathbf{M})] \hat{\mathbf{n}}.$$

The ceiling LEDs have downward optical axis $\hat{\mathbf{a}}_{\text{LED}} = [0.0, 0.0, -1.0]$. Across the mirror, this axis reflects to:
$$\hat{\mathbf{a}}'_{\text{LED}} = \hat{\mathbf{a}}_{\text{LED}} - 2 (\hat{\mathbf{a}}_{\text{LED}} \cdot \hat{\mathbf{n}}) \hat{\mathbf{n}}.$$

### 4.3 Mirror Corner Projection onto Receiver Plane
Rays radiating from virtual source $\mathbf{S}'$ through mirror corners $\mathbf{V}_k$ propagate toward the receiver plane at $Z = R_z$. The ray equation is $\mathbf{P}_k(\lambda) = \mathbf{S}' + \lambda (\mathbf{V}_k - \mathbf{S}')$. Setting the $Z$-component to $R_z$:
$$\lambda_k = \frac{R_z - S'_z}{V_{k,z} - S'_z}.$$

A forward physical projection requires $\lambda_k > 1.0$ (since the mirror is at $\lambda = 1.0$, and the receiver plane lies beyond the mirror relative to the virtual source). If for any corner $\lambda_k \le 1.0$, $|V_{k,z} - S'_z| < 10^{-12}$, or $\lambda_k$ is not finite, the specular cone does not intersect the receiver plane in the forward halfspace, yielding zero gain.

For valid projections, the 2D projected coordinates on the receiver plane are:
$$P_{k} = (P_{k,x}, P_{k,y}) = (S'_x + \lambda_k (V_{k,x} - S'_x), \; S'_y + \lambda_k (V_{k,y} - S'_y)).$$

### 4.4 Receiver Effective Entrance Aperture
The receiver photodiode has physical area $A_P = 1.0 \times 10^{-4}\text{ m}^2$ ($1\text{ cm}^2$). With refractive index $n_0 = 1.5$ and semi-FoV $\psi_F = 60^\circ$, the non-imaging optical concentrator gain is:
$$g_{\text{conc}} = \frac{n_0^2}{\sin^2\psi_F} = \frac{1.5^2}{\sin^2(60^\circ)} = \frac{2.25}{0.75} = 3.0.$$

The effective entrance aperture collecting optical rays into the concentrator has area:
$$A_{\text{eff}} = A_P \cdot g_{\text{conc}} = 3.0 \times 10^{-4}\text{ m}^2 = 3.0\text{ cm}^2.$$
The aperture is modeled as a square of side $w_{\text{eff}} = \sqrt{A_{\text{eff}}} \approx 0.01732\text{ m}$ ($1.732\text{ cm}$), centered at receiver position $(R_x, R_y)$:
$$x \in \left[R_x - \frac{w_{\text{eff}}}{2}, \; R_x + \frac{w_{\text{eff}}}{2}\right], \quad y \in \left[R_y - \frac{w_{\text{eff}}}{2}, \; R_y + \frac{w_{\text{eff}}}{2}\right].$$

> **Important**: Because the integration area is the expanded effective entrance aperture $A_{\text{eff}}$, the optical concentrator gain $g_{\text{conc}}$ is **not multiplied again** in the integrand. Doing so would double-count the concentrator gain.

### 4.5 Sutherland-Hodgman Polygon Clipping
The projected quadrilateral $[P_0, P_1, P_2, P_3]$ is clipped against the four boundary edges of the square receiver entrance aperture using the standard Sutherland-Hodgman convex polygon clipping algorithm.
If the resulting clipped polygon has fewer than 3 vertices or area $\le 10^{-18}\text{ m}^2$, the specular light cone misses the receiver aperture entirely, yielding zero gain.

### 4.6 Triangle Fan Quadrature and FoV Gating
Let the clipped polygon vertices be $\{C_0, C_1, \dots, C_{p-1}\}$. The polygon is triangulated into $p-2$ triangles:
$$T_j = (C_0, C_{j+1}, C_{j+2}), \quad j = 0, \dots, p-3.$$

On each triangle $T_j$ with area $A_{T_j}$, a symmetric 3-point order-2 Gaussian quadrature rule evaluates the integrand at edge midpoints:
$$\mathbf{q}_1 = \frac{C_0 + C_{j+1}}{2}, \quad \mathbf{q}_2 = \frac{C_{j+1} + C_{j+2}}{2}, \quad \mathbf{q}_3 = \frac{C_{j+2} + C_0}{2}, \quad w = \frac{A_{T_j}}{3}.$$

At each sample point $\mathbf{q} = (q_x, q_y, R_z)$ on the receiver plane:
1. Propagation vector: $\mathbf{L} = \mathbf{q} - \mathbf{S}'$, with length $L = \|\mathbf{L}\|$.
2. Irradiance emission angle from virtual LED:
   $$\cos\phi = \frac{\mathbf{L} \cdot \hat{\mathbf{a}}'_{\text{LED}}}{L}.$$
   If $\cos\phi \le 0$, sample contribution is 0.
3. Incidence angle on upward-facing photodiode ($\hat{\mathbf{n}}_{\text{PD}} = [0, 0, 1]$):
   $$\cos\psi = \frac{S'_z - R_z}{L}.$$
   If $\cos\psi \le 0$, sample contribution is 0.
4. **Receiver FoV Check**:
   $$\psi = \arccos(\text{clip}(\cos\psi, -1.0, 1.0)).$$
   If $\psi > \psi_F = \text{radians}(60.0^\circ)$, the ray falls outside the photodiode acceptance cone, yielding 0.
5. Differential Lambertian path contribution:
   $$dG(\mathbf{q}) = \frac{m + 1}{2\pi L^2} (\cos\phi)^m \cos\psi.$$
   where Lambertian order $m = -\frac{\ln 2}{\ln\cos\phi_{1/2}} = 1.0$ for $\phi_{1/2} = 60^\circ$.

The integrated geometric optical path gain is:
$$G_{\text{geom}} = \rho \cdot N_{\text{LED}} \sum_{j} \sum_{k=1}^3 \frac{A_{T_j}}{3} dG(\mathbf{q}_{j, k}).$$

---

## 5. Optical Power Conservation and Intercepted Power Bound

To ensure physical realism and prevent artificial power creation (e.g. if an artificially large receiver aperture is tested), each tile's reflected optical path gain is bounded by the total optical power intercepted by that tile.

For a tile centered at $\mathbf{M}$ with side $s$, local basis $(\hat{\mathbf{u}}, \hat{\mathbf{v}})$, and normal $\hat{\mathbf{n}}$:
$$F_{\text{intercepted}} = \int_{-s/2}^{s/2} \int_{-s/2}^{s/2} \frac{m+1}{2\pi d_{\text{SM}}^2} (\cos\phi_{\text{src}})^m \cos\theta_{\text{inc}} \, du \, dv,$$
where for point $\mathbf{Q}(u, v) = \mathbf{M} + u \hat{\mathbf{u}} + v \hat{\mathbf{v}}$:
- $d_{\text{SM}} = \|\mathbf{Q} - \mathbf{S}\|$.
- $\cos\phi_{\text{src}} = \frac{S_z - Q_z}{d_{\text{SM}}}$.
- $\cos\theta_{\text{inc}} = \frac{(\mathbf{S} - \mathbf{Q}) \cdot \hat{\mathbf{n}}}{d_{\text{SM}}}$.

This 2D integral is evaluated via a $3 \times 3$ Gauss-Legendre product quadrature (degree 5 accuracy).
The maximum optical power that the tile can reflect from this source fixture is:
$$G_{\text{bound}} = \rho \cdot N_{\text{LED}} \cdot F_{\text{intercepted}}.$$

The final tile optical path gain is:
$$G_{\text{tile}} = \min(G_{\text{geom}}, G_{\text{bound}}).$$

Total optical channel gain across all $N$ tiles:
$$G = \sum_{i=0}^{N-1} G_{\text{tile}, i}.$$

---

## 6. Electrical Channel Gain Conversion

In accordance with Section II-B of the baseline paper, the optical channel gain $G$ converts to electrical channel gain $h$ through:
$$h = R_{\text{pd}} \cdot \eta \cdot G,$$
where:
- $R_{\text{pd}} = 0.54\text{ A/W}$ is the photodiode responsivity.
- $\eta = 1.0\text{ W/A}$ is the electro-optical conversion efficiency.
- Fixture aggregation ($N_{\text{LED}} = 4$) occurs **exactly once** in $G$.
- Electrical conversion ($R_{\text{pd}} \cdot \eta$) occurs **exactly once** in $h$.

---

## 7. Oracle Codebook Configurations

The discrete codebook consists of five scenario-specific configurations:

| Index | Name | Physical Orientation / Tile Normals | Description |
|---|---|---|---|
| 0 | `off` | Nominal $\hat{\mathbf{n}}_0 = [0, 1, 0]$ (stowed / inactive) | Exact zero reflected electrical gains ($h_{\text{AB}} = 0, h_{\text{AE}} = 0, \mathbf{h}_{\text{JB}} = \mathbf{0}, \mathbf{h}_{\text{JE}} = \mathbf{0}$). Reference baseline state. |
| 1 | `alice_to_bob` | All tiles aimed from Alice to Bob through tile centers $\mathbf{M}_i$ | Maximizes legitimate signal power reflected to Bob. |
| 2 | `jammers_to_eve` | Deterministic round-robin: tile $i$ aimed from jammer $i \pmod 4$ to Eve | Concentrates friendly jamming optical power onto the eavesdropper. |
| 3 | `split_bob_eve` | Tiles $0 \dots 2$ aimed Alice $\to$ Bob; tiles $3 \dots 5$ aimed Jammers $\to$ Eve | Balanced allocation providing simultaneous signal boost and jamming redirect. |
| 4 | `neutral` | All tiles un-tilted: $\hat{\mathbf{n}} = [0, 1, 0]$ facing $+Y$ | Flat specular wall reflection baseline. |

### Strict Multi-Link Physical Sharing Rule
For any configuration $q \in \{0, \dots, 4\}$, each tile $i$ has a single physical orientation $\hat{\mathbf{n}}_i(q)$.
When evaluating $h_{\text{AB}}, h_{\text{AE}}, \mathbf{h}_{\text{JB}}, \mathbf{h}_{\text{JE}}$, all sources reflect off the **identical stored normal vectors**. The model never re-aims tiles independently for different links within the same codebook configuration.

---

## 8. Physical Assumptions, Limitations, and Disclaimers

1. **Stationary Oracle Codebook**:
   The codebook normals are derived from the true node positions $(\mathbf{p}_A, \mathbf{p}_B, \mathbf{p}_E, \mathbf{p}_{J})$. This represents an oracle benchmark for simulation studies. In practical deployments with an uncooperative or mobile Eve, CSI uncertainty and tracking errors must be modeled.
2. **Absence of Diffuse Scattering**:
   The model evaluates only specular reflection from the mirror array. Diffuse reflections from walls, floor, and ceiling are neglected, consistent with the direct line-of-sight baseline in the 2024 paper.
3. **No Body Blockage / Occlusion**:
   Unobstructed propagation paths between all sources, tiles, and receivers are assumed.
4. **No Empirical Prototype Validation**:
   This module implements a mathematically self-consistent geometric-optics model based on established visible-light communication physics. It has not been calibrated against physical hardware prototypes.
5. **Preservation of 2024 Baseline**:
   The direct VLC channel, friendly-jamming beamforming structure, and secrecy rate definitions from Liu et al. (2024) are preserved intact. Setting index 0 or disabling the RIS reproduces the exact direct-channel baseline.

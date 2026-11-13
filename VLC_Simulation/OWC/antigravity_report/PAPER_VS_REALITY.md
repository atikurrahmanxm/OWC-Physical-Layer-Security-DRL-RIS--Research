# Technical Audit: Paper Equations vs. Published Figures

## 1. Summary of the Discrepancy

When comparing the equations and parameters in the 2024 paper (*Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication*, IEEE TWC 2024) with the curves plotted in its figures (Fig. 5, Fig. 6, Fig. 7), an **inherent $\sim 52\text{ dB}$ numerical gap** exists between the printed secrecy formula and the printed BER formula.

---

## 2. Mathematical Derivation

### A. The Printed Secrecy Rate (Equation 21)
Corollary 1 of the paper derives the theoretical upper bound on secrecy rate under Zero-Forcing ($\mathbf{h}_{JB}^T \mathbf{w} = 0$) and optimal Eve jamming ($H^* = h_{AE}/\log_2\sqrt{e}$):
$$c_s^* = \frac{1}{2}\log_2\left(1 + \frac{2 h_{AB}^2 \alpha^2 I_D^2}{\pi e \sigma_B^2}\right) - \left[\log_2(\log_2\sqrt{e}) + 1\right]$$

Substitute the constant term:
$$\log_2\sqrt{e} = \frac{1}{2}\log_2(e) \approx 0.7213475$$
$$\log_2(\log_2\sqrt{e}) + 1 = \log_2(0.7213475) + 1 \approx -0.47123 + 1 = 0.52877$$

Now substitute the Table I parameters:
* $P_T = 1.0\text{ W}$, $\eta = 1.0$, $I_D = P_T/\eta = 1.0\text{ A}$
* Modulation index $\alpha = 10\% = 0.10$
* Noise power $\sigma_B^2 = -98.79\text{ dBm} = 10^{(-128.79/10)} \approx 1.3213 \times 10^{-13}\text{ W}$
* Alice at $(2.5, 2.5, 3.0)$, Bob at $(1.8, 1.6, 0.85)$ gives electrical gain:
  $$h_{AB} \approx 2.7183 \times 10^{-5}\text{ A/W}$$

Compute the numerator and denominator inside the log:
$$\text{Numerator} = 2 \cdot (2.7183 \times 10^{-5})^2 \cdot (0.10)^2 \cdot (1.0)^2 \approx 1.4778 \times 10^{-11}$$
$$\text{Denominator} = \pi \cdot e \cdot (1.3213 \times 10^{-13}) \approx 1.1283 \times 10^{-12}$$
$$\frac{\text{Numerator}}{\text{Denominator}} \approx 13.097$$

Therefore:
$$c_s^* = \frac{1}{2}\log_2(1 + 13.097) - 0.52877 = \frac{1}{2}\log_2(14.097) - 0.52877 = 1.90865 - 0.52877 = \mathbf{1.3799\text{ bps/Hz}}$$

* **Result 1:** Under the printed Table I noise and parameters, the theoretical bound is **$1.3799\text{ bps/Hz}$**.
* Even in the interference-free channel ($\mathbf{h}_{JB}^T \mathbf{w} = 0, \text{Eve} = 0$), Bob's capacity is $\frac{1}{2}\log_2(14.097) = \mathbf{1.90865\text{ bps/Hz}}$.
* **Fig. 6(a) Conflict:** Fig. 6(a) plots a theoretical bound of **$5.81\text{ bps/Hz}$** and a DRL curve of **$5.68\text{ bps/Hz}$**.
* To achieve $c_s^* = 5.81\text{ bps/Hz}$ from Eq. (21):
  $$\frac{1}{2}\log_2\left(1 + \text{SINR}\right) = 5.81 + 0.52877 = 6.33877 \implies 1 + \text{SINR} = 2^{12.6775} \approx 6563$$
  $$\text{SINR} \approx 6562 \implies \text{SNR (dB)} \approx \mathbf{64.47\text{ dB}}$$

---

### B. The Printed BER Formula (Equation 14 & 22)
The theoretical 4-PAM BER under Zero-Forcing is:
$$p_e^* = \frac{3}{4} \text{erfc}\left(\sqrt{\frac{2 P_T h_{AB}^2}{5 \sigma_B^2}}\right)$$

Let $\gamma = \frac{2 P_T h_{AB}^2}{5 \sigma_B^2}$.
* **Fig. 6(b) Target:** The paper plots a DRL BER of $\approx 2.0 \times 10^{-4}$ at slot 1200 and a bound around $1.0 \times 10^{-4}$.
* Solving $\frac{3}{4}\text{erfc}(\sqrt{\gamma}) = 1.0 \times 10^{-4}$:
  $$\sqrt{\gamma} \approx 2.68 \implies \gamma \approx 7.18$$
* This corresponds to an electrical SNR of:
  $$\text{SNR}_{\text{lin}} = \frac{P_T h_{AB}^2}{\sigma_B^2} = \frac{5}{2}\gamma = \frac{5}{2}(7.18) \approx 17.95 \implies \mathbf{12.54\text{ dB}}$$

---

## 3. The 52 dB Inconsistency

| Requirement | Necessary Electrical SNR | What Happens to the Other Metric? |
|---|---|---|
| **Fit Fig. 6(b) BER ($10^{-4}$)** | **$12.54\text{ dB}$** | Secrecy Rate Eq. (21) evaluates to **$0.000\text{ bps/Hz}$** (negative argument clamped to zero) |
| **Fit Fig. 6(a) Secrecy ($5.81\text{ bps/Hz}$)** | **$64.47\text{ dB}$** | BER Eq. (22) evaluates to **$0.000\text{ (float underflow } < 10^{-25}\text{)}$**, not $10^{-4}$ |

The difference between $64.47\text{ dB}$ and $12.54\text{ dB}$ is **$51.93\text{ dB}$**.

---

## 4. Why We Do Not Fake the Numbers

In prior revisions, developers attempted to bridge this gap by introducing artificial scaling:
* `snr_scale = 500`
* Hardcoded curve exponents `np.exp(-slots / 300)`
* Arbitrary JS display factors (`11.5 * gamma`, `34.3`, `schemeFactor`)

**Why this is scientifically unacceptable:**
1. It destroys the mathematical link between the code and the physical VLC wiretap model.
2. It invalidates any research on extensions (such as RIS): an extension tested on a fake curve produces fake gains.
3. It violates academic honesty.

**Our Stand:**
* We implement the exact published equations verbatim.
* We document the paper's internal discrepancy transparently.
* When testing our RIS extension, we apply the exact same physics and noise model to both baseline and RIS cases, establishing genuine, verifiable relative improvements.


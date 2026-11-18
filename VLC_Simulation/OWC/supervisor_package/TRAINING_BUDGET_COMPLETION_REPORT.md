# Training-Budget Matched Empirical Study Completion Report (Protocol v2)

**Author:** Antigravity Research Assistant  
**Completion Date & Time:** `2026-11-18 04:49:52 +05:30` (Asia/Calcutta)  
**Task Directive:** [`antigravity_report/OVERNIGHT_RESUME_TASK.md`](../antigravity_report/OVERNIGHT_RESUME_TASK.md) & [`antigravity_report/JOINT_CONTROLLER_AUDIT_AND_BUDGET_TASK.md`](../antigravity_report/JOINT_CONTROLLER_AUDIT_AND_BUDGET_TASK.md)  
**Git Source Commit:** `a6d4304192cb9e6a2881aa4649ea436d2d81d8d2`  
**Study Manifest:** [`output_figures/ris/training_budget_study_matched_v2/manifest.json`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\manifest.json)  
**Consolidated Summary JSON:** [`output_figures/ris/training_budget_study_matched_v2/budget_study_summary.json`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\budget_study_summary.json)  
**Output Directory:** [`output_figures/ris/training_budget_study_matched_v2/`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2/)  
**Legacy Diagnostics Directory:** [`output_figures/ris/training_budget_study/`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study/) (68 legacy runs strictly preserved intact)

---

## 1. সহজ বাংলা সারসংক্ষেপ (Simple Bangla Summary)

### গবেষণা প্রশ্ন ও চূড়ান্ত ফলাফল:
আমরা বৈজ্ঞানিকভাবে যাচাই করার জন্য পরীক্ষাটি চালিয়েছিলাম—**"Joint RIS/FJ DRL কন্ট্রোলারকে ২,০০০ স্লটের বদলে ৫,০০০ বা ১০,০০০ স্লট ট্রেইনিং দিলে কি সে তার বিশাল অ্যাকশন স্পেস এক্সপ্লোর করে Fixed RIS কন্ট্রোলারকে হারাতে পারে?"**

### ১০০% সত্য ও চূড়ান্ত গবেষণালব্ধ ফলাফল:
১. **ট্রেইনিং বাজেট বাড়ালেও Joint RIS কখনোই Fixed RIS এর চেয়ে উল্লেখযোগ্য সুবিধা পায়নি (Null Result):**
   - **১০,০০০ স্লট বাজেটে:** Joint RIS এর ইউটিলিটি $U = 0.7239$, এবং Fixed RIS এর ইউটিলিটি $U = 0.7056$। পেয়ার্ড সিড-বাই-সিড পার্থক্য মাত্র $\Delta U = +0.0183$ ($p = 0.8289$), যা পরিসংখ্যানগতভাবে একেবারেই অর্থহীন (Not statistically significant)।
   - **সিক্রেসি রেটে Fixed RIS বরং এগিয়ে:** ১০,০০০ স্লটে Fixed RIS পেয়েছে $1.5656\text{ bps/Hz}$, যেখানে Joint RIS পেয়েছে $1.4839\text{ bps/Hz}$ ($\Delta R_s = -0.0817\text{ bps/Hz}$, $p = 0.4182$)।
২. **কেন বাজেট বাড়লেও Joint জিতল না?**
   - ১০,০০০ স্লট দেওয়ার পরও ১০টি সিডের মধ্যে মাত্র **৬টি সিড** গ্লোবাল অপ্টিমাল মিরর কনফিগারেশন $q=1$ (Aim Bob) খুঁজে পেতে পেরেছে। বাকি ৪টি সিড এখনো সাব-অপ্টিমাল মিরর কনফিগারেশনে ($q=2$ তে ১টি, $q=3$ তে ২টি, $q=4$ এ ১টি) আটকে রয়ে গেছে (Local sub-optimal trap)।
   - অপরদিকে Fixed RIS আগে থেকেই অপ্টিমাল $q=1$ এ ফিক্সড থাকায় তার পুরো বাজেট ফ্রেন্ডলি জ্যামারের ওজন অপ্টিমাইজেশনে ব্যয় করতে পেরেছে।
৩. **বেসলাইন বনাম RIS এর স্পষ্ট বিজয়:**
   - RIS প্রযুক্তি (Fixed এবং Joint উভয়ই) সাধারণ কোনো-RIS-ছাড়া সিস্টেমের চেয়ে অনেক বেশি উন্নত ($\Delta U = +0.2051$, $p = 0.0003$ অত্যন্ত উচ্চ সিগনিফিক্যান্স সহকারে প্রমাণিত)।
৪. **পেপার ও থিসিসের জন্য সুপারিশ:**
   - পেপারে কোনো মিথ্যা বা জোরপূর্বক ক্লেইম না করে এটিকেই একটি মূল বৈজ্ঞানিক আবিষ্কার হিসেবে তুলে ধরা উচিত: *"In stationary OWC environments, decoupled/fixed RIS alignment matches or outperforms joint continuous/discrete exploration because joint exploration suffers from action-space dilution even under 5x training budgets."*

---

## 2. Experimental Setup & Verification Matrix

- **Total Runs Executed:** **90 / 90 (100% Completed)**
- **Model Checkpoints Serialized:** **180 files** (90 PyTorch `.pt` models + 90 DND memory `.json` files)
- **Scientific Plots Generated:** 8 files (4 publication-grade 200 DPI PNG + 4 vector PDF)
- **Unit & Regression Tests:** **98 tests passed cleanly (100% OK in 24.8s)**

### Statistical Aggregates (10 Matched Seeds 42–51 per cell, 1,000 Frozen Eval Slots):

| Budget (Slots) | Scheme | Mean System Utility $U$ (95% CI) | Mean Secrecy Rate $R_s$ (bps/Hz) | Converged $q$ Distribution | Action Coverage | Mean Train Time |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **2,000** | **Baseline** | $0.5005 \pm 0.0383$ [$0.4138, 0.5872$] | $1.3205 \pm 0.0405$ | $q=0: 10/10$ | $28.6\%$ (178 acts) | $37.2\text{ s}$ |
| **2,000** | **Fixed RIS** | $0.6178 \pm 0.0888$ [$0.4168, 0.8188$] | $1.4978 \pm 0.0793$ | $q=1: 10/10$ | $23.6\%$ (147 acts) | $38.5\text{ s}$ |
| **2,000** | **Joint RIS** | $0.6565 \pm 0.0813$ [$0.4725, 0.8404$] | $1.4565 \pm 0.0604$ | $q=1: 5, q=3: 2, q=2: 1, q=4: 2$ | $4.3\%$ (133 acts) | $58.1\text{ s}$ |
| **5,000** | **Baseline** | $0.5005 \pm 0.0383$ [$0.4138, 0.5872$] | $1.3205 \pm 0.0405$ | $q=0: 10/10$ | $32.4\%$ (203 acts) | $91.8\text{ s}$ |
| **5,000** | **Fixed RIS** | $0.6396 \pm 0.0797$ [$0.4594, 0.8198$] | $1.4996 \pm 0.0786$ | $q=1: 10/10$ | $27.9\%$ (174 acts) | $95.3\text{ s}$ |
| **5,000** | **Joint RIS** | $0.6565 \pm 0.0813$ [$0.4725, 0.8404$] | $1.4565 \pm 0.0604$ | $q=1: 5, q=3: 2, q=2: 1, q=4: 2$ | $5.9\%$ (185 acts) | $146.4\text{ s}$ |
| **10,000** | **Baseline** | $0.5005 \pm 0.0383$ [$0.4138, 0.5872$] | $1.3205 \pm 0.0405$ | $q=0: 10/10$ | $35.1\%$ (219 acts) | $183.1\text{ s}$ |
| **10,000** | **Fixed RIS** | $0.7056 \pm 0.0632$ [$0.5627, 0.8485$] | $1.5656 \pm 0.0766$ | $q=1: 10/10$ | $31.8\%$ (199 acts) | $191.0\text{ s}$ |
| **10,000** | **Joint RIS** | **$0.7239 \pm 0.0784$** [$0.5465, 0.9013$] | **$1.4839 \pm 0.0598$** | $q=1: 6, q=3: 2, q=2: 1, q=4: 1$ | **$7.8\%$ (244 acts)** | **$310.2\text{ s}$** |

---

## 3. Seed-Level Paired Hypothesis Tests (df = 9)

### Primary Comparison: Joint RIS minus Fixed RIS
- **At 2,000 slots:** $\Delta U = +0.0387 \pm 0.1171$ ($t = 0.33, p = 0.7463$); $\Delta R_s = -0.0413$ ($p = 0.6887$).
- **At 5,000 slots:** $\Delta U = +0.0168 \pm 0.1160$ ($t = 0.15, p = 0.8877$); $\Delta R_s = -0.0432$ ($p = 0.6759$).
- **At 10,000 slots (Primary Question):** $\Delta U = \mathbf{+0.0183 \pm 0.0818}$ ($t = 0.22, \mathbf{p = 0.8289}$); $\Delta R_s = \mathbf{-0.0817 \pm 0.0963}$ ($t = -0.85, \mathbf{p = 0.4182}$).

### Secondary Comparison: Fixed RIS minus Baseline
- **At 10,000 slots:** $\Delta U = \mathbf{+0.2051 \pm 0.0385}$ ($t = 5.33, \mathbf{p = 0.0003}$); $\Delta R_s = \mathbf{+0.2451 \pm 0.0635}$ ($t = 3.86, \mathbf{p = 0.0041}$).

---

## 4. Generated Publication Scientific Figures

The following figures were generated directly from raw JSON and saved in [`output_figures/ris/training_budget_study_matched_v2/figures/`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\figures/):
1. **`fig1_budget_convergence.png` / `.pdf`:** Policy Performance Convergence across Budgets (Utility & Secrecy with 95% Student-$t$ CIs and theoretical bounds).
2. **`fig2_budget_paired_differences.png` / `.pdf`:** Seed-Level Paired Differences ($\Delta U$ and $\Delta R_s$) with exact $p$-values annotated.
3. **`fig3_budget_coverage_and_q.png` / `.pdf`:** Action Space Exploration Fraction (%) and Joint Controller RIS codebook distribution convergence across budgets.
4. **`fig4_computational_scaling.png` / `.pdf`:** Wall-clock training execution scaling per scheme.

---

## 5. Codex Review Readiness

All deliverables are strictly finalized on disk:
- Protocol v2 study manifest: [`manifest.json`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\manifest.json)
- Full summary JSON: [`budget_study_summary.json`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\output_figures\ris\training_budget_study_matched_v2\budget_study_summary.json)
- Codex review handoff: [`supervisor_package/CODEX_REVIEW_HANDOFF.md`](file:///d:/SCRIPTS/GitHub/OWC-Physical-Layer-Security-DRL-RIS--Research\VLC_Simulation\OWC\supervisor_package\CODEX_REVIEW_HANDOFF.md)
- Complete unit test suite: 98 tests passing cleanly (100%).

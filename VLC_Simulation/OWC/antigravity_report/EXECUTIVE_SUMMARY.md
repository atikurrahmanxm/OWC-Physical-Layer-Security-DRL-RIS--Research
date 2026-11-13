# Executive Summary / নির্বাহী সারসংক্ষেপ

## English

### Project Scope & Mandate
This research project implements the indoor Visible Light Communication (VLC) physical-layer security framework from the 2024 IEEE Transactions on Wireless Communications paper:
*“Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication”* (Liu et al., DOI: 10.1109/TWC.2024.3458046).

The agreed research objective is to retain the original system model as the baseline and extend it with a wall-mounted **Optical Reconfigurable Intelligent Surface (RIS)** (an array of tiltable micro-mirrors) jointly controlled with the four Friendly Jammers via **Deep Reinforcement Learning (DRL)**:
$$\text{Architecture: } \mathbf{RIS + FJ + VLC + DRL}$$

### What Was Accomplished & Verified
1. **Model & Equation Implementation:** The core equations (Eq. 1 to 23) and Table I parameter framework from the 2024 paper are implemented cleanly, with explicit energy model options (`l1` non-negative vs. `paper_signed`).
2. **Comprehensive Test Suite:** All **87 unit tests** across the codebase pass (`tests/` -> `Ran 87 tests in 28.438s OK`).
3. **Physical Optical RIS:** Designed and implemented with Snell's law specular reflection, mirror incidence/reflection boundaries, receiver FoV checks, sub-tile quadrature, and strict optical power conservation bounds.
4. **Matched Multi-Seed Simulations Executed:** Completed **36 separate 2,000-slot training experiments** across seeds 42, 43, 44:
   - Nominal scenario under signed and L1 energy models (18 runs).
   - Near-Bob adversarial scenario (9 runs).
   - Colocated boundary scenario (9 runs).
5. **Key Empirical Findings & Statistical Rigor:**
   - In nominal settings ($L_1$ energy), the sample mean secrecy rate in the final training window is **$1.5230\text{ bps/Hz}$** for Joint RIS vs. **$1.3504\text{ bps/Hz}$** for Baseline without RIS (a sample mean difference of $+0.1726\text{ bps/Hz}$).
   - However, the two-sided 95% Student-$t$ confidence interval across $N=3$ seeds is $[-0.7403, +1.0854]\text{ bps/Hz}$, which includes zero; statistical superiority is not yet established and requires expanded evaluations ($N \ge 10$).
   - In adversarial near-Bob and colocated tests, secrecy rate evaluates strictly to **$0.0000\text{ bps/Hz}$**, confirming physical channel boundaries when spatial separation between legitimate and eavesdropper channels collapses.

---

## বাংলা (Bengali Summary)

### ১. প্রজেক্টের মূল লক্ষ্য
২০২৪ সালের সেপ্টেম্বর মাসে IEEE Transactions on Wireless Communications-এ প্রকাশিত সিকিউর ইনডোর VLC পেপারের মূল আর্কিটেকচার বজায় রেখে তার সাথে দেওয়ালে মাউন্ট করা একটি অপটিক্যাল **Reconfigurable Intelligent Surface (RIS)** যুক্ত করা। এরপর **Deep Reinforcement Learning (DRL)**-এর মাধ্যমে Friendly Jammer (FJ) এবং Optical RIS-কে যৌথভাবে নিয়ন্ত্রণ করা।

### ২. কী কী কাজ সম্পন্ন ও প্রমাণিত হয়েছে
1. **সমীকরণ বাস্তবায়ন ও অডিট:** পেপারের Eq. (1) থেকে Eq. (23) এবং Table I-এর প্যারামিটার বাস্তবায়ন করা হয়েছে। এনার্জি মডেলের ক্ষেত্রে আক্ষরিক সাইনড এনার্জি ও অশূন্য $L_1$ মডেল আলাদাভাবে রেকর্ড করা হয়েছে।
2. **টেস্ট সুইট:** পুরো প্রজেক্টের **৮৭টি টেস্টের ৮৭টিই সফলভাবে পাস করেছে (`OK`)**।
3. **বাস্তব অপটিক্যাল RIS মডেল:** স্নেলের সূত্র, পাওয়ার কনজারভেশন এবং রিসিভার FoV সীমা মেনে ফিজিক্স মডেল তৈরি ও ভেরিফাই করা হয়েছে।
4. **৩৬টি সিমুলেশন রান সম্পন্ন:** ৩টি স্বতন্ত্র seed (`42, 43, 44`) এবং প্রতিটি ২,০০০ স্লটের মোট ৩৬টি সিমুলেশন সফলভাবে সম্পন্ন করে ডেটা সেভ করা হয়েছে (`output_figures/ris/`)।
5. **বাস্তব ফলাফল ও পরিসংখ্যানিক সত্যতা:**
   - সাধারণ অবস্থায় (Nominal), ফাইনাল ট্রেনিং উইন্ডোতে Joint RIS-এর গড় Secrecy Rate পাওয়া গেছে **$1.5230\text{ bps/Hz}$**, যেখানে RIS ছাড়া বেসলাইনে ছিল **$1.3504\text{ bps/Hz}$** (নমুনা গড় পার্থক্য $+0.1726\text{ bps/Hz}$)।
   - তবে ৩টি সিডের ওপর ভিত্তি করে ৯৫% কনফিডেন্স ইন্টারভ্যাল $[-0.7403, +1.0854]\text{ bps/Hz}$, যার মধ্যে শূন্য রয়েছে—তাই চূড়ান্ত বৈজ্ঞানিক শ্রেষ্ঠত্ব নিশ্চিত করতে আরও বেশি সিড ($N \ge 10$) ও ফ্রোজেন-পলিসি ইভালুয়েশন প্রয়োজন।
   - Bob এবং Eve অতি সন্নিকটে থাকলে (Near-Bob) অথবা একই অবস্থানে থাকলে (Colocated) Secrecy Rate শূন্য (**$0.0000\text{ bps/Hz}$**) হয়, যা তারবিহীন অপটিক্যাল চ্যানেলের বাস্তব সীমাবদ্ধতাকে নির্ভুলভাবে তুলে ধরে।

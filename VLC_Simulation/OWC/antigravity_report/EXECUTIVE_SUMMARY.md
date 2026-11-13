# Executive Summary / নির্বাহী সারসংক্ষেপ

## English

### Project Scope & Mandate
This research project implements the state-of-the-art indoor Visible Light Communication (VLC) physical-layer security framework from the 2024 IEEE Transactions on Wireless Communications paper:  
*“Smart Jamming for Secrecy: Deep Reinforcement Learning Enabled Secure Visible Light Communication”* (Liu et al.).

The central research objective is to retain the original system model as the baseline and extend it with an **Optical Reconfigurable Intelligent Surface (RIS)** (an array of tiltable micro-mirrors on the room wall) jointly controlled with the four Friendly Jammers via **Deep Reinforcement Learning (DRL)**:
$$\text{Architecture: } \mathbf{RIS + FJ + VLC + DRL}$$

### What Was Accomplished & Verified
1. **Verbatim Equation Fidelity:** Every single equation (Eq. 1 to 23) and Table I parameter from the 2024 paper is implemented cleanly without artificial scaling factors (`snr_scale = 500`).
2. **Comprehensive Test Suite:** All **87 unit tests** across the entire codebase passed (`tests/` -> `Ran 87 tests in 28.438s OK`).
3. **Physical Optical RIS:** Designed and implemented with Snell's law specular reflection, mirror incidence/reflection boundaries, receiver FoV checks, sub-tile quadrature, and strict optical power conservation bounds.
4. **Matched Multi-Seed Simulations Executed:** Completed **36 separate 2,000-slot training experiments** across seeds 42, 43, 44:
   - Nominal scenario under signed and L1 energy models (18 runs).
   - Near-Bob adversarial scenario (9 runs).
   - Colocated boundary scenario (9 runs).
5. **Key Numerical Finding:**
   - In nominal settings, adding an Optical RIS under joint DRL control improves the converged secrecy rate from **$1.3504\text{ bps/Hz}$ to $1.5230\text{ bps/Hz}$** ($+0.1726\text{ bps/Hz}$ gain), increases policy utility from **$0.6114$ to $0.6543$**, and reduces Bob's BER from **$1.30 \times 10^{-4}$ down to $4.84 \times 10^{-12}$**.
   - In the colocated boundary test, secrecy rate is identically **$0.0000\text{ bps/Hz}$**, confirming physical validity.

---

## বাংলা (Bengali Summary)

### ১. প্রজেক্টের মূল লক্ষ্য
২০২৪ সালের সেপ্টেম্বর মাসে IEEE Transactions on Wireless Communications-এ প্রকাশিত সিকিউর ইনডোর VLC পেপারের মূল আর্কিটেকচার বজায় রেখে তার সাথে দেওয়ালে মাউন্ট করা একটি অপটিক্যাল **Reconfigurable Intelligent Surface (RIS)** যুক্ত করা। এরপর **Deep Reinforcement Learning (DRL)**-এর মাধ্যমে Friendly Jammer (FJ) এবং Optical RIS-কে একসাথে যৌথভাবে নিয়ন্ত্রণ করা।

### ২. কী কী কাজ সম্পন্ন ও প্রমাণিত হয়েছে
1. **১০০% নিখুঁত সমীকরণ:** পেপারের Eq. (1) থেকে Eq. (23) এবং Table I-এর প্রতিটি ভ্যালু কোডে সরাসরি বাস্তবায়ন করা হয়েছে। কোনো প্রকার কৃত্রিম গুণক (`snr_scale = 500`) ব্যবহার করা হয়নি।
2. **পুরো টেস্ট সুইট সফল:** পুরো প্রজেক্টের **৮৭টি টেস্টের ৮৭টিই সফলভাবে পাস করেছে (`OK`)**।
3. **বাস্তব অপটিক্যাল RIS মডেল:** রিফ্লেকশন ফিজিক্স, স্নেলের সূত্র, পাওয়ার কনজারভেশন এবং রিসিভার FoV সীমা যাচাই করে RIS তৈরি করা হয়েছে।
4. **বাস্তব ৩৬টি সিমুলেশন রান সম্পন্ন:** ৩টি স্বতন্ত্র seed (`42, 43, 44`) এবং প্রতিটি ২,০০০ স্লটের মোট ৩৬টি সিমুলেশন সফলভাবে সম্পন্ন করে ডেটা সেভ করা হয়েছে (`output_figures/ris/`)।
5. **বাস্তব ফলাফল:**
   - সাধারণ ক্ষেত্রে (Nominal), RIS ছাড়া বেসলাইনে Secrecy Rate ছিল **$1.3504\text{ bps/Hz}$**, যা Joint RIS যুক্ত করার পর বৃদ্ধি পেয়ে **$1.5230\text{ bps/Hz}$** হয়েছে।
   - Bob-এর Bit Error Rate (BER) $1.30 \times 10^{-4}$ থেকে কমে গিয়ে **$4.84 \times 10^{-12}$**-এ নেমে এসেছে (অর্থাৎ বৈধ ব্যবহারকারীর ডেটা লস প্রায় শূন্য)।
   - Bob এবং Eve একই অবস্থানে থাকলে (Colocated) Secrecy Rate একদম **$0.0000\text{ bps/Hz}$** পাওয়া গেছে, যা ওয়্যারট্যাপ চ্যানেলের বাস্তব পদার্থবিজ্ঞানকে পুরোপুরি সমর্থন করে।


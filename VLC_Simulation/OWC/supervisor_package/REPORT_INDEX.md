# Master Report Index & Scientific Provenance Catalog

**Project:** Physical Layer Security in Visible Light Communications (VLC) via Optical RIS and Friendly Jamming (FJ) using Deep Reinforcement Learning (DRL)  
**Deliverable:** Master catalog distinguishing active authoritative reports from historical/superseded documents  

---

## 1. Active & Authoritative Reports (Supervisor Takeaway Package)

> **Offline Portability Note:** The `supervisor_package/` directory is designed to be fully readable offline as a standalone folder. All reports in this section, the publication plots in `figures/` (PNG and vector PDF), the dataset provenance (`PROVENANCE.json`), and the compact data (`compact_results.json`) are self-contained. References to parent project files in Sections 2 and 3 require the complete repository.

These documents contain the verified, phase-separated, code-reconciled findings and constitute the primary deliverable for supervisor evaluation:

| Document | Relative Path | Purpose & Key Contents |
| :--- | :--- | :--- |
| **Start Here Guide** | [`START_HERE.md`](START_HERE.md) | Launcher commands, Windows batch script, 5-minute meeting flow, clean shutdown instructions. |
| **Bengali Demo Script** | [`DEMO_SCRIPT_BN.md`](DEMO_SCRIPT_BN.md) | 5–10 minute step-by-step walkthrough in Bengali with English technical terms, expected metrics, and FAQ. |
| **Implementation & Verification** | [`IMPLEMENTATION_AND_VERIFICATION.md`](IMPLEMENTATION_AND_VERIFICATION.md) | Complete system architecture, FeatureCNN ($m_0=11$, flatten $2560$), DND, $|\mathcal{A}|=3125$ action space, 94 unit tests. |
| **Authoritative Results** | [`RESULTS.md`](RESULTS.md) | Programmatically generated phase-separated tables (Phases 1, 2, 3), paired 95% Student-$t$ CIs, per-seed breakdown, boundary conditions. |
| **Master Index** | [`REPORT_INDEX.md`](REPORT_INDEX.md) | This document: catalog of active vs. historical project reports. |
| **Completion Report** | [`COMPLETION_REPORT.md`](COMPLETION_REPORT.md) | Final execution summary, test outcomes, checklist against supervisor delivery task, and handoff. |
| **Dataset Provenance** | [`PROVENANCE.json`](PROVENANCE.json) | SHA-256 hashes of datasets and critical source files, sample counts, protocol flags. |
| **Compact Summary Data** | [`compact_results.json`](compact_results.json) | Standalone JSON export of 10-seed aggregates and paired comparisons (38 KB). |
| **Publication Figures** | [`figures/`](figures/) | High-resolution publication plots (DPI 200) for training curves, frozen eval, paired differences, channel gains, and near-Bob boundary. |

---

## 2. Active Technical Artifacts in Project Root & antigravity_report/

| Document | Relative Path | Status & Relevance |
| :--- | :--- | :--- |
| **Supervisor Demo HTML** | [`../supervisor_demo.html`](../supervisor_demo.html) | **Active & Live:** Served at `/demo`. Features SVG room layout, dynamic optical ray paths, live Python metrics, and embedded figures. |
| **Demo Launcher Script** | [`../launch_supervisor_demo.py`](../launch_supervisor_demo.py) | **Active:** Starts loopback service on ephemeral port and opens `/demo`. |
| **Windows Batch Launcher**| [`../run_supervisor_demo.bat`](../run_supervisor_demo.bat) | **Active:** Double-clickable launcher for Windows. |
| **Authoritative Tables** | [`../antigravity_report/AUTHORITATIVE_TABLES.md`](../antigravity_report/AUTHORITATIVE_TABLES.md) | **Active & Authoritative:** Machine-generated phase-separated reference tables. |
| **Master Agent Handoff** | [`../Agent.MD`](../Agent.MD) | **Active & Authoritative:** Central cross-agent research log and master task specification. |
| **Status Dashboard** | [`../ANTIGRAVITY_STATUS.md`](../ANTIGRAVITY_STATUS.md) | **Active & Authoritative:** Live progress tracking and test status. |

---

## 3. Historical & Superseded Documents (For Context Only)

The following earlier documents represent intermediate development milestones. Where statements conflict with the active reports above, the active reports take strict precedence:

| Document | Path | Historical Role & Superseded Aspects |
| :--- | :--- | :--- |
| `antigravity_report/RESEARCH_RESULTS.md` | `../antigravity_report/RESEARCH_RESULTS.md` | **Historical Milestone:** Initial report of the 10-seed RIS run. Contains early narrative before formal phase separation of training outages vs. frozen evaluation was formalized. |
| `antigravity_report/TODAY_COMPLETION_REPORT.md`| `../antigravity_report/TODAY_COMPLETION_REPORT.md`| **Historical Milestone:** End-of-day report for earlier agent session. Replaced by `COMPLETION_REPORT.md`. |
| `antigravity_report/COMPLETION_REVIEW.md` | `../antigravity_report/COMPLETION_REVIEW.md` | **Review Task Brief:** Auditor review that identified discrepancies in early manuscript drafts. All findings resolved in active reports. |
| `antigravity_report/RECONCILIATION_RECHECK.md`| `../antigravity_report/RECONCILIATION_RECHECK.md`| **Reconciliation Brief:** Outlined necessary corrections for FeatureCNN dimensions and action spaces. Reconciled in code and documentation. |
| `antigravity_report/SUPERVISOR_SIMULATION_DELIVERY_TASK.md` | `../antigravity_report/SUPERVISOR_SIMULATION_DELIVERY_TASK.md` | **Active Task Brief:** The user-provided instruction specification that defined the requirements executed in this package. |
| `PAPER_REPRODUCTION.md` | `../PAPER_REPRODUCTION.md` | **Diagnostic Reference:** Detailed investigation into why the 2024 paper's published numerical curves ($R_s \approx 5.68$) cannot be reproduced using its declared physical constants. |


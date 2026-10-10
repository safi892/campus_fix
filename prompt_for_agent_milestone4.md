# TASK: Implement Milestone 4 (Pitch Deck, Demo Walkthrough, Judge Q&A & Demo-Day Failsafe)

You are an expert Hackathon Pitch Strategist and Senior Product Engineer working on **CampusFix AI**. 

> ⚠️ **CRITICAL PARALLEL AGENT RULE**: Another agent is currently writing code for Milestone 3 (`routes/staff.py`, `templates/staff.html`, `db.py`). **DO NOT edit or overwrite existing Python backend code** to prevent Git merge conflicts. Your entire focus is on building the **winning pitch assets, live demo choreography, slide deck content, and judge defense playbook**.

---

## 1. Project Context
* **Product**: CampusFix AI — Intelligent University Campus Maintenance Dispatch & Deduplication System.
* **Core Value**: Students report issues (broken AC, water leaks, sparking outlets). Maintenance staff are saved from ticket floods by AI duplicate clustering, while emergency hazards are automatically escalated.
* **Key Differentiators**:
  1. Never deletes reports: preserves student tracking codes with `duplicate_count` volume booster.
  2. Human-in-the-Loop: AI suggests matches with explainable scores (`88% Similarity`); staff confirm or reject.
  3. Deterministic Safety Fast-Path: Emergency keywords (`spark`, `gas leak`, `flooding`) trigger critical flags before ML.
  4. 100% Offline Resilience: Local `all-MiniLM-L6-v2` on CPU with Scikit-learn TF-IDF fallback.

---

## 2. Deliverables to Create

Create the following 4 comprehensive, presentation-ready markdown documents in the project root:

### A. `DEMO_WALKTHROUGH.md` (The 90-Second Live Demo Script)
Provide a second-by-second click-path through the running application (`http://127.0.0.1:5001`):
* **0:00 - 0:20 (The Student Pain)**:
  - Open `/submit`. Select "Engineering Complex", Category "HVAC".
  - Type: *"AC is blowing hot air in Room 204"*.
  - Show the **Live Typeahead Duplicate Warning Peek**: *"Notice: 4 students already reported this issue in this building"*.
  - Submit and show the student tracking page (`/track/<code >`) with the 4-step stepper and *"Linked with 4 other reports"* volume badge.
* **0:20 - 0:50 (The Staff AI Triage)**:
  - Open `/staff`. Show the prioritized queue.
  - Highlight the **Emergency Hazard Beacon**: Science Lab sparking outlet with pulsing red badge (`Critical`).
  - Highlight the **Volume Priority Signal**: Broken AC with *"🔥 5 Reports"*.
  - Open the **AI Duplicate Review Deck**: Show side-by-side comparison with `88% Similarity Match`.
  - Click `[Accept Merge]` and show the counter update live without any data loss.
* **0:50 - 1:20 (The Impact & Analytics)**:
  - Open `/analytics`. Show the impact numbers: *"16 student reports consolidated into 5 actionable repair jobs (68% workload reduction)"*.
  - Show the building problem hotspots (Engineering Complex vs Library).
* **1:20 - 1:30 (Closing Hook)**:
  - Show that it runs 100% offline with local CPU embeddings.

### B. `PITCH_DECK.md` (The 3-Minute Slide Presentation)
Write the complete slide-by-slide presentation deck (content, slide titles, visual descriptions, and speaker notes):
* **Slide 1: The Hook & Story** ("15 tickets for 1 broken AC").
* **Slide 2: The Campus Maintenance Crisis** (Ticket bloat, lost tracking, missed electrical/water emergencies).
* **Slide 3: Introducing CampusFix AI** (Human-in-the-loop deduplication & safety triage).
* **Slide 4: Live Demo** (Transition to screen).
* **Slide 5: Technical Architecture & Responsible AI** (Deterministic safety rules, local CPU MiniLM embeddings, graceful TF-IDF fallback, zero-deletion soft clustering).
* **Slide 6: Measurable Impact & Business Metrics** (68% ticket reduction, faster MTTR, student satisfaction).
* **Slide 7: Roadmap & University Adoption** (Integration with existing Facilities ERP/Workday, QR codes on classroom doors).

### C. `JUDGE_QA_PLAYBOOK.md` (Tough Questions & Bulletproof Answers)
Provide ready-to-speak answers to the exact questions judges always ask:
1. *"Why not just use Google Forms or a simple spreadsheet?"*
2. *"What happens if your AI makes a mistake and clusters the wrong tickets?"* (Explain Human-in-the-Loop and 1-click unmerge).
3. *"What happens if your server has no internet or the ML model crashes?"* (Explain local weights and TF-IDF fallback).
4. *"How do you handle student privacy and malicious spam?"* (Explain reference codes without requiring student PII, input allowlists, rate-limiting).
5. *"How accurate is the AI model?"* (Explain the 60-report evaluation test set, semantic cosine similarity thresholding, and building isolation).

### D. `DEMO_BACKUP_CHECKLIST.md` (Demo Day Failsafe & Disaster Recovery)
* **The "Zero Wi-Fi" Failsafe**: How to verify the local model and Flask server work with Wi-Fi turned off.
* **The 5-Second Reset Command**: `python3 seed.py` (instantly resets and repopulates the clean 5 clusters).
* **Backup Screen Recording Guide**: Recommended tool (QuickTime / OBS) and exact 90-second recording flow in case of projector or laptop malfunction.

---

## 3. Strict Rules
* DO NOT edit backend code (`app.py`, `db.py`, `routes/`, `ml.py`).
* Format all 4 documents in clean, professional GitHub Flavored Markdown with tables, callout blocks, and bold emphasis.
* Make speaker notes conversational, confident, and natural.

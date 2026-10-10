# Walkthrough: Senior Developer Review & AI Guardrails

The project review has been completed and codified into persistent guardrails in the `.ai/` directory.

---

## 1. What Was Created

1. **AI Agent Rules & Anti-Pitfall Guardrails**: [`.ai/rules.md`](file:///Volumes/Data/hackthon/.ai/rules.md)
   - Documents the 8 fatal traps that cause 90% of hackathon teams and AI agents to fail:
     - The Authentication Trap (wasting hours on login/JWT).
     - The Microservices/Multi-Server Trap (CORS bugs, dual servers).
     - The Fragile ML Trap (HTTP 500 when model fails).
     - The Deletion Trap (destroying student tickets when deduplicating).
     - The Autonomous AI Trap (unsupervised black-box decisions).
     - Neglecting Emergency Safety (relying on embeddings for physical hazards).
     - The Empty DB Trap (unseeded demo).
     - Scope Creep (unnecessary features).
   - Establishes binding rules for any developer or AI agent modifying this project.

2. **System Architecture & Database Specification**: [`.ai/design.md`](file:///Volumes/Data/hackthon/.ai/design.md)
   - Outlines the complete dataflow: Student submission $\rightarrow$ Deterministic emergency check $\rightarrow$ AI deduplication $\rightarrow$ Staff review $\rightarrow$ Hotspot analytics.
   - Defines the SQLite `complaints` table schema with soft parent-child clustering (`parent_id`) and duplicate counters (`duplicate_count`).
   - Details the ML fallback mechanism (MiniLM $\rightarrow$ TF-IDF).

---

## 2. Git Checkpoint

All changes have been committed cleanly:
* Commit: `docs: add senior dev review, agent guardrails, and architecture to .ai/`

---

## 3. Next Milestone Readiness

The project is now protected against architectural regressions and ready for **Milestone 2**:
* Database creation & connection helper (`db.py`).
* Student complaint submission form (`/submit`) with validation.
* Student issue tracking view (`/track/<reference_code>`).
* Seed dataset script (`seed.py`) with 30+ realistic campus reports.

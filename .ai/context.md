# CampusFix AI — Quick Agent Context Index

> **AI INSTRUCTION**: Read this file first. Do NOT re-read entire codebases or write exploratory prompts. Pick the exact modular file below for your specific task to save tokens.

---

## 1. Quick Navigation Matrix

| Task / Domain | Target File | What You Will Find |
|---|---|---|
| **Coding & Architecture Guardrails** | [`.ai/rules.md`](file:///Volumes/Data/hackthon/.ai/rules.md) | The 8 fatal hackathon traps, hard constraints (no auth, no deletion, ML fallbacks). |
| **UI, Styling, Colors & Tokens** | [`.ai/design.md`](file:///Volumes/Data/hackthon/.ai/design.md) | Pure design tokens, hex codes, typography scale, CSS classes, micro-interactions. |
| **Database & Schema Queries** | [`.ai/database.md`](file:///Volumes/Data/hackthon/.ai/database.md) | Exact SQLite DDL, parameterized queries, soft-clustering schema (`parent_id`). |
| **AI / ML & Duplicate Logic** | [`.ai/ml_pipeline.md`](file:///Volumes/Data/hackthon/.ai/ml_pipeline.md) | MiniLM CPU inference, TF-IDF fallback code, safety regex keywords, similarity cutoff. |
| **Routes, URLs & API Contracts** | [`.ai/routes.md`](file:///Volumes/Data/hackthon/.ai/routes.md) | All Flask endpoint signatures, parameters, JSON responses, form fields. |
| **Security & Safe Coding** | [`.ai/security.md`](file:///Volumes/Data/hackthon/.ai/security.md) | Parameterized SQL, zero-XSS Jinja auto-escaping, input validation, DoS safety. |
| **Demo Data & Testing Scenarios** | [`.ai/seed_data.md`](file:///Volumes/Data/hackthon/.ai/seed_data.md) | Ready-to-load realistic campus complaints, pre-arranged duplicate clusters. |
| **Add a Navbar Item** | [`templates/base.html`](file:///Volumes/Data/hackthon/templates/base.html) | Append `(endpoint, label, icon)` to the `nav_items` list at the top of `<body>`. |

---

## 2. Fast Environment Facts
* **Stack**: Python 3.11, Flask 3.0, SQLite, Bootstrap 5, Jinja2.
* **Startup Command**: `python3 app.py` (Port 5001).
* **Virtual Environment**: `source /Volumes/Data/hackthon/.venv/bin/activate`.
* **Current Status**: Milestone 3 Complete (staff dashboard, AI duplicate review, analytics).

---

## 3. Code Layout
| Path | Responsibility |
|---|---|
| `routes/` | HTTP only: parse input, call a service or `db`, render HTML / return JSON (`submit.py`, `track.py`, `staff.py`). |
| `services/triage.py` | AI duplicate suggestions + merge / keep-separate validation (`TriageError` → HTTP status). |
| `db.py` | All SQL (parameterized `?`), schema init + additive migrations. |
| `ml.py` | Safety regex scan + MiniLM similarity with TF-IDF / lexical fallbacks. |
| `formatting.py` | Jinja filter `friendly_date` (registered in `app.py`). |
| `templates/components/ui.html` | Reusable macros: urgency / safety / volume / status / similarity badges, `stat_card`, `filter_select`. |
| `static/js/staff.js` | Staff board interactions (status dropdown, Accept Merge, Keep Separate). `textContent` only. |

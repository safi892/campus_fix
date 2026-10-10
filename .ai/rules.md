# CampusFix AI — Engineering & AI Agent Rules

> **CRITICAL**: Every AI agent and developer contributing to this project MUST strictly comply with these rules. Violating these rules will result in broken demos, wasted hackathon hours, or disqualification.

---

## 1. The 8 Fatal Traps to Avoid

### Trap 1: The Authentication Trap
* **Mistake**: Spending 6–8 hours building user login, JWT tokens, OAuth, password reset, and registration tables.
* **Rule**: **DO NOT BUILD AUTHENTICATION.** Use lightweight role switching (e.g., student submission at `/submit` and maintenance staff view at `/staff`). A university hackathon judges the core AI deduplication workflow, not generic login forms.

### Trap 2: The Multi-Server / Microservices Trap
* **Mistake**: Attempting to run Next.js/React + Flask + Fastify + separate vector database containers.
* **Rule**: **STICK STRICTLY TO THE FLASK MONOLITH.** All HTML is rendered with Jinja2 and styled with Bootstrap 5. Zero CORS issues, zero API contract desync, and single-command startup (`python3 app.py`).

### Trap 3: The Fragile ML Trap (HTTP 500 Disasters)
* **Mistake**: Letting the entire website crash if PyTorch or `sentence-transformers` runs out of RAM, fails to download, or takes too long on CPU.
* **Rule**: **MANDATORY GRACEFUL DEGRADATION.** Every AI/embedding function must be wrapped in a `try...except` block with a lightweight keyword or TF-IDF fallback. The website must remain 100% operational even if the ML model completely fails.

### Trap 4: The Deletion Trap (Data Loss)
* **Mistake**: Running `DELETE FROM complaints WHERE id = ?` when duplicate tickets are found.
* **Rule**: **NEVER HARD-DELETE STUDENT COMPLAINTS.** When grouping duplicates, assign `parent_id = <original_complaint_id>` and increment a counter (`duplicate_count`). Every student must retain their tracking code and be able to see their issue's resolution.

### Trap 5: The Autonomous AI Trap (Black-Box Decisions)
* **Mistake**: Letting the AI automatically merge or close complaints without human staff approval.
* **Rule**: **HUMAN-IN-THE-LOOP IS MANDATORY.** AI only generates a similarity proposal with an explainability metric (e.g., *"88% match with Issue #14: AC Leak"*). Maintenance staff have dedicated `[Accept Merge]` and `[Keep Separate]` buttons.

### Trap 6: Relying on Embeddings for Emergency Safety
* **Mistake**: Running cosine similarity on sentence vectors to decide if an exposed electrical wire is dangerous.
* **Rule**: **DETERMINISTIC KEYWORD ESCALATION.** Run an instantaneous regex scanner for emergency safety terms (`spark`, `exposed wire`, `gas smell`, `flooding`, `smoke`, `fire hazard`) at submission time. Never rely on non-deterministic AI for physical safety.

### Trap 7: The Empty Database Demo Trap
* **Mistake**: Walking up to judges with an empty database or 1 test ticket saying *"test"*.
* **Rule**: **SEED DATA IS MANDATORY.** Provide a `seed.py` script containing 30–50 realistic university reports with pre-arranged duplicate clusters across real campus buildings.

### Trap 8: Scope Creep
* **Mistake**: Building email servers, SMS notifications, mobile apps, or cloud S3 uploaders.
* **Rule**: Focus solely on the 3 winning flows:
  1. Student submit & track
  2. Staff duplicate clustering & safety triage
  3. Campus hotspot analytics

---

## 2. Technical Commandments for AI Agents

1. **Python 3.11 Runtime**: Always use `.venv` with Python 3.11 (`python3 app.py`). Do not use global Python 3.14.
2. **Safe Database Practices**: Always use parameterized SQLite queries (`cursor.execute("SELECT ... WHERE id = ?", (id,))`) to prevent SQL injection.
3. **Verification First**: Never state that a feature or route works without executing it and testing response status codes.
4. **Clean Code & Surgical Edits**: Follow Karpathy guidelines—write simple, readable code without speculative abstractions or bloated boilerplate.
5. **Clear Commit Checkpoints**: Commit changes to Git after each milestone.

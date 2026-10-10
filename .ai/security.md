# CampusFix AI — Security & Secure Coding Standards

> **AI INSTRUCTION**: Every AI agent and developer writing backend, API, or frontend code MUST comply with these security rules. Do NOT introduce vulnerabilities under hackathon rush.

---

## 1. Top 7 Security Commandments

### 1. Zero SQL Injection (Strict Parameterization)
* **RULE**: NEVER format strings into SQL queries. NEVER use `f"SELECT ... {var}"`, `%s`, or `.format()`.
* **VULNERABLE**:
  ```python
  # DO NOT DO THIS
  cursor.execute(f"SELECT * FROM complaints WHERE reference_code = '{ref}'")
  ```
* **SECURE**:
  ```python
  # ALWAYS DO THIS
  cursor.execute("SELECT * FROM complaints WHERE reference_code = ?", (ref,))
  ```

---

### 2. Zero Stored & Reflected XSS (Jinja2 Auto-Escaping)
* **RULE**: User input (`title`, `description`, `room`) must NEVER be marked as `| safe` in Jinja2 templates.
* **VULNERABLE**:
  ```html
  <!-- DO NOT DO THIS: Allows malicious script injection -->
  <h3>{{ complaint.title | safe }}</h3>
  <p>{{ complaint.description | safe }}</p>
  ```
* **SECURE**:
  ```html
  <!-- ALWAYS DO THIS: Auto-escaped by default -->
  <h3>{{ complaint.title }}</h3>
  <p>{{ complaint.description }}</p>
  ```
* In API routes, never return unescaped user strings in HTML responses; always return JSON via `jsonify()`.

---

### 3. Strict Input Validation & Allowlisting
* **RULE**: Validate all incoming form fields and reject illegal or oversized values before processing.
* **Implementation Standard**:
  ```python
  ALLOWED_CATEGORIES = {"HVAC", "Electrical", "Plumbing", "Furniture", "Cleanliness", "Safety"}
  ALLOWED_BUILDINGS = {
      "Engineering Complex",
      "Central Library",
      "Science Laboratory B",
      "Student Center & Cafeteria",
      "Residential Hall West"
  }

  def validate_complaint_input(data: dict) -> tuple[bool, str]:
      title = (data.get("title") or "").strip()
      desc = (data.get("description") or "").strip()
      category = (data.get("category") or "").strip()
      building = (data.get("building") or "").strip()

      if not (5 <= len(title) <= 150):
          return False, "Title must be between 5 and 150 characters."
      if not (10 <= len(desc) <= 2000):
          return False, "Description must be between 10 and 2000 characters."
      if category not in ALLOWED_CATEGORIES:
          return False, "Invalid category selected."
      if building not in ALLOWED_BUILDINGS:
          return False, "Invalid campus building selected."

      return True, ""
  ```

---

### 4. DoS & ReDoS Protection in AI Pipeline
* **RULE**: Truncate user text before feeding into embedding vectorizers or regex scanners to prevent memory exhaustion and catastrophic backtracking.
  ```python
  # Cap input text length before embedding or regex scanning
  MAX_AI_INPUT_LENGTH = 1000
  sanitized_text = raw_text[:MAX_AI_INPUT_LENGTH]
  ```

---

### 5. Safe File Uploads (When Handling Images)
If photo uploads are added in later milestones:
* **RULE**:
  1. Never trust the client-supplied filename; always use `werkzeug.utils.secure_filename`.
  2. Validate file extension against an explicit allowlist (`.jpg`, `.jpeg`, `.png`, `.webp`).
  3. Validate magic bytes / MIME types, not just the file extension.
  4. Enforce strict size limit in Flask config (`app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024`).
  5. Never place uploads into executable directories; serve them through `send_from_directory` with `as_attachment=False`.

---

### 6. Information Disclosure & Error Shielding
* **RULE**: Never reveal database errors, internal file paths, or raw stack traces in user-facing responses.
* **VULNERABLE**:
  ```python
  # DO NOT DO THIS
  except Exception as e:
      return jsonify({"error": str(e)}), 500
  ```
* **SECURE**:
  ```python
  # ALWAYS DO THIS
  except Exception as e:
      app.logger.error("Internal processing error: %s", e)
      return jsonify({"error": "Unable to process request. Please try again."}), 500
  ```

---

### 7. Secret & Environment Hygiene
* Keep `.env`, `.venv`, and `*.db` files inside [`.gitignore`](file:///Volumes/Data/hackthon/.gitignore).
* Use fallback development secret keys only when `SECRET_KEY` is not provided in environment variables:
  ```python
  import os
  app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "campusfix-dev-fallback-key")
  ```

# CampusFix AI — Routes & API Contracts

> **AI INSTRUCTION**: Implement all routes directly in Flask. Follow REST-style conventions for mutations. Render Jinja2 templates for views, return JSON for async API helpers.

---

## 1. Route Summary Table

| HTTP Method | Route URL | Purpose | Return Type |
|---|---|---|---|
| `GET` | `/` | Public landing page & live stats | HTML (`index.html`) |
| `GET` | `/health` | Application health check | JSON `{ status: "healthy", ... }` |
| `GET` | `/submit` | Student complaint form | HTML (`submit.html`) |
| `POST` | `/submit` | Process report & generate tracking code | Redirect to `/track/<reference_code>` |
| `GET` | `/track/<reference_code>` | Student real-time tracking receipt | HTML (`track.html`) |
| `GET` | `/staff` | Staff triage board & AI cluster review | HTML (`staff.html`) |
| `POST` | `/api/cluster/merge` | Staff confirms duplicate merge | JSON `{ success: true, ... }` |
| `POST` | `/api/cluster/dismiss` | Staff marks report as distinct | JSON `{ success: true, ... }` |
| `POST` | `/api/status/update` | Update complaint status (In Progress/Resolved) | JSON `{ success: true, ... }` |
| `GET` | `/api/check-duplicates` | Live typeahead duplicate peek for `/submit` | JSON `[{ id, title, count }, ...]` |
| `GET` | `/analytics` | Campus problem hotspots & efficiency chart | HTML (`analytics.html`) |

---

## 2. Request & Response Payloads

### `POST /submit` (Form Data)
* **Fields**:
  * `building` (string, required): e.g., `"Engineering Hall"`
  * `room` (string, optional): e.g., `"Room 204"`
  * `category` (string, required): `HVAC | Electrical | Plumbing | Furniture | Cleanliness | Safety`
  * `title` (string, required): Short summary (min 5 chars)
  * `description` (string, required): Full description (min 10 chars)
* **Behavior**:
  * Scans safety keywords deterministically.
  * Generates random reference code: `f"CFX-{year}-{random_4_digits}"`.
  * Inserts record into database.
  * Redirects to `url_for('track_issue', reference_code=ref_code)`.

### `GET /api/check-duplicates?building=...&query=...`
* **Query Params**: `building`, `query`
* **Response**:
  ```json
  {
    "matches": [
      {
        "id": 4,
        "title": "Broken AC Unit in Room 204",
        "duplicate_count": 5,
        "similarity": 0.86
      }
    ]
  }
  ```

### `POST /api/cluster/merge` (JSON)
* **Body**:
  ```json
  {
    "parent_id": 4,
    "child_id": 19
  }
  ```
* **Response**:
  ```json
  {
    "success": true,
    "message": "Report #19 successfully linked to cluster #4.",
    "new_cluster_count": 6
  }
  ```

### `POST /api/status/update` (JSON)
* **Body**:
  ```json
  {
    "id": 4,
    "status": "In Progress"
  }
  ```
* **Valid Status Values**: `"Submitted" | "Under Review" | "In Progress" | "Resolved"`

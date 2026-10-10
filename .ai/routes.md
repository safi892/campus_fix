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
| `POST` | `/api/cluster/merge` | Staff confirms duplicate merge | JSON `{ success, parent_id, child_id, new_count, message }` |
| `POST` | `/api/cluster/dismiss` | Staff marks report as distinct | JSON `{ success }` |
| `POST` | `/api/status/update` | Update complaint status (cascades to linked reports) | JSON `{ success, id, status }` |
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

### Staff JSON API — common rules
* **No authentication by design** (hackathon demo): `/staff`, `/analytics` and the `/api/*` staff endpoints are open.
* Requests **must** send `Content-Type: application/json` with a JSON object body; anything else → `400`. (A cross-site HTML form cannot send this content type.)
* Ids must be positive integers (booleans and strings rejected).
* Errors: `{ "success": false, "error": "..." }` with `400` (bad input), `404` (not found), `409` (conflict, e.g. already linked).

### `POST /api/cluster/merge` (JSON)
* **Body**: `{ "parent_id": 4, "child_id": 19 }`
* **Validation** (`services/triage.py`): not self, both exist, parent is canonical, child not already linked and not a cluster itself, same building.
* **Response**:
  ```json
  {
    "success": true,
    "parent_id": 4,
    "child_id": 19,
    "new_count": 6,
    "message": "Report #19 linked to cluster #4."
  }
  ```

### `POST /api/cluster/dismiss` (JSON)
* **Body**: `{ "complaint_id": 19 }`
* **Behavior**: sets `ai_reviewed = 1` so the report is never suggested again.
* **Response**: `{ "success": true }`

### `POST /api/status/update` (JSON)
* **Body**: `{ "id": 4, "status": "In Progress" }`
* **Valid Status Values**: `"Submitted" | "Under Review" | "In Progress" | "Resolved"`
* **Behavior**: cascades to every report linked to the job.
* **Response**: `{ "success": true, "id": 4, "status": "In Progress" }`

### `GET /staff?building=&category=&status=`
* Filters are allowlisted; unknown values are ignored (no filter). Without `status`, resolved jobs are hidden.

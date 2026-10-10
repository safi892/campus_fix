# CampusFix AI — Demo Day Failsafe & Disaster Recovery Checklist

> **Purpose**: A step-by-step operational survival guide for demo day. Hackathon stage presentations fail due to bad Wi-Fi, port collisions, dirty demo data, or projector glitches. Follow this checklist 30 minutes before stepping on stage.

---

## 1. The 5-Second Database Reset Command

Whenever you need to restore the application to a pristine, predictable demo state:

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Reset and seed database
python3 seed.py
```

### What This Does Instantly:
* Drops the existing `instance/campusfix.db` SQLite database.
* Rebuilds tables and performance indexes.
* Seeds all **16 verified reports across 5 demo clusters**:
  1. **Engineering 204 AC Breakdown** (1 parent + 4 duplicates)
  2. **Library 2nd Floor Water Leak** (1 parent + 3 duplicates)
  3. **Science Lab 110 Sparking Outlet** (1 parent + 1 duplicate, ⚠️ **Critical Safety**)
  4. **Student Center Broken Chairs** (1 parent + 1 duplicate)
  5. **Dorm West 3rd Floor Wi-Fi Outage** (1 parent + 2 duplicates)

---

## 2. The "Zero Wi-Fi" Failsafe Verification

**Rule**: Never rely on hackathon venue Wi-Fi during judging. CampusFix AI is built to run 100% offline.

### Verification Steps (Do this 15 minutes before your slot):
1. **Turn OFF your laptop Wi-Fi**:
   - macOS: Click Wi-Fi icon $\rightarrow$ Toggle **Off**.
2. **Start the local server**:
   ```bash
   python3 app.py
   ```
   *Note: Server runs on `http://127.0.0.1:5001` (Port 5001 avoids macOS AirPlay port 5000 collisions).*
3. **Run the offline verification test**:
   ```bash
   python3 test_ml.py
   ```
   *Expected output:*
   ```text
   INFO:campusfix.ml:Loading local offline model from: .../models/all-MiniLM-L6-v2
   [ACTIVE ENGINE] Primary: sentence-transformers (all-MiniLM-L6-v2) on CPU
   [SUCCESS] Semantic clustering correctly grouped the AC reports!
   ```
4. **Open the browser**:
   - Visit `http://127.0.0.1:5001/`
   - Visit `http://127.0.0.1:5001/health` $\rightarrow$ Must return `{"status": "healthy"}`.

---

## 3. The 90-Second Backup Screen Recording

If the stage projector cable fails, your laptop crashes, or the live server is interrupted, immediately play your **pre-recorded backup video**.

### Recommended Tool:
* **macOS**: Built-in QuickTime Player or Screen Capture (`Cmd + Shift + 5`).
* **Format**: 1080p MP4 or MOV, 60fps.
* **Storage Location**: Save directly to Desktop as `CampusFix_AI_90s_Demo_Backup.mp4` AND copy to a USB thumb drive.

### Exact Recording Flow (Follow [DEMO_WALKTHROUGH.md](file:///Volumes/Data/hackthon/DEMO_WALKTHROUGH.md)):
1. **0:00 - 0:20**: Open `/submit`. Type `AC blowing hot air in Room 204`. Show the yellow duplicate alert banner appear. Click Submit. Show the `/track/<ref>` progress receipt and volume elevation badge.
2. **0:20 - 0:45**: Navigate to `/staff`. Point to the Science Lab red pulsing safety beacon. Scroll to the AI suggestions panel showing `88% Similarity Match`. Click `[Accept Merge]`. Show the cluster counter increase live.
3. **0:45 - 1:15**: Navigate to `/analytics`. Hover over `68% Workload Reduction` and the building failure distribution charts.
4. **1:15 - 1:30**: Return to landing page `/`.

> [!TIP]
> **Audio Advice**: Do NOT record audio on the backup video! Keep the video silent so you can speak live over it if you need to play it on stage.

---

## 4. 15-Minute Pre-Stage Inspection Checklist

Print or review this checklist on your phone:

- [ ] **Python Process Check**: Ensure no zombie Flask processes are occupying port 5001:
  ```bash
  lsof -ti :5001 | xargs kill -9 2>/dev/null || true
  ```
- [ ] **Fresh Data Seeded**: Ran `python3 seed.py`.
- [ ] **Browser Prepared**:
  - Open Google Chrome in a dedicated clean window (no clutter tabs).
  - Open 4 pre-loaded tabs:
    1. Tab 1: `http://127.0.0.1:5001/submit`
    2. Tab 2: `http://127.0.0.1:5001/staff`
    3. Tab 3: `http://127.0.0.1:5001/analytics`
    4. Tab 4: `http://127.0.0.1:5001/`
  - Zoom set to **125%** for projector visibility (`Cmd +`).
- [ ] **Do Not Disturb Enabled**: macOS Focus Mode / Do Not Disturb turned **ON** to suppress Slack/WhatsApp popups.
- [ ] **Backup Video Ready**: Video file queued up in QuickTime and paused at 0:00, minimized in the dock.
- [ ] **Laptop Battery & Charger**: Battery at > 80% or plugged in.
- [ ] **Screen Timeout**: Set Mac display sleep to "Never" during the demo slot.

---

## 5. Emergency Trouble-Shooting Matrix

| Symptom | Probable Cause | Instant 5-Second Fix |
|---|---|---|
| `Address already in use: 5001` | Previous Flask process still running | Run: `lsof -ti :5001 \| xargs kill -9` |
| `TemplateNotFound: ...` | File path typo or missing template | Verify all files are in `templates/` and restart `python3 app.py`. |
| Database has weird/messy numbers | Manual testing created extra tickets | Run: `python3 seed.py` |
| MiniLM model loads slowly | First-time CPU compilation | Run `python3 test_ml.py` once in advance to warm up cache. |
| Projector resolution distorts UI | Auditorium projector is 720p/1080p | Hit `Cmd -` or `Cmd +` in browser to adjust Bootstrap grid fit. |

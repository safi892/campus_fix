# CampusFix AI — 90-Second Live Demo Walkthrough Script

> **Purpose**: A rehearsed, second-by-second choreography for the live hackathon stage. Two presenters recommended: **Presenter A (Speaker)** and **Presenter B (Driver/Clicker)**.
> **Target Run Time**: Exactly 90 seconds (leaving 90 seconds for pitch opening & closing).
> **URL Base**: `http://127.0.0.1:5001`

---

## Pre-Demo Quick Verification (Run 60s Before Stage)

Run this single command in terminal to ensure pristine demo state:
```bash
source .venv/bin/activate
python3 seed.py
```
*Expected: 16 complaints loaded across 5 clusters in 0.2 seconds.*

---

## Second-by-Second Demo Choreography

```
Timeline:
[0:00 ─── 0:20] Student Submission Flow & Typeahead Warning
[0:20 ─── 0:50] Staff Dashboard: Emergency Triage & AI Cluster Merge
[0:50 ─── 1:20] Executive Analytics & Hotspot Reduction
[1:20 ─── 1:30] 100% Offline Resilience & Closing Hook
```

---

### Act 1: The Student Experience (0:00 – 0:20)

| Time | Driver Screen Action | Speaker Voiceover Script | Visual Highlight |
|---|---|---|---|
| **0:00 - 0:05** | Navigate to `http://127.0.0.1:5001/submit` | *"Let's look at what happens when a student walks into a stifling lecture hall."* | Clean, accessible submission form. |
| **0:05 - 0:12** | 1. Select Building: **`Engineering Complex`**<br>2. Select Category: **`HVAC`**<br>3. Type Title: `AC blowing hot air in Room 204`<br>4. Begin typing Description: `Room is completely sweltering...` | *"Watch what happens before they even finish typing. The AI instantly peeks at active complaints in this exact building."* | Yellow alert banner slides in dynamically: **"Notice: 4 students already reported this issue in this building"**. |
| **0:12 - 0:17** | Click **Submit Issue** button. Page redirects to `/track/CFX-2026-XXXX`. | *"Instead of filing blind into a black hole, the student gets an instant tracking receipt with their unique reference code."* | 4-step progress stepper: `Submitted` $\rightarrow$ `Under Review` $\rightarrow$ `In Progress` $\rightarrow$ `Resolved`. |
| **0:17 - 0:20** | Point cursor to the volume badge. | *"Notice the volume booster: 'Linked with 4 other reports. Priority elevated.' The student feels heard, without spamming staff."* | Highlighting badge: `🔥 5 Reports Linked`. |

---

### Act 2: Staff Triage & Human-in-the-Loop AI (0:20 – 0:50)

| Time | Driver Screen Action | Speaker Voiceover Script | Visual Highlight |
|---|---|---|---|
| **0:20 - 0:28** | Click navbar **Staff Dashboard** (`/staff`). | *"Now switch over to the facilities manager view. Notice how our priority queue is organized."* | Sorted queue showing emergency safety issues at top, followed by volume clusters. |
| **0:28 - 0:35** | Hover over the top row: **Science Lab B Outlet**. | *"Right at the top: an outlet sparking in Science Lab 110. Our deterministic safety scanner escalated this to Critical in under 2 milliseconds before any ML model even ran."* | Pulsing red beacon badge: `⚠️ Critical Safety Hazard`. |
| **0:35 - 0:42** | Scroll to the **AI Duplicate Suggestions** panel on the right. Point to the suggestion comparing `AC rattle in 204` with `AC hot air 204`. | *"Here is our core differentiator: Explainable AI with Human-in-the-Loop. The AI proposes: '88% semantic similarity match with Report #1'. But the AI NEVER makes unsupervised merges."* | Side-by-side comparison card with similarity score `88% Match`. |
| **0:42 - 0:50** | Click **`[Accept Merge]`** button on the suggestion. | *"The staff clicks Accept. Instantly, the ticket joins the cluster. The volume counter ticks up. And critically—zero student tickets were deleted."* | Counter updates smoothly; suggestion disappears from queue. |

---

### Act 3: Campus Impact & Hotspot Analytics (0:50 – 1:20)

| Time | Driver Screen Action | Speaker Voiceover Script | Visual Highlight |
|---|---|---|---|
| **0:50 - 0:58** | Click navbar **Analytics** (`/analytics`). | *"At the executive level, CampusFix transforms chaos into operational clarity."* | Clean KPI summary dashboard. |
| **0:58 - 1:10** | Hover over top stat cards: **16 Reports** $\rightarrow$ **5 Actionable Jobs**. Point to **68% Workload Reduction**. | *"Look at this number: 16 separate student submissions consolidated into just 5 actionable work orders. That's a 68% reduction in ticket bloat for campus dispatchers."* | Big metric card: `68% Workload Reduction`. |
| **1:10 - 1:20** | Scroll to **Building Problem Hotspots** bar chart / breakdown. | *"Facilities directors can immediately see that the Engineering Complex generates 40% of all HVAC issues, allowing preventative maintenance before midterms."* | Building distribution bars showing Engineering Complex at top. |

---

### Act 4: The 100% Offline Resilience Hook (1:20 – 1:30)

| Time | Driver Screen Action | Speaker Voiceover Script | Visual Highlight |
|---|---|---|---|
| **1:20 - 1:26** | Pull down macOS Wi-Fi menu showing Wi-Fi disabled (or display terminal running locally). | *"And the engineering kicker: CampusFix AI runs 100% locally on CPU. Zero OpenAI API costs, zero cloud latency, and zero Wi-Fi dependencies."* | URL bar showing `127.0.0.1:5001` running smoothly offline. |
| **1:26 - 1:30** | Switch back to `/` Landing Page. Presenter delivers final pitch punchline. | *"CampusFix AI: Faster repairs for students, zero ticket floods for staff. Thank you."* | Hero section of CampusFix AI on screen. |

---

## Presenter Rehearsal Pro-Tips

> [!TIP]
> **Pacing Rule**: If the driver gets ahead of the speaker, the driver should hover over badges and wait. Never click before the speaker announces what is about to happen.

> [!IMPORTANT]
> **Browser Zoom Level**: Press `Cmd +` twice in Google Chrome or Safari to set zoom to **125%**. Hackathon auditorium projectors wash out 14px body text.

> [!WARNING]
> **Do NOT Open DevTools or Terminal During the 90s**: Keep the browser full-screen. Judges want to see a polished, finished product, not debug output.

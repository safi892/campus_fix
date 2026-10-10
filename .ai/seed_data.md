# CampusFix AI — Seed Data & Demo Scenarios

> **AI INSTRUCTION**: Use these exact datasets for `seed.py` and automated test fixtures. Do NOT use fake gibberish (e.g. "asdf", "test"). Realistic university scenarios make or break demo credibility with judges.

---

## 1. Campus Buildings & Categories Taxonomy

### Standard Campus Buildings
* `Engineering Complex`
* `Central Library`
* `Science Laboratory B`
* `Student Center & Cafeteria`
* `Residential Hall West`

### Maintenance Categories
* `HVAC` (Heating, Ventilation, Air Conditioning)
* `Electrical`
* `Plumbing`
* `Furniture`
* `Cleanliness`
* `Safety`

---

## 2. Pre-Engineered Demo Clusters

### Cluster 1: AC Failure (HVAC) — High Volume (5 Reports)
* **Building**: `Engineering Complex` | **Room**: `Room 204` | **Category**: `HVAC`
* **Canonical Issue #1**: *"Air conditioning unit blowing hot air in Room 204"*
* **Duplicate Submissions**:
  1. *"AC is completely broken in room 204, lecture is unbearable"*
  2. *"Room 204 engineering hall is boiling hot, please turn on cooling"*
  3. *"The central AC in 204 is making rattling noise and blowing warm air"*
  4. *"HVAC unit malfunctioning in Eng Hall 204, sweating through class"*

### Cluster 2: Ceiling Water Leak (Plumbing) — Medium Volume (4 Reports)
* **Building**: `Central Library` | **Room**: `2nd Floor Restroom` | **Category**: `Plumbing`
* **Canonical Issue #2**: *"Water dripping rapidly from ceiling tile near sinks"*
* **Duplicate Submissions**:
  1. *"Puddle on the floor in 2nd floor library bathroom, ceiling leaking"*
  2. *"Major water leak above bathroom sink on second floor library"*
  3. *"Water leak from ceiling tile in library level 2 washroom"*

### Cluster 3: Sparking Wall Outlet (Safety Emergency) — Critical (2 Reports)
* **Building**: `Science Laboratory B` | **Room**: `Lab 110` | **Category**: `Safety`
* **Canonical Issue #3**: *"Wall outlet sparks and makes crackling noise when plugging in equipment"*
* **Duplicate Submission**:
  1. *"Exposed wire and visible sparks from socket in science lab 110"*
* **Expected Flag**: `safety_hazard = 1`, `urgency = 'Critical'` (Triggers red pulse beacon).

### Cluster 4: Broken Study Chairs (Furniture) — Normal (2 Reports)
* **Building**: `Student Center & Cafeteria` | **Room**: `Quiet Study Lounge` | **Category**: `Furniture`
* **Canonical Issue #4**: *"Two wooden chairs have cracked armrests and wobbly legs"*
* **Duplicate Submission**:
  1. *"Damaged chair in study lounge student center, sharp wood edge"*

### Cluster 5: Wi-Fi Access Point Offline (Electrical) — (3 Reports)
* **Building**: `Residential Hall West` | **Room**: `3rd Floor Hallway` | **Category**: `Electrical`
* **Canonical Issue #5**: *"Wi-Fi router on 3rd floor ceiling has no power light and zero signal"*
* **Duplicate Submissions**:
  1. *"No internet on West dorm 3rd floor, access point appears dead"*
  2. *"Dorm 3rd floor wifi router completely powered off"*

---

## 3. Seed Execution Command
Once implemented in Milestone 2:
```bash
python3 seed.py
```
This populates the database with these 5 clusters (16 total reports), establishing an instant, rich demonstration for hackathon judges.

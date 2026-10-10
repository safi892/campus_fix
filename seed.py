#!/usr/bin/env python3
"""
CampusFix AI — Database Seed Script
Populates database with realistic demo data for hackathon demonstration.
"""

import sys
from datetime import datetime, timedelta

from db import reset_database, insert_complaint, link_duplicate, get_all_complaints

def seed_demo_data():
    """
    Seeds database with 5 realistic complaint clusters as specified in .ai/seed_data.md
    """
    print("=" * 70)
    print("CampusFix AI - Database Seed Script")
    print("=" * 70)
    print()
    
    # Reset database (WARNING: Deletes all existing data)
    print("🗑️  Resetting database...")
    reset_database()
    print("✅ Database reset complete\n")
    
    complaints_created = []
    
    # =================================================================
    # CLUSTER 1: AC Failure (HVAC) — High Volume (5 Reports)
    # =================================================================
    print("📊 Creating Cluster 1: AC Failure in Engineering Complex...")
    
    c1_parent = insert_complaint(
        reference_code="CFX-2026-1001",
        title="Air conditioning unit blowing hot air in Room 204",
        description="The AC unit in Engineering Room 204 is completely broken. It's blowing hot air instead of cold air. The room temperature is unbearable during lectures.",
        building="Engineering Complex",
        room="Room 204",
        category="HVAC",
        urgency="High",
        safety_hazard=0
    )
    complaints_created.append(("CFX-2026-1001", "Parent - AC Failure"))
    
    # Duplicates for Cluster 1
    c1_dup1 = insert_complaint(
        reference_code="CFX-2026-1002",
        title="AC is completely broken in room 204, lecture is unbearable",
        description="Please fix the air conditioning in Engineering 204. Students are sweating through class and it's making it very difficult to concentrate.",
        building="Engineering Complex",
        room="Room 204",
        category="HVAC",
        urgency="Normal",
        safety_hazard=0
    )
    
    c1_dup2 = insert_complaint(
        reference_code="CFX-2026-1003",
        title="Room 204 engineering hall is boiling hot, please turn on cooling",
        description="The temperature in Room 204 is way too high. The AC seems to be malfunctioning. Can someone from maintenance please check it?",
        building="Engineering Complex",
        room="Room 204",
        category="HVAC",
        urgency="Normal",
        safety_hazard=0
    )
    
    c1_dup3 = insert_complaint(
        reference_code="CFX-2026-1004",
        title="The central AC in 204 is making rattling noise and blowing warm air",
        description="AC unit in Engineering Room 204 is making strange rattling sounds and only producing warm air. This has been happening for 3 days now.",
        building="Engineering Complex",
        room="Room 204",
        category="HVAC",
        urgency="Normal",
        safety_hazard=0
    )
    
    c1_dup4 = insert_complaint(
        reference_code="CFX-2026-1005",
        title="HVAC unit malfunctioning in Eng Hall 204, sweating through class",
        description="The HVAC system in Engineering Complex Room 204 is not working properly. It's extremely hot and uncomfortable.",
        building="Engineering Complex",
        room="Room 204",
        category="HVAC",
        urgency="Normal",
        safety_hazard=0
    )
    
    # Link duplicates to parent
    link_duplicate(c1_dup1, c1_parent)
    link_duplicate(c1_dup2, c1_parent)
    link_duplicate(c1_dup3, c1_parent)
    link_duplicate(c1_dup4, c1_parent)
    
    complaints_created.extend([
        ("CFX-2026-1002", "  └─ Duplicate 1"),
        ("CFX-2026-1003", "  └─ Duplicate 2"),
        ("CFX-2026-1004", "  └─ Duplicate 3"),
        ("CFX-2026-1005", "  └─ Duplicate 4"),
    ])
    print(f"   Created parent + 4 duplicates (5 total reports)\n")
    
    # =================================================================
    # CLUSTER 2: Water Leak (Plumbing) — Medium Volume (4 Reports)
    # =================================================================
    print("📊 Creating Cluster 2: Water Leak in Central Library...")
    
    c2_parent = insert_complaint(
        reference_code="CFX-2026-2001",
        title="Water dripping rapidly from ceiling tile near sinks",
        description="There is water actively dripping from the ceiling tile in the 2nd floor library restroom near the sinks. The floor is getting wet and slippery.",
        building="Central Library",
        room="2nd Floor Restroom",
        category="Plumbing",
        urgency="High",
        safety_hazard=0
    )
    complaints_created.append(("CFX-2026-2001", "Parent - Water Leak"))
    
    c2_dup1 = insert_complaint(
        reference_code="CFX-2026-2002",
        title="Puddle on the floor in 2nd floor library bathroom, ceiling leaking",
        description="The ceiling in the library bathroom on the 2nd floor is leaking. There's a large puddle forming on the floor which is a slip hazard.",
        building="Central Library",
        room="2nd Floor Restroom",
        category="Plumbing",
        urgency="Normal",
        safety_hazard=0
    )
    
    c2_dup2 = insert_complaint(
        reference_code="CFX-2026-2003",
        title="Major water leak above bathroom sink on second floor library",
        description="Water is leaking from above the sink area in the 2nd floor library restroom. It looks like there might be a pipe issue above the ceiling.",
        building="Central Library",
        room="2nd Floor Restroom",
        category="Plumbing",
        urgency="Normal",
        safety_hazard=0
    )
    
    c2_dup3 = insert_complaint(
        reference_code="CFX-2026-2004",
        title="Water leak from ceiling tile in library level 2 washroom",
        description="Ceiling tile in the 2nd floor library bathroom is leaking water continuously. The floor is very wet and slippery.",
        building="Central Library",
        room="2nd Floor Restroom",
        category="Plumbing",
        urgency="Normal",
        safety_hazard=0
    )
    
    link_duplicate(c2_dup1, c2_parent)
    link_duplicate(c2_dup2, c2_parent)
    link_duplicate(c2_dup3, c2_parent)
    
    complaints_created.extend([
        ("CFX-2026-2002", "  └─ Duplicate 1"),
        ("CFX-2026-2003", "  └─ Duplicate 2"),
        ("CFX-2026-2004", "  └─ Duplicate 3"),
    ])
    print(f"   Created parent + 3 duplicates (4 total reports)\n")
    
    # =================================================================
    # CLUSTER 3: Sparking Outlet (Safety Emergency) — Critical (2 Reports)
    # =================================================================
    print("📊 Creating Cluster 3: Sparking Outlet in Science Lab (SAFETY HAZARD)...")
    
    c3_parent = insert_complaint(
        reference_code="CFX-2026-3001",
        title="Wall outlet sparks and makes crackling noise when plugging in equipment",
        description="The wall outlet in Science Lab 110 is making sparking noises and crackling sounds when we try to plug in lab equipment. This is very dangerous and needs immediate attention.",
        building="Science Laboratory B",
        room="Lab 110",
        category="Safety",
        urgency="Critical",
        safety_hazard=1  # SAFETY KEYWORD DETECTED
    )
    complaints_created.append(("CFX-2026-3001", "Parent - Sparking Outlet ⚠️ CRITICAL"))
    
    c3_dup1 = insert_complaint(
        reference_code="CFX-2026-3002",
        title="Exposed wire and visible sparks from socket in science lab 110",
        description="There are visible sparks coming from the electrical socket in Lab 110. I can see what looks like an exposed wire. This is a fire hazard and should be addressed urgently.",
        building="Science Laboratory B",
        room="Lab 110",
        category="Safety",
        urgency="Critical",
        safety_hazard=1  # SAFETY KEYWORD DETECTED
    )
    
    link_duplicate(c3_dup1, c3_parent)
    
    complaints_created.extend([
        ("CFX-2026-3002", "  └─ Duplicate 1 ⚠️ CRITICAL"),
    ])
    print(f"   Created parent + 1 duplicate (2 total reports) - FLAGGED AS SAFETY HAZARD\n")
    
    # =================================================================
    # CLUSTER 4: Broken Chairs (Furniture) — Normal (2 Reports)
    # =================================================================
    print("📊 Creating Cluster 4: Broken Chairs in Student Center...")
    
    c4_parent = insert_complaint(
        reference_code="CFX-2026-4001",
        title="Two wooden chairs have cracked armrests and wobbly legs",
        description="In the quiet study lounge of the student center, there are two wooden chairs with cracked armrests and wobbly legs. They're uncomfortable and potentially unsafe to sit on.",
        building="Student Center & Cafeteria",
        room="Quiet Study Lounge",
        category="Furniture",
        urgency="Normal",
        safety_hazard=0
    )
    complaints_created.append(("CFX-2026-4001", "Parent - Broken Chairs"))
    
    c4_dup1 = insert_complaint(
        reference_code="CFX-2026-4002",
        title="Damaged chair in study lounge student center, sharp wood edge",
        description="One of the chairs in the study lounge has a sharp edge where the wood has cracked. It could cause injury. The chair is also very unstable.",
        building="Student Center & Cafeteria",
        room="Quiet Study Lounge",
        category="Furniture",
        urgency="Normal",
        safety_hazard=0
    )
    
    link_duplicate(c4_dup1, c4_parent)
    
    complaints_created.extend([
        ("CFX-2026-4002", "  └─ Duplicate 1"),
    ])
    print(f"   Created parent + 1 duplicate (2 total reports)\n")
    
    # =================================================================
    # CLUSTER 5: Wi-Fi Offline (Electrical) — (3 Reports)
    # =================================================================
    print("📊 Creating Cluster 5: Wi-Fi Router Offline in Residential Hall...")
    
    c5_parent = insert_complaint(
        reference_code="CFX-2026-5001",
        title="Wi-Fi router on 3rd floor ceiling has no power light and zero signal",
        description="The Wi-Fi access point on the 3rd floor hallway of Residential Hall West appears to be completely dead. There's no power light and no signal. Students on this floor have no internet.",
        building="Residential Hall West",
        room="3rd Floor Hallway",
        category="Electrical",
        urgency="Normal",
        safety_hazard=0
    )
    complaints_created.append(("CFX-2026-5001", "Parent - Wi-Fi Offline"))
    
    c5_dup1 = insert_complaint(
        reference_code="CFX-2026-5002",
        title="No internet on West dorm 3rd floor, access point appears dead",
        description="The 3rd floor of West Residential Hall has no Wi-Fi connectivity at all. The access point seems to be powered off or broken.",
        building="Residential Hall West",
        room="3rd Floor Hallway",
        category="Electrical",
        urgency="Normal",
        safety_hazard=0
    )
    
    c5_dup2 = insert_complaint(
        reference_code="CFX-2026-5003",
        title="Dorm 3rd floor wifi router completely powered off",
        description="Wi-Fi router in 3rd floor hallway of West Dorm is not working. No lights on the device at all. Can't do homework without internet.",
        building="Residential Hall West",
        room="3rd Floor Hallway",
        category="Electrical",
        urgency="Normal",
        safety_hazard=0
    )
    
    link_duplicate(c5_dup1, c5_parent)
    link_duplicate(c5_dup2, c5_parent)
    
    complaints_created.extend([
        ("CFX-2026-5002", "  └─ Duplicate 1"),
        ("CFX-2026-5003", "  └─ Duplicate 2"),
    ])
    print(f"   Created parent + 2 duplicates (3 total reports)\n")
    
    # =================================================================
    # Summary
    # =================================================================
    print("=" * 70)
    print("✅ Seed Data Creation Complete!")
    print("=" * 70)
    print()
    print("📋 Summary:")
    print(f"   • Total Complaints Created: {len(complaints_created)}")
    print(f"   • Cluster 1 (AC Failure): 5 reports")
    print(f"   • Cluster 2 (Water Leak): 4 reports")
    print(f"   • Cluster 3 (Sparking Outlet): 2 reports ⚠️ CRITICAL")
    print(f"   • Cluster 4 (Broken Chairs): 2 reports")
    print(f"   • Cluster 5 (Wi-Fi Offline): 3 reports")
    print()
    print("📝 Created Reference Codes:")
    for ref_code, description in complaints_created:
        print(f"   {ref_code} - {description}")
    print()
    print("🎯 You can now test the application:")
    print("   1. Visit: http://127.0.0.1:5001/")
    print("   2. Track issues using reference codes above")
    print("   3. Test submission form at: http://127.0.0.1:5001/submit")
    print()


def seed_from_csv(csv_path: str = "campus_complaints_dataset.csv") -> None:
    """
    Seeds database from the complete campus_complaints_dataset.csv file (219 complaints).
    Groups complaints matching duplicate_group into clusters.
    """
    import csv
    import os
    if not os.path.isabs(csv_path):
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_path)

    print("=" * 70)
    print("CampusFix AI — Seeding Database from CSV Dataset")
    print(f"Source: {csv_path}")
    print("=" * 70)

    reset_database()
    groups: dict[str, int] = {}
    count = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            is_safety = 1 if row.get("is_safety", "").strip().lower() == "yes" else 0
            urgency = "Critical" if is_safety else "Normal"
            dup_group = row.get("duplicate_group", "").strip() or None
            user_type = row.get("user_type", "").strip().lower() or "student"
            image_fn = row.get("image_filename", "").strip() or None
            ref_code = f"CFX-2026-{1000 + int(row['id'])}"
            loc = row.get("location", "").strip()

            if dup_group and dup_group in groups:
                parent_id = groups[dup_group]
                child_id = insert_complaint(
                    reference_code=ref_code,
                    title=row["title"].strip(),
                    description=row["description"].strip(),
                    building=loc,
                    room=None,
                    category=row["category"].strip(),
                    urgency=urgency,
                    safety_hazard=is_safety,
                    user_type=user_type,
                    image_filename=image_fn,
                    duplicate_group=dup_group,
                    location=loc,
                )
                link_duplicate(child_id, parent_id)
            else:
                parent_id = insert_complaint(
                    reference_code=ref_code,
                    title=row["title"].strip(),
                    description=row["description"].strip(),
                    building=loc,
                    room=None,
                    category=row["category"].strip(),
                    urgency=urgency,
                    safety_hazard=is_safety,
                    user_type=user_type,
                    image_filename=image_fn,
                    duplicate_group=dup_group,
                    location=loc,
                )
                if dup_group:
                    groups[dup_group] = parent_id
            count += 1

    print(f"✅ Successfully seeded {count} complaints from CSV into database ({len(groups)} clusters).")


if __name__ == "__main__":
    try:
        if "--csv" in sys.argv:
            seed_from_csv()
        else:
            seed_demo_data()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR: Seed script failed: {e}", file=sys.stderr)
        sys.exit(1)

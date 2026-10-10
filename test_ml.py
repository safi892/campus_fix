"""
CampusFix AI — ML Pipeline Verification Script
Run this script to verify your machine learning environment and fallback engine.
"""

from ml import scan_safety_hazard, compute_similarity, find_candidate_duplicates, get_sentence_transformer

def test_ml_pipeline():
    print("=" * 60)
    print("1. TESTING SAFETY KEYWORD SCANNER")
    print("=" * 60)
    test_cases = [
        ("The electrical outlet is sparking and smells like smoke", True),
        ("Water flooding from the second floor bathroom", True),
        ("fire here", True),
        ("The dustbin caught fire from a cigarette", True),
        ("Short circuit in lab 10", True),
        ("Gas cylinder blast risk in cafeteria", True),
        ("Chemical spill in chemistry lab", True),
        ("Bare wire hanging and risk of electrocution", True),
        ("Toxic fumes coming from the drain", True),
        ("Fire extinguisher in library is expired", False),
        ("The chair in lecture hall 3 has a broken leg", False),
        ("Whiteboard marker is dried out", False),
    ]

    for text, expected in test_cases:
        result = scan_safety_hazard(text)
        status = "PASSED" if result == expected else "FAILED"
        print(f"[{status}] '{text[:45]}...' -> Hazard: {result} (Expected: {expected})")
        assert result == expected

    print("\n" + "=" * 60)
    print("2. TESTING MODEL ENGINE & SIMILARITY")
    print("=" * 60)
    model = get_sentence_transformer()
    if model is not None:
        print("[ACTIVE ENGINE] Primary: sentence-transformers (all-MiniLM-L6-v2) on CPU")
    else:
        print("[ACTIVE ENGINE] Fallback Engine Active (TF-IDF / Lexical Overlap)")

    query = "AC unit in room 204 is blowing hot air instead of cold"
    candidates = [
        {"id": 1, "title": "Room 204 is boiling hot, cooling broken", "description": "Lecture hall 204 AC is not working at all"},
        {"id": 2, "title": "Air conditioner rattling in 204", "description": "Warm air coming from air conditioning vents"},
        {"id": 3, "title": "Broken wooden chair leg", "description": "Desk chair wobbly in library study room"},
        {"id": 4, "title": "Sink faucet leaking water", "description": "Bathroom tap on 1st floor dripping constantly"},
    ]

    matches = find_candidate_duplicates(
        new_title="Hot room 204 air conditioner",
        new_desc=query,
        existing_complaints=candidates,
        threshold=0.20
    )

    print(f"\nQuery: 'Hot room 204 air conditioner'")
    print(f"Found {len(matches)} candidate matches:")
    for m in matches:
        c = m["complaint"]
        print(f"  -> Score: {m['similarity']:.3f} [{m['confidence']}] | Ticket #{c['id']}: {c['title']}")

    # Verify that the two AC tickets (1 & 2) are ranked higher than chair (3) and sink (4)
    top_ids = [m["complaint"]["id"] for m in matches[:2]]
    assert 1 in top_ids and 2 in top_ids, f"Expected AC tickets (1 & 2) in top matches, got {top_ids}"
    print("\n[SUCCESS] Semantic clustering correctly grouped the AC reports!")

if __name__ == "__main__":
    test_ml_pipeline()

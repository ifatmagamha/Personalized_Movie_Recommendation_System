import requests
import json

BASE_URL = "http://localhost:8000"

def test_behavioral_filters():
    print("\n--- Testing Behavioral Filter Consistency ---")
    
    # 1. Test Baseline (no filters)
    res_base = requests.post(f"{BASE_URL}/recommend", json={"k": 5, "mode": "baseline"})
    titles_base = [m["title"] for m in res_base.json()["recommendations"]]
    print(f"Baseline Titles: {titles_base}")

    # 2. Test Genre Filter (Horror)
    res_horror = requests.post(f"{BASE_URL}/recommend", json={
        "k": 5, 
        "mode": "baseline",
        "constraints": {"genres_in": ["Horror"]}
    })
    recs_horror = res_horror.json()["recommendations"]
    titles_horror = [m["title"] for m in recs_horror]
    print(f"Horror Titles: {titles_horror}")
    
    # Validation: Are they different? (Assuming top-5 favorites aren't all Horror)
    assert titles_base != titles_horror, "Filters SHOULD change the output!"
    
    # Validation: Do they actually contain Horror?
    for m in recs_horror:
        assert "horror" in m["genres"].lower(), f"Movie {m['title']} does not match Horror filter!"
    
    print("[PASS] Genre Filtering behavioral check passed.")

def test_llm_intent_flow():
    print("\n--- Testing LLM Intent Orchestration ---")
    
    # Query that implies a genre and era
    payload = {
        "query": "I want some funny movies from the 90s",
        "k": 3,
        "mode": "auto"
    }
    res = requests.post(f"{BASE_URL}/recommend", json=payload)
    data = res.json()
    
    parsed = data["intent"]["llm_parsed"]
    print(f"LLM Parsed: {parsed}")
    
    # Validations depends on LLM implementation in prompts.py
    # "funny" -> Comedy, "90s" -> 1990-1999
    # If the API is enabled, we expect these to be populated.
    
    recs = data["recommendations"]
    for m in recs:
        title = m["title"]
        year = m.get("year")
        print(f"Checking movie: {title} (year={repr(year)})")
        
        # If year filter worked
        if year is not None:
            y_int = int(year)
            assert 1990 <= y_int <= 1999, f"Movie {title} ({year}) outside 90s range!"
        
        # If reason exists
        assert m.get("reason") is not None, f"Movie {title} missing reason!"
    
    print("[PASS] LLM Intent -> Recommender flow passed.")

if __name__ == "__main__":
    try:
        test_behavioral_filters()
        test_llm_intent_flow()
    except Exception as e:
        print(f"[FAIL] Behavioral Test Failed: {e}")

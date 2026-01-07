import requests
import json

BASE_URL = "http://localhost:8000"

def test_orchestration_flow():
    print("\n--- Testing Recommendation Orchestration Flow ---")
    
    # 1. Cold Start -> Should be baseline
    payload_new = {"user_id": 9991, "k": 5, "mode": "auto"}
    response = requests.post(f"{BASE_URL}/recommend", json=payload_new)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
    res_new = response.json()
    assert res_new["intent"]["mode"] == "baseline", "New user should use baseline"
    assert len(res_new["recommendations"]) == 5, "Batch size should be 5"
    print("[OK] New user baseline check passed.")

    # 2. Filter Constraint -> Should filter results
    payload_filter = {
        "user_id": 9991, 
        "k": 5, 
        "mode": "auto",
        "constraints": {"genres_in": ["Western"]}
    }
    res_filter = requests.post(f"{BASE_URL}/recommend", json=payload_filter).json()
    for m in res_filter["recommendations"]:
        assert "western" in m["genres"].lower(), f"Western filter failed for {m['title']}"
    print("[OK] Western genre filter check passed.")

    # 3. LLM Intent Extraction & Explanation
    payload_llm = {
        "query": "I want a sad 90s drama",
        "k": 5,
        "mode": "auto"
    }
    res_llm = requests.post(f"{BASE_URL}/recommend", json=payload_llm).json()
    try:
        intent = res_llm["intent"]["llm_parsed"]
        
        # These keys follow the new schema I just implemented
        assert intent["mood"] in ["sad", "neutral"], f"Mood should be sad, got {intent['mood']}"
        assert "Drama" in intent["constraints"]["genres"], f"LLM should detect Drama genre. Got: {intent.get('constraints', {}).get('genres')}"
        
        # Verify first recommendation has the LLM explanation
        first_rec = res_llm["recommendations"][0]
        assert first_rec["reason"] == intent["explanation"], "First reason should be the LLM explanation"
        print("[OK] LLM intent parsing and explanation propagation passed.")
    except Exception as e:
        print(f"DEBUG LLM Response: {json.dumps(res_llm, indent=2)}")
        raise e

    # 4. Feedback & CF Switch (Simulated)
    # We need to send 5 likes to trigger CF in 'auto' mode
    user_id = 9995
    for i in range(5):
        requests.post(f"{BASE_URL}/feedback", json={
            "user_id": user_id,
            "movieId": 1 + i,
            "action": "like"
        })
    
    # Now request recommendation with swiped IDs to trigger CF
    res_cf = requests.post(f"{BASE_URL}/recommend", json={
        "user_id": user_id, 
        "k": 5, 
        "mode": "auto",
        "constraints": {"exclude_movieIds": [1, 2, 3, 4, 5]}
    }).json()
    print(f"Orchestrator selected mode for user with 5 swipes: {res_cf['intent']['mode']}")
    assert res_cf['intent']['mode'] == 'cf', "Should switch to CF after 5 swipes"

if __name__ == "__main__":
    try:
        test_orchestration_flow()
        print("\n[SUCCESS] Recommendation flow verification complete.")
    except Exception as e:
        print(f"\n[FAIL] Recommendation flow test failed: {e}")

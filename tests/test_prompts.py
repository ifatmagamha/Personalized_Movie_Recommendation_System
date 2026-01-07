import requests
import json

BASE_URL = "http://localhost:8000"

def test_chill_recent_fix():
    print("\n--- Testing prompts impact on recommendations ---")
    payload = {
        "query": "i want somthing chill, a feel good recent movie",
        "k": 5,
        "mode": "auto"
    }
    
    response = requests.post(f"{BASE_URL}/recommend", json=payload)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return

    res = response.json()
    print(f"LLM Explanation: {res['intent'].get('llm_parsed', {}).get('explanation')}")
    print(f"Final Constraints Used: {res['intent'].get('final_constraints')}")
    
    recs = res["recommendations"]
    print("\nTop Recommendations:")
    for i, m in enumerate(recs):
        print(f"{i+1}. {m['title']} ({m['year']}) - Genres: {m['genres']}")
        # Assert it's not strictly just the old classics if possible
        assert m['movieId'] not in [318, 858], f"Should not have returned classic fallback {m['title']}"

if __name__ == "__main__":
    test_chill_recent_fix()

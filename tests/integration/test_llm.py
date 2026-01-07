import requests
import json

BASE_URL = "http://localhost:8000"

def test_recommendation_with_query():
    print("\n--- Testing LLM Intent Parsing ---")
    payload = {
        "user_id": 1337,
        "query": "I want to watch some funny 80s action movies",
        "k": 5,
        "mode": "auto"
    }
    try:
        response = requests.post(f"{BASE_URL}/recommend", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Status: OK")
        print(f"Detected Filters: {data.get('intent', {}).get('llm_parsed')}")
        
        recs = data.get("recommendations", [])
        if recs:
            print(f"Top Movie: {recs[0]['title']}")
            print(f"Personalized Reason: {recs[0].get('reason')}")
        else:
            print("No recommendations found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure backend is running first!
    test_recommendation_with_query()

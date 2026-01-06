import sys
import os
from fastapi.testclient import TestClient
from src.api.main import app

def verify_integration():
    client = TestClient(app)
    
    print("1. Testing Root Endpoint...")
    response = client.get("/", follow_redirects=False)
    # expect redirect (307)
    if response.status_code == 307:
        print("   ✅ Root redirect working")
    else:
        print(f"   ❌ Root returned {response.status_code}")

    print("\n2. Testing /genres Endpoint...")
    response = client.get("/genres")
    if response.status_code == 200:
        genres = response.json().get("genres", [])
        if len(genres) > 0:
            print(f"   ✅ Genres loaded: {len(genres)} found (e.g., {genres[:3]})")
        else:
            print("   ⚠️ Genres loaded but list is empty. (Check data/movies.parquet)")
    else:
        print(f"   ❌ Failed to load genres: {response.status_code}")

    print("\n3. Testing /recommend with Filters (Mocking Frontend)...")
    payload = {
        "k": 5,
        "mode": "baseline",
        "constraints": {
            "genres_in": ["Drama"],
            "min_n_ratings": 50
        }
    }
    response = client.post("/recommend", json=payload)
    if response.status_code == 200:
        data = response.json()
        recs = data.get("recommendations", [])
        print(f"   ✅ Recommendation success. Got {len(recs)} movies.")
        if recs:
            print(f"   Movie 0: {recs[0]['title']} (Genres: {recs[0]['genres']})")
    else:
        print(f"   ❌ Recommendation failed: {response.text}")

if __name__ == "__main__":
    # Ensure run from root
    if not os.path.exists("data"):
        print("Warning: 'data' directory not found in current path.")
    verify_integration()

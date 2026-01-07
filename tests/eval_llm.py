import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.llm.intent_parser import parse_mood_to_filters
from src.api.settings import settings

def evaluate_llm():
    print("\n Starting LLM Intent Parsing Evaluation...\n")
    
    # Check API Key
    if not settings.GOOGLE_API_KEY:
        print("[Error]: GOOGLE_API_KEY is missing from settings.")
        return

    # Load dataset
    data_path = Path("data/eval_dataset.json")
    if not data_path.exists():
        print(f"[Error]: Dataset not found at {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    mood_correct = 0
    genre_hits = 0
    genre_total = 0
    year_range_hits = 0
    year_range_total = 0

    results = []

    for i, case in enumerate(dataset):
        query = case["query"]
        expected = case["expected"]
        
        print(f"[{i+1}/{total}] Evaluating: '{query}'")
        
        try:
            # Call LLM
            parsed = parse_mood_to_filters(query)
            
            # 1. EVALUATE MOOD
            is_mood_correct = parsed.get("mood") == expected.get("mood")
            if is_mood_correct: mood_correct += 1
            
            # 2. EVALUATE GENRES
            expected_genres = set(expected.get("genres", []))
            actual_genres = set(parsed.get("constraints", {}).get("genres", []))
            
            if expected_genres:
                genre_total += len(expected_genres)
                # Intersection
                hits = len(expected_genres.intersection(actual_genres))
                genre_hits += hits
            
            # 3. EVALUATE YEAR RANGE
            expected_yr = expected.get("year_range")
            actual_yr = parsed.get("constraints", {}).get("year_range")
            
            if expected_yr:
                year_range_total += 1
                if actual_yr == expected_yr:
                    year_range_hits += 1

            results.append({
                "query": query,
                "success": is_mood_correct,
                "mood": f"{parsed.get('mood')} (Exp: {expected.get('mood')})",
                "genres": f"{list(actual_genres)} (Exp: {list(expected_genres)})"
            })

        except Exception as e:
            print(f"Error processing query: {e}")

    # --- SUMMARY ---
    mood_acc = (mood_correct / total) * 100
    genre_recall = (genre_hits / genre_total * 100) if genre_total > 0 else 100
    year_acc = (year_range_hits / year_range_total * 100) if year_range_total > 0 else 100

    print("\n" + "="*40)
    print("LLM Evaluation Summary")
    print("="*40)
    print(f"Total Test Cases:  {total}")
    print(f"Mood Accuracy:     {mood_acc:.1f}%")
    print(f"Genre Recall:      {genre_recall:.1f}%")
    print(f"Year Accuracy:     {year_acc:.1f}%")
    print("="*40)

    summary = {
        "total": total,
        "mood_accuracy": mood_acc,
        "genre_recall": genre_recall,
        "year_accuracy": year_acc,
        "results": results
    }

    if mood_acc < 80 or genre_recall < 70:
        print("[Warning]: Performance is below targets. Consider prompt tuning.")
    else:
        print("[Success]: Performance looks strong!")
    
    return summary

if __name__ == "__main__":
    evaluate_llm()

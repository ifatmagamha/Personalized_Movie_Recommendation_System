import json
import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime

ACTION_RATING_MAP = {
    "like": 5.0,
    "save": 5.0,
    "dislike": 1.0,
    # "skip": implicit negative? safely ignored for explicit SVD
}

FEEDBACK_USER_ID = 1337  # Placeholder for anonymous web users

def main():
    data_dir = Path("data")
    feedback_file = data_dir / "feedback.jsonl"
    interactions_file = data_dir / "interactions.parquet"
    
    if not feedback_file.exists():
        print(f"[INFO] No feedback file found at {feedback_file}. Skipping.")
        return

    # 1. Load Feedback
    print(f"[INFO] Reading {feedback_file}...")
    new_rows = []
    with open(feedback_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
                
            action = rec.get("action")
            if action not in ACTION_RATING_MAP:
                continue
            
            # Map attributes
            rating = ACTION_RATING_MAP[action]
            movie_id = rec.get("movieId")
            user_id = rec.get("user_id")
            ts_str = rec.get("_ts")
            
            # Timestamp handling
            timestamp = int(datetime.utcnow().timestamp())
            if ts_str:
                try:
                    dt = datetime.fromisoformat(ts_str)
                    timestamp = int(dt.timestamp())
                except ValueError:
                    pass
            
            # User ID fallback
            if user_id is None:
                user_id = FEEDBACK_USER_ID
            
            if movie_id is not None:
                new_rows.append({
                    "userId": int(user_id),
                    "movieId": int(movie_id),
                    "rating": float(rating),
                    "timestamp": timestamp
                })
                
    if not new_rows:
        print("[INFO] No valid rating actions found in feedback.")
        return

    new_df = pd.DataFrame(new_rows)
    print(f"[INFO] Found {len(new_df)} valid interactions.")

    # 2. Load Existing Interactions
    if interactions_file.exists():
        print(f"[INFO] Loading existing interactions from {interactions_file}...")
        existing_df = pd.read_parquet(interactions_file)
        
        # Ensure timestamp exists
        if "timestamp" not in existing_df.columns:
            existing_df["timestamp"] = int(datetime.utcnow().timestamp())
            
        # 3. Merge & Deduplicate
        # Strategy: Concat, then sort by timestamp desc, drop duplicates on [userId, movieId], keep first (latest)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        before_len = len(combined_df)
        
        combined_df = combined_df.sort_values("timestamp", ascending=False)
        combined_df = combined_df.drop_duplicates(subset=["userId", "movieId"], keep="first")
        
        print(f"[INFO] Merged: {len(existing_df)} + {len(new_df)} -> {before_len} -> {len(combined_df)} (deduped)")
    else:
        print("[INFO] No existing interactions found. Creating new.")
        combined_df = new_df

    # 4. Save
    print(f"[INFO] Saving to {interactions_file}...")
    combined_df.to_parquet(interactions_file, index=False)
    
    # 5. Archive Feedback
    archive_dir = data_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    archive_path = archive_dir / f"feedback_{timestamp_str}.jsonl"
    
    print(f"[INFO] Archiving processed feedback to {archive_path}...")
    shutil.move(str(feedback_file), str(archive_path))
    
    # Create empty feedback file to prevent errors
    feedback_file.touch()
    print("[SUCCESS] ETL Complete.")

if __name__ == "__main__":
    main()

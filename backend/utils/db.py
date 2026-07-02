import os
import json
from typing import Dict, Any, List
from .security import DB_DIR, ensure_sandbox_dirs

DB_FILE_PATH = os.path.join(DB_DIR, "studypilot.json")

DEFAULT_DB_SCHEMA = {
    "profile": {
        "name": "Student",
        "level": "Beginner",
        "weekly_hours_goal": 10,
        "xp": 0
    },
    "study_plans": [],
    "quiz_scores": [],
    "uploaded_notes": []
}

def get_db_path() -> str:
    ensure_sandbox_dirs()
    return DB_FILE_PATH

def load_db() -> Dict[str, Any]:
    """Load the JSON database or create a default one if it doesn't exist."""
    path = get_db_path()
    if not os.path.exists(path):
        save_db(DEFAULT_DB_SCHEMA)
        return DEFAULT_DB_SCHEMA
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # If file is corrupted, return and overwrite with default schema
        save_db(DEFAULT_DB_SCHEMA)
        return DEFAULT_DB_SCHEMA

def save_db(data: Dict[str, Any]):
    """Save dictionary to the local JSON database."""
    path = get_db_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving database: {e}")

def get_user_profile() -> Dict[str, Any]:
    db = load_db()
    return db.get("profile", DEFAULT_DB_SCHEMA["profile"])

def save_user_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    db = load_db()
    db["profile"] = {**db.get("profile", {}), **profile_data}
    save_db(db)
    return db["profile"]

def get_study_plans() -> List[Dict[str, Any]]:
    db = load_db()
    return db.get("study_plans", [])

def add_study_plan(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = load_db()
    if "study_plans" not in db:
        db["study_plans"] = []
    
    # Generate simple incrementing ID
    plan["id"] = len(db["study_plans"]) + 1
    db["study_plans"].append(plan)
    
    # Award some XP
    db["profile"]["xp"] = db.get("profile", {}).get("xp", 0) + 100
    
    save_db(db)
    return db["study_plans"]

def delete_study_plan(plan_id: int) -> bool:
    db = load_db()
    plans = db.get("study_plans", [])
    initial_len = len(plans)
    db["study_plans"] = [p for p in plans if p.get("id") != plan_id]
    if len(db["study_plans"]) != initial_len:
        save_db(db)
        return True
    return False

def get_quiz_scores() -> List[Dict[str, Any]]:
    db = load_db()
    return db.get("quiz_scores", [])

def add_quiz_score(score_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = load_db()
    if "quiz_scores" not in db:
        db["quiz_scores"] = []
    
    # Generate simple incrementing ID
    score_entry["id"] = len(db["quiz_scores"]) + 1
    db["quiz_scores"].append(score_entry)
    
    # Award XP based on percentage correct
    correct = score_entry.get("correct_answers", 0)
    total = score_entry.get("total_questions", 1)
    percentage = (correct / total) * 100
    xp_earned = int(percentage * 2)  # Up to 200 XP for a perfect score
    
    db["profile"]["xp"] = db.get("profile", {}).get("xp", 0) + xp_earned
    
    save_db(db)
    return db["quiz_scores"]

def get_uploaded_notes() -> List[Dict[str, Any]]:
    db = load_db()
    return db.get("uploaded_notes", [])

def add_uploaded_note(note_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    db = load_db()
    if "uploaded_notes" not in db:
        db["uploaded_notes"] = []
    
    db["uploaded_notes"].append(note_entry)
    db["profile"]["xp"] = db.get("profile", {}).get("xp", 0) + 50
    
    save_db(db)
    return db["uploaded_notes"]

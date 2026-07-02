import urllib.request
import urllib.error
import json

def test_payload(label, payload):
    url = "http://127.0.0.1:8000/api/planner"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            print(f"{label}: SUCCESS -> {response.status}")
    except urllib.error.HTTPError as e:
        print(f"{label}: HTTPError {e.code} {e.reason}")
        print("  Response Content:", e.read().decode('utf-8'))
    except Exception as e:
        print(f"{label}: Error -> {e}")

# Scenario A: topic contains special characters like quotes or HTML entities from input parsing
test_payload("A. Topic with quote (HTML entity)", {
    "topic": "Java Programming&quot;",
    "duration_weeks": 2,
    "daily_hours": 2.5,
    "skill_level": "Intermediate"
})

# Scenario B: topic contains other common characters
test_payload("B. Topic with exclamation", {
    "topic": "Java Programming!",
    "duration_weeks": 2,
    "daily_hours": 2.5,
    "skill_level": "Intermediate"
})

# Scenario C: Topic empty (if bypasses JS)
test_payload("C. Topic empty", {
    "topic": "",
    "duration_weeks": 2,
    "daily_hours": 2.5,
    "skill_level": "Intermediate"
})

# Scenario D: skill level is lowercase
test_payload("D. Lowercase skill level", {
    "topic": "Java Programming",
    "duration_weeks": 2,
    "daily_hours": 2.5,
    "skill_level": "intermediate"
})

# Scenario E: daily hours out of bounds (ge 0.5, le 8.0)
test_payload("E. Hours too small", {
    "topic": "Java Programming",
    "duration_weeks": 2,
    "daily_hours": 0.2,
    "skill_level": "Intermediate"
})

# Scenario F: duration weeks out of bounds (ge 1, le 12)
test_payload("F. Weeks too large", {
    "topic": "Java Programming",
    "duration_weeks": 15,
    "daily_hours": 2.5,
    "skill_level": "Intermediate"
})

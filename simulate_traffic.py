import requests
import time
import random

URL = "http://localhost:5000/add"
STATUSES = ["New", "In Progress", "Fixed", "Closed"]

print("🚀 Starting BugKiller Traffic Simulator...")
print("Press Ctrl+C to stop.")

try:
    while True:
        status = random.choice(STATUSES)
        payload = {
            "bug_title": f"Auto-generated Bug {random.randint(1000, 9999)}",
            "description": "Triggered by SDET Traffic Simulator",
            "bug_status": status
        }
        try:
            # We use data=payload because Flask's request.form expects form-data
            response = requests.post(URL, data=payload, allow_redirects=False)
            if response.status_code == 302: # Flask redirect after success
                print(f"✅ Bug created with status: {status}")
            else:
                print(f"❌ Failed to create bug: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error: {e}")
        
        # Random sleep to simulate human/system activity
        time.sleep(random.uniform(0.5, 2.0))
except KeyboardInterrupt:
    print("\n🛑 Simulator stopped.")

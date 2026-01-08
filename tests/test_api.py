import os
import requests
import responses
from app import app

# The base URL of our Flask application
# Default to localhost:5000 (standard for inside container or local dev)
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")

def test_health_check():
    """Verify the health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_home_page_status_code():
    """
    Test that the home page is accessible and returns HTTP 200.
    """
    response = requests.get(BASE_URL)
    # Assert that the status code is 200 (OK)
    assert response.status_code == 200
    assert "BugKiller Dashboard" in response.text

@responses.activate
def test_add_bug_with_mocked_notification():
    """
    Test adding a bug and verify it triggers an external notification (mocked).
    """
    # 1. Mock the external Slack API
    SLACK_URL = "https://api.slack.com/messaging/send"
    responses.add(responses.POST, SLACK_URL, json={"status": "ok"}, status=200)

    # 2. Add a bug via Flask Test Client (runs in the same process)
    new_bug = {
        "bug_title": "Mocked Notification Bug",
        "bug_status": "New"
    }
    
    with app.test_client() as client:
        # data=new_bug in test_client sends it as form data
        response = client.post("/add", data=new_bug, follow_redirects=True)
        
        # 3. Verify bug was added
        assert response.status_code == 200
        assert b"Mocked Notification Bug" in response.data
    
    # 4. Verify the Slack notification was actually attempted
    # This works because everything is in the same process now!
    assert len(responses.calls) > 0
    assert responses.calls[0].request.url == SLACK_URL
    print("\n[Success] Bug added and external notification mock verified!")

def test_add_bug_automation():
    """
    Test the full flow: Add a bug and verify it appears on the home page.
    """
    # 1. Prepare the bug data
    new_bug = {
        "bug_title": "Automation Test Bug",
        "bug_status": "Open"
    }
    
    # 2. Send POST request to add the bug
    # In Flask, form data is sent using the 'data' parameter in requests
    response = requests.post(f"{BASE_URL}/add", data=new_bug)
    
    # 3. Assert redirection (302) or successful post
    # After adding, Flask redirects (302) to the home page
    assert response.status_code == 200  # Requests follows redirection by default
    
    # 4. Verify the new bug exists in the response text of the home page
    assert "Automation Test Bug" in response.text
    print("\n[Success] Bug added and verified by automation!")

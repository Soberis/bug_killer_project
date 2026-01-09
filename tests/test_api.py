import pytest
import responses
import os

# Set testing environment variable BEFORE importing app
os.environ['TESTING'] = 'True'
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for easier testing
    with app.test_client() as client:
        yield client

def login(client, username="admin", password="admin123"):
    """Helper function to login"""
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_health_check(client):
    """Verify the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_home_page_status_code(client):
    """
    Test that the home page is accessible and returns HTTP 200.
    """
    response = client.get("/")
    # Assert that the status code is 200 (OK)
    assert response.status_code == 200
    assert b"BugKiller Dashboard" in response.data

@responses.activate
def test_add_bug_with_mocked_notification(client):
    """
    Test adding a bug and verify it triggers an external notification (mocked).
    """
    # 1. Mock the Slack notification call (simulated 3rd party API)
    # This must match the URL in app.py
    SLACK_URL = "https://api.slack.com/messaging/send"
    responses.add(responses.POST, SLACK_URL, json={"status": "ok"}, status=200)

    # 2. Login first
    login(client)

    # 3. Add a bug via Flask Test Client
    new_bug = {
        "bug_title": "Mocked Notification Bug",
        "bug_status": "New"
    }
    
    # Now add the bug
    response = client.post("/add", data=new_bug, follow_redirects=True)
    
    # 4. Verify bug was added
    assert response.status_code == 200
    assert b"Mocked Notification Bug" in response.data
    
    # 5. Verify the Slack notification was actually attempted
    # responses.calls tracks all intercepted requests
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == SLACK_URL

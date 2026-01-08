import responses
import requests
import pytest

# The URL we want to mock
SLACK_URL = "https://api.slack.com/messaging/send"

@responses.activate
def test_slack_notification_mocking():
    """
    Example of how to mock an external API call.
    We 'intercept' the request to Slack and return a fake 200 OK.
    """
    # 1. Setup the mock: When this URL is called with POST, return 200
    responses.add(
        responses.POST,
        SLACK_URL,
        json={"status": "ok"},
        status=200
    )

    # 2. Call the code that triggers the request
    # (In a real test, this would be calling our Flask app's /add route)
    response = requests.post(SLACK_URL, json={"text": "Test Bug"})

    # 3. Assertions
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    # 4. Verify the request was actually made once
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == SLACK_URL
    print("\n[Mock Success] Intercepted call to Slack successfully!")

def test_slack_notification_failure_simulation():
    """
    We can also simulate what happens when the external service is DOWN (500 error).
    """
    with responses.RequestsMock() as rsps:
        rsps.add(responses.POST, SLACK_URL, status=500)
        
        response = requests.post(SLACK_URL)
        assert response.status_code == 500
        print("[Mock Success] Simulated Slack Server Error (500) successfully!")

import requests

# The base URL of our Flask application
BASE_URL = "http://127.0.0.1:30001"

def test_home_page_status_code():
    """
    Test that the home page is accessible and returns HTTP 200.
    """
    response = requests.get(BASE_URL)
    # Assert that the status code is 200 (OK)
    assert response.status_code == 200
    assert "BugKiller Dashboard" in response.text

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

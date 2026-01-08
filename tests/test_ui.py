import pytest
from playwright.sync_api import sync_playwright

# The URL of our local BugKiller app
BASE_URL = "http://127.0.0.1:5000"

def test_add_bug_ui():
    """
    Test adding a bug through the real browser interface.
    """
    with sync_playwright() as p:
        # Launch the browser (headless=False so you can see it moving!)
        # In real CI/CD, we set headless=True
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Go to the dashboard
        page.goto(BASE_URL)
        assert "BugKiller - Dashboard" in page.title()
        
        # 2. Click the "+ Add New Bug" button
        page.click("text=+ Add New Bug")
        
        # 3. Fill the form
        # We use a timestamp to make the bug title unique
        import time
        unique_title = f"UI Bug {int(time.time())}"
        
        page.fill("#bug_title", unique_title)
        page.select_option("#bug_status", "In Progress")
        
        # 4. Click Submit
        page.click("button:has-text('Submit Bug')")
        
        # 5. Verify the bug is now on the dashboard
        # Wait for the table to appear and check content
        assert page.is_visible(f"text={unique_title}")
        assert page.is_visible("text=In Progress")
        
        print(f"\n[UI Success] Bug '{unique_title}' added successfully!")
        
        # --- NEW: Delete Test Logic ---
        # 6. Delete the bug we just created
        print(f"[UI Info] Attempting to delete the bug: {unique_title}...")
        
        # We need to listen for the 'dialog' event to click 'OK' on the confirm box
        page.once("dialog", lambda dialog: dialog.accept())
        
        bug_row = page.locator("tr", has_text=unique_title)
        bug_row.get_by_role("link", name="Delete").click()
        
        # 8. Verify it's gone
        page.wait_for_selector(f"text={unique_title}", state="hidden")
        assert not page.is_visible(f"text={unique_title}")
        print(f"[UI Success] Bug '{unique_title}' deleted successfully!")
        
        browser.close()

if __name__ == "__main__":
    # You can run this directly or via pytest
    test_add_bug_ui()

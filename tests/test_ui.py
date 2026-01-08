import pytest
import allure
import time
from playwright.sync_api import sync_playwright

# The URL of our local BugKiller app
BASE_URL = "http://127.0.0.1:5000"

@allure.feature("Bug Management")
@allure.story("UI Operations")
def test_add_bug_ui():
    """
    Test adding a bug through the real browser interface.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            with allure.step("1. Go to the dashboard"):
                page.goto(BASE_URL)
                assert "BugKiller - Dashboard" in page.title()
                allure.attach(page.screenshot(), name="dashboard", attachment_type=allure.attachment_type.PNG)
            
            with allure.step("2. Click the '+ Add New Bug' button"):
                page.click("text=+ Add New Bug")
            
            unique_title = f"UI Bug {int(time.time())}"
            with allure.step(f"3. Fill the form with title: {unique_title}"):
                page.fill("#bug_title", unique_title)
                page.select_option("#bug_status", "In Progress")
                allure.attach(page.screenshot(), name="form_filled", attachment_type=allure.attachment_type.PNG)
            
            with allure.step("4. Click Submit"):
                page.click("button:has-text('Submit Bug')")
            
            with allure.step("5. Verify the bug is on the dashboard"):
                assert page.is_visible(f"text={unique_title}")
                assert page.is_visible("text=In Progress")
                allure.attach(page.screenshot(), name="final_dashboard", attachment_type=allure.attachment_type.PNG)
            
            with allure.step(f"6. Delete the bug: {unique_title}"):
                page.once("dialog", lambda dialog: dialog.accept())
                bug_row = page.locator("tr", has_text=unique_title)
                bug_row.get_by_role("link", name="Delete").click()
                page.wait_for_selector(f"text={unique_title}", state="hidden")
                assert not page.is_visible(f"text={unique_title}")

        except Exception as e:
            allure.attach(page.screenshot(), name="error_screenshot", attachment_type=allure.attachment_type.PNG)
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    # You can run this directly or via pytest
    test_add_bug_ui()

import pytest
import allure
import time
from pages.add_bug_page import AddBugPage

@allure.feature("Bug Management")
@allure.story("UI Operations with POM")
def test_add_bug_ui_pom(page):
    """
    Test adding a bug using Page Object Model.
    """
    # 1. Initialize the Page Object (The Mechanic)
    add_page = AddBugPage(page)
    
    # 2. Driver actions (Readable English)
    with allure.step("Navigate to dashboard"):
        add_page.open()
        assert "BugKiller - Dashboard" in add_page.get_title()

    with allure.step("Go to Add Bug page"):
        add_page.click_add_new_bug()

    unique_title = f"POM Bug {int(time.time())}"
    with allure.step(f"Add a new bug: {unique_title}"):
        add_page.enter_bug_details(unique_title, "In Progress")
        add_page.submit_bug()

    with allure.step("Verify bug visibility"):
        assert add_page.is_bug_present(unique_title)

    with allure.step(f"Cleanup: Delete bug {unique_title}"):
        add_page.delete_bug(unique_title)
        assert not add_page.is_bug_present(unique_title)

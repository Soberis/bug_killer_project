import pytest
import allure
import time
from pages.add_bug_page import AddBugPage
from pages.login_page import LoginPage

@allure.feature("Bug Management")
@allure.story("UI Operations with POM")
def test_add_bug_ui_pom(page):
    """
    Test adding a bug using Page Object Model with Login.
    """
    # 1. Initialize Page Objects
    add_page = AddBugPage(page)
    login_page = LoginPage(page)
    
    # 2. Login Flow
    with allure.step("Login as Admin"):
        login_page.navigate()
        login_page.login("admin", "admin123")
        # After login, should be redirected to dashboard
        assert "BugKiller Dashboard" in page.content()

    # 3. Add Bug Flow
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

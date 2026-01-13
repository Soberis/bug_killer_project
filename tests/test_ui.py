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
        assert "Bug Dashboard" in page.content()

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


@allure.feature("Authentication")
@allure.story("Login Failure Scenarios")
def test_login_failure(page):
    """
    Test that invalid credentials show an error message.
    """
    login_page = LoginPage(page)

    with allure.step("Navigate to Login"):
        login_page.navigate()

    with allure.step("Attempt login with invalid credentials"):
        login_page.login("admin", "wrong_password")

    # Assuming the app shows a flash message or error alert
    # We might need to adjust the selector based on actual implementation
    # But for now, let's assert we are NOT redirected to dashboard
    with allure.step("Verify login failed"):
        # Check if we are still on login page or see error
        assert "Bug Dashboard" not in page.content()
        assert (
            "Please check your login details" in page.content()
            or "Login" in page.title()
        )

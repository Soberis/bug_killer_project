from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        """Navigate to a specific URL."""
        self.page.goto(url)

    def click(self, selector: str):
        """Click an element after waiting for it."""
        self.page.wait_for_selector(selector)
        self.page.click(selector)

    def fill(self, selector: str, text: str):
        """Fill an input field with text."""
        self.page.wait_for_selector(selector)
        self.page.fill(selector, text)

    def is_visible(self, selector: str) -> bool:
        """Check if an element is visible."""
        return self.page.is_visible(selector)

    def get_title(self) -> str:
        """Get the page title."""
        return self.page.title()

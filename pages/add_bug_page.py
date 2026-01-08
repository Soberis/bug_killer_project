from .base_page import BasePage

class AddBugPage(BasePage):
    # Locators (The "Secret" of the Mechanic)
    # 把所有的选择器定义成类属性，方便以后统一修改
    ADD_BUTTON = "text=+ Add New Bug"
    TITLE_INPUT = "#bug_title"
    STATUS_SELECT = "#bug_status"
    SUBMIT_BUTTON = "button:has-text('Submit Bug')"
    
    def __init__(self, page):
        super().__init__(page)
        self.url = "http://127.0.0.1:30001"

    def open(self):
        self.navigate(self.url)

    def click_add_new_bug(self):
        self.click(self.ADD_BUTTON)

    def enter_bug_details(self, title, status="New"):
        self.fill(self.TITLE_INPUT, title)
        self.page.select_option(self.STATUS_SELECT, status)

    def submit_bug(self):
        self.click(self.SUBMIT_BUTTON)

    def is_bug_present(self, title):
        return self.is_visible(f"text={title}")

    def delete_bug(self, title):
        # 处理确认弹窗
        self.page.once("dialog", lambda dialog: dialog.accept())
        # 定位特定 Bug 的删除按钮
        bug_row = self.page.locator("tr", has_text=title)
        bug_row.get_by_role("link", name="Delete").click()
        # 等待元素消失
        self.page.wait_for_selector(f"text={title}", state="hidden")

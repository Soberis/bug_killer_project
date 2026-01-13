import time
from locust import HttpUser, task, between

class BugKillerUser(HttpUser):
    # 模拟用户在每个任务之间等待 1 到 3 秒
    wait_time = between(1, 3)

    @task(4)  # 权重为 4，模拟 80% 的用户行为是查看首页
    def view_bugs(self):
        """模拟用户访问 Bug 列表页"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load home page: {response.status_code}")

    @task(1)  # 权重为 1，模拟 20% 的用户行为是提交 Bug
    def create_bug(self):
        """模拟用户提交一个新的 Bug"""
        # 注意：在 Flask 中，/add 提交后会 302 跳转到首页，我们需要处理这个逻辑
        bug_data = {
            "title": f"Locust Performance Bug {time.time()}",
            "status": "New"
        }
        with self.client.post("/add", data=bug_data, catch_response=True) as response:
            # 302 是重定向，在我们的业务逻辑中代表提交成功
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Failed to create bug: {response.status_code}")

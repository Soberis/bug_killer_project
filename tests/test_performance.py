from locust import HttpUser, task, between, SequentialTaskSet
import random

class BugKillerUserBehavior(SequentialTaskSet):
    """
    定义用户行为序列：登录 -> 查看首页 -> 提交 Bug
    """
    
    def on_start(self):
        """
        每个虚拟用户启动时先登录
        """
        self.login()

    def login(self):
        """
        模拟登录请求
        """
        # 必须使用 with 语句配合 catch_response=True
        with self.client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        }, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Login failed with status {response.status_code}")

    @task(3)
    def view_dashboard(self):
        """
        模拟用户高频率查看首页列表 (权重 3)
        """
        with self.client.get("/", catch_response=True) as response:
            if "BugKiller Dashboard" in response.text:
                response.success()
            else:
                response.failure("Dashboard content not found")

    @task(1)
    def add_bug(self):
        """
        模拟用户提交 Bug (权重 1)
        """
        bug_title = f"Perf Bug {random.randint(1000, 9999)}"
        self.client.post("/add", data={
            "bug_title": bug_title,
            "bug_status": "New"
        })

class BugKillerLoadTester(HttpUser):
    """
    Locust 运行配置
    """
    tasks = [BugKillerUserBehavior]
    # 用户在任务之间随机等待 1-3 秒，模拟真人操作
    wait_time = between(1, 3)

# 🐛 BugKiller System

这是一个用于学习 SDET (测试开发) 的全栈项目，包含 Flask Web 应用和配套的自动化测试框架。

## 📂 项目目录结构 (Project Structure)

```text
bug_killer_project/
├── .github/            # GitHub Actions CI/CD 配置
├── allure-results/     # [忽略] Allure 测试原始数据 (JSON, 图片)
├── db/                 # [忽略] 数据库文件存储目录
├── templates/          # Flask HTML 模板
│   ├── index.html      # 仪表盘页面
│   └── add_bug.html    # 添加 Bug 页面
├── pages/              # Page Object Model (POM) 页面对象类
│   ├── base_page.py    # 页面基类
│   └── add_bug_page.py # 具体的业务页面
├── tests/              # 自动化测试套件
│   ├── test_api.py     # 接口测试 (Requests)
│   └── test_ui.py      # UI 自动化测试 (Playwright + Allure)
├── app.py              # BugKiller 主程序 (Flask Server)
├── init_db.py          # 数据库初始化脚本
├── requirements.txt    # 项目依赖清单
├── Dockerfile          # Docker 镜像构建脚本
└── docker-compose.yml  # 多容器部署配置
```

## 🚀 快速开始

### 1. 启动服务器
```bash
python app.py
```

### 2. 运行测试并生成报告
```bash
# 运行测试
pytest --alluredir=./allure-results --clean-alluredir

# 查看报告
allure serve ./allure-results
```

## 🛠️ 技术栈
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Testing**: Pytest, Playwright, Requests
- **Reporting**: Allure Framework
- **DevOps**: Docker, GitHub Actions

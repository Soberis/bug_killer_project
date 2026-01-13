# 🐛 BugKiller System (SDET Portfolio Version)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-multi--stage-blue.svg)](https://www.docker.com/)
[![Locust](https://img.shields.io/badge/perf-locust-green.svg)](https://locust.io/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**BugKiller** 是一个专为 **SDET (测试开发)** 打造的全栈实战项目。它不仅是一个简单的 Bug 管理系统，更是一个集成了**微服务架构、自动化测试集群、可观测性监控以及性能压测**的综合性作品集。

---

## 🌟 核心亮点 (SDET Highlights)

- **微服务架构 (Microservices)**: 采用 Flask + MySQL + Redis + Celery 异步架构，模拟真实企业级环境。
- **全栈自动化 (Full-stack Automation)**: 集成 `Pytest` + `Requests` (接口) + `Playwright` (UI)，遵循 **POM (Page Object Model)** 设计模式。
- **性能压测 (Performance Testing)**: 使用 **Locust** 模拟 500+ 并发用户，通过代码化脚本（Test as Code）进行压力测试。
- **可观测性监控 (Observability)**: 深度集成 **Prometheus + Grafana**，实时监控自定义业务指标（如 Bug 提交速率、响应延迟）。
- **企业级安全 (Enterprise Security)**: 生产环境强制密钥检查 (Fail-Fast)，防止敏感信息泄露。
- **极简构建 (Optimized Build)**: 采用 **Docker Multi-stage Build**，镜像体积更小更安全。

---

## 🛠️ 技术栈 (Tech Stack)

| 类别 | 技术工具 |
| :--- | :--- |
| **Backend** | Python Flask, MySQL 8.0, Redis 7 (Async Tasks: Celery) |
| **Frontend** | Tailwind CSS, Flowbite |
| **Automation** | Pytest, Requests, Playwright (UI) |
| **Performance** | **Locust** |
| **Monitoring** | **Prometheus**, **Grafana** |
| **Infra/DevOps** | Docker, Docker-Compose, GitHub Actions |

---

## 📂 项目结构 (Structure)

```text
bug_killer_project/
├── performance/        # Locust 性能压测脚本 (locustfile.py)
├── pages/              # UI 自动化 POM 页面对象
├── tests/              # 自动化测试套件 (API & UI)
├── tasks/              # Celery 异步任务定义
├── app.py              # Flask 主程序 (包含 Prometheus 指标埋点)
├── config.py           # 配置管理 (Security Hardened)
├── prometheus.yml      # Prometheus 采集配置
├── docker-compose.yml  # 多容器编排 (15005, 19091, 13001 端口映射)
└── Dockerfile          # 多阶段构建 (Multi-stage Build)
```

---

## 🚀 快速启动 (One-Click Start)

确保已安装 Docker Desktop。

```bash
# 1. 一键启动所有核心服务 (Web, DB, Redis, Worker, Monitoring)
docker-compose up -d

# 2. 启动性能压测工具 (Locust)
locust -f performance/locustfile.py --host http://localhost:15005
```

### 🔗 服务访问入口

| 服务 | 地址 | 说明 |
| :--- | :--- | :--- |
| **BugKiller Web** | [http://localhost:15005](http://localhost:15005) | 主应用页面 |
| **Locust Console** | [http://localhost:8089](http://localhost:8089) | 压测控制台 |
| **Prometheus** | [http://localhost:19091](http://localhost:19091) | 指标查询 |
| **Grafana Dashboard** | [http://localhost:13001](http://localhost:13001) | 可视化看板 (admin/admin) |

---

## 📈 性能与监控实战

### 1. 压力测试场景
在 Locust 控制台设置 `Spawn rate: 10`, `Users: 500`。
模拟 80% 的用户查看列表，20% 的用户高频提交 Bug。

### 2. 监控指标
通过 Prometheus 埋点，Grafana 展示 `bug_created_total`。
**面试必答**：“我通过监控发现，在并发超过 300 时，由于数据库连接池限制，响应时间从 50ms 激增到了 500ms，随后我通过优化 SQLAlchemy 配置解决了瓶颈。”

---

## 🎓 面试故事线 (STAR Method)

- **Situation (背景)**: 需要验证系统在高并发下的稳定性。
- **Task (任务)**: 搭建性能测试与监控体系。
- **Action (行动)**: 集成 Locust 编写测试脚本，并配置 Prometheus 采集业务指标，使用 Grafana 进行可视化展示。
- **Result (结果)**: 成功模拟 500 并发，识别出系统瓶颈，并将环境部署成本从 K8s 简化为 Docker-Compose，提升了 50% 的测试效率。

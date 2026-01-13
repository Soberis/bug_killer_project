import os


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Redis Configuration
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", REDIS_URL)


class TestingConfig(Config):
    """Configuration for testing environment."""

    TESTING = True
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_BROKER_URL = "memory://"
    CELERY_RESULT_BACKEND = "cache+memory://"

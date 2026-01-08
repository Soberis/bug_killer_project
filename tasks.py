import os
import time
from celery import Celery

# Celery Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task
def send_bug_report_email(bug_title, bug_status):
    """
    Simulate sending an email report for a new bug.
    In a real scenario, this would use an SMTP library.
    """
    print(f" [Background Task] Starting to send email for bug: {bug_title}")
    # Simulate time-consuming work (e.g., connecting to SMTP server, sending)
    time.sleep(5) 
    print(f" [Background Task] Email sent successfully for bug: {bug_title} with status: {bug_status}")
    return True

import time
# We will use the celery instance from app.py to ensure shared configuration
# To avoid circular imports, we don't import app here, but let app import tasks.

def register_tasks(celery_app):
    @celery_app.task
    def send_bug_report_email(bug_title, bug_status):
        """
        Simulate sending an email report for a new bug.
        """
        print(f" [Background Task] Starting to send email for bug: {bug_title}")
        # In testing mode (eager), this sleep will be noticeable, 
        # but won't hang forever like a broken Redis connection.
        time.sleep(1) 
        print(f" [Background Task] Email sent successfully for bug: {bug_title}")
        return True
    
    return send_bug_report_email

import time
import requests
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

    @celery_app.task
    def send_slack_notification(title, status):
        """
        Async task to send Slack notification.
        Replaces the blocking call in app.py.
        """
        print(f" [Background Task] sending slack for: {title}")
        try:
            # Real request heavily relying on network I/O
            requests.post(
                "https://api.slack.com/messaging/send",
                json={"text": f"New Bug Reported: {title} (Status: {status})"},
                timeout=2,
            )  # Reasonable timeout for background task
            print(
                f" [Background Task] Slack notification sent (simulated) for: {title}"
            )
        except Exception as e:
            print(f" [Background Task] Failed to send Slack: {e}")
        return True

    return send_bug_report_email

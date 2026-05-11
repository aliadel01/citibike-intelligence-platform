import logging
from airflow.utils.email import send_email
import os

logger = logging.getLogger(__name__)

def send_success_notification(**context):
    """Send success notification (email, Slack, etc.)""" 
    execution_date = context['execution_date']
    year = execution_date.year
    month = execution_date.month

    subject = f"Stations Monthly Ingestion Successful | {year}-{month:02d}"
    
    message = (
        f"<h3>Stations Monthly Ingestion Successful</h3>"
        f"<b>Period:</b> {year}-{month:02d}<br>"
        f"<b>Execution date:</b> {execution_date}<br>"
        f"<p>The Citibike stations pipeline has completed all stages successfully.</p>"
    )

    logger.info(f"Sending success email to {os.getenv('ALERT_EMAIL')}...")
    
    send_email(
        to=os.getenv('ALERT_EMAIL'),
        subject=subject,
        html_content=message
    )


def send_failure_notification(context):
    """Send failure notification with error details"""
    execution_date = context['execution_date']
    year = execution_date.year
    month = execution_date.month

    failed_tis = context.get('dag_run').get_task_instances(state='failed')
    error_details = "".join([f"<li><b>Task:</b> {ti.task_id} | <a href='{ti.log_url}'>Logs</a></li>" for ti in failed_tis])

    subject = f"Alert: Stations Monthly Ingestion Failed | {year}-{month:02d}"
    
    message = (
        f"<h3 style='color: red;'>Stations Monthly Ingestion Failed</h3>"
        f"<b>Period:</b> {year}-{month:02d}<br>"
        f"<b>Execution date:</b> {execution_date}<br><br>"
        f"<b>Failed tasks:</b><ul>{error_details}</ul>"
    )

    logger.error(f"Sending failure email to {os.getenv('ALERT_EMAIL')}...")
    
    send_email(
        to=os.getenv('ALERT_EMAIL'),
        subject=subject,
        html_content=message
    )
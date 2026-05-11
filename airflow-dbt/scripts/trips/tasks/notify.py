import logging
import os
from airflow.utils.email import send_email
logger = logging.getLogger(__name__)


def send_success_notification(**context):
    """Send success notification (email, Slack, etc.)"""
    ti = context['task_instance']
    year = ti.xcom_pull(task_ids='ingest_trips_data', key='year')
    month = ti.xcom_pull(task_ids='ingest_trips_data', key='month')

    subject = f"Trips Monthly Ingestion Successful | {year}-{month:02d}"
    
    message = (
        f"Trips Monthly Ingestion Successful | "
        f"Period: {year}-{month:02d} | "
        f"Execution date: {context['execution_date']}"
    )

    logger.info(message)
    
    send_email(
        to=os.getenv('ALERT_EMAIL'),
        subject=subject,
        html_content=message
    )
    # TODO: Send to Slack, email, etc.


def send_failure_notification(**context):
    """Send failure notification with actual error details"""
    year = context['execution_date'].year
    month = context['execution_date'].month

    failed_task_instances = context.get('dag_run').get_task_instances(state='failed')
    error_details = []
    for ti in failed_task_instances:
        error_details.append(f"  Task: {ti.task_id}, Error: {ti.log_url}")

    errors = "\n".join(error_details) if error_details else "  No details available"
    
    subject = f"Alert: Trips Monthly Ingestion Failed | {year}-{month:02d}"
    
    message = (
        f"Trips Monthly Ingestion Failed | "
        f"Period: {year}-{month:02d} | "
        f"Execution date: {context['execution_date']}\n"
        f"Failed tasks:\n{errors}"
    )

    logger.error(message)
    
    send_email(
        to=os.getenv('ALERT_EMAIL'),
        subject=subject,
        html_content=message
    )
    # TODO: Send to Slack, email, PagerDuty

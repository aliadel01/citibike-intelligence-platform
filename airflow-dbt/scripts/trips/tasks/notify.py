import logging

logger = logging.getLogger(__name__)


def send_success_notification(**context):
    """Send success notification (email, Slack, etc.)"""
    ti = context['task_instance']
    year = ti.xcom_pull(task_ids='ingest_trips_data', key='year')
    month = ti.xcom_pull(task_ids='ingest_trips_data', key='month')

    message = (
        f"Trips Monthly Ingestion Successful | "
        f"Period: {year}-{month:02d} | "
        f"Execution date: {context['execution_date']}"
    )

    logger.info(message)
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

    message = (
        f"Trips Monthly Ingestion Failed | "
        f"Period: {year}-{month:02d} | "
        f"Execution date: {context['execution_date']}\n"
        f"Failed tasks:\n{errors}"
    )

    logger.error(message)
    # TODO: Send to Slack, email, PagerDuty

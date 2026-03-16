import logging

def send_success_notification(**context):
    """Send success notification (email, Slack, etc.)"""
    year = context['task_instance'].xcom_pull(task_ids='ingest_stations_data', key='year')
    month = context['task_instance'].xcom_pull(task_ids='ingest_stations_data', key='month')
    row_count = context['task_instance'].xcom_pull(task_ids='validate_data', key='row_count')
    
    message = f"""
    ✅ Stations Monthly Ingestion Successful
    
    Period: {year}-{month:02d}
    Rows ingested: {row_count:,}
    Execution date: {context['execution_date']}
    
    All data quality tests passed.
    """
    
    logging.info(message)
    # TODO: Send to Slack, email, etc.


def send_failure_notification(**context):
    """Send failure notification"""
    year = context['task_instance'].xcom_pull(task_ids='ingest_stations_data', key='year')
    month = context['task_instance'].xcom_pull(task_ids='ingest_stations_data', key='month')
    
    message = f"""
    ❌ Stations Monthly Ingestion Failed
    
    Period: {year}-{month:02d}
    Execution date: {context['execution_date']}
    
    Check Airflow logs for details.
    """
    
    logging.error(message)
    # TODO: Send to Slack, email, PagerDuty
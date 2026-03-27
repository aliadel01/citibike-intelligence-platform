"""
Citibike (Monthly) Trips Ingestion DAG

Schedule: None (triggered by stations DAG)
Catchup: True (backfill from 2021-01-01)
Purpose: Download, validate, and process monthly trip data

Data Flow:
1. Ingest CSV from Citibike S3
2. Validate the downloaded file
3. Refresh Snowflake external table
4. Bronze quality checks
5. Run dbt (Silver + Gold)
6. Log ingestion metadata
7. Send alerts
"""

import os
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.utils.trigger_rule import TriggerRule
from cosmos import DbtTaskGroup, ProjectConfig, RenderConfig

from scripts.trips.tasks.ingest import ingest_tripdata
from scripts.trips.tasks.validate import validate_csv_file
from scripts.trips.tasks.notify import send_success_notification, send_failure_notification
from scripts.utils.config import MIN_ROWS_PER_MONTH, DEFAULT_ARGS
from scripts.utils.dbt_config import (
    SNOWFLAKE_CONN_ID,
    profile_config,
    execution_config,
    snowflake_hook_params,
)

# ========================================
# DAG Definition
# ========================================

with DAG(
    dag_id='citibike_monthly_trips',
    default_args=DEFAULT_ARGS,
    description='Monthly ingestion of Citibike trip data from S3 to Snowflake',
    doc_md = __doc__ ,
    schedule=None,  # <-- triggered only after stations are ready
    start_date=datetime(2021, 1, 1),
    end_date=datetime(2021, 1, 3),  # <-- for testing, run only once
    catchup=True,
    max_active_runs=1,
    tags=['citibike', 'batch', 'monthly', 'trips'],
) as dag:

    # Task 1: Start
    start = EmptyOperator(task_id='start')

    # Task 2: Download data
    ingest_trips_task = PythonOperator(
        task_id='ingest_trips_data',
        python_callable=ingest_tripdata,
    )

    # Task 3: Validate data
    validate_data_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_csv_file,
    )

    # Task 4: Refresh external table
    refresh_external_table = SQLExecuteQueryOperator(
        task_id='refresh_external_table',
        conn_id=SNOWFLAKE_CONN_ID,
        sql="scripts/trips/sql/refresh_external_table.sql",
        hook_params=snowflake_hook_params,
    )

    # Task 5: Data quality checks on Bronze (fails on bad data)
    bronze_quality_check = SQLExecuteQueryOperator(
        task_id='bronze_quality_check',
        conn_id=SNOWFLAKE_CONN_ID,
        sql="scripts/trips/sql/bronze_quality.sql",
        hook_params=snowflake_hook_params,
        params={'min_rows': MIN_ROWS_PER_MONTH},
    )

    # Task 6: Run dbt
    dbt_run_trips = DbtTaskGroup(
        group_id='dbt_run_trips',
        project_config=ProjectConfig(os.getenv("PATH_TO_DBT_PROJECT")),
        profile_config=profile_config,
        execution_config=execution_config,
        render_config=RenderConfig(
            select=["tag:trips"],
            exclude=["tag:stations"],
        ),
        default_args={"retries": 0},
    )

    # Task 7: Log successful ingestion
    log_ingestion = SQLExecuteQueryOperator(
        task_id='log_ingestion',
        conn_id=SNOWFLAKE_CONN_ID,
        sql="scripts/trips/sql/log_ingestion.sql",
        hook_params=snowflake_hook_params,
    )

    # Task 8: Success notification
    success_notification = PythonOperator(
        task_id='success_notification',
        python_callable=send_success_notification,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    # Task 9: Failure notification
    failure_notification = PythonOperator(
        task_id='failure_notification',
        python_callable=send_failure_notification,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    # Task 10: End
    end = EmptyOperator(
        task_id='end',
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # ========================================
    # Task Dependencies
    # ========================================

    start >> ingest_trips_task >> validate_data_task >> refresh_external_table >> bronze_quality_check
    bronze_quality_check >> dbt_run_trips >> log_ingestion >> success_notification

    # Cleanup runs regardless
    [success_notification, failure_notification] >> end

    # Failure path
    [ingest_trips_task, validate_data_task, refresh_external_table, bronze_quality_check, dbt_run_trips] >> failure_notification
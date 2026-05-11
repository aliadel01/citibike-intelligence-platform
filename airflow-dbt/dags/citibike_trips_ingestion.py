"""
    Citibike (Monthly) Trips Ingestion DAG

    Schedule: None (triggered by stations DAG)
    Catchup: True (backfill from 2021-01-01)
    Purpose: Download, validate, and process monthly trip data

    Data Flow:
    1. Ingest trip data from S3 to Azure Blob Storage (temp folder)
    2. Validate the ingested data (file size, columns, row count, data quality)
    3. Move validated data to final Bronze location
    4. Refresh Snowflake external table
    5. Run dbt transformations
    6. Log ingestion and send notifications
"""

import os
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.utils.trigger_rule import TriggerRule
from cosmos import DbtTaskGroup, ProjectConfig, RenderConfig

from scripts.trips.tasks.ingest import ingest_tripdata_to_temp
from scripts.trips.tasks.validate import validate_tripdata_in_temp
from scripts.trips.tasks.move import move_trips_to_bronze
from scripts.trips.tasks.notify import (
    send_success_notification,
    send_failure_notification,
)
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
    dag_id="citibike_monthly_trips",
    default_args=DEFAULT_ARGS,
    description="Monthly ingestion of Citibike trip data from S3 to Snowflake",
    doc_md=__doc__,
    schedule=None,  # <-- triggered only after stations are ready
    start_date=datetime(2021, 1, 1),
    catchup=True,
    max_active_runs=1,
    tags=["citibike", "batch", "monthly", "trips"],
) as dag:

    # Task 1: Start
    start = EmptyOperator(task_id="start")

    # Task 2: Download data
    ingest_trips_task = PythonOperator(
        task_id="ingest_trips_data",
        python_callable=ingest_tripdata_to_temp,
    )

    # Task 3: Validate data
    validate_data_task = PythonOperator(
        task_id="validate_data",
        python_callable=validate_tripdata_in_temp,
    )
    
    # Task 4: Move validated file to final Bronze location
    move_to_bronze_task = PythonOperator(
        task_id="move_to_bronze",
        python_callable=move_trips_to_bronze,
    )

    # Task 5: Refresh external table
    refresh_external_table = SQLExecuteQueryOperator(
        task_id="refresh_external_table",
        conn_id=SNOWFLAKE_CONN_ID,
        sql="""
        ALTER EXTERNAL TABLE CITIBIKE_DB.EXTERNAL.V_TRIPS_RAW REFRESH;

        SELECT COUNT(*) AS row_count 
        FROM CITIBIKE_DB.EXTERNAL.V_TRIPS_RAW
        WHERE METADATA$FILENAME LIKE '%%{{ ti.xcom_pull(task_ids="ingest_trips_data", key="year") }}{{ "%02d" | format(ti.xcom_pull(task_ids="ingest_trips_data", key="month") | int) }}%%';
        """,
        hook_params=snowflake_hook_params,
    )

    # Task 6: Run dbt
    dbt_run_trips = DbtTaskGroup(
        group_id="dbt_run_trips",
        project_config=ProjectConfig(os.getenv("PATH_TO_DBT_PROJECT")),
        profile_config=profile_config,
        execution_config=execution_config,
        render_config=RenderConfig(
            select=["tag:trips"],
            exclude=["tag:stations"],
        ),
        default_args={"retries": 0},
    )

    # Task 7: Success notification
    success_notification = PythonOperator(
        task_id="success_notification",
        python_callable=send_success_notification,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    # Task 8: Failure notification
    failure_notification = PythonOperator(
        task_id="failure_notification",
        python_callable=send_failure_notification,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    # Task 9: End
    end = EmptyOperator(
        task_id="end",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # ========================================
    # Task Dependencies
    # ========================================

    (
    start
    >> ingest_trips_task
    >> validate_data_task
    >> move_to_bronze_task
    >> refresh_external_table
    >> dbt_run_trips 
    >> success_notification
    )
    
    # Cleanup runs regardless
    [success_notification, failure_notification] >> end

    # Failure path
    [
        ingest_trips_task,
        validate_data_task,
        move_to_bronze_task,
        refresh_external_table,
        dbt_run_trips,
    ] >> failure_notification

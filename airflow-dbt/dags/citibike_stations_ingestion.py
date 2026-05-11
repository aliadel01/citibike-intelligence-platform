"""
Citibike Stations (Monthly) Ingestion DAG

Schedule: Monthly (1st of each month at 2 AM)
Purpose: Download, validate, and process monthly station data

Data Flow:
- Fetch GBFS station metadata (station_information.json)
- Validate JSON structure and required fields
- Store it to ADLS bronze as a dated snapshot
- Refresh Snowflake external table metadata
- Run dbt to update Silver + Gold station dimension
- Run dbt tests
- Data quality checks
- Send alerts
"""

import os
from datetime import datetime

from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.utils.trigger_rule import TriggerRule
from cosmos import DbtTaskGroup, ProjectConfig, RenderConfig, TestBehavior

from scripts.utils.config import DEFAULT_ARGS
from scripts.utils.dbt_config import (
    SNOWFLAKE_CONN_ID,
    profile_config,
    execution_config,
    snowflake_hook_params,
)
from scripts.stations.tasks.ingest import ingest_stations_data
from scripts.stations.tasks.validate import validate_json_file
from scripts.stations.tasks.move import move_to_bronze_and_cleanup
from scripts.stations.tasks.notify import (
    send_success_notification,
    send_failure_notification,
)

# ========================================
# DAG Definition
# ========================================

with DAG(
    dag_id="citibike_monthly_stations_ingestion",
    description="Monthly ingestion of Citibike station metadata (GBFS) into ADLS + Snowflake + dbt",
    doc_md=__doc__,
    default_args=DEFAULT_ARGS,
    start_date=datetime(2021, 1, 1),
    end_date=datetime(2022, 1, 5),  
    schedule="0 2 1 * *",  # 2 AM on 1st of each month
    catchup=True,
    max_active_runs=1,
    tags=["citibike", "stations", "monthly"],
) as dag:

    # Task 1
    start = EmptyOperator(task_id="start")

    # Task 2
    download_task = PythonOperator(
        task_id="ingest_stations_data",
        python_callable=ingest_stations_data,
    )

    # Task 2.5: Validate data
    validate_task = PythonOperator(
        task_id="validate_json_file",
        python_callable=validate_json_file,
    )

    # Task 2.6: Move validated data to bronze
    move_task = PythonOperator(
        task_id="move_to_bronze",
        python_callable=move_to_bronze_and_cleanup,
    )

    # Task 3: Refresh external table
    refresh_external_table = SQLExecuteQueryOperator(
        task_id="refresh_external_table",
        conn_id=SNOWFLAKE_CONN_ID,
        sql="""
        ALTER EXTERNAL TABLE CITIBIKE_DB.EXTERNAL.v_station_metadata REFRESH;

        SELECT COUNT(*) AS row_count 
        FROM CITIBIKE_DB.EXTERNAL.v_station_metadata
        WHERE METADATA$FILENAME LIKE '%%{{ ti.xcom_pull(task_ids="ingest_stations_data", key="year") }}{{ "%02d" | format(ti.xcom_pull(task_ids="ingest_stations_data", key="month") | int) }}%%';
        """,
        hook_params=snowflake_hook_params,
    )

    # Task 4: Run dbt
    dbt_run_stations = DbtTaskGroup(
        group_id="dbt_run_stations",
        project_config=ProjectConfig(os.getenv("PATH_TO_DBT_PROJECT")),
        profile_config=profile_config,
        execution_config=execution_config,
        render_config=RenderConfig(
            select=["tag:stations"],
            exclude=[
                "tag:test_trips",
                "stg_trips",
                "stg_trips+",
                "fact_trips",
                "fact_trips+",
            ],
            test_behavior=TestBehavior.AFTER_EACH,
        ),
        operator_args={
            "indirect_selection": "cautious",
        },
        default_args={"retries": 0},
    )

    # Task 5: Success notification
    success_notification = PythonOperator(
        task_id="success_notification",
        python_callable=send_success_notification,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    # Task 6: Failure notification
    failure_notification = PythonOperator(
        task_id="failure_notification",
        python_callable=send_failure_notification,
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    # Task 7: Trigger trips DAG (if stations ingestion is successful)
    trigger_trips = TriggerDagRunOperator(
        task_id="trigger_trips_dag",
        trigger_dag_id="citibike_monthly_trips",
        execution_date="{{ execution_date }}",
        wait_for_completion=False,
    )

    # Task 8: End
    end = EmptyOperator(task_id="end")

    # ========================================
    # Task Dependencies
    # ========================================
    (
        start
        >> download_task
        >> validate_task
        >> move_task
        >> refresh_external_table
        >> dbt_run_stations
    )
    dbt_run_stations >> [success_notification, trigger_trips] >> end

    # Failure path
    [
        download_task,
        validate_task,
        move_task,
        refresh_external_table,
        dbt_run_stations,
    ] >> failure_notification

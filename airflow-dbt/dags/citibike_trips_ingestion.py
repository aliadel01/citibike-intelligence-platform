"""
Citibike (Monthly) Trips Ingestion DAG

Schedule: Monthly (1st of each month at 2 AM)
Catchup: True (backfill from 2021-01-01)
Purpose: Download, validate, and process monthly trip data

Data Flow:
1. Ingest CSV from Citibike S3
4. Refresh Snowflake external table
5. Run dbt (Silver + Gold)
6. Run dbt tests
7. Data quality checks
8. Send alerts
"""

import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.utils.trigger_rule import TriggerRule
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, RenderConfig
from cosmos.profiles import SnowflakeUserPasswordProfileMapping

# scripts
from scripts.trips.tasks.ingest import ingest_tripdata
from scripts.trips.tasks.notify import send_success_notification, send_failure_notification
from scripts.utils.config import (
    MIN_ROWS_PER_MONTH,
    DEFAULT_ARGS
)
# libraries
from datetime import datetime


# ========================================
# dbt Configuration 
# ========================================

profile_config = ProfileConfig(
    profile_name="dbt_project",
    target_name="dev",
    profile_mapping=SnowflakeUserPasswordProfileMapping(
        conn_id=os.getenv("SNOWFLAKE_CONN_ID", "snowflake_default"),
        profile_args={
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "database": os.getenv("SNOWFLAKE_DATABASE", "CITIBIKE_DB"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA", "EXTERNAL"),
            "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "CITIBIKE_DWH"),
        },
    ),
)

execution_config = ExecutionConfig(
    dbt_executable_path=os.getenv("PATH_TO_DBT_VENV"),  # dbt installed inside container
)


# ========================================
# DAG Definition
# ========================================

with DAG(
    dag_id='citibike_monthly_trips',
    default_args=DEFAULT_ARGS,
    description='Monthly ingestion of Citibike trip data from S3 to Snowflake',
    schedule_interval=None,  # <-- triggered only after stations are ready
    start_date=datetime(2021, 1, 1),  # Start from January 2021
    end_date=datetime(2021, 1, 3),  # <-- for testing, run only once
    catchup=True,  # Backfill historical data
    max_active_runs=1,  # Process one month at a time
    tags=['citibike', 'batch', 'monthly', 'trips'],
) as dag:
    
    # Task 1: Start
    start = EmptyOperator(task_id='start')
    
    # Task 2: Download data
    ingest_trips_task = PythonOperator(
        task_id='ingest_trips_data',
        python_callable=ingest_tripdata,
        provide_context=True,
    )
    
    # Task 3: Refresh external table
    refresh_external_table = SQLExecuteQueryOperator(
        task_id='refresh_external_table',
        conn_id=os.getenv("SNOWFLAKE_CONN_ID", "snowflake_default"),
        sql="scripts/trips/sql/refresh_external_table.sql",
        hook_params={
            'warehouse': 'CITIBIKE_DWH',
            'database': 'CITIBIKE_DB',
            'schema': 'EXTERNAL',
        },
    )
    
    # Task 4: Data quality checks on Bronze
    bronze_quality_check = SQLExecuteQueryOperator(
        task_id='bronze_quality_check',
        conn_id=os.getenv("SNOWFLAKE_CONN_ID", "snowflake_default") ,
        sql="scripts/trips/sql/bronze_quality.sql",
        hook_params={
            'warehouse': 'CITIBIKE_DWH',
            'database': 'CITIBIKE_DB',
            'schema': 'EXTERNAL',
        },
        params={'min_rows': MIN_ROWS_PER_MONTH},
    )

    # Task 5: Run dbt
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
    

    # Task 6: Log successful ingestion
    log_ingestion = SQLExecuteQueryOperator(
        task_id='log_ingestion',
        conn_id=os.getenv("SNOWFLAKE_CONN_ID", "snowflake_default"),
        sql="scripts/trips/sql/log_ingestion.sql",
        hook_params={
            'warehouse': 'CITIBIKE_DWH',
            'database': 'CITIBIKE_DB',
            'schema': 'EXTERNAL',
        },
    )
    
    # Task 7: Success notification
    success_notification = PythonOperator(
        task_id='success_notification',
        python_callable=send_success_notification,
        provide_context=True,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )
    
    # Task 8: Failure notification
    failure_notification = PythonOperator(
        task_id='failure_notification',
        python_callable=send_failure_notification,
        provide_context=True,
        trigger_rule=TriggerRule.ONE_FAILED,
    )
    
    # Task 9: End
    end = EmptyOperator(
        task_id='end',
        trigger_rule=TriggerRule.ALL_DONE,
    )
    
    # ========================================
    # Task Dependencies
    # ========================================
    
    start >> ingest_trips_task >> refresh_external_table >> bronze_quality_check
    bronze_quality_check >> dbt_run_trips >> log_ingestion >> success_notification
    
    # Cleanup runs regardless
    [success_notification, failure_notification] >> end
    
    # Failure path
    [ingest_trips_task, refresh_external_table, bronze_quality_check, dbt_run_trips] >> failure_notification
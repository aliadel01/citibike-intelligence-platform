import os

from cosmos import ProfileConfig, ExecutionConfig
from cosmos.profiles import SnowflakeUserPasswordProfileMapping

SNOWFLAKE_CONN_ID = os.getenv("SNOWFLAKE_CONN_ID", "snowflake_default")

profile_config = ProfileConfig(
    profile_name="dbt_project",
    target_name="dev",
    profile_mapping=SnowflakeUserPasswordProfileMapping(
        conn_id=SNOWFLAKE_CONN_ID,
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
    dbt_executable_path=os.getenv("PATH_TO_DBT_VENV"),
)

snowflake_hook_params = {
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "CITIBIKE_DWH"),
    "database": os.getenv("SNOWFLAKE_DATABASE", "CITIBIKE_DB"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA", "EXTERNAL"),
}

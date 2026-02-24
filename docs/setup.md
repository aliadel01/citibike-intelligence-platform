

# Setup dbt & airflow
Using astro cli, cosmos

## Steps
1. run `astro dev init` in airflow-dbt dir

2. Add to airflow-dbt/requirements.txt 
```
astronomer-cosmos
pandas
snowflake-connector-python
astro-run-dag # This package is needed for the astro run command. It will be removed before a deploy
```

3. Add `dbt-snowflake` to airflow-dbt/dbt-requirements.txt

4. Add to Dockerfile
```
FROM quay.io/astronomer/astro-runtime:11.3.0

# install dbt into a venv to avoid package dependency conflicts
WORKDIR "/usr/local/airflow"
COPY dbt-requirements.txt ./
RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-snowflake && deactivate
```

5. Add to  docker-compose.override.yml
```
services:
  scheduler:
    volumes:
      - ./dbt_project:/usr/local/airflow/dbt_project:rw
      - ./scripts:/usr/local/airflow/scripts:rw
      - ./config:/usr/local/airflow/config:rw
      - ./logs:/usr/local/airflow/logs:rw

  webserver:
    volumes:
      - ./dbt_project:/usr/local/airflow/dbt_project:rw
      - ./scripts:/usr/local/airflow/scripts:rw
      - ./config:/usr/local/airflow/config:rw
      - ./logs:/usr/local/airflow/logs:rw

  triggerer:
    volumes:
      - ./dbt_project:/usr/local/airflow/dbt_project:rw
      - ./scripts:/usr/local/airflow/scripts:rw
      - ./config:/usr/local/airflow/config:rw
      - ./logs:/usr/local/airflow/logs:rw
```

6. `dbt init dbt_project` in airflow-dbt/dbt

7. `astro dev start`

make sure to update the profiles.yml file with the correct credentials for your Snowflake account. You can find an example profiles.yml file in the dbt documentation: https://docs.getdbt.com/reference/profiles.yml
{{
  config(
    materialized='incremental',
    unique_key='trip_id',
    schema='gold',
    cluster_by=['DATE(start_time)', 'start_station_id'],
    tags=['gold', 'fact'],
    contract={'enforced': true},
    on_schema_change='append_new_columns',
    pre_hook=[
      "USE WAREHOUSE CITIBIKE_DWH"
    ]
  )
}}

/*
  Gold Layer: Trip Fact Table
  
  Grain: One row per trip
  Target: CITIBIKE_DB.GOLD.fact_trips
  
  Foreign Keys:
  - start_station_id → dim_station.station_id
  - end_station_id → dim_station.station_id
*/

WITH base_trips AS (
    SELECT * FROM {{ ref('stg_trips') }}
    
    {% if is_incremental() %}
    -- Only process new trips
    WHERE started_at > (
    SELECT COALESCE(MAX(start_time), '1900-01-01')
    FROM {{ this }})
    {% endif %}
)

SELECT
    ride_id::VARCHAR(100) AS trip_id,
    started_at AS start_time,
    ended_at AS stop_time,
    trip_duration_seconds::INTEGER AS trip_duration_seconds,
    start_station_id::VARCHAR(100) AS start_station_id,
    end_station_id::VARCHAR(100) AS end_station_id,
    member_casual,
    rideable_type,
    processed_at::TIMESTAMP_NTZ AS processed_at,
    sourcefile::VARCHAR(500) AS sourcefile
    
FROM base_trips
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
    -- Matches your exact schema
    ride_id::VARCHAR(100) AS trip_id,
    started_at AS start_time,
    ended_at AS stop_time,
    trip_duration_seconds::INTEGER AS trip_duration_seconds,
    start_station_id::VARCHAR(100) AS start_station_id,
    end_station_id::VARCHAR(100) AS end_station_id,
    bike_id::VARCHAR(255) AS bike_id,
    user_type::VARCHAR(50) AS user_type,
    birth_year::INTEGER AS birth_year,
    gender::VARCHAR(10) AS gender,
    processed_at,
    source_file::VARCHAR(500) AS source_file
    
FROM base_trips
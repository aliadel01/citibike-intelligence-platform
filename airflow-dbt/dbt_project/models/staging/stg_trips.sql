{{
  config(
    materialized='incremental',
    unique_key='ride_id',
    schema='silver',
    cluster_by=['started_at::DATE', 'start_station_id'],
    tags=['silver', 'fact', 'trips']
  )
}}

/*
  Staging model for trip facts.
  
  Grain: One row per trip
  Source: External table V_TRIPS_RAW (CSV)
  
  Note: Schema changed in 2021
  - Old schema (2013-2020): Has bike_id, birth_year, gender, usertype
  - New schema (2021+): Has member_casual (usertype in old schema), rideable_type, NO bike_id/birth_year/gender
  but we will only work with (2021+) schema for this project, so we can ignore the old columns

*/

WITH source AS (
    SELECT *, METADATA$FILENAME AS sourcefile  FROM {{ source('external', 'v_trips_raw') }}
    
    {% if is_incremental() %}
    -- Only process new trips
    WHERE started_at > (SELECT MAX(started_at) FROM {{ this }})
    {% endif %}
),

cleaned AS (
    SELECT
        -- Identifiers
        ride_id,
        
        -- Timestamps
        started_at,
        ended_at,
        
        -- Calculate duration
        TIMESTAMPDIFF(SECOND, started_at, ended_at) AS trip_duration_seconds,
        
        -- Station references (ensure VARCHAR)
        start_station_id::VARCHAR(100) AS start_station_id,
        end_station_id::VARCHAR(100) AS end_station_id,
        
        member_casual,
        rideable_type,
        
        -- Metadata
        sourcefile,
        CURRENT_TIMESTAMP()::TIMESTAMP_NTZ AS processed_at
        
    FROM source
)

SELECT * FROM cleaned
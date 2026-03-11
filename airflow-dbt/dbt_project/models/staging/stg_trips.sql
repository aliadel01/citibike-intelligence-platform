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
  - New schema (2021+): Has member_casual, rideable_type, NO bike_id/birth_year/gender
*/

WITH source AS (
    SELECT * FROM {{ source('external', 'v_trips_raw') }}
    
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
        
        -- User info - map new schema to old schema
        -- New schema: member_casual ('member' or 'casual')
        -- Old schema: user_type ('Subscriber' or 'Customer')
        member_casual,
        rideable_type,
        CASE 
            WHEN member_casual = 'member' THEN 'Subscriber'
            WHEN member_casual = 'casual' THEN 'Customer'
            ELSE member_casual  -- Pass through if old data
        END AS user_type,
        
        -- Legacy fields (will be NULL for new data)
        NULL AS bike_id,     -- Not in new schema
        NULL AS birth_year,  -- Removed in 2021 for privacy
        NULL AS gender,      -- Removed in 2021 for privacy
        
        -- Metadata
        source_file,
        CURRENT_TIMESTAMP()::TIMESTAMP_NTZ AS processed_at
        
    FROM source
    WHERE 
        -- Data quality filters
        ride_id IS NOT NULL
        AND started_at IS NOT NULL
        AND ended_at IS NOT NULL
        AND started_at < ended_at
        AND TIMESTAMPDIFF(SECOND, started_at, ended_at) BETWEEN 60 AND 86400  -- 1 min to 24 hours
        AND start_station_id IS NOT NULL
        AND end_station_id IS NOT NULL
)

SELECT * FROM cleaned
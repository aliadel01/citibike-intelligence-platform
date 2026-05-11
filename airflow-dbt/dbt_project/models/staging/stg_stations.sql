{{
  config(
    materialized='table',
    schema='silver',
    tags=['silver', 'dimension', 'stations']
  )
}}

WITH base_data AS (
    SELECT
        value:data:stations AS stations_array,
        METADATA$FILENAME AS meta_source_file
    FROM {{ source('external','v_station_metadata') }}
),

flattened_stations AS (
    SELECT
        s.value AS station_record,
        b.meta_source_file
    FROM base_data AS b,
    LATERAL FLATTEN(input => b.stations_array) AS s
)

SELECT
    station_record:station_id::VARCHAR AS station_id,
    station_record:name::VARCHAR AS name,
    station_record:lat::FLOAT AS lat,
    station_record:lon::FLOAT AS lon,
    station_record:capacity::INTEGER AS capacity,
    station_record:short_name::VARCHAR AS short_name,
    station_record:rental_methods::VARIANT AS rental_methods_array,
    station_record:region_id::VARCHAR AS region_id,
    
    meta_source_file AS sourcefile,
    CURRENT_TIMESTAMP()::timestamp_ntz AS processed_at
FROM flattened_stations
where meta_source_file like '%%'
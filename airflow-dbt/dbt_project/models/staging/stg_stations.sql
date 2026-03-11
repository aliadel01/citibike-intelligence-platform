{{
  config(
    materialized='table',
    schema='silver',
    tags=['silver', 'dimension', 'stations']
  )
}}

/*
  Staging model for station dimension.
  
  Grain: One row per station (latest version)
  Source: External table V_STATION_METADATA (GBFS JSON)
*/

WITH raw AS (

SELECT
    value:data:stations AS stations,
    source_file
    
    
FROM {{ source('external','v_station_metadata') }}

),

flattened AS (

SELECT
    station.value,
    source_file
FROM raw,
LATERAL FLATTEN(input => stations) station

)

SELECT
    value:station_id::VARCHAR AS station_id,
    value:name::VARCHAR AS station_name,
    value:lat::FLOAT AS lat,
    value:lon::FLOAT AS lon,
    value:capacity::INTEGER AS capacity,
    value:station_type::VARCHAR AS station_type,
    value:has_kiosk::BOOLEAN AS has_kiosk,
    value:eightd_has_key_dispenser::BOOLEAN AS eightd_has_key_dispenser,
    value:electric_bike_surcharge_waiver::BOOLEAN AS electric_bike_surcharge_waiver,
    value:short_name::VARCHAR AS short_name,
    value:rental_methods::VARIANT AS rental_methods_array,
    value:external_id::VARCHAR AS external_id,
    value:region_id::VARCHAR AS region_id,
    source_file,
    CURRENT_TIMESTAMP()::timestamp_ntz AS processed_at
FROM flattened
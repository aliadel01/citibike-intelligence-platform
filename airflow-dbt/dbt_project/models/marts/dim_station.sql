{{
  config(
    materialized='table',
    schema='gold',
    cluster_by=['station_id'],
    tags=['gold', 'dimension'],
    contract={'enforced': true},
    on_schema_change='append_new_columns',
    pre_hook=[
      "USE WAREHOUSE CITIBIKE_DWH"
    ]
  )
}}

/*
  Gold Layer: Station Dimension Table
  
  Grain: One row per station (current state)
  Target: CITIBIKE_DB.GOLD.dim_station
*/

with station_data as (

SELECT
    -- Matches your exact schema
    station_id,
    region_id,
    name,
    capacity,
    lat,
    lon,
    station_type,
    has_kiosk,
    eightd_has_key_dispenser,
    short_name,
    rental_methods_array,
    external_id,
    electric_bike_surcharge_waiver,
    source_file,
    processed_at
    
FROM {{ ref('stg_stations') }}

)

SELECT  * from station_data
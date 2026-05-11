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
    short_name,
    rental_methods_array,
    sourcefile,
    processed_at
    
FROM {{ ref('stg_stations') }}

)

SELECT  * from station_data
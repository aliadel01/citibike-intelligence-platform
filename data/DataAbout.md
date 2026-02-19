# Citibike Trip Data Documentation

## Overview

This project uses **Citibike System Data**, the official trip history data from New York City's bike-sharing system operated by Lyft. This dataset provides comprehensive information about every bike trip taken in the Citibike network, making it ideal for analyzing urban mobility patterns, user behavior, and transportation trends.

## Dataset Information

### Source
- **Provider**: Citibike (operated by Lyft)
- **Official Website**: [https://citibikenyc.com/system-data](https://citibikenyc.com/system-data)
- **Data Portal**: [https://s3.amazonaws.com/tripdata/index.html](https://s3.amazonaws.com/tripdata/index.html)
- **Documentation**: [https://citibikenyc.com/system-data](https://citibikenyc.com/system-data)
- **License**: [Citibike Data License Agreement](https://www.citibikenyc.com/data-sharing-policy)

### Update Frequency
- **Historical Coverage**: June 2013 - Present
- **Update Schedule**: Monthly (released ~2 weeks after month end)
- **Data Freshness**: Near real-time trip completion
- **Current Status**: Actively maintained ✅

---

## Dataset Characteristics

### Format
- **File Type**: CSV (Comma-Separated Values) and ZIP archives
- **Compression**: ZIP (extract to CSV)
- **Structure**: 1 row per trip
- **File Naming**: `YYYYMM-citibike-tripdata.csv.zip`
  - Example: `202401-citibike-tripdata.csv.zip` (January 2024)
- **Size per Month**: 
  - Compressed: ~10-30 MB
  - Uncompressed: ~50-200 MB
  - Rows: 1-3 million trips per month
- **Encoding**: UTF-8

### Geographic Coverage
- **Primary Service Area**: New York City
  - Manhattan
  - Brooklyn
  - Queens
  - Bronx
  - Jersey City, NJ (since 2015)
  - Hoboken, NJ (since 2015)
- **Stations**: 1,500+ bike stations
- **Service Zone**: ~60 square miles

### Temporal Coverage
- **Start Date**: June 1, 2013
- **End Date**: Ongoing (present day)
- **Granularity**: Individual trip level (second-level precision)
- **Total Historical Trips**: 100M+ rides
- **Seasonal Patterns**: Strong seasonal variation (peak in summer)

---

## Data Schema & Variables

The Citibike dataset schema has evolved over time. Here are the current and historical schemas:

### Current Schema (2021 - Present)

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `ride_id` | STRING | Unique identifier for each trip | `A1B2C3D4E5F6G7H8` |
| `rideable_type` | STRING | Type of bike used | `classic_bike`, `electric_bike`, `docked_bike` |
| `started_at` | TIMESTAMP | Start date and time | `2024-01-15 08:23:45` |
| `ended_at` | TIMESTAMP | End date and time | `2024-01-15 08:38:12` |
| `start_station_name` | STRING | Name of start station | `Broadway & W 58 St` |
| `start_station_id` | STRING | ID of start station | `6926.01` |
| `end_station_name` | STRING | Name of end station | `Central Park S & 6 Ave` |
| `end_station_id` | STRING | ID of end station | `6023.05` |
| `start_lat` | FLOAT | Latitude of start location | `40.7664` |
| `start_lng` | FLOAT | Longitude of start location | `-73.9818` |
| `end_lat` | FLOAT | Latitude of end location | `40.7660` |
| `end_lng` | FLOAT | Longitude of end location | `-73.9764` |
| `member_casual` | STRING | User type | `member`, `casual` |

**Total Columns**: 13

### Legacy Schema (2013 - 2020)

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `tripduration` | INTEGER | Trip duration in seconds | `892` |
| `starttime` | TIMESTAMP | Start date and time | `2020-01-01 00:01:23` |
| `stoptime` | TIMESTAMP | Stop date and time | `2020-01-01 00:16:15` |
| `start station id` | INTEGER | Start station ID | `3183` |
| `start station name` | STRING | Start station name | `Exchange Place` |
| `start station latitude` | FLOAT | Start latitude | `40.7163` |
| `start station longitude` | FLOAT | Start longitude | `-74.0334` |
| `end station id` | INTEGER | End station ID | `3638` |
| `end station name` | STRING | End station name | `Washington St & Gansevoort St` |
| `end station latitude` | FLOAT | End latitude | `40.7394` |
| `end station longitude` | FLOAT | End longitude | `-74.0081` |
| `bikeid` | INTEGER | Unique bike identifier | `35305` |
| `usertype` | STRING | User type | `Subscriber`, `Customer` |
| `birth year` | INTEGER | User birth year (if available) | `1988` |
| `gender` | INTEGER | User gender (0=unknown, 1=male, 2=female) | `1` |

**Total Columns**: 15

**Note**: Birth year and gender fields were removed in 2021 for privacy compliance.

---

## Data Categories & Metrics

### 1. **Trip Information** (Core Metrics)

| Metric | Description | Calculation |
|--------|-------------|-------------|
| **Trip Duration** | Length of ride in seconds | `ended_at - started_at` |
| **Trip Distance** | Approximate straight-line distance | Haversine formula on lat/lng |
| **Trip Speed** | Average speed | `distance / duration` |
| **Trip Count** | Total number of trips | `COUNT(ride_id)` |

**Use Cases**:
- Identify short vs long trips
- Calculate average trip characteristics
- Detect anomalies (very long/short trips)

### 2. **Station Metrics**

| Metric | Description |
|--------|-------------|
| **Station Popularity** | Number of trips starting/ending at station |
| **Net Flow** | Trips starting - trips ending (rebalancing need) |
| **Peak Hours** | Busiest times at each station |
| **Station Utilization** | Usage rate compared to capacity |

**Use Cases**:
- Station capacity planning
- Bike rebalancing optimization
- Infrastructure investment decisions

### 3. **User Behavior**

| Metric | Description |
|--------|-------------|
| **Member vs Casual** | Subscriber percentage |
| **Ride Frequency** | Trips per user (if trackable) |
| **Typical Routes** | Most common station pairs |
| **Usage Patterns** | Commute vs leisure identification |

**User Type Definitions**:
- **Member** (formerly Subscriber): Annual or monthly pass holders
- **Casual** (formerly Customer): Single-ride or day-pass users

**Behavioral Patterns**:
- Members: Shorter trips, weekday peaks (commuters)
- Casual: Longer trips, weekend peaks (tourists/leisure)

### 4. **Temporal Patterns**

| Dimension | Analysis |
|-----------|----------|
| **Hour of Day** | Morning/evening rush hours |
| **Day of Week** | Weekday vs weekend patterns |
| **Month** | Seasonal trends |
| **Year** | Growth over time |
| **Holidays** | Special event impacts |

**Seasonal Insights**:
- Peak: June - September (summer)
- Low: December - February (winter)
- Weather dependency: Strong correlation with temperature

### 5. **Geographic Patterns**

| Metric | Description |
|--------|-------------|
| **Borough Distribution** | Trips by NYC borough |
| **Neighborhood Clusters** | High-activity zones |
| **Route Density** | Popular corridors |
| **Expansion Areas** | New station coverage |

### 6. **Bike Type Performance** (2021+)

| Type | Characteristics |
|------|-----------------|
| **Classic Bike** | Traditional pedal bikes |
| **Electric Bike** | Pedal-assist e-bikes (faster, easier) |
| **Docked Bike** | Must return to station |

**Analysis**:
- E-bike adoption rate
- Trip duration by bike type
- Preference patterns

---

## Data Quality Notes

### Strengths
✅ **Official Source**: Directly from Citibike operator  
✅ **Complete Coverage**: Every trip recorded  
✅ **High Accuracy**: GPS-tracked start/end points  
✅ **Long History**: 10+ years of data  
✅ **Regular Updates**: Consistent monthly releases  
✅ **Well-Documented**: Clear data dictionary  

### Known Issues & Limitations

⚠️ **Schema Changes**:
- 2021: Removed birth year and gender (privacy)
- 2021: Changed column names (e.g., `tripduration` → calculated from timestamps)
- Requires data harmonization for historical analysis

⚠️ **Missing Data**:
- Some trips have NULL station IDs/names (test rides, maintenance)
- Electric bike data only available from 2020+
- Early years (2013-2014) may have incomplete station info

⚠️ **Data Anomalies**:
- **Very Short Trips**: < 60 seconds (likely false starts, docking errors)
- **Very Long Trips**: > 24 hours (lost bikes, unreturned bikes, system errors)
- **Station ID Changes**: Stations may change IDs over time
- **Coordinate Drift**: Slight GPS variations for same station

⚠️ **Outliers**:
```sql
-- Recommended filters for clean analysis:
WHERE 
  trip_duration BETWEEN 60 AND 86400  -- 1 min to 24 hours
  AND start_station_id IS NOT NULL
  AND end_station_id IS NOT NULL
```

⚠️ **Temporal Gaps**:
- COVID-19 impact: Significant drop in March-May 2020
- System outages: Occasional days with reduced data
- Hurricane/weather events: Service suspensions

⚠️ **Privacy Considerations**:
- No personally identifiable information (PII)
- User demographics removed in 2021
- Ride IDs are anonymized

---

## Sample Data Records

### Current Format (2024)
```csv
ride_id,rideable_type,started_at,ended_at,start_station_name,start_station_id,end_station_name,end_station_id,start_lat,start_lng,end_lat,end_lng,member_casual
A1B2C3D4E5F6G7H8,classic_bike,2024-01-15 08:23:45,2024-01-15 08:38:12,Broadway & W 58 St,6926.01,Central Park S & 6 Ave,6023.05,40.7664,-73.9818,40.7660,-73.9764,member
X9Y8Z7W6V5U4T3S2,electric_bike,2024-01-15 14:05:22,2024-01-15 14:22:11,Pershing Square North,5557.03,E 47 St & Park Ave,6342.08,40.7519,-73.9777,40.7564,-73.9734,casual
```

### Legacy Format (2019)
```csv
tripduration,starttime,stoptime,start station id,start station name,start station latitude,start station longitude,end station id,end station name,end station latitude,end station longitude,bikeid,usertype,birth year,gender
892,2019-07-01 00:01:23,2019-07-01 00:16:15,3183,Exchange Place,40.7163,-74.0334,3638,Washington St & Gansevoort St,40.7394,-74.0081,35305,Subscriber,1988,1
1456,2019-07-01 00:02:45,2019-07-01 00:27:01,519,Pershing Square North,40.7519,-73.9777,497,E 17 St & Broadway,40.7369,-73.9905,28712,Customer,,0
```

---

## Access Information

### Download Options

#### **Option 1: Direct Download (Individual Months)**
```bash
# Pattern: https://s3.amazonaws.com/tripdata/YYYYMM-citibike-tripdata.csv.zip

# Example: January 2024
wget https://s3.amazonaws.com/tripdata/202401-citibike-tripdata.csv.zip

# Extract
unzip 202401-citibike-tripdata.csv.zip
```

#### **Option 2: Bulk Download (Multiple Months)**
```bash
# Download last 12 months
for month in {01..12}; do
  wget https://s3.amazonaws.com/tripdata/2024${month}-citibike-tripdata.csv.zip
done
```

#### **Option 3: Python Script**
```python
import requests
from datetime import datetime, timedelta

def download_citibike_data(year, month):
    url = f"https://s3.amazonaws.com/tripdata/{year}{month:02d}-citibike-tripdata.csv.zip"
    response = requests.get(url)
    
    if response.status_code == 200:
        filename = f"{year}{month:02d}-citibike-tripdata.csv.zip"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Failed: {year}-{month:02d}")

# Download 2023 data
for month in range(1, 13):
    download_citibike_data(2023, month)
```

#### **Option 4: AWS CLI (S3 Bucket)**
```bash
# List all available files
aws s3 ls s3://tripdata/ --no-sign-request

# Download specific file
aws s3 cp s3://tripdata/202401-citibike-tripdata.csv.zip . --no-sign-request

# Download all 2023 files
aws s3 sync s3://tripdata/ . --exclude "*" --include "2023*" --no-sign-request
```

### File Index URL
Browse all available files: [https://s3.amazonaws.com/tripdata/index.html](https://s3.amazonaws.com/tripdata/index.html)

---

## Supplementary Datasets

### 1. **Station Information**
- **Source**: [Citibike Station Feed (GBFS)](https://gbfs.citibikenyc.com/gbfs/gbfs.json)
- **Format**: JSON (real-time API)
- **Data**: Station locations, capacity, bike availability
- **Update**: Real-time (every 10 seconds)

**Example Usage**:
```bash
# Get station information
curl https://gbfs.citibikenyc.com/gbfs/en/station_information.json

# Get station status (real-time)
curl https://gbfs.citibikenyc.com/gbfs/en/station_status.json
```

### 2. **Weather Data** (for correlation analysis)
- **Source**: [NOAA NYC Weather](https://www.weather.gov/okx/)
- **Source**: [OpenWeather API](https://openweathermap.org/api)
- **Metrics**: Temperature, precipitation, wind speed
- **Use**: Analyze weather impact on ridership

### 3. **NYC Open Data**
- **Subway Ridership**: Compare with MTA data
- **Events Calendar**: Correlate with special events
- **Demographics**: Neighborhood characteristics

---

## Data Processing Applied

### In This Project

Our pipeline applies the following transformations:

#### 1. **Schema Harmonization**
- Standardize column names across historical periods
- Convert legacy `tripduration` to calculated duration
- Map `usertype` → `member_casual`
- Handle NULL values in station fields

#### 2. **Data Cleaning**
```sql
-- Remove outliers
WHERE 
  trip_duration_seconds BETWEEN 60 AND 86400
  AND start_station_id IS NOT NULL
  AND end_station_id IS NOT NULL
  AND start_lat BETWEEN 40.5 AND 41.0
  AND start_lng BETWEEN -74.5 AND -73.5
```

#### 3. **Feature Engineering**
- **Trip Duration**: Calculate from timestamps (minutes, hours)
- **Trip Distance**: Haversine formula on coordinates
- **Trip Speed**: Distance / duration
- **Time Features**: Hour, day of week, month, season, is_weekend
- **Station Metrics**: Net flow, popularity rank
- **Route ID**: Concatenate start/end stations for common routes

#### 4. **Aggregations**
- Daily/weekly/monthly ride counts
- Station-level summaries
- User type distributions
- Hourly patterns

#### 5. **Data Warehouse Optimization**
- **Partition**: By `started_at` (date)
- **Cluster**: By `start_station_id`, `member_casual`
- **Indexing**: Station IDs for fast lookups

---

## Key Relationships & Schema

### Entity-Relationship Model

```
Trip (Fact Table)
├── ride_id (PK)
├── started_at (partition key)
├── start_station_id (FK → Station)
├── end_station_id (FK → Station)
├── member_casual
├── rideable_type
└── calculated metrics (duration, distance)

Station (Dimension Table)
├── station_id (PK)
├── station_name
├── latitude
├── longitude
├── borough
└── capacity

Date (Dimension Table)
├── date (PK)
├── year, month, day
├── day_of_week
├── is_weekend
├── is_holiday
└── season

Time (Dimension Table)
├── hour (PK)
├── time_of_day (morning, afternoon, evening, night)
└── is_rush_hour
```

### Primary Keys
- **Trip Fact**: `ride_id` (unique per trip)
- **Station Dim**: `station_id` (one station can appear in multiple trips)
- **Date Dim**: `date`
- **Time Dim**: `hour`

---

## Expected Data Volumes

### Monthly Data (2024)
- **Rows**: ~2-3 million trips
- **File Size (CSV)**: ~150-200 MB uncompressed
- **BigQuery Size**: ~50-80 MB (compressed columnar)

### Annual Data
- **Rows**: ~25-35 million trips
- **Storage**: ~2-3 GB

### Full Historical (2013-2024)
- **Rows**: ~150-200 million trips
- **Storage**: ~20-30 GB

### Recommended Project Scope
For DE Zoomcamp project:
- **Option 1**: Last 2 years (2023-2024) → ~50M rows, ~4GB
- **Option 2**: Last 1 year (2024) → ~30M rows, ~2GB
- **Option 3**: Specific months (e.g., summer 2023) → ~10M rows, ~1GB

---

## Use Cases in This Project

### Primary Analyses

1. **Station Performance Dashboard**
   - Most popular stations
   - Underutilized stations
   - Rebalancing needs

2. **User Behavior Analysis**
   - Member vs casual patterns
   - Trip duration distributions
   - Peak usage times

3. **Temporal Trends**
   - Seasonal ridership patterns
   - Weekday vs weekend differences
   - Hourly demand curves

4. **Geographic Insights**
   - Popular routes
   - Borough-level comparisons
   - Expansion opportunities

5. **Operational Metrics**
   - System growth over time
   - Bike type preferences
   - Average trip characteristics

### Machine Learning Applications

1. **Demand Forecasting**
   - Predict trips per hour/station
   - Seasonal demand modeling

2. **Trip Duration Prediction**
   - Estimate trip time based on route
   - User type classification

3. **Station Clustering**
   - Group stations by usage patterns
   - Identify commuter vs tourist hubs

4. **Anomaly Detection**
   - Identify unusual trip patterns
   - Detect system issues

---

## Related Resources

### Official Citibike Resources
- [System Map](https://citibikenyc.com/system-data)
- [Pricing](https://citibikenyc.com/pricing)
- [How It Works](https://citibikenyc.com/how-it-works)
- [Expansion Plans](https://citibikenyc.com/blog)

### Documentation & APIs
- [GBFS (General Bikeshare Feed Specification)](https://gbfs.citibikenyc.com/gbfs/gbfs.json)
- [Real-Time Station Data API](https://gbfs.citibikenyc.com/gbfs/en/station_status.json)

### Analysis Examples
- [Citibike Data Analysis (Kaggle)](https://www.kaggle.com/datasets/citibikenyc/citibike-trip-data)
- [NYC Open Data Portal](https://opendata.cityofnewyork.us/)
- [Todd Schneider's Analysis](http://toddwschneider.com/posts/a-tale-of-twenty-two-million-citi-bikes-analyzing-the-nyc-bike-share-system/)

### Academic Research
- Urban mobility patterns
- Bike-sharing system optimization
- Transportation equity studies

---

## Citation & Attribution

### Required Citation

When using this dataset, please cite:

```
Citibike System Data
Provided by Lyft Bikes and Scooters, LLC
Available at: https://citibikenyc.com/system-data
Accessed: [Your Access Date]
```

### Data License

**License**: [Citibike Data License Agreement](https://citibikenyc.com/data-sharing-policy)

**Key Terms**:
- ✅ Free to use for analysis and visualization
- ✅ Can be used for commercial and non-commercial purposes
- ✅ Must provide attribution
- ⚠️ Data provided "as-is" without warranty
- ⚠️ Must comply with applicable privacy laws

---

## Data Quality Checks

### Validation Rules

```sql
-- Check 1: Valid timestamps
SELECT COUNT(*) 
FROM trips 
WHERE started_at >= ended_at;  -- Should be 0

-- Check 2: Reasonable durations
SELECT 
  COUNT(*) as total_trips,
  COUNTIF(trip_duration < 60) as too_short,
  COUNTIF(trip_duration > 86400) as too_long
FROM trips;

-- Check 3: Valid coordinates (NYC area)
SELECT COUNT(*)
FROM trips
WHERE 
  start_lat NOT BETWEEN 40.5 AND 41.0
  OR start_lng NOT BETWEEN -74.5 AND -73.5;

-- Check 4: NULL station information
SELECT 
  COUNTIF(start_station_id IS NULL) as null_start,
  COUNTIF(end_station_id IS NULL) as null_end
FROM trips;
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-19 | Initial dataset selection for DE Zoomcamp Citibike project |

---

**Last Updated**: February 19, 2026  
**Dataset Status**: Actively maintained ✅  
**Project Maintainer**: aliadel01  
**Selected Scope**: 2023-2024 (24 months of data)
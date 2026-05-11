
# Citibike Technical Documentation
## Data Engineering Phase

### Terraform
Using IaC to create the following resources:
#### 🔵 Azure
- Resource Group
- ADLS Gen2 Storage Account
- Container (bronze)
#### ❄️ Snowflake
- Warehouse (CITIBIKE_DWH)
- Database (CITIBIKE_DB)
- Schemas (EXTERNAL, SILVER, GOLD)
- 2 File Formats (CSV, JSON)
- An External Stage (BRONZE_STAGE)
- Storage Integration

### Data Sources
1. **Batch** Processed Data
- Trip Data
- Station Metadata
2. **Real-Time** Data
- Station Status (GBFS API)
3. External Data
- **Weather** Data
- Calendar / Events

### Airflow
Two DAGs:
- citibike_monthly_stations_ingestion
![alt text](images/citibike_monthly_stations_ingestion.png)    
- citibike_trips_ingestion
![alt text](images/citibike_trips_ingestion.png)

## Analytics Engineering Phase
Using dbt
### Data Modeling & Warehouse
![Data Model](images/schema.jpg)
- Trips Data -> fact_trips
- Station Metadata -> dim_station
### Data Quality
Stage-gate approach: external → validate → staging → validate → marts

## Data Analytics Phase
### Power BI Dashboards
### Reverse ETL for 
## Machine Learning Phase
# Citibike Analytics Pipeline

> ⚠️ Work in Progress - This project is under active development and not yet complete.

A real-time + historical analytics system that helps Citibike operations team make data-driven decisions.



## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  DELIVERABLE COMPONENTS                                         │
└─────────────────────────────────────────────────────────────────┘

1. Real-Time Dashboard (Grafana)
   └─ Shows live + historical bike usage

2. Automated Data Pipeline (Airflow + Kafka)
   └─ Ingests batch + stream data automatically

3. Data Warehouse (Snowflake)
   └─ Combined historical + real-time data

4. Infrastructure as Code (Terraform)
   └─ Entire system reproducible in 1 command

```
### Project Architecture Diagram:
![Architecture Diagram](docs/images/architecture.png)

## Business Problems Solved


## Data Sources

- **Source**: [Citibike System Data](https://citibikenyc.com/system-data)
- **Scope**: 2013-2024 (24 months)
- **Size**: ~50M trips, ~4GB
- **Format**: CSV

## Repository Structure
```
citibike-analytics-pipeline/ 
├── airflow-dbt/ 
├── terraform/ 
├── dashboard/
└── README.md
```

## Dashboard Overview
### Tab 1: Real-Time Operations 

### Tab 2: Historical Analytics 📈


## Setup



License

MIT License - see LICENSE
Data Attribution

Citibike System Data provided by Lyft Bikes and Scooters, LLC.
Available at: https://citibikenyc.com/system-data
Author

GitHub: https://github.com/aliadel
LinkedIn: https://www.linkedin.com/in/aliadel01/

Built with ❤️ by Ali Adel
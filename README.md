# Citibike Analytics Pipeline

> ⚠️ Work in Progress - This project is under active development and not yet complete.

End-to-end data pipeline for analyzing NYC Citibike trip data with automated ingestion, transformation, and visualization.

**🔗 [Live Dashboard](your-dashboard-link-here)** | **📊 [Data Documentation](docs/DataAbout.md)**

![Dashboard Preview](docs/dashboard_screenshots/dashboard.png)

---

## Problem Description

This pipeline processes millions of Citibike trips to answer key questions:
- Which stations need more bikes?
- How do members vs casual riders behave differently?
- What are peak usage times for bike rebalancing?
- How has ridership grown over time?

Enables data-driven decisions for urban mobility planning and operations optimization.

---

## Architecture

---

## Tech Stack

---

## Dataset

- **Source**: [Citibike System Data](https://citibikenyc.com/system-data)
- **Scope**: 2023-2024 (24 months)
- **Size**: ~50M trips, ~4GB
- **Format**: CSV (monthly files)

See [DataAbout.md](docs/DataAbout.md) for full documentation.

---

## Project Structure
```
citibike-analytics-pipeline/ 
├── airflow/ 
│ └── dags/ 
│ ├── citibike_monthly_pipeline.py 
│ └── utils/ 
├── dbt/citibike_pipeline/ 
│ └── models/ 
│ ├── staging/ 
│ ├── intermediate/ 
│ └── marts/ 
├── terraform/ 
│ ├── main.tf 
│ ├── variables.tf 
│ └── outputs.tf 
├── notebooks/ 
├── docs/ 
└── README.md

```

---

## Setup



License

MIT License - see LICENSE
Data Attribution

Citibike System Data provided by Lyft Bikes and Scooters, LLC.
Available at: https://citibikenyc.com/system-data
Author

GitHub: 
LinkedIn: 

Built for DataTalks.Club Data Engineering Zoomcamp
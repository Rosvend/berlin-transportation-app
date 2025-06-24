# Real-Time Public Transport Data Pipeline

---

## Purpose

The purpose of this project is to build a modern, production-grade real-time data pipeline that extracts, stores, transforms, and visualizes live public transport data from Berlin’s BVG system using the [v6.bvg.transport.rest](https://v6.bvg.transport.rest) API. The pipeline is designed to be modular, cloud-portable (AWS-ready), and suitable for a data engineering portfolio.

---

## Scope

This project covers the **end-to-end lifecycle** of a real-time data pipeline:
- API data extraction
- Ingestion into a raw zone
- Loading into Snowflake
- Transformation with dbt
- DAG orchestration with Airflow
- Dashboard visualization
- CI/CD and automated data quality testing

---

## Tech Stack

| Layer             | Technology (Local)              | Cloud Equivalent (AWS)             |
|------------------|----------------------------------|------------------------------------|
| Ingestion         | Python + Airflow (Docker)        | MWAA / ECS / EKS                   |
| Storage           | MinIO or local filesystem        | Amazon S3                          |
| Warehouse         | Snowflake (Free Trial)           | Snowflake (Cloud)                  |
| Transformation    | dbt + Snowflake SQL              | dbt Cloud + Snowflake              |
| Orchestration     | Airflow (Docker Compose)         | MWAA / Airflow on ECS              |
| Stream (Optional) | Kafka + PySpark (simulated)      | MSK or Kinesis + Glue / EMR        |
| Visualization     | Streamlit or Jupyter             | EC2, Fargate, S3 + CloudFront      |
| CI/CD             | GitHub Actions                   | GitHub Actions / CodePipeline      |
| Data Quality      | Great Expectations + Pytest      | Same (CI/CD + S3, Snowflake)       |

---

## 🗂️ Repo Structure

```bash
berlin-transport-pipeline/
├── dags/                      # Airflow DAGs
│   └── ingest_departures.py
├── extract/                   # API data fetch logic
│   └── departures.py
├── transform/                 # dbt project lives here
│   └── dbt_project/
├── config/                    # Configuration files
│   └── config.yaml
├── scripts/                   # Manual tests, utilities
│   └── test_connection.py
├── tests/                     # Pytest unit + integration tests
├── notebooks/                 # Exploration notebooks (optional)
├── dashboard/                 # Streamlit dashboards
│   └── delays_dashboard.py
├── data/                      # Local raw storage (MinIO mount)
│   ├── raw/
│   ├── staging/
│   └── processed/
├── docker-compose.yml         # Orchestration of local stack
├── requirements.txt
├── .env                       # Secrets + credentials
├── README.md
├── .gitignore

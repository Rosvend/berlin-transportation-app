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
├── airflow/                  # Airflow DAGs and configurations
│   ├── dags/
│   │   ├── __init__.py
│   │   └── ingest_departure.py
│   └── .gitkeep
├── config/                   # Configuration files
│   └── config.yaml
├── dashboards/               # Streamlit dashboards
│   ├── __init__.py
│   └── app.py
├── data/                     # Local raw storage (MinIO mount)
│   ├── mart/
│   ├── raw/
│   └── staging/
├── dbt/                      # dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── marts/
│       └── staging/
├── docker/                   # Dockerfiles and initialization scripts
│   ├── dockerfile.airflow
│   ├── dockerfile.streamlit
│   └── init-airflow.sh
├── extract/                  # API data fetch logic
│   ├── __init__.py
│   ├── departures.py
│   └── utils.py
├── logs/                     # Logs directory
├── notebooks/                # Exploration notebooks
│   └── EDA.ipynb
├── scripts/                  # Manual tests, utilities
│   ├── bucket_creation.sh
│   └── setup.sh
├── tests/                    # Pytest unit + integration tests
│   ├── __init__.py
│   └── test_departures.py
├── transform/                # Transformation logic
├── docker-compose.yml        # Orchestration of local stack
├── makefile                  # Makefile for convenience commands
├── requirements-streamlit.txt
├── requirements.txt
├── .env                      # Secrets + credentials
├── README.md                 # Project documentation
├── .gitignore                # Git ignore file
```

---

### Prerequisites

**Install Docker and Docker Compose**:
- [Docker Installation Guide](https://docs.docker.com/get-docker/)
- [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

## How to Run in 5 simple steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rosvend/berlin-transport-elt-snowflake.git
   cd berlin-transport-elt-snowflake
   ```

2. **Set Up Environment Variables**:
   - Copy `.env.template` to `.env`:
     ```bash
     cp .env.template .env
     ```
   - Update `.env` with your credentials (e.g., Snowflake, MinIO).

3. **Run setup script**:
   ```bash
     bash scripts/setup.sh
   ```

4. **Build and Start Services**:
   ```bash
   make up
   ```

5. **Access Services**:
   - **Airflow UI**: [http://localhost:8080](http://localhost:8080) (admin/admin)
   - **MinIO Console**: [http://localhost:9001](http://localhost:9001) (minioadmin/minioadmin123)
   - **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)

### Useful Commands

- **Stop Services**:
  ```bash
  make down
  ```

- **View Logs**:
  ```bash
  make logs
  ```

- **Clean Up Containers and Volumes**:
  ```bash
  make clean
  ```

- **Check Service Health**:
  ```bash
  make health
  ```

---

## Next Steps

1. **Run Airflow DAGs**:
   - Navigate to the Airflow UI and trigger the DAGs.

2. **Explore Data**:
   - Use the Streamlit dashboard to visualize transport data.

3. **Extend the Pipeline**:
   - Add new DAGs, dbt models, or dashboards as needed.

---

## Troubleshooting

- **Airflow UI Not Accessible**:
  - Ensure the containers are running:
    ```bash
    docker-compose ps
    ```
  - Rebuild and restart services:
    ```bash
    make up
    ```

- **MinIO Buckets Not Created**:
  - Run the bucket creation script:
    ```bash
    make create-buckets
    ```

- **Streamlit Dashboard Not Loading**:
  - Check the logs:
    ```bash
    make logs
    ```

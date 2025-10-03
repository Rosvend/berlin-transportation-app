# Product Requirements Document (PRD) – Real-Time Public Transport Data Pipeline

## Introduction

This document outlines the product requirements for building a **real-time data pipeline** designed to ingest, process, and analyze **live public transport data** from Berlin's BVG system. The objective is to create a **production-grade, modular, and cloud-portable solution** suitable for a professional **data engineering portfolio**. The system will offer insights into transport efficiency and potential delays.

---

## Functional Requirements

| Requirement ID | Description | User Story | Expected Behavior/Outcome |
|----------------|-------------|------------|----------------------------|
| **FR001** | Data Ingestion | As a data engineer, I want to reliably extract live departure data from the BVG API to serve as the foundation for the pipeline. | The system must pull data from the `/stops/:id/departures` endpoint every 5 minutes. Raw data must be saved as timestamped JSON files in a raw storage zone (e.g., MinIO/S3), orchestrated by an Airflow DAG. |
| **FR002** | Data Storage (Snowflake) | As a data engineer, I want to load the raw, unprocessed data into Snowflake to ensure a persistent, raw copy is available for reprocessing. | Raw JSON files should be loaded into a `RAW.departures_raw` table in Snowflake using VARIANT types. |
| **FR003** | Data Transformation (dbt) | As a data modeler, I want to clean, structure, and aggregate the raw data to make it suitable for analysis. | Using dbt, create staging models (`STAGING.departures_clean`) and analytical marts (`MARTS.delays_by_stop`, `MARTS.busyness_per_hour`). |
| **FR004** | dbt Testing & Documentation | As a data modeler, I want to ensure the quality and integrity of my transformations and document them clearly. | Implement dbt tests (uniqueness, not-null, referential integrity). Generate comprehensive documentation using `dbt docs`. |
| **FR005** | Dashboard Visualization | As a data analyst, I want to visualize key transport performance indicators to identify trends and anomalies. | Build a Streamlit dashboard showing average delays per line/stop, congestion trends, and top delayed stations. |
| **FR006** | CI/CD Automation | As a developer, I want to automate testing and deployment to ensure code quality and a streamlined release process. | Use GitHub Actions to run `pytest` and `dbt test` on every push to main. Successful runs trigger DAG and dbt model deployment. |
| **FR007** | Data Quality Checks | As a data engineer, I want to validate incoming data to prevent low-quality data from corrupting the pipeline. | Use Great Expectations for row count, null checks, and type validation. Integrated into Airflow to halt execution on failure. |

---

## 🔒 Non-Functional Requirements

| Requirement ID | Description | User Story | Expected Behavior/Outcome |
|----------------|-------------|------------|----------------------------|
| **NFR001** | Performance & Latency | As a user, I want the data to be fresh and dashboards to be responsive so I can make timely decisions. | End-to-end latency (API to mart) ≤ 15 minutes. Dashboard load time ≤ 5 seconds. |
| **NFR002** | Scalability | As a data engineer, I want the system to handle growing data volumes without performance degradation. | Must scale from one stop ID to the full BVG network. Compute should be configurable. |
| **NFR003** | Reliability & Resilience | As a data engineer, I want the pipeline to be robust against transient failures and easy to monitor. | Airflow tasks should have retry logic. Logging and alerting must be included for failures or anomalies. |
| **NFR004** | Security | As a security admin, I want all sensitive credentials and data to be protected against unauthorized access. | API keys and credentials managed via secrets manager or environment variables. All data encrypted in transit and at rest. |
| **NFR005** | Maintainability & Extensibility | As a developer, I want the project to be well-documented and modular so I can easily fix bugs or add new features. | Modular ETL codebase, inline comments, detailed `README.md`, and parameterized config files. |
| **NFR006** | Observability | As a data engineer, I want to have clear visibility into the pipeline's health and performance. | Implement structured logging and track metrics: DAG run time, load volume, dbt model execution time. |

---
# Real-Time Fraud Detection Platform 2.0

A production-oriented **real-time fraud detection platform** built with Python, Apache Kafka, Apache Spark Structured Streaming, PostgreSQL and FastAPI.

The project demonstrates an end-to-end Data Engineering architecture capable of ingesting transactions as events, processing them in real time, applying stateful fraud detection rules, persisting the results and exposing them through a REST API.

---

## Architecture

```text
                         ┌─────────────────────┐
                         │ Transaction Generator│
                         │       Python        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Apache        │
                         │        Kafka        │
                         │ fraud-transactions  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────┐
                    │   Spark Structured Streaming│
                    └──────────────┬──────────────┘
                                   │
                         ┌─────────▼─────────┐
                         │      Bronze       │
                         │ Raw event data    │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │      Silver       │
                         │ Cleaned/enriched  │
                         │ transaction data  │
                         └─────────┬─────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │ Stateful Fraud Detection    │
                    │                             │
                    │ • Velocity detection        │
                    │ • Country hopping           │
                    │ • Stateful rules             │
                    │ • Fraud scoring              │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   Fraud Engine    │
                         │ Rules + scoring   │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │       Gold        │
                         │ Fraud decisions   │
                         │ Parquet           │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    PostgreSQL     │
                         │ fraud_transactions│
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │      FastAPI      │
                         │ REST API + Swagger│
                         └───────────────────┘
```

---

## Project Goals

The platform was designed to demonstrate practical Data Engineering capabilities across the complete data lifecycle:

* Event-driven data ingestion
* Real-time stream processing
* Apache Kafka
* Spark Structured Streaming
* Stateful stream processing
* Medallion architecture
* Fraud detection rules
* Data quality and validation
* Parquet-based data storage
* PostgreSQL persistence
* REST API development
* Docker containerization
* Automated testing
* Ruff linting
* GitHub Actions CI
* Reproducible local development

---

## Technology Stack

| Area              | Technology              |
| ----------------- | ----------------------- |
| Language          | Python 3.12             |
| Streaming         | Apache Kafka            |
| Stream Processing | Apache Spark 4.0.4      |
| Processing API    | PySpark                 |
| Storage           | Parquet                 |
| Database          | PostgreSQL 16           |
| API               | FastAPI                 |
| API Server        | Uvicorn                 |
| Validation        | Pydantic                |
| Database Driver   | Psycopg                 |
| Containers        | Docker / Docker Compose |
| Testing           | Pytest                  |
| Linting           | Ruff                    |
| CI                | GitHub Actions          |
| Version Control   | Git / GitHub            |

---

# Data Pipeline

## 1. Transaction Generation

The platform generates realistic transaction events containing information such as:

* Transaction ID
* Customer ID
* Timestamp
* Amount
* Currency
* Country
* Merchant
* Device ID

Transactions are published to Kafka as JSON events.

---

## 2. Kafka

Transactions are published to:

```text
fraud-transactions
```

The Kafka topic is configured with multiple partitions to demonstrate distributed event ingestion.

Kafka provides the event-driven backbone of the platform.

---

## 3. Bronze Layer

The Bronze layer stores the raw transaction events received from Kafka.

The objective is to preserve the original event data before applying business transformations.

```text
Kafka
  ↓
Bronze
```

---

## 4. Silver Layer

The Silver layer transforms the raw events into cleaned and structured transaction data.

Typical processing includes:

* Schema enforcement
* Type conversion
* Timestamp handling
* Data validation
* Normalization
* Preparation for fraud analysis

```text
Bronze
  ↓
Silver
```

---

## 5. Stateful Fraud Detection

The platform performs stateful processing using Spark Structured Streaming.

This allows the system to evaluate transactions using information from previous events rather than evaluating every transaction independently.

Examples of implemented fraud scenarios include:

### Velocity attacks

Detecting customers generating an unusually high number of transactions within a short period.

### Country hopping

Detecting suspicious changes in transaction countries within a short time window.

### Stateful transaction behaviour

Maintaining streaming state to identify patterns across multiple transactions.

```text
Silver
  ↓
Stateful Fraud Detection
  ↓
Fraud Engine
```

---

## 6. Fraud Engine

The Fraud Engine evaluates fraud rules and produces:

* Fraud decision
* Fraud score
* Triggered fraud rules
* Fraud reasons

Example result:

```json
{
  "is_fraud": true,
  "fraud_score": 0.85,
  "fraud_reasons": [
    "velocity_attack",
    "country_hopping"
  ]
}
```

---

## 7. Gold Layer

The Gold layer contains the final fraud detection results in Parquet format.

The data is structured for downstream analytical and operational consumption.

```text
Gold
└── fraud_transactions
```

Stateful processing also uses checkpointing to support incremental stream processing.

---

# PostgreSQL

Fraud decisions are incrementally written from the Gold layer into PostgreSQL.

Main table:

```text
fraud_transactions
```

Schema:

| Column         | Type        |
| -------------- | ----------- |
| transaction_id | varchar     |
| customer_id    | varchar     |
| timestamp      | timestamptz |
| amount         | numeric     |
| currency       | varchar     |
| country        | varchar     |
| merchant       | varchar     |
| device_id      | varchar     |
| is_fraud       | boolean     |
| fraud_score    | numeric     |
| fraud_reasons  | text[]      |
| created_at     | timestamptz |

PostgreSQL provides the operational data store used by the API.

---

# FastAPI

The platform exposes the fraud detection results through a REST API.

## Health Check

```http
GET /health
```

Example:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Query Transactions

```http
GET /transactions
```

Example:

```bash
curl "http://localhost:8000/transactions?limit=10"
```

Supported filters include:

```text
limit
is_fraud
country
min_score
```

Example:

```bash
curl "http://localhost:8000/transactions?is_fraud=true&limit=10"
```

---

## Get a Transaction

```http
GET /transactions/{transaction_id}
```

Example:

```bash
curl "http://localhost:8000/transactions/TXN-10001"
```

Returns `404` when the transaction does not exist.

---

## Fraud Transactions

```http
GET /fraud/transactions
```

Returns transactions identified as fraudulent.

---

## Fraud Investigation

```http
GET /fraud/investigate/{transaction_id}
```

This endpoint provides an investigation-oriented response containing:

* Original transaction
* Fraud decision
* Fraud score
* Risk level
* Triggered rules

Example:

```json
{
  "fraud_detected": true,
  "fraud_score": 0.85,
  "risk_level": "CRITICAL",
  "triggered_rules": [
    "velocity_attack",
    "country_hopping"
  ]
}
```

---

# Swagger

Interactive API documentation is available at:

```text
http://localhost:8000/docs
```

The OpenAPI specification can also be accessed at:

```text
http://localhost:8000/openapi.json
```

---

# Docker

The platform uses Docker Compose to provide the main infrastructure services.

Current services:

```text
fraud-kafka
fraud-spark
fraud-postgres
fraud-api
```

Start the complete environment:

```bash
docker compose up -d --build
```

Check running services:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Stop the environment:

```bash
docker compose down
```

---

## Environment Variables

Database configuration is provided through `.env`.

Example:

```env
POSTGRES_DB=fraud_detection
POSTGRES_USER=fraud_user
POSTGRES_PASSWORD=change_me
POSTGRES_HOST=fraud-postgres
POSTGRES_PORT=5432
```

The real `.env` file should not be committed to Git.

An `.env.example` file is provided as a template.

---

# Running the API

Once Docker Compose is running:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

API documentation:

```text
http://localhost:8000/docs
```

---

# Local Development

Create the Conda environment:

```bash
conda create -n fraud-platform python=3.12 -y
```

Activate it:

```bash
conda activate fraud-platform
```

Install the project:

```bash
pip install -e .
```

Run the tests:

```bash
pytest -q
```

Run Ruff:

```bash
ruff check .
```

Automatically apply safe Ruff fixes:

```bash
ruff check . --fix
```

---

# Testing

The project includes unit, integration and API tests.

Run the complete test suite:

```bash
pytest -q
```

The current test suite contains **57 passing tests**.

The tests cover areas including:

* Transaction generation
* Kafka producer
* Fraud rules
* Fraud engine
* Stateful processing
* Window processing
* Gold processing
* Silver processing
* API endpoints
* Integration behaviour

---

# Continuous Integration

GitHub Actions automatically runs the project validation pipeline.

The CI pipeline performs:

```text
Checkout
   ↓
Python 3.12
   ↓
Install project
   ↓
Ruff
   ↓
Pytest
```

Every push to the development branches and pull requests are automatically validated.

The goal is to ensure that new changes do not break the existing pipeline.

---

# Project Structure

```text
real-time-fraud-detection/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── docs/
│   └── data_model/
│
├── scripts/
│
├── src/
│   └── fraud_detection/
│       │
│       ├── api/
│       │   ├── database.py
│       │   ├── main.py
│       │   └── models.py
│       │
│       ├── fraud_engine/
│       │
│       ├── generator/
│       │
│       ├── processing/
│       │
│       ├── streaming/
│       │
│       └── ...
│
├── tests/
│   ├── api/
│   ├── integration/
│   └── unit/
│
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── Dockerfile.api
├── pyproject.toml
└── README.md
```

---

# Design Principles

## Medallion Architecture

The pipeline follows a Bronze / Silver / Gold architecture:

```text
Bronze → Silver → Gold
```

This separates:

* Raw ingestion
* Data transformation
* Business-ready results

and makes the processing pipeline easier to maintain and extend.

---

## Event-Driven Architecture

Kafka decouples transaction generation from downstream processing.

```text
Producer → Kafka → Spark
```

This allows the processing layer to consume events independently from the transaction producer.

---

## Stateful Stream Processing

Fraud detection cannot always be performed using a single transaction.

Some fraud patterns require historical context.

Spark Structured Streaming state is therefore used to evaluate transaction behaviour across time windows.

---

## Separation of Responsibilities

The project separates:

```text
Ingestion
Processing
Fraud Detection
Storage
API
Infrastructure
Testing
```

This makes individual components easier to test and evolve.

---

# Current Status

### Completed

* [x] Python transaction generator
* [x] Kafka ingestion
* [x] Bronze streaming
* [x] Silver streaming
* [x] Stateful fraud detection
* [x] Fraud Engine
* [x] Gold Parquet layer
* [x] Incremental Gold → PostgreSQL pipeline
* [x] PostgreSQL database
* [x] FastAPI REST API
* [x] Swagger / OpenAPI
* [x] API filtering
* [x] Fraud investigation endpoint
* [x] Docker Compose infrastructure
* [x] FastAPI Docker image
* [x] Automated tests
* [x] Ruff linting
* [x] GitHub Actions CI

### Planned Extensions

* [ ] Power BI fraud monitoring dashboard
* [ ] Machine Learning fraud model
* [ ] MLflow experiment tracking
* [ ] Model serving
* [ ] dbt transformation/testing layer
* [ ] Cloud deployment
* [ ] Infrastructure as Code with Terraform
* [ ] Advanced monitoring and observability

---

# Future Architecture

The platform is designed to evolve towards a cloud-based architecture:

```text
                    Kafka
                      │
                      ▼
             Spark Structured Streaming
                      │
              ┌───────┴───────┐
              ▼               ▼
           Bronze           Silver
                              │
                              ▼
                    Fraud Detection
                              │
                              ▼
                            Gold
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                PostgreSQL          Data Lake
                    │
                    ▼
                 FastAPI
                    │
             ┌──────┴──────┐
             ▼             ▼
          Clients       Power BI
```

Future cloud components may include:

```text
GCP
├── GCS
├── BigQuery
├── Dataproc
└── Terraform
```

---

# What This Project Demonstrates

This project demonstrates practical experience with:

**Data Engineering**

* Batch and streaming concepts
* Event-driven pipelines
* Distributed processing
* Data modelling
* Medallion architecture
* Stateful stream processing

**Software Engineering**

* Python packaging
* Modular architecture
* REST APIs
* Automated testing
* Linting
* Git workflows
* CI pipelines

**Infrastructure**

* Docker
* Docker Compose
* Kafka
* Spark
* PostgreSQL

**Data & Analytics**

* Parquet
* SQL
* PostgreSQL
* Fraud analytics
* Real-time decisioning

---

# Author

Built as a portfolio project focused on **Data Engineering, Data Platforms and Real-Time Data Processing**.

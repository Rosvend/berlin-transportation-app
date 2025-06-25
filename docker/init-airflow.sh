#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U airflow > /dev/null 2>&1; do
  sleep 1
done
echo "✅ PostgreSQL is ready."

# Init the DB
echo "🔧 Initializing DB..."
airflow db init

# Create admin user
echo "🔐 Creating admin user (if not exists)..."
airflow users create \
  --username admin \
  --firstname Roy \
  --lastname Admin \
  --role Admin \
  --email admin@example.com \
  --password admin || true

# Start the webserver
echo "🚀 Starting Airflow webserver..."
exec airflow webserver

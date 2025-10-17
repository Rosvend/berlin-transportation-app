#!/bin/bash

# Berlin Transport Backend - Development Startup Script

set -e

echo "🚇 Berlin Transport Live - Starting Development Environment"
echo "============================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please review and update if needed."
fi

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "⚠️  Redis is not running. Starting Redis with Docker..."
    docker compose up -d redis
    echo "⏳ Waiting for Redis to be ready..."
    sleep 3
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $PYTHON_VERSION"

# Install/update dependencies
echo "📦 Installing dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv for faster dependency installation..."
    uv pip install -r pyproject.toml
else
    echo "Using pip for dependency installation..."
    pip install -r pyproject.toml
fi

echo "✅ Dependencies installed"

# Run application
echo "🚀 Starting FastAPI application..."
echo "📍 Web UI will be available at: http://localhost:8000"
echo "📍 API docs will be available at: http://localhost:8000/docs"
echo "============================================================"
echo ""

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

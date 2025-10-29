#!/bin/bash

# Berlin Transport App - One-Line Startup Script
# This script starts the entire application stack

set -e

echo "================================================"
echo "Berlin Transport App - Starting Application"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning "No .env file found. Creating from template..."
    cat > .env << 'EOF'
# Backend Application Settings
APP_NAME="Berlin Transport Live"
ENVIRONMENT=development
DEBUG=true

# BVG API Configuration
BVG_API_BASE_URL=https://v6.bvg.transport.rest
API_TIMEOUT=10

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
CACHE_TTL=300

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
EOF
    print_success ".env file created"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_warning "Docker is not installed. Skipping Redis container setup."
    print_warning "Application will use in-memory cache instead."
    SKIP_DOCKER=true
else
    # Check if Docker daemon is running
    if ! docker ps &> /dev/null 2>&1; then
        print_warning "Docker daemon is not running. Skipping Redis container setup."
        print_warning "Application will use in-memory cache instead."
        SKIP_DOCKER=true
    else
        print_success "Docker is running"
        SKIP_DOCKER=false
    fi
fi

if [ "$SKIP_DOCKER" = false ]; then
    # Check if Redis is already running
    print_info "Checking Redis status..."
    if docker ps | grep -q bvg_redis; then
        print_success "Redis is already running"
    else
        print_info "Starting Redis container..."
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d redis 2>&1 | grep -v "WARN"
        else
            docker compose up -d redis 2>&1 | grep -v "WARN"
        fi
        sleep 3
        print_success "Redis started"
    fi
else
    print_info "Redis will not be started. Using in-memory cache."
fi

# Check if Python is available
if [ -d "venv" ]; then
    print_info "Using existing virtual environment"
    source venv/bin/activate
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_success "Using Python $PYTHON_VERSION"

# Install dependencies
print_info "Installing/updating dependencies..."
cd backend

if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "pip is not available. Please install pip."
    exit 1
fi

$PYTHON_CMD -m pip install -q -r requirements.txt
print_success "Dependencies installed"

# Run tests
print_info "Running tests..."
if $PYTHON_CMD -m pytest tests/ -v --tb=short 2>&1 | tee /tmp/test_output.log; then
    print_success "All tests passed"
else
    print_warning "Some tests failed. Check /tmp/test_output.log for details."
    print_info "Continuing with startup..."
fi

echo ""
print_info "Starting backend API server..."

# Start backend in background
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend started on http://localhost:8000"
else
    print_error "Backend failed to start. Check /tmp/backend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend server
cd ..
print_info "Starting frontend server..."

# Use Python's built-in HTTP server for the frontend
cd frontend
$PYTHON_CMD -m http.server 3000 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 2

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend started on http://localhost:3000"
else
    print_error "Frontend failed to start. Check /tmp/frontend.log"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "================================================"
print_success "Application is running!"
echo "================================================"
echo ""
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /tmp/backend.log"
echo "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Cleanup function
cleanup() {
    echo ""
    print_info "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    print_success "Servers stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Keep script running and show logs
tail -f /tmp/backend.log /tmp/frontend.log

#!/bin/bash

# Berlin Transport Data Pipeline - Setup Script
# This script sets up the initial project structure and configuration

set -e  # Exit on any error

echo "🚀 Setting up Berlin Transport Data Pipeline..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Create directory structure
create_directories() {
    print_info "Creating directory structure..."
    
    directories=(
        "airflow/dags"
        "extract"
        "transform"
        "config"
        "scripts"
        "tests"
        "notebooks"
        "dashboards"
        "data/raw"
        "data/staging"
        "data/mart"
        "docker"
        "dbt/models/staging"
        "dbt/models/marts"
        "logs"
        ".github/workflows"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_status "Created directory: $dir"
    done
}

# Setup environment file
setup_environment() {
    if [ ! -f .env ]; then
        print_info "Creating .env file from template..."
        cp .env.template .env
        print_status "Created .env file"
        print_warning "Please update .env with your actual credentials before running the pipeline"
    else
        print_warning ".env file already exists, skipping creation"
    fi
}

# Generate Fernet key for Airflow
generate_fernet_key() {
    print_info "Generating Fernet key for Airflow..."
    
    # Check if python is available
    if command -v python3 &> /dev/null; then
        FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
        
        # Update .env file with generated key
        if [ -f .env ]; then
            sed -i.bak "s/AIRFLOW__CORE__FERNET_KEY=your-fernet-key-here/AIRFLOW__CORE__FERNET_KEY=$FERNET_KEY/" .env
            print_status "Generated and updated Fernet key in .env"
        fi
    else
        print_warning "Python3 not found. Please manually generate a Fernet key and update .env"
        print_info "Run: python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    fi
}

# Create initial placeholder files
create_placeholder_files() {
    print_info "Creating placeholder files..."
    
    # Create a simple DAG placeholder
    if [ ! -f airflow/dags/__init__.py ]; then
        touch airflow/dags/__init__.py
        print_status "Created airflow/dags/__init__.py"
    fi
    
    # Create extract module placeholder
    if [ ! -f extract/__init__.py ]; then
        touch extract/__init__.py
        print_status "Created extract/__init__.py"
    fi
    
    # Create tests placeholder
    if [ ! -f tests/__init__.py ]; then
        touch tests/__init__.py
        print_status "Created tests/__init__.py"
    fi
    
    # Create dashboards placeholder
    if [ ! -f dashboards/__init__.py ]; then
        touch dashboards/__init__.py
        print_status "Created dashboards/__init__.py"
    fi
    
    # Create dbt placeholder files (if they don't exist)
    if [ ! -f dbt/dbt_project.yml ]; then
        touch dbt/dbt_project.yml
        print_status "Created dbt/dbt_project.yml"
    fi
    
    if [ ! -f dbt/profiles.yml ]; then
        touch dbt/profiles.yml
        print_status "Created dbt/profiles.yml"
    fi
}

# Setup Git repository (if not already initialized)
setup_git() {
    if [ ! -d .git ]; then
        print_info "Initializing Git repository..."
        git init
        git add .
        git commit -m "Initial commit: Project setup"
        print_status "Git repository initialized"
    else
        print_info "Git repository already exists"
    fi
}

# Validate configuration
validate_setup() {
    print_info "Validating setup..."
    
    # Check if all required files exist
    required_files=(
        "docker-compose.yml"
        "requirements.txt"
        "requirements-streamlit.txt"
        "config/config.yaml"
        ".env"
        ".gitignore"
        "Makefile"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
    
    print_status "All required files present"
}

# Main setup function
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          Berlin Transport Data Pipeline Setup           ║"
    echo "║                                                          ║"
    echo "║  This script will set up your development environment   ║"
    echo "║  for the BVG real-time transport data pipeline.         ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Run setup steps
    check_docker
    create_directories
    setup_environment
    generate_fernet_key
    create_placeholder_files
    validate_setup
    
    echo ""
    echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Update .env file with your Snowflake credentials"
    echo "2. Run 'make up' to start all services"
    echo "3. Run 'make init-airflow' to initialize Airflow"
    echo "4. Run 'make create-buckets' to set up MinIO storage"
    echo ""
    echo -e "${BLUE}Access your services at:${NC}"
    echo "• Airflow UI: http://localhost:8080 (admin/admin)"
    echo "• MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)"
    echo "• Streamlit Dashboard: http://localhost:8501"
    echo ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo "• make help    - Show all available commands"
    echo "• make logs    - View service logs"
    echo "• make status  - Check service status"
    echo "• make clean   - Clean up containers"
}

# Run main function
main "$@"
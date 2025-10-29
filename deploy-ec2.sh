#!/bin/bash

# EC2 Deployment Script for Berlin Transport App
# Run this script ON your EC2 instance after cloning the repo

set -e

echo "================================================"
echo "Berlin Transport App - EC2 Deployment"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running on EC2
if [ ! -d "/home/ubuntu" ]; then
    print_warning "This script is designed for Ubuntu on EC2"
fi

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    print_info "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose
    sudo usermod -aG docker ubuntu
    print_success "Docker installed"
    print_warning "Please log out and back in for Docker group changes to take effect"
    exit 0
fi

# Stop any running containers
print_info "Stopping existing containers..."
sudo docker-compose down 2>/dev/null || true

# Build and start containers
print_info "Building and starting containers..."
sudo docker-compose up -d --build

# Wait for services to be ready
print_info "Waiting for services to start..."
sleep 10

# Check container status
print_info "Container status:"
sudo docker-compose ps

# Test backend health
print_info "Testing backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is healthy"
else
    print_warning "Backend health check failed"
    print_info "Checking backend logs:"
    sudo docker-compose logs backend | tail -20
fi

# Get EC2 public IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "unknown")

echo ""
echo "================================================"
print_success "Deployment Complete!"
echo "================================================"
echo ""
echo "Access your app at:"
echo "  Frontend: http://${EC2_IP}:3000"
echo "  Backend:  http://${EC2_IP}:8000"
echo "  API Docs: http://${EC2_IP}:8000/docs"
echo ""
echo "View logs:"
echo "  sudo docker-compose logs -f"
echo ""
echo "IMPORTANT: Make sure your EC2 Security Group allows:"
echo "  - Port 3000 (frontend)"
echo "  - Port 8000 (backend)"
echo "  - Port 22 (SSH)"
echo ""

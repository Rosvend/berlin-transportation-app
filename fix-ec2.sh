#!/bin/bash
# Run this script ON YOUR EC2 INSTANCE to fix the deployment

echo "🚀 Fixing Berlin Transport App deployment..."
echo ""

# Navigate to app directory
cd ~/berlin-transportation-app

# Pull latest changes with the fixes
echo "📥 Pulling latest changes..."
git pull origin main

# Stop current containers
echo "🛑 Stopping current containers..."
sudo docker-compose down

# Rebuild with new configuration
echo "🔨 Building containers with new configuration..."
sudo docker-compose up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Check status
echo ""
echo "📊 Container Status:"
sudo docker-compose ps

# Test backend health
echo ""
echo "🏥 Testing backend health..."
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend health check failed"
    echo "Logs:"
    sudo docker-compose logs backend | tail -20
    exit 1
fi

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)

echo ""
echo "================================================"
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "================================================"
echo ""
echo "Access your app at:"
echo "  🌐 Frontend: http://${PUBLIC_IP}:3000"
echo "  🔧 Backend:  http://${PUBLIC_IP}:8000"
echo "  📚 API Docs: http://${PUBLIC_IP}:8000/docs"
echo ""
echo "Share with your classmates: http://${PUBLIC_IP}:3000"
echo ""

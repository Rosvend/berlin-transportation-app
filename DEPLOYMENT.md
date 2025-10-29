# EC2 Deployment Guide

## Quick Deploy (On Your EC2 Instance)

1. **Clone the repository:**
```bash
git clone https://github.com/rosvend/berlin-transportation-app.git
cd berlin-transportation-app
```

2. **Run the deployment script:**
```bash
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

That's it! The script will:
- Install Docker if needed
- Build and start all containers
- Show you the access URLs

## Manual Deployment Steps

If you prefer to deploy manually:

```bash
# 1. Install Docker (Ubuntu)
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
# Log out and back in

# 2. Pull latest changes
git pull origin main

# 3. Rebuild and start containers
sudo docker-compose down
sudo docker-compose up -d --build

# 4. Check status
sudo docker-compose ps
sudo docker-compose logs -f
```

## EC2 Security Group Configuration

Make sure your EC2 instance allows these inbound rules:

| Type  | Protocol | Port Range | Source    | Description      |
|-------|----------|------------|-----------|------------------|
| SSH   | TCP      | 22         | Your IP   | SSH access       |
| HTTP  | TCP      | 3000       | 0.0.0.0/0 | Frontend         |
| HTTP  | TCP      | 8000       | 0.0.0.0/0 | Backend API      |

## Accessing Your App

After deployment, access at:
- **Frontend:** `http://YOUR_EC2_PUBLIC_IP:3000`
- **Backend API:** `http://YOUR_EC2_PUBLIC_IP:8000`
- **API Docs:** `http://YOUR_EC2_PUBLIC_IP:8000/docs`

## Troubleshooting

### Check container status:
```bash
sudo docker-compose ps
```

### View logs:
```bash
# All containers
sudo docker-compose logs -f

# Specific container
sudo docker-compose logs -f backend
sudo docker-compose logs -f frontend
sudo docker-compose logs -f redis
```

### Backend shows (unhealthy):
```bash
# Check backend logs
sudo docker-compose logs backend

# Restart backend
sudo docker-compose restart backend

# Check health endpoint
curl http://localhost:8000/health
```

### Rebuild after code changes:
```bash
git pull origin main
sudo docker-compose down
sudo docker-compose up -d --build
```

## Re-deploying After Changes

After pushing code changes to GitHub:

```bash
# On EC2
cd berlin-transportation-app
git pull origin main
sudo docker-compose up -d --build
```

## Stopping the Application

```bash
sudo docker-compose down
```

To also remove volumes (cache data):
```bash
sudo docker-compose down -v
```

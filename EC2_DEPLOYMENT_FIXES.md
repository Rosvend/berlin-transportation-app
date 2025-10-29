# 🚀 EC2 Deployment - Quick Reference

## What Was Fixed

### 1. **Frontend API URL Configuration** ✅
- **Problem:** Hardcoded `localhost:8000` won't work from browser
- **Solution:** Created `frontend/config.js` with auto-detection:
  - Detects if running locally → uses `localhost:8000`
  - Detects if on EC2 → uses EC2 IP + port 8000

### 2. **CORS Configuration** ✅
- **Problem:** Backend only allowed `localhost` origins
- **Solution:** Updated `backend/app/main.py` to allow all origins (safe for demo)

### 3. **Docker Health Check** ✅
- **Problem:** Backend container missing `curl` for health checks
- **Solution:** Added `curl` installation in `Dockerfile.backend`

### 4. **Nginx Configuration** ✅
- **Problem:** No proper MIME types for JS/CSS files
- **Solution:** Created `docker/nginx.conf` with proper configuration

---

## 📋 Deployment Steps on EC2

### Option 1: Automated (Recommended)
```bash
# SSH into your EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Clone repo
git clone https://github.com/rosvend/berlin-transportation-app.git
cd berlin-transportation-app

# Run deployment script
./deploy-ec2.sh
```

### Option 2: Manual
```bash
# Pull latest changes (if already cloned)
cd berlin-transportation-app
git pull origin main

# Rebuild and restart
sudo docker-compose down
sudo docker-compose up -d --build

# Check status
sudo docker-compose ps
```

---

## 🔧 On Your Current EC2 Instance

Since you already have it running with errors, do this:

```bash
# 1. Pull the latest changes
cd ~/berlin-transportation-app
git pull origin main

# 2. Rebuild containers with new configuration
sudo docker-compose down
sudo docker-compose up -d --build

# 3. Wait 30 seconds, then check
sudo docker-compose ps

# 4. All containers should show "healthy" now
```

---

## ✅ Verification

After deployment, verify:

```bash
# 1. Check all containers are running
sudo docker-compose ps
# Should show: frontend (Up), backend (Up healthy), redis (Up healthy)

# 2. Test backend
curl http://localhost:8000/health
# Should return: {"status":"healthy","service":"berlin-transport-web"}

# 3. Test frontend
curl http://localhost:3000
# Should return HTML content

# 4. Get your EC2 public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

Then access in browser:
- **Frontend:** `http://YOUR_EC2_IP:3000`
- **API Docs:** `http://YOUR_EC2_IP:8000/docs`

---

## 📊 What Changed

| File | Change |
|------|--------|
| `frontend/config.js` | **NEW** - Auto-detects API URL based on environment |
| `frontend/index.html` | Added config.js import |
| `frontend/js/app.js` | Removed hardcoded localhost:8000 |
| `backend/app/main.py` | CORS allows all origins |
| `docker/Dockerfile.backend` | Added curl for health checks |
| `docker/Dockerfile.frontend` | Uses custom nginx.conf |
| `docker/nginx.conf` | **NEW** - Proper MIME types |
| `deploy-ec2.sh` | **NEW** - Automated deployment script |
| `DEPLOYMENT.md` | **NEW** - Full deployment guide |

---

## 🔍 Troubleshooting

### Container shows (unhealthy)
```bash
sudo docker-compose logs backend
```

### Network errors in browser
1. Check EC2 Security Group allows ports 3000 and 8000
2. Verify backend is healthy: `curl http://localhost:8000/health`
3. Check browser console for actual error

### After git pull, changes not reflected
```bash
sudo docker-compose up -d --build  # Force rebuild
```

---

## 🎯 Next Steps

1. **Commit and push your changes:**
   ```bash
   git add .
   git commit -m "fix: EC2 deployment configuration"
   git push origin main
   ```

2. **On EC2, pull and redeploy:**
   ```bash
   cd ~/berlin-transportation-app
   git pull origin main
   sudo docker-compose up -d --build
   ```

3. **Share with classmates:**
   - Give them: `http://YOUR_EC2_IP:3000`
   - No need to specify port 8000 - frontend handles it!

---

## 💡 Pro Tips

- **View live logs:** `sudo docker-compose logs -f`
- **Restart single service:** `sudo docker-compose restart backend`
- **Check Redis:** `sudo docker-compose exec redis redis-cli ping`
- **Free up space:** `sudo docker system prune -a` (careful!)

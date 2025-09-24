# Week 1 Tasks: Foundation & Backend Core (Day 0-7)

## 🎯 Sprint Goal
Build a working FastAPI backend that serves real-time Berlin transport data

## Day 0 (Tomorrow) - Project Setup & Cleanup
**Time Estimate: 4-6 hours**

### Morning (2-3 hours)
- [ ] **Read cleanup plan** and understand what stays vs goes
- [ ] **Backup current project** (git commit current state)
- [ ] **Create new branch** `feature/web-app-migration`
- [ ] **Delete unnecessary files** per cleanup plan
- [ ] **Update .gitignore** for web app files

### Afternoon (2-3 hours)
- [ ] **Set up FastAPI project structure**:
  ```
  app/
  ├── __init__.py
  ├── main.py
  ├── api/
  ├── models/
  ├── services/
  ├── templates/
  └── static/
  ```
- [ ] **Install dependencies** from requirements-web.txt
- [ ] **Create basic FastAPI app** with health check endpoint
- [ ] **Test FastAPI server** runs locally

### Evening (1 hour)
- [ ] **Git commit** day's progress
- [ ] **Plan tomorrow's tasks**

## Day 1 - BVG API Integration
**Time Estimate: 6-8 hours**

### Morning (3-4 hours)
- [ ] **Refactor `extract/departures.py`** into `app/services/bvg_client.py`
- [ ] **Create Pydantic models** in `app/models/transport.py`
- [ ] **Test BVG client** with existing radar endpoint
- [ ] **Add logging and error handling**

### Afternoon (3-4 hours)
- [ ] **Create stations API** (`/api/stations/search`)
- [ ] **Create departures API** (`/api/departures/{station_id}`)
- [ ] **Test APIs** with Postman/curl
- [ ] **Add featured stations endpoint**

## Day 2 - API Completion & Basic Caching
**Time Estimate: 6-8 hours**

### Morning (3-4 hours)
- [ ] **Add in-memory caching** to BVG client (simple dict-based)
- [ ] **Implement cache expiration** (2-minute TTL)
- [ ] **Add API rate limiting protection**
- [ ] **Test cache performance**

### Afternoon (3-4 hours)
- [ ] **Create comprehensive API tests** with pytest
- [ ] **Add API documentation** (FastAPI auto-docs)
- [ ] **Handle edge cases** (station not found, API down)
- [ ] **Performance benchmarking**

## Day 3 - Docker & Infrastructure
**Time Estimate: 4-6 hours**

### Morning (2-3 hours)
- [ ] **Create Dockerfile** for FastAPI app
- [ ] **Update docker-compose.yml** (remove MinIO/Streamlit, add Redis)
- [ ] **Test containerized app**

### Afternoon (2-3 hours)
- [ ] **Add Redis** for proper caching
- [ ] **Update BVG client** to use Redis
- [ ] **Test full Docker stack**
- [ ] **Update makefile** for web app commands

## Day 4-5 - Simplified Airflow Pipeline
**Time Estimate: 8-10 hours over 2 days**

### Day 4 (4-5 hours)
- [ ] **Simplify Airflow DAG** to only refresh cache
- [ ] **Remove Snowflake/dbt dependencies**
- [ ] **Create simple data refresh task**
- [ ] **Test DAG execution**

### Day 5 (4-5 hours)
- [ ] **Add data quality checks** (basic validation)
- [ ] **Configure DAG scheduling** (every 2 minutes)
- [ ] **Test end-to-end data flow**
- [ ] **Add monitoring/logging**

## Day 6-7 - Testing & Documentation
**Time Estimate: 6-8 hours over 2 days**

### Day 6 (3-4 hours)
- [ ] **Write comprehensive tests** for all APIs
- [ ] **Test error scenarios** (API down, invalid data)
- [ ] **Performance testing** (response times)

### Day 7 (3-4 hours)
- [ ] **Update README.md** for web app
- [ ] **Document API endpoints**
- [ ] **Create development guide**
- [ ] **Prepare for Week 2** (frontend)

## 📊 Week 1 Success Criteria

### Technical Deliverables
- [ ] **Working FastAPI backend** serving BVG data
- [ ] **Station search** and **departures** APIs functional
- [ ] **Caching system** operational (Redis)
- [ ] **Simplified Airflow** updating cache every 2 minutes
- [ ] **Docker environment** running smoothly
- [ ] **Test coverage** > 80% for core APIs

### Performance Targets
- [ ] **API response time** < 200ms (with cache)
- [ ] **BVG API integration** working reliably
- [ ] **Cache hit rate** > 90% for popular stations
- [ ] **System uptime** during development

### Documentation
- [ ] **API documentation** complete
- [ ] **Setup instructions** updated
- [ ] **Architecture decisions** documented

## 🚨 Risk Mitigation

### If Behind Schedule
1. **Skip Redis** initially, use in-memory caching
2. **Simplify Airflow** to just run Python scripts
3. **Reduce test coverage** to core functionality only

### If Ahead of Schedule  
1. **Add route planning** basic functionality
2. **Implement WebSocket** for real-time updates
3. **Add more comprehensive** error handling

## 📝 Daily Checklist Template

**Each Day:**
- [ ] Start with `git pull` and create daily branch
- [ ] Morning: Review tasks and time estimates  
- [ ] Mid-day: Test what you've built
- [ ] Evening: Git commit with meaningful message
- [ ] Document blockers/questions for next day

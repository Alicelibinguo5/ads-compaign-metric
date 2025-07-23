# 🚀 Quick Dashboard Setup Guide

## 🔧 **Immediate Issues & Solutions**

### **Issue 1: Missing `requests` module**
```bash
# Install dependencies
poetry install

# Or install requests directly
pip install requests
```

### **Issue 2: `docker-compose` not found**
```bash
# Use the newer Docker Compose syntax
docker compose up -d

# Or install docker-compose if needed
pip install docker-compose
```

### **Issue 3: Port 8080 conflict**
```bash
# Check what's using port 8080
lsof -i :8080

# Stop conflicting service or modify docker-compose.yml
```

## 🚀 **Quick Start (Fixed)**

### **Option 1: Use the Setup Script**
```bash
# Run the automated setup script
./setup_dashboard.sh
```

### **Option 2: Manual Setup**
```bash
# 1. Install dependencies
poetry install

# 2. Start services
docker compose up -d

# 3. Wait for services to be ready
sleep 15

# 4. Run dashboard setup
poetry run python src/superset/simple_dashboard_setup.py
```

### **Option 3: Manual Dashboard Creation**
```bash
# 1. Start services
docker compose up -d

# 2. Access Superset manually
# URL: http://localhost:8088
# Username: admin
# Password: admin

# 3. Follow the manual guide
# See: docs/superset_dashboard_guide.md
```

## 📊 **Dashboard Access**

Once setup is complete:
- **URL**: http://localhost:8088
- **Username**: admin
- **Password**: admin

## 🔍 **Troubleshooting**

### **Check Service Status**
```bash
# Check if containers are running
docker compose ps

# Check logs
docker compose logs superset
docker compose logs postgres
```

### **Check Port Availability**
```bash
# Check what's using port 8080
lsof -i :8080

# Check what's using port 8088
lsof -i :8088
```

### **Restart Services**
```bash
# Stop all services
docker compose down

# Start fresh
docker compose up -d
```

## 📈 **Expected Dashboard**

Once working, you should see:
1. **CTR Trend by Campaign** - Line chart
2. **CVR Trend by Campaign** - Line chart  
3. **Revenue by Campaign** - Bar chart
4. **Campaign Performance Summary** - Table

## 🎯 **Next Steps**

1. **Verify Data**: Check if campaign data exists in PostgreSQL
2. **Create Charts**: Follow the manual guide if automated setup fails
3. **Test Dashboard**: Verify all charts are working
4. **Monitor Performance**: Check real-time updates

---

**Need Help?** See `docs/superset_dashboard_guide.md` for detailed instructions. 
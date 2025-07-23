# 🌐 Port Configuration

## 📊 **Service Ports**

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **Kafka** | 9092 | - | Message broker |
| **Kafka UI** | 8082 | http://localhost:8082 | Kafka management interface |
| **Zookeeper** | 2181 | - | Kafka coordination |
| **PostgreSQL** | 5432 | - | Metadata storage |
| **Superset** | 8088 | http://localhost:8088 | Dashboard interface |
| **Flink JobManager** | 8081 | http://localhost:8081 | Flink job management |

## 🔧 **Port Conflict Resolution**

### **Issue**: Port 8080 was already in use by Airflow
### **Solution**: Changed Kafka UI port from 8080 to 8082

## 🚀 **Quick Access**

### **Dashboard**
- **Superset**: http://localhost:8088
- **Username**: admin
- **Password**: admin

### **Kafka Management**
- **Kafka UI**: http://localhost:8082
- **Kafka Broker**: localhost:9092

### **Flink Management**
- **Flink UI**: http://localhost:8081

## 🔍 **Troubleshooting**

### **Check Port Usage**
```bash
# Check all ports
lsof -i :8080  # Airflow (if running)
lsof -i :8081  # Flink JobManager
lsof -i :8082  # Kafka UI
lsof -i :8088  # Superset
lsof -i :9092  # Kafka
lsof -i :5432  # PostgreSQL
```

### **Restart Services**
```bash
# Stop all services
docker compose down

# Start with new port configuration
docker compose up -d
```

## 📝 **Notes**

- **Kafka UI**: Changed from 8080 to 8082 to avoid conflict with Airflow
- **Superset**: Remains on 8088 (no conflict)
- **All other ports**: Unchanged 
# 🔄 Data Sync Strategies: Iceberg ↔ Superset

## 🎯 **The Challenge**

How to keep data synchronized between:
- **Iceberg Tables** (S3/MinIO) - Your data lake
- **Superset** - Your visualization layer

## 🏗️ **Strategy 1: Direct Connection (Recommended)**

### **Architecture**
```
Superset → Trino/Presto → Iceberg Tables → S3/MinIO
```

### **Implementation**
```yaml
# Add to docker-compose.yml
trino:
  image: trinodb/trino:latest
  ports:
    - "8080:8080"
  environment:
    - AWS_ACCESS_KEY_ID=minioadmin
    - AWS_SECRET_ACCESS_KEY=minioadmin
  volumes:
    - ./config/trino:/etc/trino
  depends_on:
    - minio
```

### **Benefits**
- ✅ **Real-time sync** - Always latest data
- ✅ **No duplication** - Single source of truth
- ✅ **Automatic updates** - No manual sync needed
- ✅ **Scalable** - Handles large datasets

### **Setup Steps**
1. **Add Trino service** to docker-compose
2. **Configure Iceberg catalog** in Trino
3. **Connect Superset** to Trino
4. **Create datasets** from Iceberg tables

## 🏗️ **Strategy 2: Flink Pipeline Sync**

### **Architecture**
```
Flink → Iceberg Tables → Flink → PostgreSQL → Superset
```

### **Implementation**
```python
# In your Flink job
def sync_to_postgres():
    # Read from Iceberg
    iceberg_table = table_env.from_path("iceberg_catalog.default.campaign_metrics")
    
    # Write to PostgreSQL for Superset
    postgres_sink = """
    INSERT INTO campaign_metrics 
    SELECT * FROM iceberg_table
    ON CONFLICT (campaign_id, date, platform) 
    DO UPDATE SET 
        impressions = EXCLUDED.impressions,
        clicks = EXCLUDED.clicks,
        conversions = EXCLUDED.conversions,
        revenue = EXCLUDED.revenue,
        ctr = EXCLUDED.ctr,
        cvr = EXCLUDED.cvr,
        updated_at = CURRENT_TIMESTAMP
    """
    
    table_env.execute_sql(postgres_sink)
```

### **Benefits**
- ✅ **Fast queries** - PostgreSQL is optimized
- ✅ **Simple setup** - Standard database
- ✅ **Caching** - Can cache results

### **Drawbacks**
- ❌ **Data duplication** - Same data in two places
- ❌ **Sync complexity** - Need to manage consistency
- ❌ **Storage cost** - Double storage

## 🏗️ **Strategy 3: Scheduled Sync**

### **Architecture**
```
Iceberg Tables → Scheduled Job → PostgreSQL → Superset
```

### **Implementation**
```python
# Scheduled sync script
import schedule
import time
from pyiceberg import Table
import psycopg2

def sync_iceberg_to_postgres():
    # Read from Iceberg
    table = Table.from_name("campaign_metrics")
    df = table.scan().to_pandas()
    
    # Write to PostgreSQL
    with psycopg2.connect("postgresql://...") as conn:
        df.to_sql("campaign_metrics", conn, if_exists="replace", index=False)

# Schedule sync every 5 minutes
schedule.every(5).minutes.do(sync_iceberg_to_postgres)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### **Benefits**
- ✅ **Controlled sync** - Predictable updates
- ✅ **Error handling** - Can retry failed syncs
- ✅ **Monitoring** - Track sync status

### **Drawbacks**
- ❌ **Not real-time** - Data lag
- ❌ **Complex scheduling** - Need to manage timing
- ❌ **Data duplication** - Same data in two places

## 🏗️ **Strategy 4: Event-Driven Sync**

### **Architecture**
```
Flink → Iceberg Tables → Kafka → Sync Service → PostgreSQL → Superset
```

### **Implementation**
```python
# Event-driven sync service
from kafka import KafkaConsumer
import json

def sync_on_iceberg_update():
    consumer = KafkaConsumer(
        'iceberg-updates',
        bootstrap_servers=['kafka:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    for message in consumer:
        table_name = message.value['table']
        operation = message.value['operation']
        
        if table_name == 'campaign_metrics':
            sync_campaign_metrics()

# In Flink job, publish events
def publish_iceberg_event(table_name, operation):
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    producer.send('iceberg-updates', {
        'table': table_name,
        'operation': operation,
        'timestamp': datetime.now().isoformat()
    })
```

## 🎯 **Recommended Approach**

### **For Your Use Case: Strategy 1 (Direct Connection)**

**Why?**
1. **Real-time data** - Always see latest metrics
2. **No sync complexity** - Single source of truth
3. **Cost effective** - No data duplication
4. **Scalable** - Handles growing data

### **Implementation Steps**

#### **Step 1: Add Trino Service**
```yaml
# docker-compose.yml
trino:
  image: trinodb/trino:latest
  container_name: trino
  ports:
    - "8080:8080"
  environment:
    - AWS_ACCESS_KEY_ID=minioadmin
    - AWS_SECRET_ACCESS_KEY=minioadmin
  volumes:
    - ./config/trino:/etc/trino
  depends_on:
    - minio
```

#### **Step 2: Configure Trino**
```properties
# config/trino/catalog/iceberg.properties
connector.name=iceberg
iceberg.catalog.type=hive
hive.metastore.uri=thrift://hive-metastore:9083
hive.s3.endpoint=http://minio:9000
hive.s3.aws-access-key=minioadmin
hive.s3.aws-secret-key=minioadmin
```

#### **Step 3: Connect Superset**
1. **Data → Databases → + Database**
2. **Database Type**: Trino
3. **Connection String**: `trino://trino:8080/iceberg`
4. **Test Connection**

#### **Step 4: Create Datasets**
1. **Data → Datasets → + Dataset**
2. **Database**: Trino connection
3. **Schema**: default
4. **Table**: campaign_metrics

## 🔍 **Monitoring Sync Status**

### **Health Checks**
```python
def check_sync_health():
    # Check Iceberg table
    iceberg_count = table.scan().to_pandas().shape[0]
    
    # Check PostgreSQL table
    with psycopg2.connect("...") as conn:
        pg_count = pd.read_sql("SELECT COUNT(*) FROM campaign_metrics", conn).iloc[0,0]
    
    # Compare
    if iceberg_count == pg_count:
        print("✅ Sync is healthy")
    else:
        print(f"❌ Sync issue: Iceberg={iceberg_count}, PG={pg_count}")
```

### **Sync Metrics**
```python
# Track sync performance
sync_metrics = {
    'last_sync_time': datetime.now(),
    'records_synced': 1000,
    'sync_duration': 5.2,
    'sync_status': 'success'
}
```

## 🚀 **Next Steps**

1. **Choose your strategy** (recommend Strategy 1)
2. **Implement the solution**
3. **Test data consistency**
4. **Monitor sync performance**
5. **Optimize as needed**

---

**Which strategy would you like to implement?** 🎯 
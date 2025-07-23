# 🚀 Quick Chart Setup Guide

## 📊 **Manual Chart Creation (Recommended)**

Since the API approach has authentication issues, here's the quickest way to create charts:

### **Step 1: Access Superset**
```
URL: http://localhost:8088
Username: admin
Password: admin
```

### **Step 2: Create Database Connection**
1. **Go to**: Data → Databases → + Database
2. **Database Type**: PostgreSQL
3. **Connection String**: `postgresql://postgres:postgres@postgres:5432/ads_campaign`
4. **Test Connection** ✅
5. **Save**

### **Step 3: Create Dataset**
1. **Go to**: Data → Datasets → + Dataset
2. **Database**: Your PostgreSQL connection
3. **Schema**: public
4. **Table**: `campaign_metrics`
5. **Save**

### **Step 4: Create Charts (5 minutes)**

#### **Chart 1: CTR Trend**
1. **Charts → + Chart**
2. **Dataset**: campaign_metrics
3. **Chart Type**: Line Chart
4. **Time Column**: date
5. **Metrics**: AVG(ctr)
6. **Group By**: campaign_id
7. **Save as**: "CTR Trend by Campaign"

#### **Chart 2: CVR Trend**
1. **Charts → + Chart**
2. **Dataset**: campaign_metrics
3. **Chart Type**: Line Chart
4. **Time Column**: date
5. **Metrics**: AVG(cvr)
6. **Group By**: campaign_id
7. **Save as**: "CVR Trend by Campaign"

#### **Chart 3: Revenue**
1. **Charts → + Chart**
2. **Dataset**: campaign_metrics
3. **Chart Type**: Bar Chart
4. **X-Axis**: campaign_id
5. **Y-Axis**: SUM(revenue)
6. **Save as**: "Revenue by Campaign"

#### **Chart 4: Summary Table**
1. **Charts → + Chart**
2. **Dataset**: campaign_metrics
3. **Chart Type**: Table
4. **Columns**: campaign_id, platform, impressions, clicks, conversions, revenue, ctr, cvr
5. **Save as**: "Campaign Performance Summary"

### **Step 5: Create Dashboard**
1. **Dashboards → + Dashboard**
2. **Name**: "Campaign Metrics Dashboard"
3. **Add Charts**: Select all 4 charts
4. **Save**

## 🎯 **Expected Results**

You should see:
- ✅ **CTR Trend**: Line chart showing CTR over time
- ✅ **CVR Trend**: Line chart showing CVR over time  
- ✅ **Revenue Chart**: Bar chart showing revenue by campaign
- ✅ **Performance Table**: Summary table with all metrics

## 🔧 **Troubleshooting**

### **No Data Showing?**
```sql
-- Check if data exists
SELECT COUNT(*) FROM campaign_metrics;
SELECT * FROM campaign_metrics LIMIT 5;
```

### **Connection Issues?**
```bash
# Check PostgreSQL
docker compose ps postgres

# Check Superset
docker compose ps superset
```

## 📈 **Sample Data Verification**

Run this in PostgreSQL to verify data:
```sql
-- Check data exists
SELECT COUNT(*) FROM campaign_metrics;

-- Check CTR data
SELECT campaign_id, AVG(ctr) as avg_ctr 
FROM campaign_metrics 
GROUP BY campaign_id;

-- Check revenue data
SELECT campaign_id, SUM(revenue) as total_revenue 
FROM campaign_metrics 
GROUP BY campaign_id;
```

## ⚡ **Quick Commands**

```bash
# Check if services are running
docker compose ps

# Check Superset logs
docker compose logs superset

# Restart Superset if needed
docker compose restart superset
```

## 🎉 **Success!**

Once complete, you'll have:
- **Real-time dashboard** with campaign metrics
- **CTR/CVR trends** over time
- **Revenue analysis** by campaign
- **Performance summary** table

**Total time**: ~10 minutes manual setup

---

**Need help?** Check the logs or restart services! 🚀 
# 📊 Superset Charts Setup Guide

## 🚀 **Quick Setup Steps**

### **1. Access Superset**
```
URL: http://localhost:8088
Username: admin
Password: admin
```

### **2. Connect Database**
1. **Data → Databases → + Database**
2. **Database Type**: PostgreSQL
3. **Connection String**: `postgresql://postgres:postgres@postgres:5432/ads_campaign`
4. **Test Connection** ✅
5. **Save**

### **3. Create Dataset**
1. **Data → Datasets → + Dataset**
2. **Database**: Your PostgreSQL connection
3. **Schema**: public
4. **Table**: `campaign_metrics`
5. **Save**

### **4. Create Charts**

#### **Chart 1: CTR Trend (Line Chart)**
1. **Charts → + Chart**
2. **Dataset**: campaign_metrics
3. **Chart Type**: Line Chart
4. **Time Column**: date
5. **Metrics**: AVG(ctr)
6. **Group By**: campaign_id
7. **Save as**: "CTR Trend by Campaign"

#### **Chart 2: CVR Trend (Line Chart)**
1. **Charts → + Chart**
2. **Dataset**: campaign_metrics
3. **Chart Type**: Line Chart
4. **Time Column**: date
5. **Metrics**: AVG(cvr)
6. **Group By**: campaign_id
7. **Save as**: "CVR Trend by Campaign"

#### **Chart 3: Revenue by Campaign (Bar Chart)**
1. **Charts → + Chart**
2. **Dataset**: campaign_metrics
3. **Chart Type**: Bar Chart
4. **X-Axis**: campaign_id
5. **Y-Axis**: SUM(revenue)
6. **Save as**: "Revenue by Campaign"

#### **Chart 4: Platform Performance (Table)**
1. **Charts → + Chart**
2. **Dataset**: campaign_metrics
3. **Chart Type**: Table
4. **Columns**: campaign_id, platform, impressions, clicks, conversions, revenue, ctr, cvr
5. **Save as**: "Campaign Performance Summary"

### **5. Create Dashboard**
1. **Dashboards → + Dashboard**
2. **Name**: "Campaign Metrics Dashboard"
3. **Add Charts**: Select all 4 charts
4. **Save**

## 🎯 **Expected Results**

You should now see:
- ✅ **CTR Trend**: Line chart showing CTR over time
- ✅ **CVR Trend**: Line chart showing CVR over time  
- ✅ **Revenue Chart**: Bar chart showing revenue by campaign
- ✅ **Performance Table**: Summary table with all metrics

## 🔧 **Troubleshooting**

### **No Data Showing?**
- Check database connection
- Verify tables exist: `SELECT COUNT(*) FROM campaign_metrics;`
- Check dataset configuration

### **Charts Not Loading?**
- Refresh the page
- Check browser console for errors
- Verify chart configuration

### **Connection Issues?**
- Ensure PostgreSQL is running: `docker compose ps postgres`
- Check logs: `docker compose logs postgres`

## 📈 **Sample Queries to Test**

```sql
-- Test data exists
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

---

**Need help?** Check the logs or restart Superset if needed! 🚀 
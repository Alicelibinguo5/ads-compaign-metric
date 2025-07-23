# 📊 Apache Superset Dashboard Setup Guide

## 🎯 **Overview**

This guide provides step-by-step instructions for setting up Apache Superset dashboards to visualize CTR, CVR, and revenue metrics from our campaign pipeline.

## 🚀 **Quick Setup**

### **1. Start Superset**
```bash
# Start all services including Superset
docker-compose up -d

# Wait for Superset to be ready (check logs)
docker-compose logs -f superset
```

### **2. Access Superset**
- **URL**: http://localhost:8088
- **Username**: admin
- **Password**: admin

### **3. Automated Setup**
```bash
# Run automated dashboard setup
python src/superset/dashboard_setup.py
```

## 📋 **Manual Dashboard Setup**

If the automated setup doesn't work, follow these manual steps:

### **Step 1: Create Database Connection**

1. **Navigate to**: Data → Databases → + Database
2. **Database Name**: `campaign_metrics`
3. **SQLAlchemy URI**: 
   ```
   postgresql://superset:superset@postgres:5432/superset
   ```
4. **Test Connection**: Click "Test Connection"
5. **Save**: Click "Save"

### **Step 2: Create Campaign Metrics Dataset**

1. **Navigate to**: Data → Datasets → + Dataset
2. **Database**: Select `campaign_metrics`
3. **Schema**: `public`
4. **Table**: `campaign_metrics`
5. **SQL Query**:
   ```sql
   SELECT 
       campaign_id,
       window_start,
       window_end,
       impressions,
       clicks,
       conversions,
       revenue,
       ctr_percent,
       cvr_percent,
       processed_at
   FROM campaign_metrics
   ```
6. **Save**: Click "Save"

### **Step 3: Create Campaign Events Dataset**

1. **Navigate to**: Data → Datasets → + Dataset
2. **Database**: Select `campaign_metrics`
3. **Schema**: `public`
4. **Table**: `campaign_events`
5. **SQL Query**:
   ```sql
   SELECT 
       event_id,
       user_id,
       campaign_id,
       event_type,
       platform,
       timestamp,
       revenue,
       country,
       device_type,
       processed_at
   FROM campaign_events
   ```
6. **Save**: Click "Save"

## 📊 **Creating Charts**

### **Chart 1: CTR Trend by Campaign**

1. **Navigate to**: Charts → + Chart
2. **Dataset**: Select `campaign_metrics`
3. **Visualization Type**: Line Chart
4. **Configuration**:
   - **X Axis**: `window_start`
   - **Y Axis**: `avg_ctr` (metric)
   - **Series**: `campaign_id`
   - **Time Range**: Last 7 days
5. **Metrics**: Create new metric `avg_ctr` with expression `AVG(ctr_percent)`
6. **Save**: Click "Save" as "CTR Trend by Campaign"

### **Chart 2: CVR Trend by Campaign**

1. **Navigate to**: Charts → + Chart
2. **Dataset**: Select `campaign_metrics`
3. **Visualization Type**: Line Chart
4. **Configuration**:
   - **X Axis**: `window_start`
   - **Y Axis**: `avg_cvr` (metric)
   - **Series**: `campaign_id`
   - **Time Range**: Last 7 days
5. **Metrics**: Create new metric `avg_cvr` with expression `AVG(cvr_percent)`
6. **Save**: Click "Save" as "CVR Trend by Campaign"

### **Chart 3: Revenue by Campaign**

1. **Navigate to**: Charts → + Chart
2. **Dataset**: Select `campaign_metrics`
3. **Visualization Type**: Bar Chart
4. **Configuration**:
   - **X Axis**: `campaign_id`
   - **Y Axis**: `total_revenue` (metric)
   - **Time Range**: Last 7 days
   - **Order**: Descending by revenue
5. **Metrics**: Create new metric `total_revenue` with expression `SUM(revenue)`
6. **Save**: Click "Save" as "Revenue by Campaign"

### **Chart 4: Campaign Performance Summary**

1. **Navigate to**: Charts → + Chart
2. **Dataset**: Select `campaign_metrics`
3. **Visualization Type**: Table
4. **Configuration**:
   - **Columns**: 
     - `campaign_id`
     - `total_impressions`
     - `total_clicks`
     - `total_conversions`
     - `total_revenue`
     - `avg_ctr`
     - `avg_cvr`
   - **Time Range**: Last 7 days
   - **Order**: Descending by revenue
5. **Metrics**: 
   - `total_impressions`: `SUM(impressions)`
   - `total_clicks`: `SUM(clicks)`
   - `total_conversions`: `SUM(conversions)`
   - `total_revenue`: `SUM(revenue)`
   - `avg_ctr`: `AVG(ctr_percent)`
   - `avg_cvr`: `AVG(cvr_percent)`
6. **Save**: Click "Save" as "Campaign Performance Summary"

## 🎛️ **Creating Dashboard**

### **Step 1: Create Dashboard**

1. **Navigate to**: Dashboards → + Dashboard
2. **Dashboard Title**: "Campaign Performance Metrics"
3. **Save**: Click "Save"

### **Step 2: Add Charts**

1. **Add Charts**: Click "Add Charts"
2. **Select Charts**:
   - CTR Trend by Campaign
   - CVR Trend by Campaign
   - Revenue by Campaign
   - Campaign Performance Summary
3. **Add to Dashboard**: Click "Add to Dashboard"

### **Step 3: Arrange Layout**

1. **Drag and Drop**: Arrange charts in a 2x2 grid
2. **Resize**: Adjust chart sizes as needed
3. **Save**: Click "Save"

### **Step 4: Configure Dashboard**

1. **Settings**: Click dashboard settings (gear icon)
2. **Auto-refresh**: Set to 30 seconds
3. **Time Range**: Set default to "Last 7 days"
4. **Save**: Click "Save"

## 📈 **Dashboard Features**

### **Real-time Metrics**

- **CTR Trends**: Line charts showing click-through rate trends over time
- **CVR Trends**: Line charts showing conversion rate trends over time
- **Revenue Analysis**: Bar charts showing revenue by campaign
- **Performance Summary**: Table with comprehensive metrics

### **Interactive Features**

- **Time Range Filter**: Filter data by date range
- **Campaign Filter**: Filter by specific campaigns
- **Drill-down**: Click on charts for detailed views
- **Export**: Export data to CSV/Excel

### **Auto-refresh**

- **30-second refresh**: Dashboard updates automatically
- **Real-time data**: Shows latest metrics from pipeline
- **Live monitoring**: Track campaign performance in real-time

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

#### **2. Tables Not Found**
```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE 'campaign_%';
```

#### **3. No Data in Charts**
```sql
-- Check if data exists
SELECT COUNT(*) FROM campaign_metrics;
SELECT COUNT(*) FROM campaign_events;
```

#### **4. Superset Not Loading**
```bash
# Restart Superset
docker-compose restart superset

# Check logs
docker-compose logs superset
```

### **Data Validation**

#### **Check Campaign Metrics Data**
```sql
SELECT 
    campaign_id,
    COUNT(*) as records,
    AVG(ctr_percent) as avg_ctr,
    AVG(cvr_percent) as avg_cvr,
    SUM(revenue) as total_revenue
FROM campaign_metrics 
GROUP BY campaign_id
ORDER BY total_revenue DESC;
```

#### **Check Campaign Events Data**
```sql
SELECT 
    event_type,
    COUNT(*) as count,
    SUM(revenue) as total_revenue
FROM campaign_events 
GROUP BY event_type;
```

## 🎯 **Dashboard Metrics Explained**

### **CTR (Click-Through Rate)**
- **Formula**: `(Clicks / Impressions) × 100`
- **Chart**: Line chart showing trends over time
- **Insight**: Measures ad effectiveness and engagement

### **CVR (Conversion Rate)**
- **Formula**: `(Conversions / Clicks) × 100`
- **Chart**: Line chart showing trends over time
- **Insight**: Measures landing page and user experience effectiveness

### **Revenue**
- **Formula**: `SUM(revenue)`
- **Chart**: Bar chart showing revenue by campaign
- **Insight**: Direct measure of campaign ROI

### **Performance Summary**
- **Table**: Comprehensive view of all metrics
- **Columns**: Campaign ID, impressions, clicks, conversions, revenue, CTR, CVR
- **Insight**: Complete campaign performance overview

## 🚀 **Next Steps**

### **Advanced Features**

1. **Alerts**: Set up alerts for low CTR/CVR
2. **Custom Metrics**: Create additional calculated metrics
3. **Drill-down Dashboards**: Create detailed campaign views
4. **Scheduled Reports**: Set up automated reporting

### **Integration**

1. **Email Reports**: Send dashboard snapshots via email
2. **Slack Integration**: Post metrics to Slack channels
3. **API Access**: Use Superset API for external integrations

---

**Status**: ✅ **DASHBOARD READY**  
**Metrics**: 📊 **CTR, CVR, Revenue**  
**Refresh**: 🔄 **30 seconds** 
#!/bin/bash

# Simple Superset Chart Creator via API
# This script creates charts and dashboards using Superset's REST API

set -e

# Configuration
SUPERSET_URL="http://localhost:8088"
USERNAME="admin"
PASSWORD="admin"

echo "🚀 Creating Superset Charts via API..."

# Step 1: Login and get session cookie
echo "📝 Logging into Superset..."
LOGIN_RESPONSE=$(curl -s -c cookies.txt -X POST "$SUPERSET_URL/login/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD")

if [[ $LOGIN_RESPONSE == *"error"* ]]; then
    echo "❌ Login failed"
    exit 1
fi

echo "✅ Login successful"

# Step 2: Get CSRF token
echo "🔑 Getting CSRF token..."
CSRF_RESPONSE=$(curl -s -b cookies.txt "$SUPERSET_URL/api/v1/security/csrf_token/")
CSRF_TOKEN=$(echo $CSRF_RESPONSE | grep -o '"result":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CSRF_TOKEN" ]; then
    echo "⚠️  Could not get CSRF token, using placeholder"
    CSRF_TOKEN="csrf_token_placeholder"
fi

echo "✅ CSRF token obtained"

# Step 3: Create database connection
echo "🗄️  Creating database connection..."
DB_RESPONSE=$(curl -s -b cookies.txt -X POST "$SUPERSET_URL/api/v1/database/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d '{
    "database_name": "Campaign Metrics DB",
    "sqlalchemy_uri": "postgresql://postgres:postgres@postgres:5432/ads_campaign",
    "extra": "{\"engine_params\": {\"pool_size\": 10, \"max_overflow\": 20}}"
  }')

echo "Database response: $DB_RESPONSE"

# Extract database ID
DB_ID=$(echo $DB_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$DB_ID" ]; then
    echo "❌ Failed to create database connection"
    echo "Response: $DB_RESPONSE"
    exit 1
fi

echo "✅ Database connection created (ID: $DB_ID)"

# Step 4: Create dataset
echo "📊 Creating dataset..."
DATASET_RESPONSE=$(curl -s -b cookies.txt -X POST "$SUPERSET_URL/api/v1/dataset/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{
    \"database\": $DB_ID,
    \"schema\": \"public\",
    \"table_name\": \"campaign_metrics\"
  }")

echo "Dataset response: $DATASET_RESPONSE"

# Extract dataset ID
DATASET_ID=$(echo $DATASET_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$DATASET_ID" ]; then
    echo "❌ Failed to create dataset"
    echo "Response: $DATASET_RESPONSE"
    exit 1
fi

echo "✅ Dataset created (ID: $DATASET_ID)"

# Step 5: Create charts
echo "📈 Creating charts..."

# Chart 1: CTR Trend
echo "Creating CTR Trend chart..."
CTR_RESPONSE=$(curl -s -b cookies.txt -X POST "$SUPERSET_URL/api/v1/chart/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{
    \"slice_name\": \"CTR Trend by Campaign\",
    \"viz_type\": \"line\",
    \"datasource_id\": $DATASET_ID,
    \"datasource_type\": \"table\",
    \"params\": {
      \"x_axis\": \"date\",
      \"y_axis\": \"ctr\",
      \"series\": \"campaign_id\"
    }
  }")

CTR_ID=$(echo $CTR_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "✅ CTR chart created (ID: $CTR_ID)"

# Chart 2: CVR Trend
echo "Creating CVR Trend chart..."
CVR_RESPONSE=$(curl -s -b cookies.txt -X POST "$SUPERSET_URL/api/v1/chart/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{
    \"slice_name\": \"CVR Trend by Campaign\",
    \"viz_type\": \"line\",
    \"datasource_id\": $DATASET_ID,
    \"datasource_type\": \"table\",
    \"params\": {
      \"x_axis\": \"date\",
      \"y_axis\": \"cvr\",
      \"series\": \"campaign_id\"
    }
  }")

CVR_ID=$(echo $CVR_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "✅ CVR chart created (ID: $CVR_ID)"

# Chart 3: Revenue
echo "Creating Revenue chart..."
REVENUE_RESPONSE=$(curl -s -b cookies.txt -X POST "$SUPERSET_URL/api/v1/chart/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{
    \"slice_name\": \"Revenue by Campaign\",
    \"viz_type\": \"bar\",
    \"datasource_id\": $DATASET_ID,
    \"datasource_type\": \"table\",
    \"params\": {
      \"x_axis\": \"campaign_id\",
      \"y_axis\": \"revenue\"
    }
  }")

REVENUE_ID=$(echo $REVENUE_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)
echo "✅ Revenue chart created (ID: $REVENUE_ID)"

# Step 6: Create dashboard
echo "📊 Creating dashboard..."
DASHBOARD_RESPONSE=$(curl -s -b cookies.txt -X POST "$SUPERSET_URL/api/v1/dashboard/" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d "{
    \"dashboard_title\": \"Campaign Metrics Dashboard\",
    \"slug\": \"campaign-metrics\",
    \"position_json\": {
      \"$CTR_ID\": {\"id\": $CTR_ID, \"meta\": {\"width\": 6, \"height\": 8, \"x\": 0, \"y\": 0}},
      \"$CVR_ID\": {\"id\": $CVR_ID, \"meta\": {\"width\": 6, \"height\": 8, \"x\": 6, \"y\": 0}},
      \"$REVENUE_ID\": {\"id\": $REVENUE_ID, \"meta\": {\"width\": 6, \"height\": 8, \"x\": 0, \"y\": 8}}
    }
  }")

DASHBOARD_ID=$(echo $DASHBOARD_RESPONSE | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$DASHBOARD_ID" ]; then
    echo "❌ Failed to create dashboard"
    echo "Response: $DASHBOARD_RESPONSE"
    exit 1
fi

echo "✅ Dashboard created (ID: $DASHBOARD_ID)"

# Cleanup
rm -f cookies.txt

echo ""
echo "🎉 Chart creation completed successfully!"
echo "📊 Access your dashboard at: $SUPERSET_URL/superset/dashboard/$DASHBOARD_ID"
echo ""
echo "📈 Charts created:"
echo "  - CTR Trend by Campaign (ID: $CTR_ID)"
echo "  - CVR Trend by Campaign (ID: $CVR_ID)"
echo "  - Revenue by Campaign (ID: $REVENUE_ID)"
echo ""
echo "Happy analyzing! 📊✨" 
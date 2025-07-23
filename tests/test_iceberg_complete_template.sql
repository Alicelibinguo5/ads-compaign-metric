-- Complete Iceberg Test (Template)
-- Replace AWS credentials with your own values

-- 1. Create the catalog
CREATE CATALOG iceberg_catalog WITH (
    'type'='iceberg',
    'warehouse'='s3a://your-iceberg-warehouse',
    's3.endpoint'='https://s3.amazonaws.com',
    's3.access-key'='YOUR_AWS_ACCESS_KEY',
    's3.secret-key'='YOUR_AWS_SECRET_KEY',
    's3.region'='your-region'
);

-- 2. Use the catalog
USE CATALOG iceberg_catalog;

-- 3. Show catalogs to verify
SHOW CATALOGS;

-- 4. Create a test table
CREATE TABLE IF NOT EXISTS test_campaign_events (
    event_id STRING,
    user_id STRING,
    campaign_id STRING,
    event_type STRING,
    platform STRING,
    timestamp TIMESTAMP(3),
    revenue DOUBLE,
    country STRING
) PARTITIONED BY (campaign_id, platform)
WITH (
    'connector' = 'iceberg',
    'write-format' = 'parquet'
);

-- 5. Show tables
SHOW TABLES;

-- 6. Insert test data
INSERT INTO test_campaign_events VALUES
('evt_001', 'user_001', 'camp_001', 'impression', 'ios', 
 TIMESTAMP '2024-01-01 10:00:00', NULL, 'US'),
('evt_002', 'user_002', 'camp_001', 'click', 'android', 
 TIMESTAMP '2024-01-01 10:01:00', 0.50, 'CA');

-- 7. Query the data
SELECT COUNT(*) as total_events FROM test_campaign_events; 
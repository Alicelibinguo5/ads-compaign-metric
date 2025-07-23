-- Test Iceberg Catalog Creation (Template)
-- Replace AWS credentials with your own values
CREATE CATALOG iceberg_catalog WITH (
    'type'='iceberg',
    'warehouse'='s3a://your-iceberg-warehouse',
    's3.endpoint'='https://s3.amazonaws.com',
    's3.access-key'='YOUR_AWS_ACCESS_KEY',
    's3.secret-key'='YOUR_AWS_SECRET_KEY',
    's3.region'='your-region'
);

-- Use the catalog
USE CATALOG iceberg_catalog;

-- Show catalogs to verify
SHOW CATALOGS; 
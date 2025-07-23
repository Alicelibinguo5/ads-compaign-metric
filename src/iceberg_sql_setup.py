"""
Local Iceberg SQL Setup for Ads Campaign Metrics.

This module provides a simple way to create and manage Iceberg tables
using SQL commands locally without requiring the full Flink runtime.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd
from pyiceberg.catalog import load_catalog
from pyiceberg.io import fsspec

from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalIcebergManager:
    """Local Iceberg manager for creating and managing tables via SQL."""
    
    def __init__(self, warehouse_path: Optional[str] = None):
        """
        Initialize local Iceberg manager.
        
        Args:
            warehouse_path: Local path for Iceberg warehouse
        """
        self.warehouse_path = warehouse_path or "./iceberg-warehouse"
        self.catalog = None
        self._setup_local_warehouse()
    
    def _setup_local_warehouse(self) -> None:
        """Set up local warehouse directory."""
        warehouse_dir = Path(self.warehouse_path)
        warehouse_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local Iceberg warehouse created at: {warehouse_dir.absolute()}")
    
    def create_local_catalog(self) -> None:
        """Create a local file-based Iceberg catalog."""
        try:
            # Create catalog configuration
            catalog_config = {
                "type": "rest",
                "uri": "http://localhost:8181",
                "warehouse": self.warehouse_path,
                "py-io-impl": "pyiceberg.io.fsspec.FsspecFileIO",
                "s3.endpoint": settings.iceberg_s3_endpoint,
                "s3.access-key": settings.iceberg_s3_access_key,
                "s3.secret-key": settings.iceberg_s3_secret_key,
            }
            
            # For local development, we'll use a simpler approach
            logger.info("Setting up local Iceberg catalog...")
            logger.info(f"Warehouse path: {self.warehouse_path}")
            
        except Exception as e:
            logger.error(f"Failed to create catalog: {e}")
            raise
    
    def create_campaign_events_table_sql(self) -> str:
        """
        Generate SQL to create campaign events table.
        
        Returns:
            SQL CREATE TABLE statement
        """
        return """
        CREATE TABLE IF NOT EXISTS campaign_events (
            event_id STRING,
            user_id STRING,
            campaign_id STRING,
            event_type STRING,
            platform STRING,
            timestamp TIMESTAMP(3),
            revenue DOUBLE,
            currency STRING,
            country STRING,
            device_type STRING,
            app_version STRING,
            creative_id STRING,
            placement_id STRING,
            metadata STRING,
            processed_at TIMESTAMP(3)
        ) PARTITIONED BY (campaign_id, platform, event_type)
        WITH (
            'connector' = 'iceberg',
            'write-format' = 'parquet',
            'write.upsert.enabled' = 'true',
            'write.metadata.delete-after-commit.enabled' = 'true',
            'write.metadata.previous-versions-max' = '10'
        )
        """
    
    def create_user_profiles_table_sql(self) -> str:
        """
        Generate SQL to create user profiles table.
        
        Returns:
            SQL CREATE TABLE statement
        """
        return """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id STRING,
            age INT,
            gender STRING,
            country STRING,
            language STRING,
            platform STRING,
            registration_date TIMESTAMP(3),
            last_active TIMESTAMP(3),
            total_revenue DOUBLE,
            total_events INT,
            preferences STRING,
            updated_at TIMESTAMP(3),
            PRIMARY KEY (user_id) NOT ENFORCED
        ) PARTITIONED BY (country, platform)
        WITH (
            'connector' = 'iceberg',
            'write-format' = 'parquet',
            'write.upsert.enabled' = 'true'
        )
        """
    
    def create_campaign_summaries_table_sql(self) -> str:
        """
        Generate SQL to create campaign summaries table.
        
        Returns:
            SQL CREATE TABLE statement
        """
        return """
        CREATE TABLE IF NOT EXISTS campaign_summaries (
            campaign_id STRING,
            date STRING,
            platform STRING,
            impressions BIGINT,
            clicks BIGINT,
            conversions BIGINT,
            revenue DOUBLE,
            ctr DOUBLE,
            cvr DOUBLE,
            cpc DOUBLE,
            cpa DOUBLE,
            roas DOUBLE,
            unique_users BIGINT,
            new_users BIGINT,
            created_at TIMESTAMP(3),
            updated_at TIMESTAMP(3),
            PRIMARY KEY (campaign_id, date, platform) NOT ENFORCED
        ) PARTITIONED BY (date, platform)
        WITH (
            'connector' = 'iceberg',
            'write-format' = 'parquet',
            'write.upsert.enabled' = 'true'
        )
        """
    
    def create_sample_data_sql(self) -> str:
        """
        Generate SQL to insert sample data.
        
        Returns:
            SQL INSERT statements
        """
        return """
        INSERT INTO campaign_events VALUES
        ('evt_001', 'user_001', 'camp_001', 'impression', 'ios', 
         TIMESTAMP '2024-01-01 10:00:00', NULL, 'USD', 'US', 'iPhone', '1.0.0', 
         'creative_001', 'placement_001', '{"source": "mobile_app"}', 
         TIMESTAMP '2024-01-01 10:00:01'),
        ('evt_002', 'user_001', 'camp_001', 'click', 'ios', 
         TIMESTAMP '2024-01-01 10:01:00', NULL, 'USD', 'US', 'iPhone', '1.0.0', 
         'creative_001', 'placement_001', '{"source": "mobile_app"}', 
         TIMESTAMP '2024-01-01 10:01:01'),
        ('evt_003', 'user_001', 'camp_001', 'conversion', 'ios', 
         TIMESTAMP '2024-01-01 10:05:00', 25.0, 'USD', 'US', 'iPhone', '1.0.0', 
         'creative_001', 'placement_001', '{"source": "mobile_app", "conversion_type": "purchase"}', 
         TIMESTAMP '2024-01-01 10:05:01')
        """
    
    def query_campaign_metrics_sql(self) -> str:
        """
        Generate SQL to query campaign metrics.
        
        Returns:
            SQL SELECT statement
        """
        return """
        SELECT 
            campaign_id,
            platform,
            COUNT(*) as total_events,
            COUNT(DISTINCT user_id) as unique_users,
            SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) as impressions,
            SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) as clicks,
            SUM(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) as conversions,
            SUM(revenue) as total_revenue,
            CASE 
                WHEN SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) > 0 
                THEN CAST(SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS DOUBLE) / 
                     CAST(SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) AS DOUBLE)
                ELSE 0.0 
            END as ctr,
            CASE 
                WHEN SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) > 0 
                THEN CAST(SUM(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) AS DOUBLE) / 
                     CAST(SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS DOUBLE)
                ELSE 0.0 
            END as cvr
        FROM campaign_events
        GROUP BY campaign_id, platform
        """
    
    def run_sql_examples(self) -> None:
        """Run SQL examples to demonstrate Iceberg table operations."""
        logger.info("=== Iceberg SQL Examples ===")
        
        # Example 1: Create tables
        logger.info("\n1. Creating Iceberg Tables:")
        logger.info(self.create_campaign_events_table_sql())
        logger.info(self.create_user_profiles_table_sql())
        logger.info(self.create_campaign_summaries_table_sql())
        
        # Example 2: Insert data
        logger.info("\n2. Inserting Sample Data:")
        logger.info(self.create_sample_data_sql())
        
        # Example 3: Query data
        logger.info("\n3. Querying Campaign Metrics:")
        logger.info(self.query_campaign_metrics_sql())
        
        # Example 4: Schema evolution
        logger.info("\n4. Schema Evolution:")
        schema_evolution_sql = """
        ALTER TABLE campaign_events ADD COLUMN attribution_source STRING;
        ALTER TABLE campaign_events ADD COLUMN user_segment STRING;
        """
        logger.info(schema_evolution_sql)
        
        # Example 5: Time travel
        logger.info("\n5. Time Travel Queries:")
        time_travel_sql = """
        -- Query specific snapshot
        SELECT * FROM campaign_events FOR VERSION AS OF 1;
        
        -- Query specific timestamp
        SELECT * FROM campaign_events FOR TIMESTAMP AS OF '2024-01-01 10:00:00';
        """
        logger.info(time_travel_sql)
        
        logger.info("\n=== SQL Examples Completed ===")


def create_iceberg_sql_script() -> str:
    """
    Create a complete SQL script for Iceberg operations.
    
    Returns:
        Complete SQL script as string
    """
    return """
-- Iceberg SQL Script for Ads Campaign Metrics
-- This script can be run in any SQL client that supports Iceberg

-- 1. Create campaign events table
CREATE TABLE IF NOT EXISTS campaign_events (
    event_id STRING,
    user_id STRING,
    campaign_id STRING,
    event_type STRING,
    platform STRING,
    timestamp TIMESTAMP(3),
    revenue DOUBLE,
    currency STRING,
    country STRING,
    device_type STRING,
    app_version STRING,
    creative_id STRING,
    placement_id STRING,
    metadata STRING,
    processed_at TIMESTAMP(3)
) PARTITIONED BY (campaign_id, platform, event_type)
WITH (
    'connector' = 'iceberg',
    'write-format' = 'parquet',
    'write.upsert.enabled' = 'true'
);

-- 2. Create user profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id STRING,
    age INT,
    gender STRING,
    country STRING,
    language STRING,
    platform STRING,
    registration_date TIMESTAMP(3),
    last_active TIMESTAMP(3),
    total_revenue DOUBLE,
    total_events INT,
    preferences STRING,
    updated_at TIMESTAMP(3),
    PRIMARY KEY (user_id) NOT ENFORCED
) PARTITIONED BY (country, platform)
WITH (
    'connector' = 'iceberg',
    'write-format' = 'parquet',
    'write.upsert.enabled' = 'true'
);

-- 3. Insert sample campaign events
INSERT INTO campaign_events VALUES
('evt_001', 'user_001', 'camp_001', 'impression', 'ios', 
 TIMESTAMP '2024-01-01 10:00:00', NULL, 'USD', 'US', 'iPhone', '1.0.0', 
 'creative_001', 'placement_001', '{"source": "mobile_app"}', 
 TIMESTAMP '2024-01-01 10:00:01'),
('evt_002', 'user_001', 'camp_001', 'click', 'ios', 
 TIMESTAMP '2024-01-01 10:01:00', NULL, 'USD', 'US', 'iPhone', '1.0.0', 
 'creative_001', 'placement_001', '{"source": "mobile_app"}', 
 TIMESTAMP '2024-01-01 10:01:01'),
('evt_003', 'user_001', 'camp_001', 'conversion', 'ios', 
 TIMESTAMP '2024-01-01 10:05:00', 25.0, 'USD', 'US', 'iPhone', '1.0.0', 
 'creative_001', 'placement_001', '{"source": "mobile_app", "conversion_type": "purchase"}', 
 TIMESTAMP '2024-01-01 10:05:01'),
('evt_004', 'user_002', 'camp_001', 'impression', 'android', 
 TIMESTAMP '2024-01-01 10:02:00', NULL, 'USD', 'US', 'Samsung Galaxy', '1.0.0', 
 'creative_001', 'placement_001', '{"source": "mobile_app"}', 
 TIMESTAMP '2024-01-01 10:02:01'),
('evt_005', 'user_002', 'camp_001', 'click', 'android', 
 TIMESTAMP '2024-01-01 10:03:00', NULL, 'USD', 'US', 'Samsung Galaxy', '1.0.0', 
 'creative_001', 'placement_001', '{"source": "mobile_app"}', 
 TIMESTAMP '2024-01-01 10:03:01');

-- 4. Query campaign metrics
SELECT 
    campaign_id,
    platform,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_id) as unique_users,
    SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) as impressions,
    SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) as clicks,
    SUM(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) as conversions,
    SUM(revenue) as total_revenue,
    CASE 
        WHEN SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) > 0 
        THEN CAST(SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS DOUBLE) / 
             CAST(SUM(CASE WHEN event_type = 'impression' THEN 1 ELSE 0 END) AS DOUBLE)
        ELSE 0.0 
    END as ctr,
    CASE 
        WHEN SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) > 0 
        THEN CAST(SUM(CASE WHEN event_type = 'conversion' THEN 1 ELSE 0 END) AS DOUBLE) / 
             CAST(SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS DOUBLE)
        ELSE 0.0 
    END as cvr
FROM campaign_events
GROUP BY campaign_id, platform;

-- 5. Schema evolution (add new columns)
ALTER TABLE campaign_events ADD COLUMN attribution_source STRING;
ALTER TABLE campaign_events ADD COLUMN user_segment STRING;

-- 6. Update data with new columns
UPDATE campaign_events 
SET attribution_source = 'organic', user_segment = 'high_value'
WHERE user_id = 'user_001';

-- 7. Time travel query (query specific snapshot)
-- SELECT * FROM campaign_events FOR VERSION AS OF 1;

-- 8. Show table history
-- DESCRIBE HISTORY campaign_events;
"""


def main() -> None:
    """Main function to demonstrate Iceberg SQL operations."""
    logger.info("Starting Local Iceberg SQL Examples")
    
    # Create Iceberg manager
    iceberg_manager = LocalIcebergManager()
    
    # Run SQL examples
    iceberg_manager.run_sql_examples()
    
    # Create SQL script file
    sql_script = create_iceberg_sql_script()
    script_path = Path("iceberg_setup.sql")
    
    with open(script_path, "w") as f:
        f.write(sql_script)
    
    logger.info(f"SQL script created at: {script_path.absolute()}")
    logger.info("You can now run these SQL commands in any Iceberg-compatible SQL client!")


if __name__ == "__main__":
    main() 
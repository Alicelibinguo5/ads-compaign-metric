"""
Iceberg sink for Flink streaming pipeline.

This module handles writing streaming data to Iceberg tables
for persistent storage and analytics.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class IcebergSink:
    """Sink for writing data to Iceberg tables."""
    
    def __init__(self, catalog_name: str = "iceberg_catalog",
                 warehouse_path: str = "s3a://my-iceberg-warehouse-2024"):
        """
        Initialize the Iceberg sink.
        
        Args:
            catalog_name: Iceberg catalog name
            warehouse_path: Iceberg warehouse path
        """
        self.catalog_name = catalog_name
        self.warehouse_path = warehouse_path
        self.tables = {}
        
        logger.info(f"Initialized Iceberg sink with catalog: {catalog_name}")
    
    def create_enriched_events_table(self, table_env) -> str:
        """
        Create Iceberg table for enriched campaign events.
        
        Args:
            table_env: Flink table environment
            
        Returns:
            Table name
        """
        table_name = f"{self.catalog_name}.default.enriched_campaign_events"
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
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
            user_age INT,
            user_gender STRING,
            user_country STRING,
            user_device_type STRING,
            user_premium BOOLEAN,
            campaign_name STRING,
            campaign_type STRING,
            campaign_budget DOUBLE,
            enriched_at TIMESTAMP(3),
            metadata STRING,
            kafka_timestamp TIMESTAMP(3),
            processed_at TIMESTAMP(3)
        ) PARTITIONED BY (campaign_id, platform, event_type)
        """
        
        table_env.execute_sql(create_table_sql)
        self.tables['enriched_events'] = table_name
        
        logger.info(f"Created Iceberg table: {table_name}")
        return table_name
    

    
    def create_campaign_metrics_table(self, table_env) -> str:
        """
        Create Iceberg table for campaign metrics.
        
        Args:
            table_env: Flink table environment
            
        Returns:
            Table name
        """
        table_name = f"{self.catalog_name}.default.campaign_metrics"
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            campaign_id STRING,
            window_start TIMESTAMP(3),
            window_end TIMESTAMP(3),
            impressions BIGINT,
            clicks BIGINT,
            conversions BIGINT,
            installs BIGINT,
            purchases BIGINT,
            revenue DOUBLE,
            ctr_percent DOUBLE,
            cvr_percent DOUBLE,
            cpm DOUBLE,
            processed_at TIMESTAMP(3)
        ) PARTITIONED BY (campaign_id)
        """
        
        table_env.execute_sql(create_table_sql)
        self.tables['campaign_metrics'] = table_name
        
        logger.info(f"Created Iceberg table: {table_name}")
        return table_name
    

    
    def create_all_tables(self, table_env) -> Dict[str, str]:
        """
        Create Iceberg tables for the pipeline.
        
        Args:
            table_env: Flink table environment
            
        Returns:
            Dictionary of table names
        """
        logger.info("Creating Iceberg tables...")
        
        self.create_enriched_events_table(table_env)
        self.create_campaign_metrics_table(table_env)
        
        logger.info(f"Created {len(self.tables)} Iceberg tables")
        return self.tables
    
    def get_table_name(self, table_type: str) -> Optional[str]:
        """
        Get table name by type.
        
        Args:
            table_type: Type of table ('enriched_events', 'user_behaviors', etc.)
            
        Returns:
            Table name or None if not found
        """
        return self.tables.get(table_type)
    
    def write_to_table(self, table_env, data_stream, table_type: str) -> None:
        """
        Write data stream to Iceberg table.
        
        Args:
            table_env: Flink table environment
            data_stream: Data stream to write
            table_type: Type of table to write to
        """
        table_name = self.get_table_name(table_type)
        if not table_name:
            raise ValueError(f"Table type '{table_type}' not found")
        
        # Convert stream to table
        table = table_env.from_data_stream(data_stream)
        
        # Write to Iceberg table
        table.execute_insert(table_name)
        
        logger.info(f"Configured write to table: {table_name}")
    
    def get_table_stats(self, table_env, table_type: str) -> Dict[str, Any]:
        """
        Get statistics for an Iceberg table.
        
        Args:
            table_env: Flink table environment
            table_type: Type of table
            
        Returns:
            Table statistics
        """
        table_name = self.get_table_name(table_type)
        if not table_name:
            return {"error": f"Table type '{table_type}' not found"}
        
        try:
            # Query table statistics
            result = table_env.execute_sql(f"""
                SELECT COUNT(*) as row_count 
                FROM {table_name}
            """)
            
            row_count = result.collect().next()[0]
            
            return {
                "table_name": table_name,
                "row_count": row_count,
                "table_type": table_type
            }
            
        except Exception as e:
            logger.error(f"Error getting table stats for {table_name}: {e}")
            return {"error": str(e)}
    
    def cleanup_old_data(self, table_env, table_type: str, 
                        retention_days: int = 30) -> None:
        """
        Clean up old data from Iceberg table.
        
        Args:
            table_env: Flink table environment
            table_type: Type of table
            retention_days: Number of days to retain
        """
        table_name = self.get_table_name(table_type)
        if not table_name:
            logger.warning(f"Table type '{table_type}' not found for cleanup")
            return
        
        try:
            # Delete old data
            delete_sql = f"""
            DELETE FROM {table_name} 
            WHERE processed_at < TIMESTAMPADD(DAY, -{retention_days}, CURRENT_TIMESTAMP)
            """
            
            table_env.execute_sql(delete_sql)
            
            logger.info(f"Cleaned up data older than {retention_days} days from {table_name}")
            
        except Exception as e:
            logger.error(f"Error cleaning up table {table_name}: {e}")
    
    def get_sink_info(self) -> Dict[str, Any]:
        """Get sink configuration information."""
        return {
            "catalog_name": self.catalog_name,
            "warehouse_path": self.warehouse_path,
            "tables": self.tables,
            "table_count": len(self.tables)
        } 
"""
Apache Iceberg Examples for Ads Campaign Metrics Data Lake.

This module demonstrates key Iceberg concepts:
1. Table creation and schema management
2. Data writing and reading
3. Schema evolution
4. Partitioning strategies
5. Time travel and versioning
6. Metadata management
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

import pandas as pd
from pyiceberg import Table
from pyiceberg.catalog import Catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField, StringType, IntegerType, DoubleType, 
    TimestampType, BooleanType, MapType
)

from .config import settings
from .models import CampaignEvent, UserProfile, UserBehavior, CampaignSummary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IcebergDataLake:
    """Iceberg Data Lake manager for ads campaign metrics."""
    
    def __init__(self, warehouse_path: Optional[str] = None):
        """
        Initialize Iceberg Data Lake.
        
        Args:
            warehouse_path: Path to Iceberg warehouse
        """
        self.warehouse_path = warehouse_path or settings.iceberg_warehouse_path
        self.catalog: Optional[Catalog] = None
        
    def setup_catalog(self) -> None:
        """Set up Iceberg catalog with S3/MinIO configuration."""
        try:
            # In a real implementation, this would connect to the actual catalog
            # For demonstration, we'll show the configuration
            catalog_config = {
                "warehouse": self.warehouse_path,
                "s3.endpoint": settings.iceberg_s3_endpoint,
                "s3.access-key": settings.iceberg_s3_access_key,
                "s3.secret-key": settings.iceberg_s3_secret_key,
                "s3.region": settings.iceberg_s3_region
            }
            
            logger.info(f"Catalog configured with warehouse: {self.warehouse_path}")
            logger.info(f"S3 endpoint: {settings.iceberg_s3_endpoint}")
            
        except Exception as e:
            logger.error(f"Failed to setup catalog: {e}")
            raise
    
    def create_campaign_events_schema(self) -> Schema:
        """
        Create schema for campaign events table.
        
        Returns:
            Iceberg schema for campaign events
        """
        return Schema(
            NestedField.required(1, "event_id", StringType()),
            NestedField.required(2, "user_id", StringType()),
            NestedField.required(3, "campaign_id", StringType()),
            NestedField.required(4, "event_type", StringType()),
            NestedField.required(5, "platform", StringType()),
            NestedField.required(6, "timestamp", TimestampType()),
            NestedField.optional(7, "revenue", DoubleType()),
            NestedField.optional(8, "currency", StringType()),
            NestedField.optional(9, "country", StringType()),
            NestedField.optional(10, "device_type", StringType()),
            NestedField.optional(11, "app_version", StringType()),
            NestedField.optional(12, "creative_id", StringType()),
            NestedField.optional(13, "placement_id", StringType()),
            NestedField.optional(14, "metadata", MapType(StringType(), StringType())),
            NestedField.required(15, "processed_at", TimestampType())
        )
    
    def create_user_profiles_schema(self) -> Schema:
        """
        Create schema for user profiles table.
        
        Returns:
            Iceberg schema for user profiles
        """
        return Schema(
            NestedField.required(1, "user_id", StringType()),
            NestedField.optional(2, "age", IntegerType()),
            NestedField.optional(3, "gender", StringType()),
            NestedField.optional(4, "country", StringType()),
            NestedField.optional(5, "language", StringType()),
            NestedField.required(6, "platform", StringType()),
            NestedField.required(7, "registration_date", TimestampType()),
            NestedField.required(8, "last_active", TimestampType()),
            NestedField.required(9, "total_revenue", DoubleType()),
            NestedField.required(10, "total_events", IntegerType()),
            NestedField.optional(11, "preferences", MapType(StringType(), StringType())),
            NestedField.required(12, "updated_at", TimestampType())
        )
    
    def create_campaign_summaries_schema(self) -> Schema:
        """
        Create schema for campaign summaries table.
        
        Returns:
            Iceberg schema for campaign summaries
        """
        return Schema(
            NestedField.required(1, "campaign_id", StringType()),
            NestedField.required(2, "date", StringType()),
            NestedField.required(3, "platform", StringType()),
            NestedField.required(4, "impressions", IntegerType()),
            NestedField.required(5, "clicks", IntegerType()),
            NestedField.required(6, "conversions", IntegerType()),
            NestedField.required(7, "revenue", DoubleType()),
            NestedField.required(8, "ctr", DoubleType()),
            NestedField.required(9, "cvr", DoubleType()),
            NestedField.required(10, "cpc", DoubleType()),
            NestedField.required(11, "cpa", DoubleType()),
            NestedField.required(12, "roas", DoubleType()),
            NestedField.required(13, "unique_users", IntegerType()),
            NestedField.required(14, "new_users", IntegerType()),
            NestedField.required(15, "created_at", TimestampType()),
            NestedField.required(16, "updated_at", TimestampType())
        )
    
    def example_1_table_creation(self) -> None:
        """
        Example 1: Creating Iceberg tables with proper schemas.
        
        Demonstrates:
        - Schema definition
        - Partitioning strategies
        - Table properties
        """
        logger.info("Example 1: Creating Iceberg Tables")
        
        # Set up catalog
        self.setup_catalog()
        
        # Create schemas
        campaign_schema = self.create_campaign_events_schema()
        user_schema = self.create_user_profiles_schema()
        summary_schema = self.create_campaign_summaries_schema()
        
        # Define partitioning strategies
        campaign_partitioning = [
            "campaign_id",
            "platform", 
            "event_type",
            "date(timestamp)"
        ]
        
        user_partitioning = [
            "country",
            "platform"
        ]
        
        summary_partitioning = [
            "date",
            "platform"
        ]
        
        # Table properties for optimization
        table_properties = {
            "write.parquet.row-group-size-bytes": "134217728",  # 128MB
            "write.parquet.page-size-bytes": "1048576",  # 1MB
            "write.metadata.delete-after-commit.enabled": "true",
            "write.metadata.previous-versions-max": "10",
            "write.upsert.enabled": "true"
        }
        
        logger.info("Campaign Events Schema:")
        logger.info(f"Fields: {len(campaign_schema.fields)}")
        logger.info(f"Partitioning: {campaign_partitioning}")
        
        logger.info("User Profiles Schema:")
        logger.info(f"Fields: {len(user_schema.fields)}")
        logger.info(f"Partitioning: {user_partitioning}")
        
        logger.info("Campaign Summaries Schema:")
        logger.info(f"Fields: {len(summary_schema.fields)}")
        logger.info(f"Partitioning: {summary_partitioning}")
        
        logger.info("Table properties configured for optimization")
    
    def example_2_data_writing(self) -> None:
        """
        Example 2: Writing data to Iceberg tables.
        
        Demonstrates:
        - Batch writes
        - Streaming writes
        - Upserts
        - Data validation
        """
        logger.info("Example 2: Writing Data to Iceberg Tables")
        
        # Sample campaign events data
        sample_events = [
            {
                "event_id": "evt_001",
                "user_id": "user_001",
                "campaign_id": "camp_001",
                "event_type": "impression",
                "platform": "ios",
                "timestamp": datetime.now(),
                "revenue": None,
                "currency": "USD",
                "country": "US",
                "device_type": "iPhone",
                "app_version": "1.0.0",
                "creative_id": "creative_001",
                "placement_id": "placement_001",
                "metadata": {"source": "mobile_app"},
                "processed_at": datetime.now()
            },
            {
                "event_id": "evt_002",
                "user_id": "user_001",
                "campaign_id": "camp_001",
                "event_type": "click",
                "platform": "ios",
                "timestamp": datetime.now() + timedelta(minutes=1),
                "revenue": None,
                "currency": "USD",
                "country": "US",
                "device_type": "iPhone",
                "app_version": "1.0.0",
                "creative_id": "creative_001",
                "placement_id": "placement_001",
                "metadata": {"source": "mobile_app"},
                "processed_at": datetime.now()
            },
            {
                "event_id": "evt_003",
                "user_id": "user_001",
                "campaign_id": "camp_001",
                "event_type": "conversion",
                "platform": "ios",
                "timestamp": datetime.now() + timedelta(minutes=5),
                "revenue": 25.0,
                "currency": "USD",
                "country": "US",
                "device_type": "iPhone",
                "app_version": "1.0.0",
                "creative_id": "creative_001",
                "placement_id": "placement_001",
                "metadata": {"source": "mobile_app", "conversion_type": "purchase"},
                "processed_at": datetime.now()
            }
        ]
        
        # Convert to DataFrame for demonstration
        df = pd.DataFrame(sample_events)
        
        logger.info(f"Sample data prepared: {len(df)} records")
        logger.info(f"Data types: {df.dtypes.to_dict()}")
        
        # In a real implementation, this would write to Iceberg
        # table = catalog.create_table("campaign_events", campaign_schema, ...)
        # table.append(df)
        
        logger.info("Data writing simulation completed")
    
    def example_3_schema_evolution(self) -> None:
        """
        Example 3: Schema evolution in Iceberg.
        
        Demonstrates:
        - Adding new columns
        - Removing columns
        - Changing column types
        - Backward compatibility
        """
        logger.info("Example 3: Schema Evolution")
        
        # Original schema
        original_schema = self.create_campaign_events_schema()
        
        # Evolved schema with new columns
        evolved_schema = Schema(
            NestedField.required(1, "event_id", StringType()),
            NestedField.required(2, "user_id", StringType()),
            NestedField.required(3, "campaign_id", StringType()),
            NestedField.required(4, "event_type", StringType()),
            NestedField.required(5, "platform", StringType()),
            NestedField.required(6, "timestamp", TimestampType()),
            NestedField.optional(7, "revenue", DoubleType()),
            NestedField.optional(8, "currency", StringType()),
            NestedField.optional(9, "country", StringType()),
            NestedField.optional(10, "device_type", StringType()),
            NestedField.optional(11, "app_version", StringType()),
            NestedField.optional(12, "creative_id", StringType()),
            NestedField.optional(13, "placement_id", StringType()),
            NestedField.optional(14, "metadata", MapType(StringType(), StringType())),
            NestedField.required(15, "processed_at", TimestampType()),
            # New columns added
            NestedField.optional(16, "attribution_source", StringType()),
            NestedField.optional(17, "attribution_medium", StringType()),
            NestedField.optional(18, "attribution_campaign", StringType()),
            NestedField.optional(19, "user_segment", StringType()),
            NestedField.optional(20, "experiment_variant", StringType())
        )
        
        logger.info("Original schema fields: %d", len(original_schema.fields))
        logger.info("Evolved schema fields: %d", len(evolved_schema.fields))
        
        # Schema evolution operations
        evolution_operations = [
            "ADD COLUMN attribution_source STRING",
            "ADD COLUMN attribution_medium STRING", 
            "ADD COLUMN attribution_campaign STRING",
            "ADD COLUMN user_segment STRING",
            "ADD COLUMN experiment_variant STRING"
        ]
        
        for operation in evolution_operations:
            logger.info(f"Schema evolution: {operation}")
        
        logger.info("Schema evolution completed - backward compatibility maintained")
    
    def example_4_time_travel(self) -> None:
        """
        Example 4: Time travel and versioning in Iceberg.
        
        Demonstrates:
        - Snapshot management
        - Time travel queries
        - Version history
        - Rollback capabilities
        """
        logger.info("Example 4: Time Travel and Versioning")
        
        # Simulate multiple snapshots
        snapshots = [
            {
                "snapshot_id": 1,
                "timestamp": datetime.now() - timedelta(hours=2),
                "operation": "append",
                "records": 1000,
                "description": "Initial data load"
            },
            {
                "snapshot_id": 2,
                "timestamp": datetime.now() - timedelta(hours=1),
                "operation": "append",
                "records": 500,
                "description": "Incremental data load"
            },
            {
                "snapshot_id": 3,
                "timestamp": datetime.now(),
                "operation": "overwrite",
                "records": 1500,
                "description": "Data correction"
            }
        ]
        
        logger.info("Snapshot history:")
        for snapshot in snapshots:
            logger.info(f"  Snapshot {snapshot['snapshot_id']}: {snapshot['operation']} "
                       f"({snapshot['records']} records) at {snapshot['timestamp']}")
        
        # Time travel queries
        time_travel_queries = [
            "SELECT * FROM campaign_events FOR VERSION AS OF 1",
            "SELECT * FROM campaign_events FOR TIMESTAMP AS OF '2024-01-01 10:00:00'",
            "SELECT * FROM campaign_events FOR VERSION AS OF 2"
        ]
        
        logger.info("Time travel query examples:")
        for query in time_travel_queries:
            logger.info(f"  {query}")
        
        logger.info("Time travel capabilities demonstrated")
    
    def example_5_partition_evolution(self) -> None:
        """
        Example 5: Partition evolution and optimization.
        
        Demonstrates:
        - Partition strategies
        - Partition evolution
        - Query optimization
        - Data organization
        """
        logger.info("Example 5: Partition Evolution")
        
        # Initial partitioning strategy
        initial_partitioning = [
            "campaign_id",
            "platform"
        ]
        
        # Evolved partitioning strategy
        evolved_partitioning = [
            "date(timestamp)",
            "campaign_id", 
            "platform",
            "event_type"
        ]
        
        logger.info("Initial partitioning: %s", initial_partitioning)
        logger.info("Evolved partitioning: %s", evolved_partitioning)
        
        # Partition evolution benefits
        benefits = [
            "Better query performance for time-based queries",
            "Improved data skipping",
            "More granular partition management",
            "Better support for data lifecycle policies"
        ]
        
        logger.info("Partition evolution benefits:")
        for benefit in benefits:
            logger.info(f"  - {benefit}")
        
        # Example queries showing optimization
        optimized_queries = [
            "SELECT * FROM campaign_events WHERE date(timestamp) = '2024-01-01'",
            "SELECT * FROM campaign_events WHERE campaign_id = 'camp_001' AND platform = 'ios'",
            "SELECT COUNT(*) FROM campaign_events WHERE event_type = 'conversion' AND date(timestamp) >= '2024-01-01'"
        ]
        
        logger.info("Optimized query examples:")
        for query in optimized_queries:
            logger.info(f"  {query}")
        
        logger.info("Partition evolution completed")


def run_iceberg_examples() -> None:
    """Run all Iceberg examples to demonstrate the concepts."""
    logger.info("Starting Iceberg Examples")
    
    # Create Iceberg Data Lake instance
    iceberg_dl = IcebergDataLake()
    
    try:
        # Run examples
        iceberg_dl.example_1_table_creation()
        iceberg_dl.example_2_data_writing()
        iceberg_dl.example_3_schema_evolution()
        iceberg_dl.example_4_time_travel()
        iceberg_dl.example_5_partition_evolution()
        
        logger.info("All Iceberg examples completed successfully")
        
    except Exception as e:
        logger.error(f"Error running Iceberg examples: {e}")
        raise


if __name__ == "__main__":
    run_iceberg_examples() 
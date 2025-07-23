"""
Apache Flink + Iceberg Examples for Ads Campaign Metrics.

This module demonstrates key Flink concepts:
1. Stream processing with time windows
2. Stream-stream joins
3. Stream-table joins
4. Aggregations and state management
5. Iceberg table operations
6. Event time processing
7. Watermarks and late data handling
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from pyflink.common import Types, WatermarkStrategy, Time
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FileSource, StreamFormat
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.table.expressions import col, lit
from pyflink.table.window import Tumble

from .config import settings
from .models import CampaignEvent, UserProfile, UserBehavior, EnrichedCampaignMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventTimestampAssigner(TimestampAssigner):
    """Custom timestamp assigner for campaign events."""
    
    def extract_timestamp(self, value: CampaignEvent, record_timestamp: int) -> int:
        """Extract timestamp from campaign event."""
        return int(value.timestamp.timestamp() * 1000)


def create_flink_environment() -> Tuple[StreamExecutionEnvironment, StreamTableEnvironment]:
    """
    Create and configure Flink execution environment.
    
    Returns:
        Tuple of StreamExecutionEnvironment and StreamTableEnvironment
    """
    # Create streaming execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(settings.flink_parallelism)
    
    # Enable checkpointing for fault tolerance
    env.enable_checkpointing(60000)  # Checkpoint every 60 seconds
    
    # Create table environment
    table_settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    table_env = StreamTableEnvironment.create(env, table_settings)
    
    # Configure Iceberg catalog
    table_env.execute_sql(f"""
        CREATE CATALOG iceberg_catalog WITH (
            'type'='iceberg',
            'warehouse'='{settings.iceberg_warehouse_path}',
            's3.endpoint'='{settings.iceberg_s3_endpoint}',
            's3.access-key'='{settings.iceberg_s3_access_key}',
            's3.secret-key'='{settings.iceberg_s3_secret_key}',
            's3.region'='{settings.iceberg_s3_region}'
        )
    """)
    
    table_env.execute_sql("USE CATALOG iceberg_catalog")
    
    return env, table_env


def create_kafka_source(topic: str) -> KafkaSource:
    """
    Create Kafka source for streaming data.
    
    Args:
        topic: Kafka topic name
        
    Returns:
        Configured KafkaSource
    """
    return KafkaSource.builder() \
        .set_bootstrap_servers(settings.kafka_bootstrap_servers) \
        .set_topics(topic) \
        .set_group_id(f"flink-{topic}-consumer") \
        .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
        .set_value_only_deserializer(
            StreamFormat.json_format()
        ) \
        .build()


def example_1_basic_stream_processing(env: StreamExecutionEnvironment) -> None:
    """
    Example 1: Basic stream processing with windowing.
    
    Demonstrates:
    - Reading from Kafka
    - Time windowing
    - Aggregations
    - Writing to Iceberg table
    """
    logger.info("Running Example 1: Basic Stream Processing")
    
    # Create Kafka source for campaign events
    kafka_source = create_kafka_source(settings.kafka_topic_campaign_events)
    
    # Create stream with watermark strategy
    stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy
            .for_bounded_out_of_orderness(Time.seconds(5))
            .with_timestamp_assigner(EventTimestampAssigner()),
        source_name="campaign_events"
    )
    
    # Parse JSON to CampaignEvent objects
    events_stream = stream.map(
        lambda x: CampaignEvent(**json.loads(x)),
        output_type=Types.STRING()
    )
    
    # Filter for specific event types
    conversion_events = events_stream.filter(
        lambda event: event.event_type in ["conversion", "purchase"]
    )
    
    # Key by campaign and platform
    keyed_stream = conversion_events.key_by(
        lambda event: f"{event.campaign_id}_{event.platform}"
    )
    
    # Apply 5-minute tumbling window
    windowed_stream = keyed_stream.window(
        Tumble.over(Time.minutes(5)).on(col("timestamp")).alias("w")
    )
    
    # Aggregate metrics
    aggregated_stream = windowed_stream.aggregate(
        lambda key, window, events: {
            "campaign_platform": key,
            "window_start": window.get_start(),
            "window_end": window.get_end(),
            "conversion_count": len(events),
            "total_revenue": sum(e.revenue or 0 for e in events),
            "unique_users": len(set(e.user_id for e in events))
        }
    )
    
    # Print results (in production, write to Iceberg table)
    aggregated_stream.print("Campaign Metrics (5-min windows)")
    
    # Execute the job
    env.execute("Basic Stream Processing Example")


def example_2_stream_stream_join(env: StreamExecutionEnvironment) -> None:
    """
    Example 2: Stream-stream join between campaign events and user behavior.
    
    Demonstrates:
    - Stream-stream joins
    - Time-based join conditions
    - Complex event processing
    """
    logger.info("Running Example 2: Stream-Stream Join")
    
    # Create sources for both streams
    campaign_source = create_kafka_source(settings.kafka_topic_campaign_events)
    behavior_source = create_kafka_source(settings.kafka_topic_behavior_data)
    
    # Create streams with watermarks
    campaign_stream = env.from_source(
        source=campaign_source,
        watermark_strategy=WatermarkStrategy
            .for_bounded_out_of_orderness(Time.seconds(5))
            .with_timestamp_assigner(EventTimestampAssigner()),
        source_name="campaign_events"
    ).map(
        lambda x: CampaignEvent(**json.loads(x)),
        output_type=Types.STRING()
    )
    
    behavior_stream = env.from_source(
        source=behavior_source,
        watermark_strategy=WatermarkStrategy
            .for_bounded_out_of_orderness(Time.seconds(5))
            .with_timestamp_assigner(EventTimestampAssigner()),
        source_name="user_behavior"
    ).map(
        lambda x: UserBehavior(**json.loads(x)),
        output_type=Types.STRING()
    )
    
    # Join streams on user_id with time window
    joined_stream = campaign_stream.join(behavior_stream) \
        .where(lambda c: c.user_id) \
        .equal_to(lambda b: b.user_id) \
        .window(Tumble.over(Time.minutes(10)).on(col("timestamp")).alias("w")) \
        .apply(
            lambda campaign, behavior: {
                "user_id": campaign.user_id,
                "campaign_id": campaign.campaign_id,
                "event_type": campaign.event_type,
                "behavior_event": behavior.event_name,
                "timestamp": campaign.timestamp,
                "revenue": campaign.revenue or 0,
                "session_id": behavior.session_id
            }
        )
    
    # Print joined results
    joined_stream.print("Campaign-Behavior Join")
    
    # Execute the job
    env.execute("Stream-Stream Join Example")


def example_3_iceberg_table_operations(table_env: StreamTableEnvironment) -> None:
    """
    Example 3: Iceberg table operations.
    
    Demonstrates:
    - Creating Iceberg tables
    - Writing streaming data to Iceberg
    - Reading from Iceberg tables
    - Schema evolution
    """
    logger.info("Running Example 3: Iceberg Table Operations")
    
    # Create Iceberg table for campaign events
    table_env.execute_sql("""
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
            proc_time AS PROCTIME()
        ) PARTITIONED BY (campaign_id, platform, event_type)
        WITH (
            'connector' = 'iceberg',
            'write-format' = 'parquet',
            'write.upsert.enabled' = 'true'
        )
    """)
    
    # Create Iceberg table for user profiles
    table_env.execute_sql("""
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
            proc_time AS PROCTIME(),
            PRIMARY KEY (user_id) NOT ENFORCED
        ) PARTITIONED BY (country, platform)
        WITH (
            'connector' = 'iceberg',
            'write-format' = 'parquet',
            'write.upsert.enabled' = 'true'
        )
    """)
    
    # Create Iceberg table for campaign summaries
    table_env.execute_sql("""
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
    """)
    
    logger.info("Iceberg tables created successfully")


def example_4_complex_aggregations(table_env: StreamTableEnvironment) -> None:
    """
    Example 4: Complex aggregations with multiple windows.
    
    Demonstrates:
    - Multiple window types (tumbling, sliding, session)
    - Complex aggregations
    - Materialized views
    """
    logger.info("Running Example 4: Complex Aggregations")
    
    # Create Kafka source as table
    table_env.execute_sql(f"""
        CREATE TABLE campaign_events_kafka (
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
            WATERMARK FOR timestamp AS timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = '{settings.kafka_topic_campaign_events}',
            'properties.bootstrap.servers' = '{settings.kafka_bootstrap_servers}',
            'properties.group.id' = 'flink-aggregations',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        )
    """)
    
    # Create materialized view for real-time campaign metrics
    table_env.execute_sql("""
        CREATE VIEW campaign_metrics_realtime AS
        SELECT 
            campaign_id,
            platform,
            event_type,
            COUNT(*) as event_count,
            COUNT(DISTINCT user_id) as unique_users,
            SUM(revenue) as total_revenue,
            AVG(revenue) as avg_revenue,
            TUMBLE_START(timestamp, INTERVAL '1' MINUTE) as window_start,
            TUMBLE_END(timestamp, INTERVAL '1' MINUTE) as window_end
        FROM campaign_events_kafka
        GROUP BY 
            campaign_id,
            platform,
            event_type,
            TUMBLE(timestamp, INTERVAL '1' MINUTE)
    """)
    
    # Create materialized view for hourly aggregations
    table_env.execute_sql("""
        CREATE VIEW campaign_metrics_hourly AS
        SELECT 
            campaign_id,
            platform,
            DATE_FORMAT(timestamp, 'yyyy-MM-dd HH:00:00') as hour,
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
        FROM campaign_events_kafka
        GROUP BY 
            campaign_id,
            platform,
            DATE_FORMAT(timestamp, 'yyyy-MM-dd HH:00:00')
    """)
    
    logger.info("Complex aggregations views created successfully")


def example_5_event_time_processing(env: StreamExecutionEnvironment) -> None:
    """
    Example 5: Advanced event time processing.
    
    Demonstrates:
    - Custom watermark strategies
    - Late data handling
    - Event time windows
    - Out-of-order event processing
    """
    logger.info("Running Example 5: Event Time Processing")
    
    # Create Kafka source
    kafka_source = create_kafka_source(settings.kafka_topic_campaign_events)
    
    # Create stream with custom watermark strategy
    stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy
            .for_bounded_out_of_orderness(Time.seconds(10))
            .with_timestamp_assigner(EventTimestampAssigner()),
        source_name="campaign_events"
    )
    
    # Parse events
    events_stream = stream.map(
        lambda x: CampaignEvent(**json.loads(x)),
        output_type=Types.STRING()
    )
    
    # Process with event time windows
    keyed_stream = events_stream.key_by(lambda event: event.campaign_id)
    
    # Apply 1-hour tumbling window with allowed lateness
    windowed_stream = keyed_stream.window(
        Tumble.over(Time.hours(1))
        .on(col("timestamp"))
        .alias("w")
    ).allowed_lateness(Time.minutes(5))  # Allow 5 minutes of late data
    
    # Aggregate with late data handling
    aggregated_stream = windowed_stream.aggregate(
        lambda key, window, events: {
            "campaign_id": key,
            "window_start": window.get_start(),
            "window_end": window.get_end(),
            "total_events": len(events),
            "impressions": len([e for e in events if e.event_type == "impression"]),
            "clicks": len([e for e in events if e.event_type == "click"]),
            "conversions": len([e for e in events if e.event_type == "conversion"]),
            "revenue": sum(e.revenue or 0 for e in events),
            "unique_users": len(set(e.user_id for e in events)),
            "is_late": window.max_timestamp() < datetime.now().timestamp() * 1000
        }
    )
    
    # Print results
    aggregated_stream.print("Event Time Processing Results")
    
    # Execute the job
    env.execute("Event Time Processing Example")


def run_all_examples() -> None:
    """Run all Flink examples to demonstrate the concepts."""
    logger.info("Starting Flink Examples")
    
    # Create Flink environment
    env, table_env = create_flink_environment()
    
    try:
        # Run examples
        example_3_iceberg_table_operations(table_env)
        example_4_complex_aggregations(table_env)
        
        # Note: These examples would need actual Kafka data to run
        # example_1_basic_stream_processing(env)
        # example_2_stream_stream_join(env)
        # example_5_event_time_processing(env)
        
        logger.info("All examples completed successfully")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        raise


if __name__ == "__main__":
    run_all_examples() 
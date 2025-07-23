# Apache Flink + Iceberg Concepts for Ads Campaign Metrics

This document provides a comprehensive overview of Apache Flink and Iceberg concepts as they apply to our real-time ads campaign metrics pipeline.

## Table of Contents

1. [Apache Flink Overview](#apache-flink-overview)
2. [Apache Iceberg Overview](#apache-iceberg-overview)
3. [Stream Processing Concepts](#stream-processing-concepts)
4. [Data Lake Concepts](#data-lake-concepts)
5. [Integration Patterns](#integration-patterns)
6. [Best Practices](#best-practices)
7. [Code Examples](#code-examples)

## Apache Flink Overview

### What is Apache Flink?

Apache Flink is a distributed stream processing framework that provides:
- **Real-time stream processing** with exactly-once semantics
- **Event time processing** with watermarks for handling late data
- **Stateful computations** for maintaining context across events
- **Fault tolerance** with checkpointing and savepoints
- **Scalability** with parallel processing

### Key Flink Concepts

#### 1. Stream Execution Environment
```python
from pyflink.datastream import StreamExecutionEnvironment

# Create streaming execution environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(2)  # Set parallelism level
env.enable_checkpointing(60000)  # Enable checkpointing every 60 seconds
```

#### 2. DataStream API
```python
# Create stream from Kafka source
kafka_source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092") \
    .set_topics("ads-campaign-events") \
    .set_group_id("flink-consumer") \
    .build()

stream = env.from_source(
    source=kafka_source,
    watermark_strategy=WatermarkStrategy.for_bounded_out_of_orderness(Time.seconds(5)),
    source_name="campaign_events"
)
```

#### 3. Window Operations
```python
# Tumbling window (fixed-size, non-overlapping)
windowed_stream = stream.key_by(lambda event: event.campaign_id) \
    .window(Tumble.over(Time.minutes(5)).on(col("timestamp")).alias("w"))

# Sliding window (fixed-size, overlapping)
sliding_window = stream.key_by(lambda event: event.campaign_id) \
    .window(Slide.over(Time.minutes(10)).every(Time.minutes(5)).on(col("timestamp")).alias("w"))
```

## Apache Iceberg Overview

### What is Apache Iceberg?

Apache Iceberg is a table format for large analytical datasets that provides:
- **Schema evolution** with backward compatibility
- **Time travel** and versioning capabilities
- **Partition evolution** without rewriting data
- **ACID transactions** for data consistency
- **Optimized file formats** (Parquet, Avro, ORC)

### Key Iceberg Concepts

#### 1. Table Schema
```python
from pyiceberg.schema import Schema
from pyiceberg.types import NestedField, StringType, IntegerType, TimestampType

# Define table schema
schema = Schema(
    NestedField.required(1, "event_id", StringType()),
    NestedField.required(2, "user_id", StringType()),
    NestedField.required(3, "campaign_id", StringType()),
    NestedField.required(4, "event_type", StringType()),
    NestedField.required(5, "timestamp", TimestampType()),
    NestedField.optional(6, "revenue", DoubleType())
)
```

#### 2. Partitioning Strategy
```sql
-- Partition by campaign and date for efficient queries
CREATE TABLE campaign_events (
    event_id STRING,
    user_id STRING,
    campaign_id STRING,
    event_type STRING,
    timestamp TIMESTAMP(3),
    revenue DOUBLE
) PARTITIONED BY (campaign_id, date(timestamp))
```

#### 3. Schema Evolution
```sql
-- Add new columns without rewriting existing data
ALTER TABLE campaign_events ADD COLUMN attribution_source STRING;
ALTER TABLE campaign_events ADD COLUMN user_segment STRING;
```

## Stream Processing Concepts

### 1. Event Time vs Processing Time

**Event Time**: When the event actually occurred
**Processing Time**: When the event is processed by the system

```python
# Event time processing with watermarks
stream = env.from_source(
    source=kafka_source,
    watermark_strategy=WatermarkStrategy
        .for_bounded_out_of_orderness(Time.seconds(10))
        .with_timestamp_assigner(EventTimestampAssigner()),
    source_name="campaign_events"
)
```

### 2. Watermarks

Watermarks help handle late-arriving data:
```python
# Allow 5 minutes of late data
windowed_stream = stream.key_by(lambda event: event.campaign_id) \
    .window(Tumble.over(Time.hours(1)).on(col("timestamp")).alias("w")) \
    .allowed_lateness(Time.minutes(5))
```

### 3. State Management

Flink maintains state for aggregations and joins:
```python
# Stateful aggregation
aggregated_stream = windowed_stream.aggregate(
    lambda key, window, events: {
        "campaign_id": key,
        "total_events": len(events),
        "total_revenue": sum(e.revenue or 0 for e in events),
        "unique_users": len(set(e.user_id for e in events))
    }
)
```

## Data Lake Concepts

### 1. Table Formats

Iceberg provides several benefits over traditional formats:
- **Schema evolution** without data migration
- **Time travel** for data versioning
- **ACID transactions** for consistency
- **Optimized metadata** for fast queries

### 2. Partitioning Strategies

Effective partitioning improves query performance:
```sql
-- Good partitioning for time-series data
PARTITIONED BY (date(timestamp), campaign_id, platform)

-- Benefits:
-- 1. Time-based queries are fast
-- 2. Campaign-specific queries are efficient
-- 3. Platform-specific analysis is optimized
```

### 3. Data Organization

Organize data for different access patterns:
```
iceberg-warehouse/
├── campaign_events/
│   ├── campaign_id=camp_001/
│   │   ├── date=2024-01-01/
│   │   │   ├── platform=ios/
│   │   │   └── platform=android/
│   │   └── date=2024-01-02/
├── user_profiles/
│   ├── country=US/
│   │   ├── platform=ios/
│   │   └── platform=android/
└── campaign_summaries/
    ├── date=2024-01-01/
    └── date=2024-01-02/
```

## Integration Patterns

### 1. Kafka → Flink → Iceberg

```python
# Read from Kafka
kafka_source = create_kafka_source("ads-campaign-events")

# Process with Flink
processed_stream = env.from_source(kafka_source) \
    .map(parse_event) \
    .key_by(lambda e: e.campaign_id) \
    .window(Tumble.over(Time.minutes(5))) \
    .aggregate(calculate_metrics)

# Write to Iceberg
processed_stream.sink_to(
    IcebergSink.for_table("campaign_metrics")
)
```

### 2. Stream-Stream Joins

```python
# Join campaign events with user behavior
joined_stream = campaign_stream.join(behavior_stream) \
    .where(lambda c: c.user_id) \
    .equal_to(lambda b: b.user_id) \
    .window(Tumble.over(Time.minutes(10)).on(col("timestamp")).alias("w")) \
    .apply(join_function)
```

### 3. Stream-Table Joins

```python
# Join streaming data with static user profiles
enriched_stream = campaign_stream.join(
    user_profiles_table,
    campaign_stream.user_id == user_profiles_table.user_id
)
```

## Best Practices

### 1. Flink Best Practices

- **Set appropriate parallelism** based on data volume
- **Enable checkpointing** for fault tolerance
- **Use event time** for accurate analytics
- **Handle late data** with watermarks
- **Optimize state backend** for your use case

### 2. Iceberg Best Practices

- **Choose effective partitioning** based on query patterns
- **Use schema evolution** for backward compatibility
- **Implement data lifecycle** policies
- **Monitor table metadata** size
- **Optimize file sizes** for query performance

### 3. Performance Optimization

```python
# Optimize Flink performance
env.set_parallelism(4)  # Match CPU cores
env.enable_checkpointing(30000)  # Frequent checkpoints
env.set_state_backend(FsStateBackend("hdfs://checkpoints"))

# Optimize Iceberg performance
table_properties = {
    "write.parquet.row-group-size-bytes": "134217728",  # 128MB
    "write.parquet.page-size-bytes": "1048576",  # 1MB
    "write.metadata.delete-after-commit.enabled": "true"
}
```

## Code Examples

### Example 1: Real-time Campaign Metrics

```python
def real_time_campaign_metrics():
    """Calculate real-time campaign metrics."""
    
    # Create stream from Kafka
    stream = create_campaign_events_stream()
    
    # Process with 5-minute windows
    metrics = stream.key_by(lambda e: e.campaign_id) \
        .window(Tumble.over(Time.minutes(5)).on(col("timestamp")).alias("w")) \
        .aggregate(
            lambda key, window, events: {
                "campaign_id": key,
                "window_start": window.get_start(),
                "impressions": len([e for e in events if e.event_type == "impression"]),
                "clicks": len([e for e in events if e.event_type == "click"]),
                "conversions": len([e for e in events if e.event_type == "conversion"]),
                "revenue": sum(e.revenue or 0 for e in events),
                "ctr": calculate_ctr(events),
                "cvr": calculate_cvr(events)
            }
        )
    
    return metrics
```

### Example 2: User Journey Analysis

```python
def user_journey_analysis():
    """Analyze user journey from impression to conversion."""
    
    # Create streams for different event types
    impressions = create_event_stream("impression")
    clicks = create_event_stream("click")
    conversions = create_event_stream("conversion")
    
    # Join streams to track user journey
    journey = impressions.join(clicks) \
        .where(lambda i: i.user_id) \
        .equal_to(lambda c: c.user_id) \
        .window(Tumble.over(Time.hours(1)).on(col("timestamp")).alias("w")) \
        .apply(join_impression_click)
    
    # Continue with conversion analysis
    conversion_journey = journey.join(conversions) \
        .where(lambda j: j.user_id) \
        .equal_to(lambda conv: conv.user_id) \
        .window(Tumble.over(Time.hours(24)).on(col("timestamp")).alias("w")) \
        .apply(join_journey_conversion)
    
    return conversion_journey
```

### Example 3: Iceberg Table Management

```python
def manage_iceberg_tables():
    """Manage Iceberg tables for campaign data."""
    
    # Create table with schema
    table = catalog.create_table(
        "campaign_events",
        schema=campaign_schema,
        partitioning=PartitionSpec.builder()
            .identity("campaign_id")
            .identity("platform")
            .day("timestamp")
            .build(),
        properties=table_properties
    )
    
    # Write data
    table.append(campaign_events_df)
    
    # Query with time travel
    historical_data = table.scan(
        snapshot_id=previous_snapshot_id
    ).to_pandas()
    
    return table
```

## Conclusion

Apache Flink and Iceberg provide a powerful combination for building real-time data pipelines:

- **Flink** handles the real-time stream processing with fault tolerance and exactly-once semantics
- **Iceberg** provides a robust data lake format with schema evolution and time travel capabilities
- **Together** they enable scalable, maintainable, and performant real-time analytics

This architecture is particularly well-suited for ads campaign metrics, where real-time insights and historical analysis are both critical for business success. 
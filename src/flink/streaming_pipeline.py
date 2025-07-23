"""
Flink streaming pipeline for ads campaign metrics.

This module implements the main Flink streaming job for processing
campaign events in real-time and writing to Iceberg tables.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.common import Types, Time
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.connectors.iceberg import IcebergSink
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream.window import TumblingEventTimeWindows

from ..models import CampaignEvent, UserProfile, UserBehavior
from .data_enrichment import DataEnrichmentProcessor
from .iceberg_sink import IcebergSink
from .metrics_aggregation import MetricsAggregator

logger = logging.getLogger(__name__)


class CampaignMetricsPipeline:
    """Main Flink streaming pipeline for campaign metrics."""
    
    def __init__(self, kafka_bootstrap_servers: str = "localhost:9092",
                 checkpoint_interval: int = 60000):
        """
        Initialize the Flink streaming pipeline.
        
        Args:
            kafka_bootstrap_servers: Kafka broker addresses
            checkpoint_interval: Checkpoint interval in milliseconds
        """
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.checkpoint_interval = checkpoint_interval
        
        # Initialize Flink environment
        self.env = self._setup_environment()
        self.table_env = self._setup_table_environment()
        
        # Initialize processors
        self.enrichment_processor = DataEnrichmentProcessor()
        self.iceberg_sink = IcebergSink()
        self.metrics_aggregator = MetricsAggregator()
        
        logger.info("Initialized Flink streaming pipeline")
    
    def _setup_environment(self) -> StreamExecutionEnvironment:
        """Setup Flink streaming execution environment."""
        env = StreamExecutionEnvironment.get_execution_environment()
        
        # Enable checkpointing
        env.enable_checkpointing(self.checkpoint_interval)
        env.get_checkpoint_config().set_min_pause_between_checkpoints(30000)
        env.get_checkpoint_config().set_checkpoint_timeout(60000)
        env.get_checkpoint_config().set_max_concurrent_checkpoints(1)
        
        # Set parallelism
        env.set_parallelism(2)
        
        logger.info("Setup Flink execution environment")
        return env
    
    def _setup_table_environment(self) -> StreamTableEnvironment:
        """Setup Flink table environment."""
        settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
        table_env = StreamTableEnvironment.create(self.env, settings)
        
        # Configure table environment
        table_env.get_config().set_idle_state_retention_time(
            Time.hours(1), Time.hours(2)
        )
        
        logger.info("Setup Flink table environment")
        return table_env
    
    def create_kafka_source(self, topic: str, group_id: str) -> KafkaSource:
        """
        Create a Kafka source for reading events.
        
        Args:
            topic: Kafka topic name
            group_id: Consumer group ID
            
        Returns:
            Kafka source configuration
        """
        return KafkaSource.builder() \
            .set_bootstrap_servers(self.kafka_bootstrap_servers) \
            .set_topics(topic) \
            .set_group_id(group_id) \
            .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
            .set_value_only_deserializer(
                self._create_json_deserializer()
            ) \
            .build()
    
    def _create_json_deserializer(self):
        """Create JSON deserializer for Kafka messages."""
        from pyflink.common.serialization import SimpleStringSchema
        
        class JsonDeserializer(SimpleStringSchema):
            def deserialize(self, message: bytes) -> Dict[str, Any]:
                import json
                return json.loads(message.decode('utf-8'))
        
        return JsonDeserializer()
    
    def create_campaign_events_stream(self) -> 'DataStream':
        """Create stream for campaign events."""
        source = self.create_kafka_source(
            topic="campaign_events",
            group_id="flink_campaign_events_group"
        )
        
        # Create data stream
        stream = self.env.from_source(
            source=source,
            watermark_strategy=WatermarkStrategy.no_watermarks(),
            source_name="campaign_events"
        )
        
        # Parse and validate events
        parsed_stream = stream.map(
            self._parse_campaign_event,
            output_type=Types.MAP(Types.STRING(), Types.STRING())
        )
        
        logger.info("Created campaign events stream")
        return parsed_stream
    

    
    def _parse_campaign_event(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Parse and validate campaign event data.
        
        Args:
            event_data: Raw event data from Kafka
            
        Returns:
            Parsed event data
        """
        try:
            # Extract event value
            event = event_data.get('value', event_data)
            
            # Validate required fields
            required_fields = ['event_id', 'user_id', 'campaign_id', 'event_type']
            for field in required_fields:
                if field not in event:
                    raise ValueError(f"Missing required field: {field}")
            
            # Convert to string format for Flink
            parsed_event = {}
            for key, value in event.items():
                if value is not None:
                    parsed_event[key] = str(value)
            
            return parsed_event
            
        except Exception as e:
            logger.error(f"Error parsing campaign event: {e}")
            # Return error event
            return {
                'event_id': 'error',
                'error': str(e),
                'raw_data': str(event_data)
            }
    

    
    def enrich_events_with_user_data(self, events_stream: 'DataStream',
                                   user_profiles: Dict[str, Dict[str, Any]]) -> 'DataStream':
        """
        Enrich campaign events with user profile data.
        
        Args:
            events_stream: Campaign events stream
            user_profiles: User profile data dictionary
            
        Returns:
            Enriched events stream
        """
        def enrich_event(event: Dict[str, str]) -> Dict[str, str]:
            user_id = event.get('user_id')
            if user_id and user_id in user_profiles:
                user_profile = user_profiles[user_id]
                # Add user profile fields
                for key, value in user_profile.items():
                    if key not in event:
                        event[f'user_{key}'] = str(value)
            return event
        
        enriched_stream = events_stream.map(
            enrich_event,
            output_type=Types.MAP(Types.STRING(), Types.STRING())
        )
        
        logger.info("Enriched events with user profile data")
        return enriched_stream
    
    def aggregate_campaign_metrics(self, events_stream: 'DataStream',
                                 window_size_minutes: int = 5) -> 'DataStream':
        """
        Aggregate campaign metrics over time windows.
        
        Args:
            events_stream: Campaign events stream
            window_size_minutes: Window size in minutes
            
        Returns:
            Aggregated metrics stream
        """
        # Convert to keyed stream by campaign_id
        keyed_stream = events_stream.key_by(
            lambda event: event.get('campaign_id', 'unknown')
        )
        
        # Apply windowing
        windowed_stream = keyed_stream.window(
            TumblingEventTimeWindows.of(Time.minutes(window_size_minutes))
        )
        
        # Aggregate metrics
        aggregated_stream = windowed_stream.aggregate(
            self._create_campaign_metrics_aggregator()
        )
        
        logger.info(f"Aggregated campaign metrics with {window_size_minutes}min windows")
        return aggregated_stream
    
    def _create_campaign_metrics_aggregator(self):
        """Create aggregator for campaign metrics."""
        from pyflink.datastream.functions import AggregateFunction
        
        class CampaignMetricsAggregator(AggregateFunction):
            def create_accumulator(self):
                return {
                    'campaign_id': '',
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0,
                    'installs': 0,
                    'purchases': 0,
                    'revenue': 0.0,
                    'start_time': None,
                    'end_time': None
                }
            
            def add(self, accumulator, event):
                campaign_id = event.get('campaign_id', 'unknown')
                event_type = event.get('event_type', 'unknown')
                revenue = float(event.get('revenue', 0) or 0)
                timestamp = event.get('timestamp', '')
                
                accumulator['campaign_id'] = campaign_id
                
                if event_type == 'impression':
                    accumulator['impressions'] += 1
                elif event_type == 'click':
                    accumulator['clicks'] += 1
                elif event_type == 'conversion':
                    accumulator['conversions'] += 1
                elif event_type == 'install':
                    accumulator['installs'] += 1
                elif event_type == 'purchase':
                    accumulator['purchases'] += 1
                
                accumulator['revenue'] += revenue
                
                if not accumulator['start_time']:
                    accumulator['start_time'] = timestamp
                accumulator['end_time'] = timestamp
                
                return accumulator
            
            def get_result(self, accumulator):
                # Calculate derived metrics
                impressions = accumulator['impressions']
                clicks = accumulator['clicks']
                conversions = accumulator['conversions']
                
                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                cvr = (conversions / clicks * 100) if clicks > 0 else 0
                cpm = (accumulator['revenue'] / impressions * 1000) if impressions > 0 else 0
                
                return {
                    'campaign_id': accumulator['campaign_id'],
                    'window_start': accumulator['start_time'],
                    'window_end': accumulator['end_time'],
                    'impressions': impressions,
                    'clicks': clicks,
                    'conversions': conversions,
                    'installs': accumulator['installs'],
                    'purchases': accumulator['purchases'],
                    'revenue': round(accumulator['revenue'], 2),
                    'ctr_percent': round(ctr, 2),
                    'cvr_percent': round(cvr, 2),
                    'cpm': round(cpm, 2),
                    'processed_at': datetime.now().isoformat()
                }
            
            def merge(self, a, b):
                # Merge accumulators (for session windows)
                merged = a.copy()
                merged['impressions'] += b['impressions']
                merged['clicks'] += b['clicks']
                merged['conversions'] += b['conversions']
                merged['installs'] += b['installs']
                merged['purchases'] += b['purchases']
                merged['revenue'] += b['revenue']
                merged['end_time'] = b['end_time']
                return merged
        
        return CampaignMetricsAggregator()
    
    def write_to_iceberg(self, stream: 'DataStream', table_name: str) -> None:
        """
        Write stream data to Iceberg table.
        
        Args:
            stream: Data stream to write
            table_name: Iceberg table name
        """
        # Convert to table
        table = self.table_env.from_data_stream(stream)
        
        # Write to Iceberg
        table.execute_insert(table_name)
        
        logger.info(f"Configured write to Iceberg table: {table_name}")
    
    def build_pipeline(self) -> None:
        """
        Build the streaming pipeline.
        """
        logger.info("Building Flink streaming pipeline...")
        
        # Create campaign events stream
        events_stream = self.create_campaign_events_stream()
        
        # Aggregate campaign metrics
        metrics_stream = self.aggregate_campaign_metrics(events_stream)
        
        # Write to Iceberg tables
        self.write_to_iceberg(events_stream, "campaign_events")
        self.write_to_iceberg(metrics_stream, "campaign_metrics")
        
        logger.info("Pipeline built successfully")
    
    def _load_user_profiles(self, file_path: str) -> Dict[str, Dict[str, Any]]:
        """Load user profiles from file."""
        import json
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            user_profiles = {}
            for user in data.get('user_profiles', []):
                user_id = user.get('user_id')
                if user_id:
                    user_profiles[user_id] = user
            
            logger.info(f"Loaded {len(user_profiles)} user profiles")
            return user_profiles
            
        except Exception as e:
            logger.error(f"Error loading user profiles: {e}")
            return {}
    
    def execute(self, job_name: str = "CampaignMetricsPipeline") -> None:
        """
        Execute the Flink streaming job.
        
        Args:
            job_name: Name of the Flink job
        """
        logger.info(f"Executing Flink job: {job_name}")
        
        try:
            # Execute the job
            self.env.execute(job_name)
            logger.info("Flink job completed successfully")
            
        except Exception as e:
            logger.error(f"Error executing Flink job: {e}")
            raise 
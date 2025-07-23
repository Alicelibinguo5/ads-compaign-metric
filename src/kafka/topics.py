"""
Kafka topics configuration for ads campaign metrics streaming pipeline.

This module defines the Kafka topics and their configurations for
real-time campaign event processing.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class TopicConfig:
    """Configuration for a Kafka topic."""
    
    name: str
    partitions: int = 3
    replication_factor: int = 1
    retention_hours: int = 24
    cleanup_policy: str = "delete"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Kafka admin client."""
        return {
            "name": self.name,
            "partitions": self.partitions,
            "replication_factor": self.replication_factor,
            "configs": {
                "retention.ms": str(self.retention_hours * 60 * 60 * 1000),
                "cleanup.policy": self.cleanup_policy
            }
        }


class KafkaTopics:
    """Kafka topics for ads campaign metrics pipeline."""
    
    # Single topic for all campaign events
    CAMPAIGN_EVENTS = TopicConfig(
        name="campaign_events",
        partitions=3,
        retention_hours=24
    )
    
    # Dead letter queue for failed events
    DEAD_LETTER_QUEUE = TopicConfig(
        name="dead_letter_queue",
        partitions=1,
        retention_hours=168  # 7 days for debugging
    )
    
    @classmethod
    def get_all_topics(cls) -> Dict[str, TopicConfig]:
        """Get all topic configurations."""
        return {
            "campaign_events": cls.CAMPAIGN_EVENTS,
            "dead_letter_queue": cls.DEAD_LETTER_QUEUE
        }
    
    @classmethod
    def get_topic_names(cls) -> list[str]:
        """Get list of all topic names."""
        return ["campaign_events", "dead_letter_queue"]


# Default Kafka configuration
DEFAULT_KAFKA_CONFIG = {
    "bootstrap_servers": "localhost:9092",
    "security_protocol": "PLAINTEXT",
    "auto_offset_reset": "earliest",
    "enable_auto_commit": True,
    "auto_commit_interval_ms": 1000,
    "session_timeout_ms": 30000,
    "heartbeat_interval_ms": 3000,
    "max_poll_records": 500,
    "max_poll_interval_ms": 300000
}

# Producer configuration
PRODUCER_CONFIG = {
    **DEFAULT_KAFKA_CONFIG,
    "acks": "all",
    "retries": 3,
    "batch_size": 16384,
    "linger_ms": 10,
    "buffer_memory": 33554432,
    "compression_type": "snappy"
}

# Consumer configuration  
CONSUMER_CONFIG = {
    **DEFAULT_KAFKA_CONFIG,
    "group_id": "ads_campaign_metrics_group",
    "enable_auto_commit": False,
    "max_poll_records": 1000
} 
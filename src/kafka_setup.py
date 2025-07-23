#!/usr/bin/env python3
"""
Kafka setup for ads campaign metrics.

This module provides a minimal Kafka configuration with just one topic
for all campaign events, making it easy to understand and maintain.
"""

import logging
from typing import Dict, Any
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer
import json

logger = logging.getLogger(__name__)


class SimpleKafkaSetup:
    """Kafka setup with minimal configuration."""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """
        Initialize simplified Kafka setup.
        
        Args:
            bootstrap_servers: Kafka broker addresses
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic_name = "campaign_events"
        
        logger.info(f"Initialized simple Kafka setup: {bootstrap_servers}")
    
    def create_topic(self) -> bool:
        """
        Create the single campaign events topic.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers
            )
            
            # Single topic for all campaign events
            topic = NewTopic(
                name=self.topic_name,
                num_partitions=3,
                replication_factor=1
            )
            
            admin_client.create_topics([topic])
            logger.info(f"Created topic: {self.topic_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create topic: {e}")
            return False
    
    def get_producer(self) -> KafkaProducer:
        """Get a Kafka producer for sending events."""
        return KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
    
    def get_consumer(self, group_id: str = "campaign_metrics_group") -> KafkaConsumer:
        """Get a Kafka consumer for reading events."""
        return KafkaConsumer(
            self.topic_name,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset='earliest',
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )
    
    def send_event(self, event: Dict[str, Any], key: str = None) -> bool:
        """
        Send a campaign event to Kafka.
        
        Args:
            event: Campaign event data
            key: Optional message key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            producer = self.get_producer()
            future = producer.send(self.topic_name, key=key, value=event)
            producer.flush()
            producer.close()
            
            logger.debug(f"Sent event: {event.get('event_id', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            return False


def main():
    """Main function to setup Kafka."""
    print("🚀 Setting up Simplified Kafka")
    print("=" * 40)
    
    # Create Kafka setup
    kafka_setup = SimpleKafkaSetup()
    
    # Create topic
    if kafka_setup.create_topic():
        print("✅ Created campaign_events topic")
    else:
        print("❌ Failed to create topic")
        return 1
    
    print("✅ Kafka setup complete!")
    print(f"📊 Topic: {kafka_setup.topic_name}")
    print(f"🔗 Bootstrap servers: {kafka_setup.bootstrap_servers}")
    
    return 0


if __name__ == "__main__":
    exit(main()) 
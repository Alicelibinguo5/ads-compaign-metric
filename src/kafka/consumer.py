"""
Kafka consumer for ads campaign events.

This module handles consuming campaign events and user behaviors
from Kafka topics for processing.
"""

import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from .topics import KafkaTopics, CONSUMER_CONFIG

logger = logging.getLogger(__name__)


class CampaignEventConsumer:
    """Kafka consumer for campaign events and user behaviors."""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092",
                 group_id: str = "ads_campaign_metrics_group"):
        """
        Initialize the Kafka consumer.
        
        Args:
            bootstrap_servers: Kafka broker addresses
            group_id: Consumer group ID
        """
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Kafka broker."""
        try:
            config = CONSUMER_CONFIG.copy()
            config["bootstrap_servers"] = self.bootstrap_servers
            config["group_id"] = self.group_id
            
            self.consumer = KafkaConsumer(
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                **config
            )
            
            logger.info(f"Connected to Kafka broker: {self.bootstrap_servers}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def subscribe_to_campaign_events(self) -> None:
        """Subscribe to campaign events topic."""
        topic = KafkaTopics.CAMPAIGN_EVENTS.name
        self.consumer.subscribe([topic])
        logger.info(f"Subscribed to topic: {topic}")
    

    
    def subscribe_to_topic(self, topic: str) -> None:
        """Subscribe to a specific topic."""
        self.consumer.subscribe([topic])
        logger.info(f"Subscribed to topic: {topic}")
    
    def consume_messages(self, message_handler: Callable[[Dict[str, Any]], None],
                        timeout_ms: int = 1000) -> None:
        """
        Consume messages from subscribed topics.
        
        Args:
            message_handler: Function to handle each message
            timeout_ms: Timeout for polling messages
        """
        if not self.consumer:
            raise RuntimeError("Consumer not connected")
        
        logger.info("Starting to consume messages...")
        
        try:
            for message in self.consumer:
                try:
                    # Extract message data
                    message_data = {
                        'topic': message.topic,
                        'partition': message.partition,
                        'offset': message.offset,
                        'key': message.key.decode('utf-8') if message.key else None,
                        'value': message.value,
                        'timestamp': message.timestamp,
                        'headers': message.headers
                    }
                    
                    # Call the message handler
                    message_handler(message_data)
                    
                    # Commit the offset
                    self.consumer.commit()
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Continue with next message
                    
        except KeyboardInterrupt:
            logger.info("Consumption interrupted by user")
        except Exception as e:
            logger.error(f"Error during message consumption: {e}")
            raise
    
    def consume_batch(self, batch_size: int = 100, 
                     timeout_ms: int = 5000) -> list[Dict[str, Any]]:
        """
        Consume a batch of messages.
        
        Args:
            batch_size: Maximum number of messages to consume
            timeout_ms: Timeout for polling messages
            
        Returns:
            List of message data
        """
        if not self.consumer:
            raise RuntimeError("Consumer not connected")
        
        messages = []
        
        try:
            # Poll for messages
            message_batch = self.consumer.poll(timeout_ms=timeout_ms)
            
            for topic_partition, partition_messages in message_batch.items():
                for message in partition_messages:
                    if len(messages) >= batch_size:
                        break
                    
                    message_data = {
                        'topic': message.topic,
                        'partition': message.partition,
                        'offset': message.offset,
                        'key': message.key.decode('utf-8') if message.key else None,
                        'value': message.value,
                        'timestamp': message.timestamp,
                        'headers': message.headers
                    }
                    
                    messages.append(message_data)
                
                if len(messages) >= batch_size:
                    break
            
            # Commit offsets for consumed messages
            if messages:
                self.consumer.commit()
                logger.debug(f"Consumed {len(messages)} messages")
            
        except Exception as e:
            logger.error(f"Error consuming batch: {e}")
            raise
        
        return messages
    
    def get_topic_info(self, topic: str) -> Dict[str, Any]:
        """
        Get information about a topic.
        
        Args:
            topic: Topic name
            
        Returns:
            Topic information
        """
        if not self.consumer:
            raise RuntimeError("Consumer not connected")
        
        try:
            partitions = self.consumer.partitions_for_topic(topic)
            if not partitions:
                return {"error": f"Topic {topic} not found"}
            
            topic_info = {
                "topic": topic,
                "partitions": list(partitions),
                "partition_count": len(partitions)
            }
            
            return topic_info
            
        except Exception as e:
            logger.error(f"Error getting topic info for {topic}: {e}")
            return {"error": str(e)}
    
    def close(self) -> None:
        """Close the consumer connection."""
        if self.consumer:
            self.consumer.close()
            logger.info("Closed Kafka consumer connection")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class MessageProcessor:
    """Base class for processing Kafka messages."""
    
    def __init__(self):
        """Initialize the message processor."""
        self.processed_count = 0
        self.error_count = 0
    
    def process_campaign_event(self, event: Dict[str, Any]) -> None:
        """
        Process a campaign event message.
        
        Args:
            event: Campaign event data
        """
        try:
            # Extract event data
            event_data = event.get('value', {})
            event_id = event_data.get('event_id', 'unknown')
            
            logger.debug(f"Processing campaign event: {event_id}")
            
            # Add processing timestamp
            event_data['processed_at'] = datetime.now().isoformat()
            
            # Process the event (to be implemented by subclasses)
            self._process_event(event_data)
            
            self.processed_count += 1
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error processing campaign event: {e}")
            
            # Send to dead letter queue
            self._send_to_dlq(event, str(e))
            
            # Don't raise the exception to continue processing other messages
            logger.warning(f"Event {event_id} sent to DLQ due to error: {e}")
    
    def _send_to_dlq(self, original_event: Dict[str, Any], error_message: str) -> None:
        """
        Send failed event to dead letter queue.
        
        Args:
            original_event: The original event that failed
            error_message: Error message explaining the failure
        """
        try:
            if not self.producer:
                logger.error("Producer not available for DLQ")
                return
            
            # Create DLQ message with error context
            dlq_message = {
                'original_event': original_event,
                'error_message': error_message,
                'failed_at': datetime.now().isoformat(),
                'retry_count': 0,
                'dlq_timestamp': datetime.now().isoformat()
            }
            
            # Send to DLQ topic
            topic = KafkaTopics.DEAD_LETTER_QUEUE.name
            future = self.producer.send(topic, value=dlq_message)
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Sent failed event to DLQ: {topic} "
                       f"[partition: {record_metadata.partition}, "
                       f"offset: {record_metadata.offset}]")
            
        except Exception as e:
            logger.error(f"Failed to send event to DLQ: {e}")
            # At this point, we've lost the event - this is a critical failure
    

    
    def _process_event(self, event_data: Dict[str, Any]) -> None:
        """
        Process campaign event data.
        
        Args:
            event_data: Campaign event data
        """
        # To be implemented by subclasses
        pass
    

    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
            "success_rate": (self.processed_count / (self.processed_count + self.error_count) * 100) 
                           if (self.processed_count + self.error_count) > 0 else 0
        } 
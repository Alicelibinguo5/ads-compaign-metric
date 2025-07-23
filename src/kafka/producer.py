"""
Kafka producer for ads campaign events.

This module handles sending campaign events and user behaviors
to Kafka topics for real-time processing.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

from .topics import KafkaTopics, PRODUCER_CONFIG

logger = logging.getLogger(__name__)


class CampaignEventProducer:
    """Kafka producer for campaign events and user behaviors."""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """
        Initialize the Kafka producer.
        
        Args:
            bootstrap_servers: Kafka broker addresses
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Kafka broker."""
        try:
            config = PRODUCER_CONFIG.copy()
            config["bootstrap_servers"] = self.bootstrap_servers
            
            self.producer = KafkaProducer(
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                **config
            )
            
            logger.info(f"Connected to Kafka broker: {self.bootstrap_servers}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def send_campaign_event(self, event: Dict[str, Any], 
                          key: Optional[str] = None) -> None:
        """
        Send a campaign event to Kafka.
        
        Args:
            event: Campaign event data
            key: Optional message key (defaults to event_id)
        """
        if not self.producer:
            raise RuntimeError("Producer not connected")
        
        topic = KafkaTopics.CAMPAIGN_EVENTS.name
        message_key = key or event.get('event_id', 'unknown')
        
        try:
            # Add timestamp if not present
            if 'kafka_timestamp' not in event:
                event['kafka_timestamp'] = datetime.now().isoformat()
            
            future = self.producer.send(topic, key=message_key, value=event)
            
            # Wait for the send to complete
            record_metadata = future.get(timeout=10)
            
            logger.debug(f"Sent event {message_key} to {topic} "
                        f"[partition: {record_metadata.partition}, "
                        f"offset: {record_metadata.offset}]")
            
        except KafkaError as e:
            logger.error(f"Failed to send event {message_key}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending event {message_key}: {e}")
            raise
    

    
    def send_batch_events(self, events: List[Dict[str, Any]]) -> None:
        """
        Send a batch of campaign events.
        
        Args:
            events: List of campaign events
        """
        logger.info(f"Sending batch of {len(events)} events")
        
        for event in events:
            try:
                self.send_campaign_event(event)
                time.sleep(0.01)  # Small delay to avoid overwhelming Kafka
            except Exception as e:
                logger.error(f"Failed to send event in batch: {e}")
                # Continue with next event
    

    
    def flush(self) -> None:
        """Flush all pending messages."""
        if self.producer:
            self.producer.flush()
            logger.info("Flushed all pending messages")
    
    def close(self) -> None:
        """Close the producer connection."""
        if self.producer:
            self.producer.close()
            logger.info("Closed Kafka producer connection")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class StreamingDataProducer:
    """Producer for streaming synthetic data to Kafka."""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        """
        Initialize the streaming producer.
        
        Args:
            bootstrap_servers: Kafka broker addresses
        """
        self.producer = CampaignEventProducer(bootstrap_servers)
        self.running = False
    
    def start_streaming(self, data_file: str, events_per_second: int = 10) -> None:
        """
        Start streaming data from a JSON file to Kafka.
        
        Args:
            data_file: Path to JSON file with events
            events_per_second: Rate of events to send
        """
        import json
        from pathlib import Path
        
        data_path = Path(data_file)
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        events = data.get('events', [])
        behaviors = data.get('behaviors', [])
        
        if not events:
            logger.warning("No events found in data file")
            return
        
        logger.info(f"Starting to stream {len(events)} events at {events_per_second} events/sec")
        
        self.running = True
        delay = 1.0 / events_per_second
        
        try:
            for i, event in enumerate(events):
                if not self.running:
                    break
                
                try:
                    self.producer.send_campaign_event(event)
                    logger.debug(f"Streamed event {i+1}/{len(events)}")
                    
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Failed to stream event {i+1}: {e}")
                    continue
            

            
            logger.info("Streaming completed")
            
        except KeyboardInterrupt:
            logger.info("Streaming interrupted by user")
        finally:
            self.running = False
            self.producer.flush()
    
    def stop_streaming(self) -> None:
        """Stop the streaming process."""
        self.running = False
        logger.info("Stopping streaming process")
    
    def close(self) -> None:
        """Close the producer."""
        self.producer.close() 
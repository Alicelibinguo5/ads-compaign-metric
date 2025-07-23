"""
Dead Letter Queue Consumer for handling failed campaign events.

This module provides functionality to consume and process events that have failed
processing in the main pipeline, allowing for debugging and potential reprocessing.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .consumer import MessageProcessor
from .topics import KafkaTopics

logger = logging.getLogger(__name__)


class DLQConsumer(MessageProcessor):
    """
    Consumer for processing events from the Dead Letter Queue.
    
    This consumer handles events that failed processing in the main pipeline,
    providing monitoring, debugging, and potential reprocessing capabilities.
    """
    
    def __init__(self, bootstrap_servers: str = "localhost:9092") -> None:
        """
        Initialize DLQ consumer.
        
        Args:
            bootstrap_servers: Kafka bootstrap servers
        """
        super().__init__(bootstrap_servers)
        self.dlq_events: List[Dict[str, Any]] = []
        self.error_patterns: Dict[str, int] = {}
        
    def subscribe_to_dlq(self) -> None:
        """Subscribe to dead letter queue topic."""
        topic = KafkaTopics.DEAD_LETTER_QUEUE.name
        self.consumer.subscribe([topic])
        logger.info(f"Subscribed to DLQ topic: {topic}")
    
    def process_dlq_event(self, dlq_message: Dict[str, Any]) -> None:
        """
        Process a message from the dead letter queue.
        
        Args:
            dlq_message: DLQ message containing failed event and error details
        """
        try:
            # Extract DLQ message components
            original_event = dlq_message.get('original_event', {})
            error_message = dlq_message.get('error_message', 'Unknown error')
            failed_at = dlq_message.get('failed_at', 'Unknown')
            retry_count = dlq_message.get('retry_count', 0)
            
            # Store for analysis
            self.dlq_events.append(dlq_message)
            
            # Track error patterns
            error_type = self._categorize_error(error_message)
            self.error_patterns[error_type] = self.error_patterns.get(error_type, 0) + 1
            
            logger.warning(f"DLQ Event - Original ID: {original_event.get('event_id', 'unknown')}, "
                          f"Error: {error_message}, Retry Count: {retry_count}")
            
            # Process the DLQ event (to be implemented by subclasses)
            self._process_dlq_event(dlq_message)
            
            self.processed_count += 1
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error processing DLQ event: {e}")
    
    def _process_dlq_event(self, dlq_message: Dict[str, Any]) -> None:
        """
        Process DLQ event - to be implemented by subclasses.
        
        Args:
            dlq_message: DLQ message to process
        """
        # Default implementation - just log the event
        original_event = dlq_message.get('original_event', {})
        error_message = dlq_message.get('error_message', 'Unknown error')
        
        logger.info(f"DLQ Event Analysis:")
        logger.info(f"  - Original Event ID: {original_event.get('event_id', 'unknown')}")
        logger.info(f"  - Error: {error_message}")
        logger.info(f"  - Failed At: {dlq_message.get('failed_at', 'unknown')}")
        logger.info(f"  - Retry Count: {dlq_message.get('retry_count', 0)}")
    
    def _categorize_error(self, error_message: str) -> str:
        """
        Categorize error message for pattern analysis.
        
        Args:
            error_message: Error message to categorize
            
        Returns:
            Error category
        """
        error_lower = error_message.lower()
        
        if 'validation' in error_lower or 'invalid' in error_lower:
            return 'validation_error'
        elif 'timeout' in error_lower:
            return 'timeout_error'
        elif 'connection' in error_lower or 'network' in error_lower:
            return 'network_error'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'permission_error'
        elif 'not found' in error_lower or 'missing' in error_lower:
            return 'not_found_error'
        else:
            return 'unknown_error'
    
    def get_dlq_stats(self) -> Dict[str, Any]:
        """
        Get statistics about DLQ events.
        
        Returns:
            Dictionary containing DLQ statistics
        """
        return {
            'total_dlq_events': len(self.dlq_events),
            'error_patterns': self.error_patterns,
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'last_processed': datetime.now().isoformat() if self.dlq_events else None
        }
    
    def export_dlq_events(self, file_path: str) -> None:
        """
        Export DLQ events to a JSON file for analysis.
        
        Args:
            file_path: Path to export file
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.dlq_events, f, indent=2, default=str)
            
            logger.info(f"Exported {len(self.dlq_events)} DLQ events to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to export DLQ events: {e}")
    
    def clear_dlq_events(self) -> None:
        """Clear stored DLQ events from memory."""
        self.dlq_events.clear()
        self.error_patterns.clear()
        logger.info("Cleared DLQ events from memory")
    
    def run_dlq_monitor(self, duration_seconds: int = 300) -> None:
        """
        Run DLQ monitoring for a specified duration.
        
        Args:
            duration_seconds: Duration to monitor in seconds
        """
        logger.info(f"Starting DLQ monitoring for {duration_seconds} seconds")
        
        self.subscribe_to_dlq()
        start_time = datetime.now()
        
        try:
            while (datetime.now() - start_time).seconds < duration_seconds:
                message = self.consumer.poll(timeout=1.0)
                
                if message is None:
                    continue
                
                if message.error():
                    logger.error(f"Consumer error: {message.error()}")
                    continue
                
                try:
                    # Parse message value
                    value = json.loads(message.value().decode('utf-8'))
                    self.process_dlq_event(value)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode DLQ message: {e}")
                    self.error_count += 1
                    
                except Exception as e:
                    logger.error(f"Unexpected error processing DLQ message: {e}")
                    self.error_count += 1
                    
        except KeyboardInterrupt:
            logger.info("DLQ monitoring interrupted by user")
        finally:
            self.close()
            
        # Print final statistics
        stats = self.get_dlq_stats()
        logger.info(f"DLQ Monitoring Complete:")
        logger.info(f"  - Total DLQ Events: {stats['total_dlq_events']}")
        logger.info(f"  - Error Patterns: {stats['error_patterns']}")
        logger.info(f"  - Processed: {stats['processed_count']}")
        logger.info(f"  - Errors: {stats['error_count']}")


def main() -> None:
    """Main function to run DLQ consumer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='DLQ Consumer for Campaign Events')
    parser.add_argument('--bootstrap-servers', default='localhost:9092',
                       help='Kafka bootstrap servers')
    parser.add_argument('--duration', type=int, default=300,
                       help='Monitoring duration in seconds')
    parser.add_argument('--export', help='Export DLQ events to file')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run DLQ consumer
    dlq_consumer = DLQConsumer(args.bootstrap_servers)
    
    try:
        dlq_consumer.run_dlq_monitor(args.duration)
        
        # Export events if requested
        if args.export:
            dlq_consumer.export_dlq_events(args.export)
            
    except Exception as e:
        logger.error(f"DLQ consumer failed: {e}")


if __name__ == "__main__":
    main() 
"""
Kafka module for ads campaign metrics streaming pipeline.

This module handles Kafka producers and consumers for real-time
campaign event ingestion and processing.
"""

from .producer import CampaignEventProducer
from .consumer import CampaignEventConsumer
from .topics import KafkaTopics

__all__ = [
    'CampaignEventProducer',
    'CampaignEventConsumer', 
    'KafkaTopics'
] 
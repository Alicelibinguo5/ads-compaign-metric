"""
Flink module for ads campaign metrics streaming pipeline.

This module handles Flink streaming jobs for real-time
campaign event processing and enrichment.
"""

from .streaming_pipeline import CampaignMetricsPipeline
from .data_enrichment import DataEnrichmentProcessor
from .iceberg_sink import IcebergSink
from .metrics_aggregation import MetricsAggregator

__all__ = [
    'CampaignMetricsPipeline',
    'DataEnrichmentProcessor',
    'IcebergSink',
    'MetricsAggregator'
] 
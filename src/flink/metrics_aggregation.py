"""
Metrics aggregation processor for Flink streaming pipeline.

This module handles real-time aggregation of campaign metrics
and user behavior analytics.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class MetricsAggregator:
    """Aggregator for real-time campaign and user metrics."""
    
    def __init__(self):
        """Initialize the metrics aggregator."""
        self.campaign_metrics = defaultdict(lambda: {
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'installs': 0,
            'purchases': 0,
            'revenue': 0.0,
            'start_time': None,
            'end_time': None,
            'events': []
        })
        
        self.user_metrics = defaultdict(lambda: {
            'total_events': 0,
            'total_revenue': 0.0,
            'session_durations': [],
            'behavior_count': 0,
            'start_time': None,
            'end_time': None,
            'events': []
        })
        
        logger.info("Initialized metrics aggregator")
    
    def aggregate_campaign_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate a campaign event into metrics.
        
        Args:
            event: Campaign event data
            
        Returns:
            Updated campaign metrics
        """
        campaign_id = event.get('campaign_id', 'unknown')
        event_type = event.get('event_type', 'unknown')
        revenue = float(event.get('revenue', 0) or 0)
        timestamp = event.get('timestamp', datetime.now().isoformat())
        
        metrics = self.campaign_metrics[campaign_id]
        
        # Update event counts
        if event_type == 'impression':
            metrics['impressions'] += 1
        elif event_type == 'click':
            metrics['clicks'] += 1
        elif event_type == 'conversion':
            metrics['conversions'] += 1
        elif event_type == 'install':
            metrics['installs'] += 1
        elif event_type == 'purchase':
            metrics['purchases'] += 1
        
        # Update revenue
        metrics['revenue'] += revenue
        
        # Update time range
        if not metrics['start_time']:
            metrics['start_time'] = timestamp
        metrics['end_time'] = timestamp
        
        # Store event for detailed analysis
        metrics['events'].append(event)
        
        # Calculate derived metrics
        derived_metrics = self._calculate_campaign_derived_metrics(metrics)
        
        return {
            'campaign_id': campaign_id,
            **metrics,
            **derived_metrics
        }
    
    def aggregate_user_behavior(self, behavior: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate a user behavior into metrics.
        
        Args:
            behavior: User behavior data
            
        Returns:
            Updated user metrics
        """
        user_id = behavior.get('user_id', 'unknown')
        duration = int(behavior.get('duration', 0))
        timestamp = behavior.get('timestamp', datetime.now().isoformat())
        
        metrics = self.user_metrics[user_id]
        
        # Update behavior count
        metrics['behavior_count'] += 1
        
        # Update session duration
        if duration > 0:
            metrics['session_durations'].append(duration)
        
        # Update time range
        if not metrics['start_time']:
            metrics['start_time'] = timestamp
        metrics['end_time'] = timestamp
        
        # Store behavior for detailed analysis
        metrics['events'].append(behavior)
        
        # Calculate derived metrics
        derived_metrics = self._calculate_user_derived_metrics(metrics)
        
        return {
            'user_id': user_id,
            **metrics,
            **derived_metrics
        }
    
    def _calculate_campaign_derived_metrics(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate derived metrics for campaign.
        
        Args:
            metrics: Campaign metrics
            
        Returns:
            Derived metrics
        """
        impressions = metrics['impressions']
        clicks = metrics['clicks']
        conversions = metrics['conversions']
        revenue = metrics['revenue']
        
        # Calculate rates
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cvr = (conversions / clicks * 100) if clicks > 0 else 0
        cpm = (revenue / impressions * 1000) if impressions > 0 else 0
        
        # Calculate cost per action
        cpa = (revenue / conversions) if conversions > 0 else 0
        cpi = (revenue / metrics['installs']) if metrics['installs'] > 0 else 0
        
        return {
            'ctr_percent': round(ctr, 2),
            'cvr_percent': round(cvr, 2),
            'cpm': round(cpm, 2),
            'cpa': round(cpa, 2),
            'cpi': round(cpi, 2)
        }
    
    def _calculate_user_derived_metrics(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate derived metrics for user.
        
        Args:
            metrics: User metrics
            
        Returns:
            Derived metrics
        """
        session_durations = metrics['session_durations']
        total_events = metrics['total_events']
        total_revenue = metrics['total_revenue']
        
        # Calculate average session duration
        avg_session_duration = (
            sum(session_durations) / len(session_durations)
            if session_durations else 0
        )
        
        # Calculate average revenue per event
        avg_revenue_per_event = (
            total_revenue / total_events
            if total_events > 0 else 0
        )
        
        # Calculate engagement score
        engagement_score = min(
            (len(session_durations) * avg_session_duration * total_revenue) / 1000,
            100
        )
        
        return {
            'avg_session_duration': round(avg_session_duration, 2),
            'avg_revenue_per_event': round(avg_revenue_per_event, 2),
            'engagement_score': round(engagement_score, 2)
        }
    
    def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get metrics for a specific campaign.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign metrics
        """
        if campaign_id not in self.campaign_metrics:
            return {"error": f"Campaign {campaign_id} not found"}
        
        metrics = self.campaign_metrics[campaign_id]
        derived_metrics = self._calculate_campaign_derived_metrics(metrics)
        
        return {
            'campaign_id': campaign_id,
            **metrics,
            **derived_metrics
        }
    
    def get_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """
        Get metrics for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            User metrics
        """
        if user_id not in self.user_metrics:
            return {"error": f"User {user_id} not found"}
        
        metrics = self.user_metrics[user_id]
        derived_metrics = self._calculate_user_derived_metrics(metrics)
        
        return {
            'user_id': user_id,
            **metrics,
            **derived_metrics
        }
    
    def get_top_campaigns(self, limit: int = 10, 
                         sort_by: str = 'revenue') -> List[Dict[str, Any]]:
        """
        Get top performing campaigns.
        
        Args:
            limit: Number of campaigns to return
            sort_by: Sort field ('revenue', 'impressions', 'ctr', etc.)
            
        Returns:
            List of top campaigns
        """
        campaigns = []
        
        for campaign_id, metrics in self.campaign_metrics.items():
            derived_metrics = self._calculate_campaign_derived_metrics(metrics)
            
            campaign_data = {
                'campaign_id': campaign_id,
                **metrics,
                **derived_metrics
            }
            
            campaigns.append(campaign_data)
        
        # Sort by specified field
        reverse = True  # Descending order
        if sort_by == 'ctr_percent' or sort_by == 'cvr_percent':
            reverse = True
        elif sort_by == 'cpa' or sort_by == 'cpi':
            reverse = False  # Lower is better
        
        campaigns.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
        
        return campaigns[:limit]
    
    def get_top_users(self, limit: int = 10, 
                     sort_by: str = 'total_revenue') -> List[Dict[str, Any]]:
        """
        Get top performing users.
        
        Args:
            limit: Number of users to return
            sort_by: Sort field ('total_revenue', 'engagement_score', etc.)
            
        Returns:
            List of top users
        """
        users = []
        
        for user_id, metrics in self.user_metrics.items():
            derived_metrics = self._calculate_user_derived_metrics(metrics)
            
            user_data = {
                'user_id': user_id,
                **metrics,
                **derived_metrics
            }
            
            users.append(user_data)
        
        # Sort by specified field
        users.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        
        return users[:limit]
    
    def get_aggregation_stats(self) -> Dict[str, Any]:
        """Get aggregation processing statistics."""
        total_campaigns = len(self.campaign_metrics)
        total_users = len(self.user_metrics)
        
        total_impressions = sum(m['impressions'] for m in self.campaign_metrics.values())
        total_clicks = sum(m['clicks'] for m in self.campaign_metrics.values())
        total_revenue = sum(m['revenue'] for m in self.campaign_metrics.values())
        
        return {
            'total_campaigns': total_campaigns,
            'total_users': total_users,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_revenue': round(total_revenue, 2),
            'overall_ctr': round((total_clicks / total_impressions * 100), 2) if total_impressions > 0 else 0
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics (useful for testing)."""
        self.campaign_metrics.clear()
        self.user_metrics.clear()
        logger.info("Reset all metrics")
    
    def cleanup_old_events(self, retention_hours: int = 24) -> None:
        """
        Clean up old events from memory.
        
        Args:
            retention_hours: Number of hours to retain events
        """
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        
        # Clean campaign events
        for campaign_id, metrics in self.campaign_metrics.items():
            metrics['events'] = [
                event for event in metrics['events']
                if self._parse_timestamp(event.get('timestamp', '')) > cutoff_time
            ]
        
        # Clean user events
        for user_id, metrics in self.user_metrics.items():
            metrics['events'] = [
                event for event in metrics['events']
                if self._parse_timestamp(event.get('timestamp', '')) > cutoff_time
            ]
        
        logger.info(f"Cleaned up events older than {retention_hours} hours")
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime object."""
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            return datetime.now() 
"""
Data enrichment processor for Flink streaming pipeline.

This module handles enriching campaign events with user profile
and behavior data for comprehensive analytics.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataEnrichmentProcessor:
    """Processor for enriching campaign events with additional data."""
    
    def __init__(self):
        """Initialize the data enrichment processor."""
        self.user_profiles = {}
        self.user_behaviors = {}
        self.campaign_data = {}
        
        logger.info("Initialized data enrichment processor")
    
    def load_user_profiles(self, profiles: List[Dict[str, Any]]) -> None:
        """
        Load user profiles for enrichment.
        
        Args:
            profiles: List of user profile data
        """
        for profile in profiles:
            user_id = profile.get('user_id')
            if user_id:
                self.user_profiles[user_id] = profile
        
        logger.info(f"Loaded {len(self.user_profiles)} user profiles")
    
    def load_campaign_data(self, campaigns: List[Dict[str, Any]]) -> None:
        """
        Load campaign data for enrichment.
        
        Args:
            campaigns: List of campaign data
        """
        for campaign in campaigns:
            campaign_id = campaign.get('campaign_id')
            if campaign_id:
                self.campaign_data[campaign_id] = campaign
        
        logger.info(f"Loaded {len(self.campaign_data)} campaigns")
    
    def enrich_campaign_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a campaign event with user and campaign data.
        
        Args:
            event: Campaign event data
            
        Returns:
            Enriched event data
        """
        enriched_event = event.copy()
        
        # Enrich with user profile
        user_id = event.get('user_id')
        if user_id and user_id in self.user_profiles:
            user_profile = self.user_profiles[user_id]
            for key, value in user_profile.items():
                if key not in enriched_event:
                    enriched_event[f'user_{key}'] = value
        
        # Enrich with campaign data
        campaign_id = event.get('campaign_id')
        if campaign_id and campaign_id in self.campaign_data:
            campaign_data = self.campaign_data[campaign_id]
            for key, value in campaign_data.items():
                if key not in enriched_event:
                    enriched_event[f'campaign_{key}'] = value
        
        # Add enrichment timestamp
        enriched_event['enriched_at'] = datetime.now().isoformat()
        
        return enriched_event
    
    def enrich_user_behavior(self, behavior: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a user behavior with user profile data.
        
        Args:
            behavior: User behavior data
            
        Returns:
            Enriched behavior data
        """
        enriched_behavior = behavior.copy()
        
        # Enrich with user profile
        user_id = behavior.get('user_id')
        if user_id and user_id in self.user_profiles:
            user_profile = self.user_profiles[user_id]
            for key, value in user_profile.items():
                if key not in enriched_behavior:
                    enriched_behavior[f'user_{key}'] = value
        
        # Add enrichment timestamp
        enriched_behavior['enriched_at'] = datetime.now().isoformat()
        
        return enriched_behavior
    
    def calculate_user_segment(self, user_profile: Dict[str, Any]) -> str:
        """
        Calculate user segment based on profile data.
        
        Args:
            user_profile: User profile data
            
        Returns:
            User segment
        """
        age = user_profile.get('age', 0)
        premium = user_profile.get('premium_user', False)
        total_sessions = user_profile.get('total_sessions', 0)
        
        if premium:
            return 'premium'
        elif age < 25:
            return 'young'
        elif age > 55:
            return 'senior'
        elif total_sessions > 100:
            return 'active'
        else:
            return 'casual'
    
    def calculate_campaign_performance_score(self, event: Dict[str, Any]) -> float:
        """
        Calculate campaign performance score.
        
        Args:
            event: Campaign event data
            
        Returns:
            Performance score (0-100)
        """
        event_type = event.get('event_type', '')
        revenue = float(event.get('revenue', 0) or 0)
        
        # Base scores for different event types
        event_scores = {
            'impression': 1,
            'click': 10,
            'conversion': 50,
            'install': 30,
            'purchase': 100
        }
        
        base_score = event_scores.get(event_type, 0)
        
        # Add revenue bonus
        revenue_bonus = min(revenue * 2, 50)  # Cap at 50 points
        
        return min(base_score + revenue_bonus, 100)
    
    def get_enrichment_stats(self) -> Dict[str, Any]:
        """Get enrichment processing statistics."""
        return {
            'user_profiles_loaded': len(self.user_profiles),
            'campaigns_loaded': len(self.campaign_data),
            'user_behaviors_loaded': len(self.user_behaviors)
        } 
"""Data models for the Ads Campaign Metrics pipeline."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of campaign events."""
    IMPRESSION = "impression"
    CLICK = "click"
    CONVERSION = "conversion"
    INSTALL = "install"
    PURCHASE = "purchase"


class Platform(str, Enum):
    """Supported platforms."""
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class CampaignEvent(BaseModel):
    """Model for campaign events from mobile and web applications."""
    
    event_id: str = Field(..., description="Unique event identifier")
    user_id: str = Field(..., description="User identifier")
    campaign_id: str = Field(..., description="Campaign identifier")
    event_type: EventType = Field(..., description="Type of event")
    platform: Platform = Field(..., description="Platform where event occurred")
    timestamp: datetime = Field(..., description="Event timestamp")
    revenue: Optional[float] = Field(default=None, description="Revenue from event")
    currency: Optional[str] = Field(default="USD", description="Currency code")
    country: Optional[str] = Field(default=None, description="User country")
    device_type: Optional[str] = Field(default=None, description="Device type")
    app_version: Optional[str] = Field(default=None, description="App version")
    creative_id: Optional[str] = Field(default=None, description="Creative identifier")
    placement_id: Optional[str] = Field(default=None, description="Ad placement identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserProfile(BaseModel):
    """Model for user profile data."""
    
    user_id: str = Field(..., description="User identifier")
    age: Optional[int] = Field(default=None, description="User age")
    gender: Optional[str] = Field(default=None, description="User gender")
    country: Optional[str] = Field(default=None, description="User country")
    language: Optional[str] = Field(default=None, description="User language")
    platform: Platform = Field(..., description="Primary platform")
    registration_date: datetime = Field(..., description="User registration date")
    last_active: datetime = Field(..., description="Last active timestamp")
    total_revenue: float = Field(default=0.0, description="Total user revenue")
    total_events: int = Field(default=0, description="Total user events")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserBehavior(BaseModel):
    """Model for user behavior data."""
    
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    event_name: str = Field(..., description="Behavior event name")
    timestamp: datetime = Field(..., description="Event timestamp")
    platform: Platform = Field(..., description="Platform")
    screen_name: Optional[str] = Field(default=None, description="Screen name")
    action_type: Optional[str] = Field(default=None, description="Action type")
    duration: Optional[int] = Field(default=None, description="Event duration in seconds")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Event properties")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EnrichedCampaignMetrics(BaseModel):
    """Model for enriched campaign metrics."""
    
    event_id: str = Field(..., description="Original event identifier")
    user_id: str = Field(..., description="User identifier")
    campaign_id: str = Field(..., description="Campaign identifier")
    event_type: EventType = Field(..., description="Event type")
    platform: Platform = Field(..., description="Platform")
    timestamp: datetime = Field(..., description="Event timestamp")
    revenue: Optional[float] = Field(default=None, description="Revenue")
    currency: str = Field(default="USD", description="Currency")
    
    # Enriched user data
    user_age: Optional[int] = Field(default=None, description="User age")
    user_gender: Optional[str] = Field(default=None, description="User gender")
    user_country: Optional[str] = Field(default=None, description="User country")
    user_language: Optional[str] = Field(default=None, description="User language")
    user_registration_date: Optional[datetime] = Field(default=None, description="User registration date")
    user_total_revenue: float = Field(default=0.0, description="User total revenue")
    user_total_events: int = Field(default=0, description="User total events")
    
    # Enriched behavior data
    user_session_count: int = Field(default=0, description="User session count")
    user_avg_session_duration: Optional[float] = Field(default=None, description="Average session duration")
    user_favorite_screen: Optional[str] = Field(default=None, description="User's most visited screen")
    
    # Campaign metrics
    campaign_total_impressions: int = Field(default=0, description="Campaign total impressions")
    campaign_total_clicks: int = Field(default=0, description="Campaign total clicks")
    campaign_total_conversions: int = Field(default=0, description="Campaign total conversions")
    campaign_ctr: float = Field(default=0.0, description="Campaign click-through rate")
    campaign_cvr: float = Field(default=0.0, description="Campaign conversion rate")
    
    # Processing metadata
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")
    enrichment_version: str = Field(default="1.0", description="Enrichment version")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CampaignSummary(BaseModel):
    """Model for campaign summary statistics."""
    
    campaign_id: str = Field(..., description="Campaign identifier")
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    platform: Platform = Field(..., description="Platform")
    
    # Daily metrics
    impressions: int = Field(default=0, description="Daily impressions")
    clicks: int = Field(default=0, description="Daily clicks")
    conversions: int = Field(default=0, description="Daily conversions")
    revenue: float = Field(default=0.0, description="Daily revenue")
    
    # Calculated metrics
    ctr: float = Field(default=0.0, description="Click-through rate")
    cvr: float = Field(default=0.0, description="Conversion rate")
    cpc: float = Field(default=0.0, description="Cost per click")
    cpa: float = Field(default=0.0, description="Cost per acquisition")
    roas: float = Field(default=0.0, description="Return on ad spend")
    
    # User metrics
    unique_users: int = Field(default=0, description="Unique users")
    new_users: int = Field(default=0, description="New users")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 
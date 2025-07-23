"""Configuration management for the Ads Campaign Metrics pipeline."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Kafka Configuration
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        description="Kafka bootstrap servers"
    )
    kafka_topic_campaign_events: str = Field(
        default="ads-campaign-events",
        description="Topic for campaign events"
    )
    kafka_topic_user_profiles: str = Field(
        default="user-profiles",
        description="Topic for user profiles"
    )
    kafka_topic_behavior_data: str = Field(
        default="user-behavior",
        description="Topic for user behavior data"
    )
    kafka_topic_enriched_metrics: str = Field(
        default="enriched-campaign-metrics",
        description="Topic for enriched metrics"
    )

    # Flink Configuration
    flink_jobmanager_host: str = Field(
        default="localhost",
        description="Flink JobManager host"
    )
    flink_jobmanager_port: int = Field(
        default=8081,
        description="Flink JobManager port"
    )
    flink_parallelism: int = Field(
        default=2,
        description="Flink parallelism level"
    )

    # Iceberg Configuration (AWS S3)
    iceberg_warehouse_path: str = Field(
        default="s3a://your-iceberg-bucket",
        description="Iceberg warehouse path (S3 bucket)"
    )
    iceberg_s3_endpoint: str = Field(
        default="https://s3.amazonaws.com",
        description="AWS S3 endpoint"
    )
    iceberg_s3_access_key: str = Field(
        default="your-aws-access-key",
        description="AWS access key"
    )
    iceberg_s3_secret_key: str = Field(
        default="your-aws-secret-key",
        description="AWS secret key"
    )
    iceberg_s3_region: str = Field(
        default="us-east-1",
        description="S3 region"
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/ads_campaign",
        description="Database connection URL"
    )
    database_pool_size: int = Field(
        default=10,
        description="Database connection pool size"
    )
    database_max_overflow: int = Field(
        default=20,
        description="Database connection pool max overflow"
    )

    # API Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="API host"
    )
    api_port: int = Field(
        default=8000,
        description="API port"
    )
    api_workers: int = Field(
        default=4,
        description="Number of API workers"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: str = Field(
        default="json",
        description="Log format"
    )

    # Monitoring Configuration
    prometheus_port: int = Field(
        default=9090,
        description="Prometheus metrics port"
    )
    metrics_enabled: bool = Field(
        default=True,
        description="Enable metrics collection"
    )

    # Development Configuration
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    environment: str = Field(
        default="development",
        description="Environment name"
    )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings() 
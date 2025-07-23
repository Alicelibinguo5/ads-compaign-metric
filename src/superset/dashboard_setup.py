"""
Apache Superset Dashboard Setup for Campaign Metrics.

This module provides functionality to set up and configure Apache Superset
dashboards for tracking CTR, CVR, and revenue metrics from the campaign pipeline.
"""

import json
import logging
import requests
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SupersetDashboardSetup:
    """
    Setup and configuration for Apache Superset dashboards.
    
    This class handles the creation and configuration of dashboards,
    charts, and datasets for campaign metrics visualization.
    """
    
    def __init__(self, base_url: str = "http://localhost:8088", 
                 username: str = "admin", password: str = "admin") -> None:
        """
        Initialize Superset dashboard setup.
        
        Args:
            base_url: Superset base URL
            username: Superset admin username
            password: Superset admin password
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf_token: Optional[str] = None
        
    def login(self) -> bool:
        """
        Login to Superset and get CSRF token.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            # Get login page to extract CSRF token
            login_url = f"{self.base_url}/login/"
            response = self.session.get(login_url)
            response.raise_for_status()
            
            # Extract CSRF token from login page
            # This is a simplified approach - in production, use proper CSRF extraction
            self.csrf_token = "csrf_token_placeholder"
            
            # Login
            login_data = {
                'username': self.username,
                'password': self.password,
                'csrf_token': self.csrf_token
            }
            
            response = self.session.post(login_url, data=login_data)
            response.raise_for_status()
            
            logger.info("Successfully logged into Superset")
            return True
            
        except Exception as e:
            logger.error(f"Failed to login to Superset: {e}")
            return False
    
    def create_database_connection(self, database_name: str = "campaign_metrics") -> Optional[int]:
        """
        Create database connection for campaign metrics.
        
        Args:
            database_name: Name for the database connection
            
        Returns:
            Database ID if successful, None otherwise
        """
        try:
            # Database connection configuration
            database_config = {
                "database_name": database_name,
                "sqlalchemy_uri": "postgresql://superset:superset@postgres:5432/superset",
                "extra": json.dumps({
                    "engine_params": {
                        "pool_size": 10,
                        "max_overflow": 20
                    }
                })
            }
            
            # Create database connection
            url = f"{self.base_url}/api/v1/database/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=database_config, headers=headers)
            response.raise_for_status()
            
            database_id = response.json().get('id')
            logger.info(f"Created database connection: {database_name} (ID: {database_id})")
            return database_id
            
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    def create_campaign_metrics_dataset(self, database_id: int) -> Optional[int]:
        """
        Create dataset for campaign metrics.
        
        Args:
            database_id: Database connection ID
            
        Returns:
            Dataset ID if successful, None otherwise
        """
        try:
            # Dataset configuration
            dataset_config = {
                "database": database_id,
                "schema": "public",
                "table_name": "campaign_metrics",
                "sql": """
                SELECT 
                    campaign_id,
                    window_start,
                    window_end,
                    impressions,
                    clicks,
                    conversions,
                    revenue,
                    ctr_percent,
                    cvr_percent,
                    processed_at
                FROM campaign_metrics
                """,
                "columns": [
                    {"column_name": "campaign_id", "type": "STRING"},
                    {"column_name": "window_start", "type": "TIMESTAMP"},
                    {"column_name": "window_end", "type": "TIMESTAMP"},
                    {"column_name": "impressions", "type": "BIGINT"},
                    {"column_name": "clicks", "type": "BIGINT"},
                    {"column_name": "conversions", "type": "BIGINT"},
                    {"column_name": "revenue", "type": "DOUBLE"},
                    {"column_name": "ctr_percent", "type": "DOUBLE"},
                    {"column_name": "cvr_percent", "type": "DOUBLE"},
                    {"column_name": "processed_at", "type": "TIMESTAMP"}
                ],
                "metrics": [
                    {
                        "metric_name": "total_impressions",
                        "expression": "SUM(impressions)"
                    },
                    {
                        "metric_name": "total_clicks", 
                        "expression": "SUM(clicks)"
                    },
                    {
                        "metric_name": "total_conversions",
                        "expression": "SUM(conversions)"
                    },
                    {
                        "metric_name": "total_revenue",
                        "expression": "SUM(revenue)"
                    },
                    {
                        "metric_name": "avg_ctr",
                        "expression": "AVG(ctr_percent)"
                    },
                    {
                        "metric_name": "avg_cvr",
                        "expression": "AVG(cvr_percent)"
                    }
                ]
            }
            
            # Create dataset
            url = f"{self.base_url}/api/v1/dataset/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=dataset_config, headers=headers)
            response.raise_for_status()
            
            dataset_id = response.json().get('id')
            logger.info(f"Created campaign metrics dataset (ID: {dataset_id})")
            return dataset_id
            
        except Exception as e:
            logger.error(f"Failed to create dataset: {e}")
            return None
    
    def create_campaign_events_dataset(self, database_id: int) -> Optional[int]:
        """
        Create dataset for campaign events.
        
        Args:
            database_id: Database connection ID
            
        Returns:
            Dataset ID if successful, None otherwise
        """
        try:
            # Dataset configuration
            dataset_config = {
                "database": database_id,
                "schema": "public", 
                "table_name": "campaign_events",
                "sql": """
                SELECT 
                    event_id,
                    user_id,
                    campaign_id,
                    event_type,
                    platform,
                    timestamp,
                    revenue,
                    country,
                    device_type,
                    processed_at
                FROM campaign_events
                """,
                "columns": [
                    {"column_name": "event_id", "type": "STRING"},
                    {"column_name": "user_id", "type": "STRING"},
                    {"column_name": "campaign_id", "type": "STRING"},
                    {"column_name": "event_type", "type": "STRING"},
                    {"column_name": "platform", "type": "STRING"},
                    {"column_name": "timestamp", "type": "TIMESTAMP"},
                    {"column_name": "revenue", "type": "DOUBLE"},
                    {"column_name": "country", "type": "STRING"},
                    {"column_name": "device_type", "type": "STRING"},
                    {"column_name": "processed_at", "type": "TIMESTAMP"}
                ],
                "metrics": [
                    {
                        "metric_name": "event_count",
                        "expression": "COUNT(*)"
                    },
                    {
                        "metric_name": "total_revenue",
                        "expression": "SUM(revenue)"
                    }
                ]
            }
            
            # Create dataset
            url = f"{self.base_url}/api/v1/dataset/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=dataset_config, headers=headers)
            response.raise_for_status()
            
            dataset_id = response.json().get('id')
            logger.info(f"Created campaign events dataset (ID: {dataset_id})")
            return dataset_id
            
        except Exception as e:
            logger.error(f"Failed to create events dataset: {e}")
            return None
    
    def create_ctr_trend_chart(self, dataset_id: int) -> Optional[int]:
        """
        Create CTR trend chart.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Chart ID if successful, None otherwise
        """
        try:
            chart_config = {
                "slice_name": "CTR Trend by Campaign",
                "viz_type": "line",
                "datasource_id": dataset_id,
                "datasource_type": "table",
                "params": {
                    "x_axis": "window_start",
                    "y_axis": "avg_ctr",
                    "series": "campaign_id",
                    "time_range": "Last 7 days",
                    "rolling_type": "mean",
                    "rolling_periods": 1
                },
                "query_context": {
                    "datasource": {"id": dataset_id, "type": "table"},
                    "force": False,
                    "queries": [{
                        "columns": ["campaign_id", "window_start", "avg_ctr"],
                        "filters": [],
                        "orderby": [["window_start", True]],
                        "row_limit": 1000
                    }]
                }
            }
            
            # Create chart
            url = f"{self.base_url}/api/v1/chart/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=chart_config, headers=headers)
            response.raise_for_status()
            
            chart_id = response.json().get('id')
            logger.info(f"Created CTR trend chart (ID: {chart_id})")
            return chart_id
            
        except Exception as e:
            logger.error(f"Failed to create CTR chart: {e}")
            return None
    
    def create_cvr_trend_chart(self, dataset_id: int) -> Optional[int]:
        """
        Create CVR trend chart.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Chart ID if successful, None otherwise
        """
        try:
            chart_config = {
                "slice_name": "CVR Trend by Campaign",
                "viz_type": "line",
                "datasource_id": dataset_id,
                "datasource_type": "table",
                "params": {
                    "x_axis": "window_start",
                    "y_axis": "avg_cvr",
                    "series": "campaign_id",
                    "time_range": "Last 7 days",
                    "rolling_type": "mean",
                    "rolling_periods": 1
                },
                "query_context": {
                    "datasource": {"id": dataset_id, "type": "table"},
                    "force": False,
                    "queries": [{
                        "columns": ["campaign_id", "window_start", "avg_cvr"],
                        "filters": [],
                        "orderby": [["window_start", True]],
                        "row_limit": 1000
                    }]
                }
            }
            
            # Create chart
            url = f"{self.base_url}/api/v1/chart/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=chart_config, headers=headers)
            response.raise_for_status()
            
            chart_id = response.json().get('id')
            logger.info(f"Created CVR trend chart (ID: {chart_id})")
            return chart_id
            
        except Exception as e:
            logger.error(f"Failed to create CVR chart: {e}")
            return None
    
    def create_revenue_chart(self, dataset_id: int) -> Optional[int]:
        """
        Create revenue chart.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Chart ID if successful, None otherwise
        """
        try:
            chart_config = {
                "slice_name": "Revenue by Campaign",
                "viz_type": "bar",
                "datasource_id": dataset_id,
                "datasource_type": "table",
                "params": {
                    "x_axis": "campaign_id",
                    "y_axis": "total_revenue",
                    "time_range": "Last 7 days",
                    "order_desc": True
                },
                "query_context": {
                    "datasource": {"id": dataset_id, "type": "table"},
                    "force": False,
                    "queries": [{
                        "columns": ["campaign_id", "total_revenue"],
                        "filters": [],
                        "orderby": [["total_revenue", False]],
                        "row_limit": 20
                    }]
                }
            }
            
            # Create chart
            url = f"{self.base_url}/api/v1/chart/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=chart_config, headers=headers)
            response.raise_for_status()
            
            chart_id = response.json().get('id')
            logger.info(f"Created revenue chart (ID: {chart_id})")
            return chart_id
            
        except Exception as e:
            logger.error(f"Failed to create revenue chart: {e}")
            return None
    
    def create_metrics_summary_chart(self, dataset_id: int) -> Optional[int]:
        """
        Create metrics summary chart.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Chart ID if successful, None otherwise
        """
        try:
            chart_config = {
                "slice_name": "Campaign Performance Summary",
                "viz_type": "table",
                "datasource_id": dataset_id,
                "datasource_type": "table",
                "params": {
                    "columns": ["campaign_id", "total_impressions", "total_clicks", 
                               "total_conversions", "total_revenue", "avg_ctr", "avg_cvr"],
                    "time_range": "Last 7 days",
                    "order_desc": True
                },
                "query_context": {
                    "datasource": {"id": dataset_id, "type": "table"},
                    "force": False,
                    "queries": [{
                        "columns": ["campaign_id", "total_impressions", "total_clicks",
                                   "total_conversions", "total_revenue", "avg_ctr", "avg_cvr"],
                        "filters": [],
                        "orderby": [["total_revenue", False]],
                        "row_limit": 50
                    }]
                }
            }
            
            # Create chart
            url = f"{self.base_url}/api/v1/chart/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=chart_config, headers=headers)
            response.raise_for_status()
            
            chart_id = response.json().get('id')
            logger.info(f"Created metrics summary chart (ID: {chart_id})")
            return chart_id
            
        except Exception as e:
            logger.error(f"Failed to create summary chart: {e}")
            return None
    
    def create_campaign_dashboard(self, chart_ids: List[int]) -> Optional[int]:
        """
        Create campaign performance dashboard.
        
        Args:
            chart_ids: List of chart IDs to include in dashboard
            
        Returns:
            Dashboard ID if successful, None otherwise
        """
        try:
            dashboard_config = {
                "dashboard_title": "Campaign Performance Metrics",
                "slug": "campaign-performance",
                "position_json": self._create_dashboard_layout(chart_ids),
                "metadata": {
                    "chart_configuration": {},
                    "global_chart_configuration": {
                        "refresh_frequency": 30,
                        "color_scheme": "supersetColors"
                    },
                    "global_slice_configuration": {
                        "time_range": "Last 7 days"
                    }
                }
            }
            
            # Create dashboard
            url = f"{self.base_url}/api/v1/dashboard/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=dashboard_config, headers=headers)
            response.raise_for_status()
            
            dashboard_id = response.json().get('id')
            logger.info(f"Created campaign dashboard (ID: {dashboard_id})")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            return None
    
    def _create_dashboard_layout(self, chart_ids: List[int]) -> Dict[str, Any]:
        """
        Create dashboard layout configuration.
        
        Args:
            chart_ids: List of chart IDs
            
        Returns:
            Dashboard layout configuration
        """
        layout = {}
        
        # Define chart positions (grid layout)
        positions = [
            {"id": chart_ids[0], "meta": {"width": 6, "height": 8, "x": 0, "y": 0}},  # CTR Trend
            {"id": chart_ids[1], "meta": {"width": 6, "height": 8, "x": 6, "y": 0}},  # CVR Trend
            {"id": chart_ids[2], "meta": {"width": 6, "height": 8, "x": 0, "y": 8}},  # Revenue
            {"id": chart_ids[3], "meta": {"width": 6, "height": 8, "x": 6, "y": 8}}   # Summary
        ]
        
        for i, chart_id in enumerate(chart_ids):
            if i < len(positions):
                layout[str(chart_id)] = positions[i]
        
        return layout
    
    def setup_complete_dashboard(self) -> bool:
        """
        Set up complete campaign dashboard with all components.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            logger.info("Starting complete dashboard setup...")
            
            # Login to Superset
            if not self.login():
                return False
            
            # Create database connection
            database_id = self.create_database_connection()
            if not database_id:
                return False
            
            # Create datasets
            metrics_dataset_id = self.create_campaign_metrics_dataset(database_id)
            events_dataset_id = self.create_campaign_events_dataset(database_id)
            
            if not metrics_dataset_id:
                return False
            
            # Create charts
            chart_ids = []
            
            ctr_chart_id = self.create_ctr_trend_chart(metrics_dataset_id)
            if ctr_chart_id:
                chart_ids.append(ctr_chart_id)
            
            cvr_chart_id = self.create_cvr_trend_chart(metrics_dataset_id)
            if cvr_chart_id:
                chart_ids.append(cvr_chart_id)
            
            revenue_chart_id = self.create_revenue_chart(metrics_dataset_id)
            if revenue_chart_id:
                chart_ids.append(revenue_chart_id)
            
            summary_chart_id = self.create_metrics_summary_chart(metrics_dataset_id)
            if summary_chart_id:
                chart_ids.append(summary_chart_id)
            
            # Create dashboard
            if chart_ids:
                dashboard_id = self.create_campaign_dashboard(chart_ids)
                if dashboard_id:
                    logger.info(f"Dashboard setup complete! Dashboard ID: {dashboard_id}")
                    logger.info(f"Access dashboard at: {self.base_url}/superset/dashboard/{dashboard_id}")
                    return True
            
            logger.error("Failed to create dashboard")
            return False
            
        except Exception as e:
            logger.error(f"Dashboard setup failed: {e}")
            return False


def main() -> None:
    """Main function to run dashboard setup."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Superset Dashboard Setup')
    parser.add_argument('--base-url', default='http://localhost:8088',
                       help='Superset base URL')
    parser.add_argument('--username', default='admin',
                       help='Superset username')
    parser.add_argument('--password', default='admin',
                       help='Superset password')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run dashboard setup
    setup = SupersetDashboardSetup(
        base_url=args.base_url,
        username=args.username,
        password=args.password
    )
    
    success = setup.setup_complete_dashboard()
    
    if success:
        logger.info("✅ Dashboard setup completed successfully!")
    else:
        logger.error("❌ Dashboard setup failed!")
        exit(1)


if __name__ == "__main__":
    main() 
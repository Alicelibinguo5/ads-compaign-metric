"""
Simple Superset Chart Creator via API.

This script creates charts and dashboards using Superset's REST API.
"""

import json
import logging
import requests
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SimpleChartCreator:
    """Simple chart creator for Superset."""
    
    def __init__(self, base_url: str = "http://localhost:8088", 
                 username: str = "admin", password: str = "admin") -> None:
        """Initialize chart creator."""
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf_token: Optional[str] = None
        
    def login(self) -> bool:
        """Login to Superset."""
        try:
            # Simple login approach
            login_url = f"{self.base_url}/login/"
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(login_url, data=login_data)
            response.raise_for_status()
            
            logger.info("✅ Successfully logged into Superset")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to login: {e}")
            return False
    
    def create_database_connection(self) -> Optional[int]:
        """Create PostgreSQL database connection."""
        try:
            # Use the existing PostgreSQL connection
            database_config = {
                "database_name": "Campaign Metrics DB",
                "sqlalchemy_uri": "postgresql://postgres:postgres@postgres:5432/ads_campaign",
                "extra": json.dumps({
                    "engine_params": {
                        "pool_size": 10,
                        "max_overflow": 20
                    }
                })
            }
            
            url = f"{self.base_url}/api/v1/database/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=database_config, headers=headers)
            response.raise_for_status()
            
            database_id = response.json().get('id')
            logger.info(f"✅ Created database connection (ID: {database_id})")
            return database_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create database: {e}")
            return None
    
    def create_dataset(self, database_id: int, table_name: str) -> Optional[int]:
        """Create dataset for a table."""
        try:
            dataset_config = {
                "database": database_id,
                "schema": "public",
                "table_name": table_name
            }
            
            url = f"{self.base_url}/api/v1/dataset/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=dataset_config, headers=headers)
            response.raise_for_status()
            
            dataset_id = response.json().get('id')
            logger.info(f"✅ Created dataset for {table_name} (ID: {dataset_id})")
            return dataset_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create dataset: {e}")
            return None
    
    def create_chart(self, dataset_id: int, chart_name: str, chart_type: str, 
                    config: Dict[str, Any]) -> Optional[int]:
        """Create a chart."""
        try:
            chart_config = {
                "slice_name": chart_name,
                "viz_type": chart_type,
                "datasource_id": dataset_id,
                "datasource_type": "table",
                "params": config
            }
            
            url = f"{self.base_url}/api/v1/chart/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=chart_config, headers=headers)
            response.raise_for_status()
            
            chart_id = response.json().get('id')
            logger.info(f"✅ Created chart: {chart_name} (ID: {chart_id})")
            return chart_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create chart {chart_name}: {e}")
            return None
    
    def create_dashboard(self, dashboard_name: str, chart_ids: List[int]) -> Optional[int]:
        """Create dashboard with charts."""
        try:
            dashboard_config = {
                "dashboard_title": dashboard_name,
                "slug": dashboard_name.lower().replace(" ", "-"),
                "position_json": self._create_layout(chart_ids)
            }
            
            url = f"{self.base_url}/api/v1/dashboard/"
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(url, json=dashboard_config, headers=headers)
            response.raise_for_status()
            
            dashboard_id = response.json().get('id')
            logger.info(f"✅ Created dashboard: {dashboard_name} (ID: {dashboard_id})")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create dashboard: {e}")
            return None
    
    def _create_layout(self, chart_ids: List[int]) -> Dict[str, Any]:
        """Create simple dashboard layout."""
        layout = {}
        
        # Simple 2x2 grid layout
        positions = [
            {"id": chart_ids[0], "meta": {"width": 6, "height": 8, "x": 0, "y": 0}},
            {"id": chart_ids[1], "meta": {"width": 6, "height": 8, "x": 6, "y": 0}},
            {"id": chart_ids[2], "meta": {"width": 6, "height": 8, "x": 0, "y": 8}},
            {"id": chart_ids[3], "meta": {"width": 6, "height": 8, "x": 6, "y": 8}}
        ]
        
        for i, chart_id in enumerate(chart_ids):
            if i < len(positions):
                layout[str(chart_id)] = positions[i]
        
        return layout
    
    def setup_campaign_dashboard(self) -> bool:
        """Set up complete campaign dashboard."""
        try:
            logger.info("🚀 Starting campaign dashboard setup...")
            
            # Login
            if not self.login():
                return False
            
            # Create database connection
            database_id = self.create_database_connection()
            if not database_id:
                return False
            
            # Create dataset
            dataset_id = self.create_dataset(database_id, "campaign_metrics")
            if not dataset_id:
                return False
            
            # Create charts
            chart_ids = []
            
            # Chart 1: CTR Trend
            ctr_config = {
                "x_axis": "date",
                "y_axis": "ctr",
                "series": "campaign_id",
                "time_range": "Last 7 days"
            }
            ctr_id = self.create_chart(dataset_id, "CTR Trend by Campaign", "line", ctr_config)
            if ctr_id:
                chart_ids.append(ctr_id)
            
            # Chart 2: CVR Trend
            cvr_config = {
                "x_axis": "date",
                "y_axis": "cvr",
                "series": "campaign_id",
                "time_range": "Last 7 days"
            }
            cvr_id = self.create_chart(dataset_id, "CVR Trend by Campaign", "line", cvr_config)
            if cvr_id:
                chart_ids.append(cvr_id)
            
            # Chart 3: Revenue
            revenue_config = {
                "x_axis": "campaign_id",
                "y_axis": "revenue",
                "time_range": "Last 7 days"
            }
            revenue_id = self.create_chart(dataset_id, "Revenue by Campaign", "bar", revenue_config)
            if revenue_id:
                chart_ids.append(revenue_id)
            
            # Chart 4: Summary Table
            table_config = {
                "columns": ["campaign_id", "platform", "impressions", "clicks", "conversions", "revenue", "ctr", "cvr"],
                "time_range": "Last 7 days"
            }
            table_id = self.create_chart(dataset_id, "Campaign Performance Summary", "table", table_config)
            if table_id:
                chart_ids.append(table_id)
            
            # Create dashboard
            if chart_ids:
                dashboard_id = self.create_dashboard("Campaign Metrics Dashboard", chart_ids)
                if dashboard_id:
                    logger.info(f"🎉 Dashboard created successfully!")
                    logger.info(f"📊 Access at: {self.base_url}/superset/dashboard/{dashboard_id}")
                    return True
            
            logger.error("❌ Failed to create dashboard")
            return False
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False


def main() -> None:
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Superset Chart Creator')
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
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create and run chart creator
    creator = SimpleChartCreator(
        base_url=args.base_url,
        username=args.username,
        password=args.password
    )
    
    success = creator.setup_campaign_dashboard()
    
    if success:
        logger.info("✅ Chart creation completed successfully!")
    else:
        logger.error("❌ Chart creation failed!")
        exit(1)


if __name__ == "__main__":
    main() 
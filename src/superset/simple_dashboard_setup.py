"""
Simple Superset Dashboard Setup for Campaign Metrics.

This module provides simplified functions to set up Apache Superset
dashboards for CTR, CVR, and revenue metrics.
"""

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SimpleDashboardSetup:
    """
    Simple setup for Apache Superset dashboards.
    
    This class provides easy-to-use methods for setting up
    campaign metrics dashboards in Superset.
    """
    
    def __init__(self, config_path: str = "config/superset/dashboard_config.json") -> None:
        """
        Initialize simple dashboard setup.
        
        Args:
            config_path: Path to dashboard configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load dashboard configuration from JSON file.
        
        Returns:
            Dashboard configuration dictionary
        """
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded dashboard config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return {}
    
    def check_superset_status(self) -> bool:
        """
        Check if Superset is running and accessible.
        
        Returns:
            True if Superset is accessible, False otherwise
        """
        try:
            import requests
            response = requests.get("http://localhost:8088/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Superset is running and accessible")
                return True
            else:
                logger.warning(f"Superset responded with status {response.status_code}")
                return False
        except ImportError:
            logger.warning("⚠️  requests module not available, skipping health check")
            return False
        except Exception as e:
            logger.error(f"❌ Superset is not accessible: {e}")
            return False
    
    def start_superset(self) -> bool:
        """
        Start Superset using docker-compose.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            logger.info("Starting Superset with docker-compose...")
            
            # Start all services (try both docker-compose and docker compose)
            try:
                result = subprocess.run(
                    ["docker", "compose", "up", "-d"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            except FileNotFoundError:
                # Fallback to docker-compose
                result = subprocess.run(
                    ["docker-compose", "up", "-d"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            
            if result.returncode == 0:
                logger.info("✅ Docker services started successfully")
                
                # Wait for Superset to be ready
                logger.info("Waiting for Superset to be ready...")
                for i in range(30):  # Wait up to 30 seconds
                    if self.check_superset_status():
                        return True
                    time.sleep(1)
                
                logger.warning("Superset took longer than expected to start")
                return False
            else:
                logger.error(f"❌ Failed to start services: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start Superset: {e}")
            return False
    
    def print_setup_instructions(self) -> None:
        """
        Print manual setup instructions.
        """
        print("\n" + "="*60)
        print("📊 SUPERSET DASHBOARD SETUP INSTRUCTIONS")
        print("="*60)
        
        print("\n🎯 **Quick Start**")
        print("1. Access Superset: http://localhost:8088")
        print("2. Login: admin / admin")
        print("3. Follow the manual setup guide in docs/superset_dashboard_guide.md")
        
        print("\n📋 **Dashboard Components**")
        dashboard = self.config.get('dashboard', {})
        print(f"   • Dashboard Title: {dashboard.get('title', 'Campaign Performance Metrics')}")
        print(f"   • Auto-refresh: {dashboard.get('refresh_frequency', 30)} seconds")
        print(f"   • Time Range: {dashboard.get('default_time_range', 'Last 7 days')}")
        
        print("\n📊 **Charts to Create**")
        charts = self.config.get('charts', [])
        for i, chart in enumerate(charts, 1):
            print(f"   {i}. {chart.get('name', 'Unknown Chart')}")
            print(f"      Type: {chart.get('type', 'Unknown')}")
            print(f"      Dataset: {chart.get('dataset', 'Unknown')}")
        
        print("\n🔧 **Datasets to Create**")
        datasets = self.config.get('datasets', [])
        for dataset in datasets:
            print(f"   • {dataset.get('name', 'Unknown')}")
            print(f"     Table: {dataset.get('table', 'Unknown')}")
        
        print("\n📈 **Key Metrics**")
        print("   • CTR (Click-Through Rate): (Clicks / Impressions) × 100")
        print("   • CVR (Conversion Rate): (Conversions / Clicks) × 100")
        print("   • Revenue: Total revenue generated by campaigns")
        
        print("\n🚀 **Next Steps**")
        print("1. Open docs/superset_dashboard_guide.md for detailed instructions")
        print("2. Create database connection to PostgreSQL")
        print("3. Create datasets for campaign_metrics and campaign_events")
        print("4. Create the 4 charts listed above")
        print("5. Create dashboard and arrange charts")
        
        print("\n" + "="*60)
    
    def validate_data_tables(self) -> bool:
        """
        Validate that required data tables exist.
        
        Returns:
            True if tables exist, False otherwise
        """
        try:
            import psycopg2
            
            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host="localhost",
                port="5432",
                database="superset",
                user="superset",
                password="superset"
            )
            
            cursor = conn.cursor()
            
            # Check if tables exist
            tables_to_check = ['campaign_metrics', 'campaign_events']
            existing_tables = []
            
            for table in tables_to_check:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table,))
                
                exists = cursor.fetchone()[0]
                if exists:
                    existing_tables.append(table)
                    logger.info(f"✅ Table {table} exists")
                else:
                    logger.warning(f"⚠️  Table {table} does not exist")
            
            cursor.close()
            conn.close()
            
            if len(existing_tables) == len(tables_to_check):
                logger.info("✅ All required tables exist")
                return True
            else:
                logger.warning(f"⚠️  Only {len(existing_tables)}/{len(tables_to_check)} tables exist")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to validate tables: {e}")
            return False
    
    def print_data_queries(self) -> None:
        """
        Print sample queries to validate data.
        """
        print("\n" + "="*60)
        print("📊 DATA VALIDATION QUERIES")
        print("="*60)
        
        print("\n🔍 **Check Campaign Metrics Data**")
        print("""
SELECT 
    campaign_id,
    COUNT(*) as records,
    AVG(ctr_percent) as avg_ctr,
    AVG(cvr_percent) as avg_cvr,
    SUM(revenue) as total_revenue
FROM campaign_metrics 
GROUP BY campaign_id
ORDER BY total_revenue DESC;
        """)
        
        print("\n🔍 **Check Campaign Events Data**")
        print("""
SELECT 
    event_type,
    COUNT(*) as count,
    SUM(revenue) as total_revenue
FROM campaign_events 
GROUP BY event_type;
        """)
        
        print("\n🔍 **Check Recent Data**")
        print("""
SELECT 
    'metrics' as table_name,
    COUNT(*) as record_count,
    MAX(processed_at) as latest_record
FROM campaign_metrics
UNION ALL
SELECT 
    'events' as table_name,
    COUNT(*) as record_count,
    MAX(processed_at) as latest_record
FROM campaign_events;
        """)
        
        print("="*60)
    
    def setup_dashboard(self) -> bool:
        """
        Complete dashboard setup process.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            logger.info("🚀 Starting dashboard setup...")
            
            # Check if Superset is running
            if not self.check_superset_status():
                logger.info("Superset not running, attempting to start...")
                if not self.start_superset():
                    logger.error("❌ Failed to start Superset")
                    return False
            
            # Validate data tables
            logger.info("Validating data tables...")
            if not self.validate_data_tables():
                logger.warning("⚠️  Some data tables may be missing")
            
            # Print setup instructions
            self.print_setup_instructions()
            
            # Print data validation queries
            self.print_data_queries()
            
            logger.info("✅ Dashboard setup instructions provided")
            logger.info("📖 See docs/superset_dashboard_guide.md for detailed steps")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Dashboard setup failed: {e}")
            return False


def main() -> None:
    """Main function to run dashboard setup."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Superset Dashboard Setup')
    parser.add_argument('--config', default='config/superset/dashboard_config.json',
                       help='Path to dashboard configuration file')
    parser.add_argument('--start-superset', action='store_true',
                       help='Start Superset if not running')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run dashboard setup
    setup = SimpleDashboardSetup(args.config)
    
    success = setup.setup_dashboard()
    
    if success:
        print("\n🎉 Dashboard setup completed successfully!")
        print("📊 Access your dashboard at: http://localhost:8088")
    else:
        print("\n❌ Dashboard setup failed!")
        exit(1)


if __name__ == "__main__":
    main() 
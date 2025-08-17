#!/usr/bin/env python3
"""
ANYmal Data Navigator API Client
Practical client for interacting with discovered Data Navigator endpoints
"""

import requests
import json
import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataNavigatorClient:
    """Client for ANYmal Data Navigator API"""
    
    def __init__(self, server_url: str, verify_ssl: bool = True):
        if server_url.startswith('http'):
            self.base_url = server_url.rstrip('/')
        else:
            self.base_url = f"https://{server_url.strip('api-').rstrip('/')}"
            
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.access_token = None
    
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the ANYmal server"""
        auth_url = f"{self.base_url}/authentication-service/auth/login"
        
        payload = {"email": email, "password": password}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = self.session.post(auth_url, headers=headers, json=payload, verify=self.verify_ssl, timeout=30)
            
            if response.status_code == 201:
                data = response.json()
                self.access_token = data.get("accessToken")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                logger.info("✅ Authentication successful")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def get_inspections(self, limit: int = None, robot_name: str = None) -> Optional[Dict[str, Any]]:
        """Get inspection events"""
        url = f"{self.base_url}/data-navigator-api/inspections"
        params = {}
        
        if limit:
            params['limit'] = limit
        if robot_name:
            params['robotName'] = robot_name
            
        try:
            response = self.session.get(url, params=params, verify=self.verify_ssl, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Get inspections failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Get inspections error: {e}")
            return None
    
    def get_missions(self) -> Optional[Dict[str, Any]]:
        """Get all missions"""
        url = f"{self.base_url}/data-navigator-api/missions"
        
        try:
            response = self.session.get(url, verify=self.verify_ssl, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Get missions failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Get missions error: {e}")
            return None
    
    def get_robots(self) -> Optional[Dict[str, Any]]:
        """Get all robots"""
        url = f"{self.base_url}/data-navigator-api/robots"
        
        try:
            response = self.session.get(url, verify=self.verify_ssl, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Get robots failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Get robots error: {e}")
            return None
    
    def get_assets(self) -> Optional[Dict[str, Any]]:
        """Get all assets"""
        url = f"{self.base_url}/data-navigator-api/assets"
        
        try:
            response = self.session.get(url, verify=self.verify_ssl, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Get assets failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Get assets error: {e}")
            return None
    
    def download_inspection_raw_data(self, filename: str, output_dir: str = "./downloads") -> Optional[str]:
        """Download inspection raw data file"""
        url = f"{self.base_url}/data-navigator-api/inspections/raw-data/{filename}"
        
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        
        try:
            response = self.session.get(url, verify=self.verify_ssl, timeout=60, stream=True)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Downloaded {filename} ({file_size} bytes)")
                return output_path
            elif response.status_code == 404:
                logger.warning(f"⚠️  File not found: {filename}")
                return None
            else:
                logger.error(f"❌ Download failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            return None
    
    def analyze_inspection_data(self, inspections_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze inspection data for insights"""
        items = inspections_data.get('items', [])
        
        if not items:
            return {'error': 'No inspection data available'}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(items)
        
        analysis = {
            'total_inspections': len(items),
            'date_range': {
                'earliest': min(item['timestamp'] for item in items),
                'latest': max(item['timestamp'] for item in items)
            },
            'outcomes': df['outcome'].value_counts().to_dict() if 'outcome' in df.columns else {},
            'robots': df['robotName'].value_counts().to_dict() if 'robotName' in df.columns else {},
            'assets': df['assetName'].value_counts().to_dict() if 'assetName' in df.columns else {},
            'missions': df['missionName'].value_counts().to_dict() if 'missionName' in df.columns else {},
            'measurement_stats': {
                'mean': float(df['measurement'].mean()) if 'measurement' in df.columns else 0,
                'min': float(df['measurement'].min()) if 'measurement' in df.columns else 0,
                'max': float(df['measurement'].max()) if 'measurement' in df.columns else 0,
                'std': float(df['measurement'].std()) if 'measurement' in df.columns else 0
            }
        }
        
        return analysis


def main():
    """Example usage of Data Navigator API client"""
    
    # Get credentials
    server_url = os.getenv("ANYMAL_SERVER_URL", "raas-ge-ver.prod.anybotics.com")
    email = os.getenv("ANYMAL_EMAIL")
    password = os.getenv("ANYMAL_PASSWORD")
    
    if not all([email, password]):
        logger.error("❌ Missing credentials. Please set ANYMAL_EMAIL and ANYMAL_PASSWORD environment variables.")
        return
    
    # Initialize client
    client = DataNavigatorClient(server_url, verify_ssl=True)
    
    # Authenticate
    if not client.authenticate(email, password):
        logger.error("❌ Authentication failed")
        return
    
    print("\n" + "="*60)
    print("🗂️  ANYmal Data Navigator API Client")
    print("="*60)
    
    # Get robots
    print("\n🤖 ROBOTS:")
    robots_data = client.get_robots()
    if robots_data:
        for robot in robots_data.get('items', []):
            print(f"  • {robot['name']} (ID: {robot['id']})")
    
    # Get assets
    print("\n🏭 ASSETS:")
    assets_data = client.get_assets()
    if assets_data:
        for asset in assets_data.get('items', [])[:10]:  # Show first 10
            breadcrumb = " > ".join([bc['name'] for bc in asset.get('breadcrumbs', [])])
            print(f"  • {asset['name']} (ID: {asset['id']}) - {breadcrumb}")
    
    # Get missions
    print("\n🎯 MISSIONS:")
    missions_data = client.get_missions()
    if missions_data:
        for mission in missions_data.get('items', []):
            outcome = mission.get('lastRunOutcome', 'Unknown')
            events = mission.get('totalInspectionEvents', 0)
            duration = mission.get('estimatedDuration', 0) or 0
            print(f"  • {mission['name']} - {outcome} ({events} events, {duration:.2f}h)")
    
    # Get recent inspections
    print("\n🔍 RECENT INSPECTIONS:")
    inspections_data = client.get_inspections(limit=10)
    if inspections_data:
        for inspection in inspections_data.get('items', [])[:5]:  # Show first 5
            timestamp = inspection.get('timestamp', '')[:19]  # Remove milliseconds
            outcome = inspection.get('outcome', 'Unknown')
            measurement = inspection.get('measurement', 0)
            asset = inspection.get('assetName', 'Unknown')
            robot = inspection.get('robotName', 'Unknown')
            print(f"  • {timestamp} - {asset} on {robot}: {measurement} ({outcome})")
    
    # Analyze inspection data
    if inspections_data:
        print("\n📊 INSPECTION ANALYSIS:")
        analysis = client.analyze_inspection_data(inspections_data)
        
        print(f"  Total Inspections: {analysis['total_inspections']}")
        print(f"  Date Range: {analysis['date_range']['earliest'][:10]} to {analysis['date_range']['latest'][:10]}")
        
        if analysis['outcomes']:
            print("  Outcomes:")
            for outcome, count in analysis['outcomes'].items():
                print(f"    • {outcome}: {count}")
        
        if analysis['robots']:
            print("  Robots:")
            for robot, count in analysis['robots'].items():
                print(f"    • {robot}: {count} inspections")
        
        stats = analysis['measurement_stats']
        print(f"  Measurements: {stats['min']:.2f} - {stats['max']:.2f} (avg: {stats['mean']:.2f})")
    
    print(f"\n✅ Data Navigator API exploration complete!")


if __name__ == "__main__":
    main()
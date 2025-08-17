#!/usr/bin/env python3
"""
Analyze the Data Navigator web portal to discover API endpoints by examining
JavaScript files and making targeted requests based on common patterns
"""
import requests
import json
import os
import re
from urllib.parse import urljoin

class PortalNetworkAnalyzer:
    def __init__(self):
        self.base_url = "https://raas-ge-ver.prod.anybotics.com"
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self):
        """Authenticate and get token"""
        email = os.getenv('ANYMAL_EMAIL')
        password = os.getenv('ANYMAL_PASSWORD')
        
        if not email or not password:
            raise ValueError("Please set ANYMAL_EMAIL and ANYMAL_PASSWORD environment variables")
        
        auth_url = f"{self.base_url}/authentication-service/auth/login"
        auth_data = {"email": email, "password": password}
        
        print("🔐 Authenticating...")
        response = self.session.post(auth_url, json=auth_data)
        
        if response.status_code in [200, 201]:
            auth_result = response.json()
            self.token = auth_result.get('accessToken')
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            print(f"✅ Authentication successful (status: {response.status_code})")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    
    def discover_common_api_patterns(self):
        """Test common API endpoint patterns based on what we know"""
        print("\n🎯 Testing common API patterns...")
        
        # Known working base
        known_base = "/data-navigator-api"
        
        # Common REST patterns to test
        test_patterns = [
            # Analytics and reporting
            f"{known_base}/analytics",
            f"{known_base}/analytics/summary",
            f"{known_base}/analytics/trends",
            f"{known_base}/reports",
            f"{known_base}/reports/summary",
            f"{known_base}/dashboard",
            f"{known_base}/dashboard/stats",
            
            # Detailed endpoints for known resources
            f"{known_base}/inspections/summary",
            f"{known_base}/inspections/stats",
            f"{known_base}/inspections/recent",
            f"{known_base}/inspections/by-asset",
            f"{known_base}/inspections/by-robot",
            f"{known_base}/inspections/by-mission",
            
            f"{known_base}/missions/summary",
            f"{known_base}/missions/stats",
            f"{known_base}/missions/recent",
            f"{known_base}/missions/active",
            f"{known_base}/missions/completed",
            
            f"{known_base}/robots/summary",
            f"{known_base}/robots/stats",
            f"{known_base}/robots/status",
            f"{known_base}/robots/active",
            
            f"{known_base}/assets/summary",
            f"{known_base}/assets/stats",
            f"{known_base}/assets/hierarchy",
            f"{known_base}/assets/tree",
            
            # Configuration and settings
            f"{known_base}/config",
            f"{known_base}/settings",
            f"{known_base}/preferences",
            
            # Search and filtering
            f"{known_base}/search",
            f"{known_base}/filters",
            
            # File management
            f"{known_base}/files",
            f"{known_base}/uploads",
            f"{known_base}/downloads",
            
            # User and permissions
            f"{known_base}/users",
            f"{known_base}/permissions",
            f"{known_base}/profile",
            
            # Other service patterns
            "/workforce-api/inspections",
            "/workforce-api/missions", 
            "/workforce-api/robots",
            "/workforce-api/assets",
            "/fleet-api/robots",
            "/fleet-api/missions",
            "/analytics-api/inspections",
            "/analytics-api/reports",
            "/reporting-api/generate",
            "/file-service/upload",
            "/file-service/download",
        ]
        
        working_endpoints = []
        
        for endpoint in test_patterns:
            try:
                url = urljoin(self.base_url, endpoint)
                print(f"🔍 Testing: {endpoint}")
                
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        data_preview = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                        print(f"   ✅ Working: {response.status_code} - {data_preview}")
                        working_endpoints.append({
                            'endpoint': endpoint,
                            'status': response.status_code,
                            'data_sample': data_preview,
                            'content_type': response.headers.get('content-type', ''),
                            'size': len(response.content)
                        })
                    except:
                        print(f"   ✅ Working: {response.status_code} (non-JSON response)")
                        working_endpoints.append({
                            'endpoint': endpoint,
                            'status': response.status_code,
                            'content_type': response.headers.get('content-type', ''),
                            'size': len(response.content)
                        })
                elif response.status_code in [401, 403]:
                    print(f"   🔐 Auth issue: {response.status_code}")
                elif response.status_code == 404:
                    print(f"   ❌ Not found: {response.status_code}")
                else:
                    print(f"   ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return working_endpoints
    
    def test_parameterized_endpoints(self):
        """Test endpoints with parameters using known data"""
        print("\n🔧 Testing parameterized endpoints...")
        
        # First get some IDs to test with
        try:
            # Get robot IDs
            robots_response = self.session.get(f"{self.base_url}/data-navigator-api/robots")
            robot_ids = []
            if robots_response.status_code == 200:
                robots = robots_response.json()
                robot_ids = [str(robot.get('id', '')) for robot in robots if robot.get('id')]
            
            # Get asset IDs  
            assets_response = self.session.get(f"{self.base_url}/data-navigator-api/assets")
            asset_ids = []
            if assets_response.status_code == 200:
                assets = assets_response.json()
                asset_ids = [str(asset.get('id', '')) for asset in assets if asset.get('id')]
            
            print(f"   Found {len(robot_ids)} robot IDs and {len(asset_ids)} asset IDs to test with")
            
        except Exception as e:
            print(f"   ⚠️  Could not get IDs for testing: {e}")
            robot_ids = ['1', '2']  # Fallback
            asset_ids = ['1', '2', '3']  # Fallback
        
        working_endpoints = []
        
        # Test parameterized endpoints
        param_patterns = [
            # Robot-specific endpoints
            ("/data-navigator-api/robots/{}/inspections", robot_ids[:2]),
            ("/data-navigator-api/robots/{}/missions", robot_ids[:2]),
            ("/data-navigator-api/robots/{}/status", robot_ids[:2]),
            ("/data-navigator-api/robots/{}/stats", robot_ids[:2]),
            
            # Asset-specific endpoints
            ("/data-navigator-api/assets/{}/inspections", asset_ids[:3]),
            ("/data-navigator-api/assets/{}/history", asset_ids[:3]),
            ("/data-navigator-api/assets/{}/stats", asset_ids[:3]),
            
            # Inspection-specific endpoints (using inspection IDs if we can get them)
            ("/data-navigator-api/inspections/{}/details", ['1', '2']),
            ("/data-navigator-api/inspections/{}/files", ['1', '2']),
            ("/data-navigator-api/inspections/{}/metadata", ['1', '2']),
        ]
        
        for pattern, test_ids in param_patterns:
            for test_id in test_ids:
                endpoint = pattern.format(test_id)
                try:
                    url = urljoin(self.base_url, endpoint)
                    print(f"🔍 Testing: {endpoint}")
                    
                    response = self.session.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            data_preview = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                            print(f"   ✅ Working: {response.status_code} - {data_preview}")
                            working_endpoints.append({
                                'endpoint': endpoint,
                                'status': response.status_code,
                                'data_sample': data_preview,
                                'parameter_used': test_id
                            })
                        except:
                            print(f"   ✅ Working: {response.status_code} (non-JSON)")
                            working_endpoints.append({
                                'endpoint': endpoint,
                                'status': response.status_code,
                                'parameter_used': test_id
                            })
                    elif response.status_code == 404:
                        print(f"   ❌ Not found: {response.status_code}")
                    else:
                        print(f"   ⚠️  Status: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
        
        return working_endpoints
    
    def run_analysis(self):
        """Run the complete analysis"""
        print("🚀 Starting Portal Network Analysis...")
        
        if not self.authenticate():
            return
        
        # Test common patterns
        common_endpoints = self.discover_common_api_patterns()
        
        # Test parameterized endpoints
        param_endpoints = self.test_parameterized_endpoints()
        
        all_working = common_endpoints + param_endpoints
        
        # Report results
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"✅ Working common endpoints: {len(common_endpoints)}")
        print(f"✅ Working parameterized endpoints: {len(param_endpoints)}")
        print(f"🎯 Total working endpoints: {len(all_working)}")
        
        if all_working:
            print(f"\n🎯 ALL WORKING ENDPOINTS:")
            for endpoint_info in all_working:
                endpoint = endpoint_info['endpoint']
                status = endpoint_info['status']
                if 'data_sample' in endpoint_info:
                    sample = endpoint_info['data_sample']
                    print(f"✅ {endpoint} - {status}")
                    print(f"   📄 Sample: {sample}")
                else:
                    print(f"✅ {endpoint} - {status}")
        
        # Save results
        results = {
            'analysis_timestamp': '2025-01-16',
            'base_url': self.base_url,
            'common_endpoints': common_endpoints,
            'parameterized_endpoints': param_endpoints,
            'total_working': len(all_working)
        }
        
        with open('portal_network_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: portal_network_analysis_results.json")
        
        return all_working

if __name__ == "__main__":
    analyzer = PortalNetworkAnalyzer()
    analyzer.run_analysis()
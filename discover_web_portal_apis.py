#!/usr/bin/env python3
"""
Discover additional API endpoints by analyzing the Data Navigator web portal
"""
import requests
import json
import os
from urllib.parse import urljoin, urlparse
import re

class WebPortalAPIDiscovery:
    def __init__(self):
        self.base_url = "https://raas-ge-ver.prod.anybotics.com"
        self.session = requests.Session()
        self.token = None
        self.discovered_endpoints = set()
        
    def authenticate(self):
        """Authenticate and get token"""
        email = os.getenv('ANYBOTICS_EMAIL')
        password = os.getenv('ANYBOTICS_PASSWORD')
        
        if not email or not password:
            raise ValueError("Please set ANYBOTICS_EMAIL and ANYBOTICS_PASSWORD environment variables")
        
        auth_url = f"{self.base_url}/authentication-service/auth/login"
        auth_data = {"email": email, "password": password}
        
        print("🔐 Authenticating...")
        response = self.session.post(auth_url, json=auth_data)
        
        if response.status_code == 200:
            auth_result = response.json()
            self.token = auth_result.get('accessToken')
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def fetch_web_portal_pages(self):
        """Fetch key web portal pages to analyze for API calls"""
        pages_to_check = [
            "/workforce/data-navigator/",
            "/workforce/data-navigator/inspections",
            "/workforce/data-navigator/missions", 
            "/workforce/data-navigator/robots",
            "/workforce/data-navigator/assets",
            "/workforce/data-navigator/analytics",
            "/workforce/data-navigator/reports",
            "/workforce/data-navigator/dashboard"
        ]
        
        print("\n🌐 Fetching web portal pages...")
        
        for page in pages_to_check:
            try:
                url = urljoin(self.base_url, page)
                print(f"📄 Checking: {page}")
                
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    self.analyze_page_content(response.text, page)
                    print(f"   ✅ Status: {response.status_code}")
                else:
                    print(f"   ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    def analyze_page_content(self, content, page_path):
        """Analyze page content for API endpoint references"""
        # Look for API calls in JavaScript
        api_patterns = [
            r'["\']([^"\']*(?:api|service)[^"\']*)["\']',  # Generic API paths
            r'fetch\(["\']([^"\']+)["\']',  # Fetch calls
            r'axios\.(?:get|post|put|delete)\(["\']([^"\']+)["\']',  # Axios calls
            r'\.(?:get|post|put|delete)\(["\']([^"\']+)["\']',  # HTTP method calls
            r'endpoint["\']?\s*[:=]\s*["\']([^"\']+)["\']',  # Endpoint definitions
            r'url["\']?\s*[:=]\s*["\']([^"\']+)["\']',  # URL definitions
            r'/[a-zA-Z0-9-]+(?:-api|service)/[^"\'\s<>]+',  # Direct API path patterns
        ]
        
        found_endpoints = set()
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if self.is_valid_api_endpoint(match):
                    found_endpoints.add(match)
        
        # Also look for direct API references in the content
        direct_api_matches = re.findall(r'/[a-zA-Z0-9-]+(?:-api|service)/[^"\'\s<>]+', content)
        for match in direct_api_matches:
            if self.is_valid_api_endpoint(match):
                found_endpoints.add(match)
        
        if found_endpoints:
            print(f"   🔍 Found {len(found_endpoints)} potential endpoints")
            for endpoint in found_endpoints:
                self.discovered_endpoints.add(endpoint)
    
    def is_valid_api_endpoint(self, path):
        """Check if a path looks like a valid API endpoint"""
        if not path or len(path) < 5:
            return False
            
        # Must contain 'api' or 'service'
        if 'api' not in path.lower() and 'service' not in path.lower():
            return False
            
        # Skip common non-API patterns
        skip_patterns = [
            'javascript:', 'mailto:', 'tel:', 'http://', 'https://',
            '.css', '.js', '.png', '.jpg', '.gif', '.svg', '.ico',
            'google', 'facebook', 'twitter', 'linkedin'
        ]
        
        for skip in skip_patterns:
            if skip in path.lower():
                return False
        
        return True
    
    def test_discovered_endpoints(self):
        """Test discovered endpoints to see which ones work"""
        print(f"\n🧪 Testing {len(self.discovered_endpoints)} discovered endpoints...")
        
        working_endpoints = []
        
        for endpoint in sorted(self.discovered_endpoints):
            try:
                # Clean up the endpoint
                if not endpoint.startswith('/'):
                    endpoint = '/' + endpoint
                
                url = urljoin(self.base_url, endpoint)
                print(f"🔍 Testing: {endpoint}")
                
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"   ✅ Working: {response.status_code}")
                    working_endpoints.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'content_type': response.headers.get('content-type', ''),
                        'size': len(response.content)
                    })
                elif response.status_code in [401, 403]:
                    print(f"   🔐 Auth required: {response.status_code}")
                    working_endpoints.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'note': 'Authentication/Authorization required'
                    })
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        return working_endpoints
    
    def run_discovery(self):
        """Run the complete discovery process"""
        print("🚀 Starting Web Portal API Discovery...")
        
        if not self.authenticate():
            return
        
        # Fetch and analyze web portal pages
        self.fetch_web_portal_pages()
        
        # Test discovered endpoints
        working_endpoints = self.test_discovered_endpoints()
        
        # Report results
        print(f"\n📊 DISCOVERY RESULTS:")
        print(f"🔍 Total endpoints discovered: {len(self.discovered_endpoints)}")
        print(f"✅ Working endpoints: {len(working_endpoints)}")
        
        if working_endpoints:
            print(f"\n🎯 WORKING ENDPOINTS:")
            for endpoint_info in working_endpoints:
                endpoint = endpoint_info['endpoint']
                status = endpoint_info['status']
                if status == 200:
                    size = endpoint_info.get('size', 0)
                    content_type = endpoint_info.get('content_type', '')
                    print(f"✅ {endpoint} - {status} ({size} bytes, {content_type})")
                else:
                    note = endpoint_info.get('note', '')
                    print(f"🔐 {endpoint} - {status} ({note})")
        
        # Save results
        self.save_results(working_endpoints)
        
        return working_endpoints
    
    def save_results(self, working_endpoints):
        """Save discovery results to file"""
        results = {
            'discovery_timestamp': '2025-01-16',
            'base_url': self.base_url,
            'total_discovered': len(self.discovered_endpoints),
            'all_discovered_endpoints': sorted(list(self.discovered_endpoints)),
            'working_endpoints': working_endpoints
        }
        
        with open('web_portal_api_discovery_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: web_portal_api_discovery_results.json")

if __name__ == "__main__":
    discovery = WebPortalAPIDiscovery()
    discovery.run_discovery()
#!/usr/bin/env python3
"""
ANYmal Data Navigator API Discovery Tool
Discovers and documents available API endpoints at the ANYmal server
"""

import requests
import json
import os
from typing import Dict, List, Any, Optional
import logging
from urllib.parse import urljoin, urlparse
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataNavigatorAPIDiscovery:
    """Tool to discover ANYmal Data Navigator API endpoints"""
    
    def __init__(self, server_url: str, verify_ssl: bool = True):
        # Clean up server URL
        if server_url.startswith('http'):
            self.base_url = server_url.rstrip('/')
        else:
            self.base_url = f"https://{server_url.strip('api-').rstrip('/')}"
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.access_token = None
        
        # Configure session with retries
        adapter = requests.adapters.HTTPAdapter(
            max_retries=requests.adapters.Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the ANYmal server"""
        auth_url = f"{self.base_url}/authentication-service/auth/login"
        
        payload = {
            "email": email,
            "password": password
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.post(
                auth_url, 
                headers=headers, 
                json=payload, 
                verify=self.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                self.access_token = data.get("accessToken")
                
                # Set default authorization header
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                logger.info("✅ Authentication successful")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Authentication request failed: {e}")
            return False
    
    def probe_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Probe a specific endpoint and return response information"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, verify=self.verify_ssl, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, verify=self.verify_ssl, timeout=10)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, verify=self.verify_ssl, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, verify=self.verify_ssl, timeout=10)
            else:
                response = self.session.request(method, url, verify=self.verify_ssl, timeout=10)
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'status_text': response.reason,
                'headers': dict(response.headers),
                'accessible': response.status_code < 400,
                'requires_auth': response.status_code == 401,
                'content_type': response.headers.get('Content-Type', ''),
                'response_size': len(response.content)
            }
            
            # Try to parse JSON response
            try:
                if 'application/json' in response.headers.get('Content-Type', ''):
                    result['json_response'] = response.json()
                else:
                    result['text_response'] = response.text[:500]  # First 500 chars
            except:
                result['text_response'] = response.text[:200] if response.text else ''
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'endpoint': endpoint,
                'method': method,
                'error': str(e),
                'accessible': False
            }
    
    def discover_data_navigator_endpoints(self) -> Dict[str, Any]:
        """Discover Data Navigator API endpoints"""
        
        logger.info("🔍 Discovering Data Navigator API endpoints...")
        
        # Known endpoint patterns to try
        endpoints_to_probe = [
            # Data Navigator specific endpoints
            "/data-navigator-api",
            "/data-navigator-api/health",
            "/data-navigator-api/version",
            "/data-navigator-api/inspections",
            "/data-navigator-api/inspections/list",
            "/data-navigator-api/inspections/search",
            "/data-navigator-api/inspections/raw-data",
            "/data-navigator-api/inspections/metadata",
            "/data-navigator-api/missions",
            "/data-navigator-api/missions/list",
            "/data-navigator-api/robots",
            "/data-navigator-api/robots/list",
            "/data-navigator-api/assets",
            "/data-navigator-api/assets/list",
            "/data-navigator-api/files",
            "/data-navigator-api/files/list",
            "/data-navigator-api/files/upload",
            "/data-navigator-api/files/download",
            
            # General API endpoints
            "/api",
            "/api/v1",
            "/api/v2",
            "/api/health",
            "/api/version",
            "/api/status",
            
            # ANYmal API endpoints
            "/anymal-api",
            "/anymal-api/health",
            "/anymal-api/version",
            "/anymal-api/liveview",
            "/anymal-api/liveview/token",
            "/anymal-api/liveview/sources",
            "/anymal-api/liveview/tracks",
            
            # Authentication endpoints
            "/authentication-service",
            "/authentication-service/health",
            "/authentication-service/auth",
            "/authentication-service/auth/login",
            "/authentication-service/auth/logout",
            "/authentication-service/auth/refresh",
            
            # Common API discovery endpoints
            "/swagger",
            "/swagger-ui",
            "/docs",
            "/api-docs",
            "/openapi.json",
            "/swagger.json",
            "/.well-known/openapi",
            "/redoc",
            "/graphql",
            "/health",
            "/status",
            "/version",
            "/info"
        ]
        
        results = {}
        
        for endpoint in endpoints_to_probe:
            logger.info(f"🔍 Probing: {endpoint}")
            result = self.probe_endpoint(endpoint)
            results[endpoint] = result
            
            # Small delay to be respectful to the server
            time.sleep(0.1)
        
        return results
    
    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze discovery results and categorize endpoints"""
        
        analysis = {
            'accessible': [],
            'requires_auth': [],
            'not_found': [],
            'server_error': [],
            'data_navigator': [],
            'anymal_api': [],
            'authentication': [],
            'documentation': [],
            'health_status': []
        }
        
        for endpoint, result in results.items():
            if result.get('error'):
                continue
                
            status_code = result.get('status_code', 0)
            
            # Categorize by status
            if status_code < 300:
                analysis['accessible'].append(endpoint)
            elif status_code == 401:
                analysis['requires_auth'].append(endpoint)
            elif status_code == 404:
                analysis['not_found'].append(endpoint)
            elif status_code >= 500:
                analysis['server_error'].append(endpoint)
            
            # Categorize by endpoint type
            if 'data-navigator' in endpoint:
                analysis['data_navigator'].append(endpoint)
            elif 'anymal-api' in endpoint:
                analysis['anymal_api'].append(endpoint)
            elif 'authentication' in endpoint:
                analysis['authentication'].append(endpoint)
            elif any(doc in endpoint for doc in ['swagger', 'docs', 'openapi', 'redoc']):
                analysis['documentation'].append(endpoint)
            elif any(health in endpoint for health in ['health', 'status', 'version', 'info']):
                analysis['health_status'].append(endpoint)
        
        return analysis
    
    def generate_report(self, results: Dict[str, Any], analysis: Dict[str, List[str]]) -> str:
        """Generate a comprehensive API discovery report"""
        
        report = []
        report.append("=" * 80)
        report.append("🔍 ANYmal Data Navigator API Discovery Report")
        report.append("=" * 80)
        report.append(f"Server: {self.base_url}")
        report.append(f"Total endpoints probed: {len(results)}")
        report.append("")
        
        # Summary statistics
        accessible_count = len(analysis['accessible'])
        auth_required_count = len(analysis['requires_auth'])
        not_found_count = len(analysis['not_found'])
        
        report.append("📊 Summary:")
        report.append(f"  ✅ Accessible: {accessible_count}")
        report.append(f"  🔐 Requires Auth: {auth_required_count}")
        report.append(f"  ❌ Not Found: {not_found_count}")
        report.append("")
        
        # Accessible endpoints
        if analysis['accessible']:
            report.append("✅ ACCESSIBLE ENDPOINTS:")
            for endpoint in analysis['accessible']:
                result = results[endpoint]
                content_type = result.get('content_type', 'unknown')
                report.append(f"  {endpoint} - {result['status_code']} ({content_type})")
                
                # Show JSON response preview if available
                if 'json_response' in result:
                    json_preview = str(result['json_response'])[:100]
                    report.append(f"    Response: {json_preview}...")
            report.append("")
        
        # Authentication required endpoints
        if analysis['requires_auth']:
            report.append("🔐 AUTHENTICATION REQUIRED:")
            for endpoint in analysis['requires_auth']:
                result = results[endpoint]
                report.append(f"  {endpoint} - {result['status_code']} {result.get('status_text', '')}")
            report.append("")
        
        # Data Navigator specific endpoints
        if analysis['data_navigator']:
            report.append("🗂️  DATA NAVIGATOR ENDPOINTS:")
            for endpoint in analysis['data_navigator']:
                result = results[endpoint]
                status = result.get('status_code', 'error')
                report.append(f"  {endpoint} - {status}")
            report.append("")
        
        # ANYmal API endpoints
        if analysis['anymal_api']:
            report.append("🤖 ANYMAL API ENDPOINTS:")
            for endpoint in analysis['anymal_api']:
                result = results[endpoint]
                status = result.get('status_code', 'error')
                report.append(f"  {endpoint} - {status}")
            report.append("")
        
        # Documentation endpoints
        if analysis['documentation']:
            report.append("📚 DOCUMENTATION ENDPOINTS:")
            for endpoint in analysis['documentation']:
                result = results[endpoint]
                status = result.get('status_code', 'error')
                report.append(f"  {endpoint} - {status}")
            report.append("")
        
        # Detailed results for interesting endpoints
        report.append("🔍 DETAILED ENDPOINT ANALYSIS:")
        report.append("")
        
        interesting_endpoints = (
            analysis['accessible'] + 
            analysis['requires_auth'][:5] +  # Limit to first 5
            [ep for ep in analysis['data_navigator'] if results[ep].get('status_code', 0) < 500]
        )
        
        for endpoint in interesting_endpoints[:15]:  # Limit to 15 most interesting
            result = results[endpoint]
            if result.get('error'):
                continue
                
            report.append(f"Endpoint: {endpoint}")
            report.append(f"  Status: {result.get('status_code')} {result.get('status_text', '')}")
            report.append(f"  Content-Type: {result.get('content_type', 'unknown')}")
            
            if 'json_response' in result:
                json_str = json.dumps(result['json_response'], indent=2)[:300]
                report.append(f"  Response: {json_str}...")
            elif 'text_response' in result and result['text_response']:
                report.append(f"  Response: {result['text_response'][:200]}...")
            
            report.append("")
        
        return "\n".join(report)
    
    def save_detailed_results(self, results: Dict[str, Any], filename: str = "api_discovery_results.json"):
        """Save detailed results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"💾 Detailed results saved to: {filename}")


def main():
    """Main discovery function"""
    
    # Get credentials from environment variables
    server_url = os.getenv("ANYMAL_SERVER_URL", "raas-ge-ver.prod.anybotics.com")
    email = os.getenv("ANYMAL_EMAIL")
    password = os.getenv("ANYMAL_PASSWORD")
    
    if not all([email, password]):
        logger.error("❌ Missing credentials. Please set ANYMAL_EMAIL and ANYMAL_PASSWORD environment variables.")
        return
    
    # Initialize discovery tool
    discovery = DataNavigatorAPIDiscovery(server_url, verify_ssl=True)
    
    # Authenticate
    if not discovery.authenticate(email, password):
        logger.error("❌ Authentication failed. Cannot proceed with API discovery.")
        return
    
    # Discover endpoints
    results = discovery.discover_data_navigator_endpoints()
    
    # Analyze results
    analysis = discovery.analyze_results(results)
    
    # Generate and display report
    report = discovery.generate_report(results, analysis)
    print(report)
    
    # Save detailed results
    discovery.save_detailed_results(results)
    
    # Save report to file
    with open("data_navigator_api_report.txt", "w") as f:
        f.write(report)
    
    logger.info("📋 Report saved to: data_navigator_api_report.txt")
    logger.info("💾 Detailed JSON results saved to: api_discovery_results.json")


if __name__ == "__main__":
    main()
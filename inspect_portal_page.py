#!/usr/bin/env python3
"""
Inspect the actual Data Navigator web portal page to find API calls
"""
import requests
import json
import os
import re
from urllib.parse import urljoin

def authenticate_and_get_portal():
    """Get the main portal page after authentication"""
    base_url = "https://raas-ge-ver.prod.anybotics.com"
    session = requests.Session()
    
    # Authenticate
    email = os.getenv('ANYMAL_EMAIL')
    password = os.getenv('ANYMAL_PASSWORD')
    
    auth_url = f"{base_url}/authentication-service/auth/login"
    auth_data = {"email": email, "password": password}
    
    print("🔐 Authenticating...")
    response = session.post(auth_url, json=auth_data)
    
    if response.status_code in [200, 201]:
        auth_result = response.json()
        token = auth_result.get('accessToken')
        session.headers.update({'Authorization': f'Bearer {token}'})
        print(f"✅ Authentication successful")
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None, None
    
    # Get the main portal page
    portal_urls = [
        "/workforce/data-navigator/",
        "/workforce/data-navigator/inspections",
        "/workforce/data-navigator/dashboard"
    ]
    
    for portal_url in portal_urls:
        try:
            print(f"📄 Fetching: {portal_url}")
            url = urljoin(base_url, portal_url)
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Got portal page: {len(response.text)} characters")
                return response.text, session
            else:
                print(f"⚠️  Status {response.status_code} for {portal_url}")
                
        except Exception as e:
            print(f"❌ Error fetching {portal_url}: {e}")
    
    return None, None

def extract_api_calls_from_html(html_content):
    """Extract API calls from HTML/JavaScript content"""
    print("\n🔍 Analyzing portal page content...")
    
    # Look for various API call patterns
    patterns = [
        # Direct API URLs
        r'["\']([^"\']*(?:api|service)[^"\']*)["\']',
        # Fetch/axios calls
        r'(?:fetch|axios\.(?:get|post|put|delete))\s*\(\s*["\']([^"\']+)["\']',
        # URL constants/variables
        r'(?:url|endpoint|path)\s*[:=]\s*["\']([^"\']+)["\']',
        # API base URLs
        r'["\']([^"\']*\/(?:api|service)\/[^"\']*)["\']',
        # Service endpoints
        r'["\']([^"\']*(?:workforce|fleet|analytics|reporting|file)-(?:api|service)[^"\']*)["\']',
    ]
    
    found_endpoints = set()
    
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if is_valid_endpoint(match):
                found_endpoints.add(match)
                print(f"   🎯 Found: {match}")
    
    # Also look for JavaScript files to analyze
    js_files = re.findall(r'<script[^>]*src=["\']([^"\']+\.js[^"\']*)["\']', html_content)
    print(f"\n📜 Found {len(js_files)} JavaScript files:")
    for js_file in js_files[:10]:  # Limit to first 10
        print(f"   📄 {js_file}")
    
    return found_endpoints, js_files

def is_valid_endpoint(path):
    """Check if a path looks like a valid API endpoint"""
    if not path or len(path) < 5:
        return False
    
    # Must contain api or service
    if 'api' not in path.lower() and 'service' not in path.lower():
        return False
    
    # Skip common non-API patterns
    skip_patterns = [
        'javascript:', 'mailto:', 'tel:', 'http://', 'https://',
        '.css', '.js', '.png', '.jpg', '.gif', '.svg', '.ico',
        'google', 'facebook', 'twitter', 'linkedin', 'cdn'
    ]
    
    for skip in skip_patterns:
        if skip in path.lower():
            return False
    
    return True

def test_discovered_endpoints(endpoints, session):
    """Test the discovered endpoints"""
    print(f"\n🧪 Testing {len(endpoints)} discovered endpoints...")
    
    base_url = "https://raas-ge-ver.prod.anybotics.com"
    working_endpoints = []
    
    for endpoint in sorted(endpoints):
        try:
            # Clean up endpoint
            if not endpoint.startswith('/'):
                endpoint = '/' + endpoint
            
            url = urljoin(base_url, endpoint)
            print(f"🔍 Testing: {endpoint}")
            
            response = session.get(url, timeout=5)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    data_preview = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                    print(f"   ✅ Working: {response.status_code} - {data_preview}")
                    working_endpoints.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'data_sample': data_preview
                    })
                except:
                    print(f"   ✅ Working: {response.status_code} (non-JSON)")
                    working_endpoints.append({
                        'endpoint': endpoint,
                        'status': response.status_code
                    })
            elif response.status_code in [401, 403]:
                print(f"   🔐 Auth required: {response.status_code}")
            elif response.status_code == 404:
                print(f"   ❌ Not found: {response.status_code}")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    return working_endpoints

def main():
    print("🚀 Inspecting Data Navigator Portal Page...")
    
    # Get portal page content
    html_content, session = authenticate_and_get_portal()
    
    if not html_content:
        print("❌ Could not get portal page content")
        return
    
    # Extract API endpoints from HTML
    endpoints, js_files = extract_api_calls_from_html(html_content)
    
    if not endpoints:
        print("⚠️  No API endpoints found in portal page")
        return
    
    # Test discovered endpoints
    working_endpoints = test_discovered_endpoints(endpoints, session)
    
    # Save results
    results = {
        'timestamp': '2025-01-16',
        'discovered_endpoints': sorted(list(endpoints)),
        'javascript_files': js_files,
        'working_endpoints': working_endpoints,
        'total_discovered': len(endpoints),
        'total_working': len(working_endpoints)
    }
    
    with open('portal_inspection_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 RESULTS:")
    print(f"🔍 Discovered endpoints: {len(endpoints)}")
    print(f"✅ Working endpoints: {len(working_endpoints)}")
    print(f"📜 JavaScript files: {len(js_files)}")
    print(f"💾 Results saved to: portal_inspection_results.json")
    
    if working_endpoints:
        print(f"\n🎯 WORKING ENDPOINTS:")
        for endpoint_info in working_endpoints:
            endpoint = endpoint_info['endpoint']
            status = endpoint_info['status']
            if 'data_sample' in endpoint_info:
                sample = endpoint_info['data_sample']
                print(f"✅ {endpoint} - {status}")
                print(f"   📄 {sample}")
            else:
                print(f"✅ {endpoint} - {status}")

if __name__ == "__main__":
    main()
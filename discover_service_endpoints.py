#!/usr/bin/env python3
"""
Discover service endpoints by testing common service patterns
"""
import requests
import json
import os
from urllib.parse import urljoin

def authenticate():
    """Authenticate and get token"""
    base_url = "https://raas-ge-ver.prod.anybotics.com"
    session = requests.Session()
    
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
        return session, base_url
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None, None

def discover_service_patterns():
    """Discover various service endpoint patterns"""
    session, base_url = authenticate()
    if not session:
        return
    
    print("\n🔍 Discovering service endpoints...")
    
    # Test various service patterns
    service_patterns = [
        # Authentication and user services
        "/authentication-service/auth/profile",
        "/authentication-service/auth/refresh",
        "/authentication-service/users/me",
        "/user-service/profile",
        "/user-service/preferences",
        
        # Known working data navigator
        "/data-navigator-api/inspections",
        "/data-navigator-api/missions",
        "/data-navigator-api/robots", 
        "/data-navigator-api/assets",
        
        # Workforce services (we know these exist but need different auth)
        "/workforce-service/inspections",
        "/workforce-service/missions",
        "/workforce-service/robots",
        "/workforce-service/dashboard",
        
        # Fleet management
        "/fleet-service/robots",
        "/fleet-service/status",
        "/fleet-service/missions",
        
        # Analytics and reporting
        "/analytics-service/inspections",
        "/analytics-service/reports",
        "/analytics-service/dashboard",
        "/reporting-service/generate",
        "/reporting-service/templates",
        
        # File and media services
        "/file-service/upload",
        "/file-service/download", 
        "/media-service/images",
        "/media-service/videos",
        
        # Configuration and settings
        "/config-service/settings",
        "/settings-service/user",
        "/preferences-service/user",
        
        # Notification services
        "/notification-service/alerts",
        "/alert-service/notifications",
        
        # API documentation endpoints
        "/api/docs",
        "/api/swagger",
        "/api/openapi",
        "/docs",
        "/swagger",
        "/openapi.json",
        "/api-docs",
        
        # Health and status endpoints
        "/health",
        "/status",
        "/ping",
        "/version",
        "/info",
        
        # Alternative API patterns
        "/api/v1/inspections",
        "/api/v1/missions",
        "/api/v1/robots",
        "/api/v1/assets",
        "/v1/inspections",
        "/v1/missions",
        "/v1/robots",
        "/v1/assets",
    ]
    
    working_endpoints = []
    auth_required_endpoints = []
    
    for endpoint in service_patterns:
        try:
            url = urljoin(base_url, endpoint)
            print(f"🔍 Testing: {endpoint}")
            
            response = session.get(url, timeout=5)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    data_preview = str(data)[:150] + "..." if len(str(data)) > 150 else str(data)
                    print(f"   ✅ Working: {response.status_code}")
                    print(f"      📄 {data_preview}")
                    working_endpoints.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'data_sample': data_preview,
                        'content_type': response.headers.get('content-type', '')
                    })
                except:
                    content_preview = response.text[:150] + "..." if len(response.text) > 150 else response.text
                    print(f"   ✅ Working: {response.status_code} (non-JSON)")
                    print(f"      📄 {content_preview}")
                    working_endpoints.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'content_preview': content_preview,
                        'content_type': response.headers.get('content-type', '')
                    })
            elif response.status_code in [401, 403]:
                print(f"   🔐 Auth required: {response.status_code}")
                auth_required_endpoints.append({
                    'endpoint': endpoint,
                    'status': response.status_code,
                    'note': 'Authentication/Authorization required'
                })
            elif response.status_code == 404:
                print(f"   ❌ Not found: {response.status_code}")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Report results
    print(f"\n📊 DISCOVERY RESULTS:")
    print(f"✅ Working endpoints: {len(working_endpoints)}")
    print(f"🔐 Auth-required endpoints: {len(auth_required_endpoints)}")
    
    if working_endpoints:
        print(f"\n🎯 WORKING ENDPOINTS:")
        for endpoint_info in working_endpoints:
            endpoint = endpoint_info['endpoint']
            status = endpoint_info['status']
            content_type = endpoint_info.get('content_type', '')
            print(f"✅ {endpoint} - {status} ({content_type})")
            if 'data_sample' in endpoint_info:
                print(f"   📄 {endpoint_info['data_sample']}")
            elif 'content_preview' in endpoint_info:
                print(f"   📄 {endpoint_info['content_preview']}")
    
    if auth_required_endpoints:
        print(f"\n🔐 AUTH-REQUIRED ENDPOINTS (these exist but need different permissions):")
        for endpoint_info in auth_required_endpoints:
            endpoint = endpoint_info['endpoint']
            status = endpoint_info['status']
            print(f"🔐 {endpoint} - {status}")
    
    # Save results
    results = {
        'timestamp': '2025-01-16',
        'base_url': base_url,
        'working_endpoints': working_endpoints,
        'auth_required_endpoints': auth_required_endpoints,
        'total_working': len(working_endpoints),
        'total_auth_required': len(auth_required_endpoints)
    }
    
    with open('service_discovery_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: service_discovery_results.json")
    
    return working_endpoints, auth_required_endpoints

if __name__ == "__main__":
    print("🚀 Starting Service Endpoint Discovery...")
    discover_service_patterns()
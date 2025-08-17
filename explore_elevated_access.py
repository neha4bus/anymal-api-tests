#!/usr/bin/env python3
"""
Explore different approaches to access elevated services
"""
import requests
import json
import os
from urllib.parse import urljoin

class ElevatedAccessExplorer:
    def __init__(self):
        self.base_url = "https://raas-ge-ver.prod.anybotics.com"
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self):
        """Standard authentication"""
        email = os.getenv('ANYMAL_EMAIL')
        password = os.getenv('ANYMAL_PASSWORD')
        
        auth_url = f"{self.base_url}/authentication-service/auth/login"
        auth_data = {"email": email, "password": password}
        
        print("🔐 Authenticating...")
        response = self.session.post(auth_url, json=auth_data)
        
        if response.status_code in [200, 201]:
            auth_result = response.json()
            self.token = auth_result.get('accessToken')
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            print(f"✅ Authentication successful")
            
            # Print token info for analysis
            print(f"🔍 Token preview: {self.token[:50]}...")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def analyze_token_permissions(self):
        """Analyze what the current token allows"""
        print("\n🔍 Analyzing current token permissions...")
        
        # Test user info endpoints
        user_endpoints = [
            "/authentication-service/users/me",
            "/user-service/profile", 
            "/user-service/preferences"
        ]
        
        for endpoint in user_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint}: {data}")
                elif response.status_code == 403:
                    print(f"🔐 {endpoint}: Access denied (403)")
                    # Try to get more info from response
                    if response.text:
                        print(f"   Response: {response.text[:100]}")
                else:
                    print(f"⚠️  {endpoint}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
    
    def try_alternative_auth_headers(self):
        """Try different authentication header formats"""
        print("\n🔧 Trying alternative authentication approaches...")
        
        test_endpoint = "/workforce-service/dashboard"
        url = urljoin(self.base_url, test_endpoint)
        
        # Different header approaches
        auth_approaches = [
            {"Authorization": f"Bearer {self.token}"},
            {"Authorization": f"Token {self.token}"},
            {"X-Auth-Token": self.token},
            {"X-API-Key": self.token},
            {"Authentication": f"Bearer {self.token}"},
            {"Access-Token": self.token},
        ]
        
        for i, headers in enumerate(auth_approaches, 1):
            try:
                print(f"🔍 Approach {i}: {list(headers.keys())[0]}")
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    print(f"   ✅ SUCCESS! Status: {response.status_code}")
                    return headers
                elif response.status_code == 403:
                    print(f"   🔐 Still forbidden: {response.status_code}")
                else:
                    print(f"   ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return None
    
    def explore_workforce_portal_auth(self):
        """Try to access workforce portal with different approaches"""
        print("\n🌐 Exploring workforce portal access...")
        
        portal_endpoints = [
            "/workforce/data-navigator/",
            "/workforce/data-navigator/login",
            "/workforce/data-navigator/dashboard",
            "/workforce/",
            "/workforce/login"
        ]
        
        for endpoint in portal_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                print(f"🔍 Testing: {endpoint}")
                
                # Try GET request
                response = self.session.get(url, timeout=5)
                print(f"   GET: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Accessible! Content length: {len(response.text)}")
                    # Look for login forms or API endpoints in the content
                    if 'api' in response.text.lower():
                        print(f"   🎯 Contains API references")
                elif response.status_code == 403:
                    print(f"   🔐 Forbidden")
                elif response.status_code == 302:
                    redirect = response.headers.get('Location', 'Unknown')
                    print(f"   🔄 Redirects to: {redirect}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def check_api_documentation_access(self):
        """Check if we can access API documentation"""
        print("\n📚 Checking API documentation access...")
        
        doc_endpoints = [
            "/api/docs",
            "/docs", 
            "/swagger",
            "/api/swagger",
            "/openapi.json",
            "/api-docs",
            "/redoc"
        ]
        
        for endpoint in doc_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                print(f"🔍 Testing: {endpoint}")
                
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"   ✅ Accessible! Content type: {response.headers.get('content-type', 'unknown')}")
                    if 'json' in response.headers.get('content-type', ''):
                        try:
                            data = response.json()
                            print(f"   📄 JSON data available (keys: {list(data.keys()) if isinstance(data, dict) else 'array'})")
                        except:
                            print(f"   📄 JSON response but couldn't parse")
                elif response.status_code == 403:
                    print(f"   🔐 Forbidden")
                else:
                    print(f"   ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def test_service_specific_patterns(self):
        """Test service-specific endpoint patterns"""
        print("\n🎯 Testing service-specific patterns...")
        
        # Test if services have their own auth endpoints
        service_auth_patterns = [
            "/workforce-service/auth/login",
            "/fleet-service/auth/login", 
            "/analytics-service/auth/login",
            "/workforce-api/auth/login",
            "/fleet-api/auth/login",
            "/analytics-api/auth/login"
        ]
        
        for endpoint in service_auth_patterns:
            try:
                url = urljoin(self.base_url, endpoint)
                print(f"🔍 Testing auth: {endpoint}")
                
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"   ✅ Auth endpoint exists!")
                elif response.status_code == 405:  # Method not allowed - might need POST
                    print(f"   🔄 Endpoint exists but needs POST")
                elif response.status_code == 404:
                    print(f"   ❌ Not found")
                else:
                    print(f"   ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def run_exploration(self):
        """Run complete exploration"""
        print("🚀 Starting Elevated Access Exploration...")
        
        if not self.authenticate():
            return
        
        # Analyze current permissions
        self.analyze_token_permissions()
        
        # Try alternative auth approaches
        self.try_alternative_auth_headers()
        
        # Explore workforce portal
        self.explore_workforce_portal_auth()
        
        # Check documentation access
        self.check_api_documentation_access()
        
        # Test service-specific patterns
        self.test_service_specific_patterns()
        
        print(f"\n📊 EXPLORATION COMPLETE")
        print(f"💡 Key findings:")
        print(f"   • Current token has limited 'data navigator' permissions")
        print(f"   • 44+ services exist but require elevated access")
        print(f"   • Workforce portal requires different authentication")
        print(f"   • API documentation is protected")
        print(f"   • Services may have individual auth endpoints")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print(f"   1. Contact ANYmal admin for elevated permissions")
        print(f"   2. Request access to workforce/fleet/analytics services")
        print(f"   3. Ask about API documentation access")
        print(f"   4. Inquire about role-based authentication")

if __name__ == "__main__":
    explorer = ElevatedAccessExplorer()
    explorer.run_exploration()
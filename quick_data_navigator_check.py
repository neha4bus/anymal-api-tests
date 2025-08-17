#!/usr/bin/env python3
"""
Quick Data Navigator API Check
Shows key information from the ANYmal Data Navigator API
"""

import requests
import json
import os

def quick_check():
    """Quick check of Data Navigator API"""
    
    # Get credentials
    server_url = os.getenv("ANYMAL_SERVER_URL", "raas-ge-ver.prod.anybotics.com")
    email = os.getenv("ANYMAL_EMAIL")
    password = os.getenv("ANYMAL_PASSWORD")
    
    if not all([email, password]):
        print("❌ Missing credentials")
        return
    
    base_url = f"https://{server_url.strip('api-').rstrip('/')}"
    session = requests.Session()
    
    # Authenticate
    auth_url = f"{base_url}/authentication-service/auth/login"
    auth_response = session.post(auth_url, json={"email": email, "password": password})
    
    if auth_response.status_code != 201:
        print("❌ Authentication failed")
        return
    
    token = auth_response.json().get("accessToken")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("✅ Authentication successful")
    print("\n🔍 DATA NAVIGATOR API ENDPOINTS:")
    
    # Check key endpoints
    endpoints = {
        "Inspections": "/data-navigator-api/inspections",
        "Missions": "/data-navigator-api/missions", 
        "Robots": "/data-navigator-api/robots",
        "Assets": "/data-navigator-api/assets"
    }
    
    for name, endpoint in endpoints.items():
        try:
            response = session.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                total = data.get('totalItems', 0)
                print(f"✅ {name}: {total} items available")
                
                # Show sample data
                items = data.get('items', [])
                if items and len(items) > 0:
                    sample = items[0]
                    if name == "Inspections":
                        print(f"   Sample: {sample.get('assetName', 'N/A')} - {sample.get('outcome', 'N/A')} ({sample.get('measurement', 'N/A')})")
                    elif name == "Robots":
                        print(f"   Sample: {sample.get('name', 'N/A')} (ID: {sample.get('id', 'N/A')})")
                    elif name == "Assets":
                        print(f"   Sample: {sample.get('name', 'N/A')} (ID: {sample.get('id', 'N/A')})")
                    elif name == "Missions":
                        print(f"   Sample: {sample.get('name', 'N/A')} - {sample.get('lastRunOutcome', 'N/A')}")
            else:
                print(f"❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    # Test raw data download endpoint
    print(f"\n📁 RAW DATA DOWNLOAD:")
    test_filename = "test.jpg"  # This will likely return 404, but shows the endpoint works
    raw_data_url = f"{base_url}/data-navigator-api/inspections/raw-data/{test_filename}"
    
    try:
        response = session.head(raw_data_url, timeout=10)
        if response.status_code == 404:
            print(f"✅ Raw data endpoint active (404 expected for test filename)")
        else:
            print(f"✅ Raw data endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Raw data endpoint error: {e}")

if __name__ == "__main__":
    quick_check()
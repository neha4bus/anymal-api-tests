#!/usr/bin/env python3
"""
Simple example for downloading ANYmal inspection data
Minimal code for quick testing and integration
"""

import os
import sys
from inspection_data_download_samples import ANYmalDataDownloader

def simple_download(server_url: str, email: str, password: str, filename: str) -> bool:
    """
    Simple function to download a single inspection file
    
    Args:
        server_url: ANYmal server URL
        email: User email
        password: User password
        filename: File to download
        
    Returns:
        True if successful, False otherwise
    """
    # Initialize downloader
    downloader = ANYmalDataDownloader(server_url, verify_ssl=True)
    
    try:
        # Authenticate
        if not downloader.authenticate(email, password):
            print("❌ Authentication failed")
            return False
        
        print("✅ Authentication successful")
        
        # Check if file exists
        file_info = downloader.get_file_info(filename)
        if not file_info or not file_info.get('exists'):
            print(f"❌ File '{filename}' not found on server")
            return False
        
        print(f"📁 File found: {filename} ({file_info.get('size', 'unknown')} bytes)")
        
        # Download file
        downloaded_path = downloader.download_inspection_file(filename)
        
        if downloaded_path:
            print(f"✅ Downloaded successfully: {downloaded_path}")
            return True
        else:
            print("❌ Download failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        downloader.close()


def interactive_download():
    """Interactive mode for downloading files"""
    print("🤖 ANYmal Inspection Data Downloader")
    print("=" * 40)
    
    # Get configuration
    server_url = input("Server URL: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    if not all([server_url, email, password]):
        print("❌ All fields are required")
        return
    
    # Initialize downloader
    downloader = ANYmalDataDownloader(server_url, verify_ssl=True)
    
    try:
        # Authenticate
        print("\n🔐 Authenticating...")
        if not downloader.authenticate(email, password):
            print("❌ Authentication failed")
            return
        
        print("✅ Authentication successful")
        
        # Download loop
        while True:
            print("\n" + "=" * 40)
            filename = input("Enter filename to download (or 'quit' to exit): ").strip()
            
            if filename.lower() in ['quit', 'exit', 'q']:
                break
                
            if not filename:
                continue
            
            # Check file exists
            print(f"🔍 Checking if '{filename}' exists...")
            file_info = downloader.get_file_info(filename)
            
            if not file_info or not file_info.get('exists'):
                print(f"❌ File '{filename}' not found")
                continue
            
            size = file_info.get('size', 'unknown')
            content_type = file_info.get('content_type', 'unknown')
            print(f"📁 File found: {size} bytes, type: {content_type}")
            
            # Download
            print(f"⬇️  Downloading '{filename}'...")
            downloaded_path = downloader.download_inspection_file(filename)
            
            if downloaded_path:
                print(f"✅ Downloaded: {downloaded_path}")
            else:
                print("❌ Download failed")
                
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        downloader.close()


def batch_download_from_list(server_url: str, email: str, password: str, filenames: list) -> dict:
    """
    Download multiple files from a list
    
    Args:
        server_url: ANYmal server URL
        email: User email
        password: User password
        filenames: List of filenames to download
        
    Returns:
        Dictionary with download results
    """
    downloader = ANYmalDataDownloader(server_url, verify_ssl=True)
    results = {'successful': [], 'failed': [], 'not_found': []}
    
    try:
        # Authenticate
        if not downloader.authenticate(email, password):
            print("❌ Authentication failed")
            return results
        
        print(f"✅ Authentication successful")
        print(f"📋 Processing {len(filenames)} files...")
        
        for i, filename in enumerate(filenames, 1):
            print(f"\n[{i}/{len(filenames)}] Processing: {filename}")
            
            # Check if file exists
            file_info = downloader.get_file_info(filename)
            if not file_info or not file_info.get('exists'):
                print(f"❌ Not found: {filename}")
                results['not_found'].append(filename)
                continue
            
            # Download file
            downloaded_path = downloader.download_inspection_file(filename)
            
            if downloaded_path:
                print(f"✅ Downloaded: {filename}")
                results['successful'].append(filename)
            else:
                print(f"❌ Failed: {filename}")
                results['failed'].append(filename)
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"✅ Successful: {len(results['successful'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        print(f"🔍 Not found: {len(results['not_found'])}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return results
        
    finally:
        downloader.close()


def main():
    """Main function with different usage examples"""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python simple_download_example.py interactive")
        print("  python simple_download_example.py single <server> <email> <password> <filename>")
        print("  python simple_download_example.py batch <server> <email> <password> <file1> <file2> ...")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == 'interactive':
        interactive_download()
        
    elif mode == 'single' and len(sys.argv) == 6:
        server_url, email, password, filename = sys.argv[2:6]
        success = simple_download(server_url, email, password, filename)
        sys.exit(0 if success else 1)
        
    elif mode == 'batch' and len(sys.argv) >= 6:
        server_url, email, password = sys.argv[2:5]
        filenames = sys.argv[5:]
        results = batch_download_from_list(server_url, email, password, filenames)
        
        # Exit with error code if any downloads failed
        if results['failed'] or results['not_found']:
            sys.exit(1)
        else:
            sys.exit(0)
            
    else:
        print("❌ Invalid arguments")
        sys.exit(1)


if __name__ == "__main__":
    main()
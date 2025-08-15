#!/usr/bin/env python3
"""
ANYmal Inspection Raw Data Download Examples
Demonstrates how to authenticate and download inspection data files
"""

import requests
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ANYmalDataDownloader:
    """Client for downloading inspection data from ANYmal API"""
    
    def __init__(self, server_url: str, verify_ssl: bool = True, timeout: int = 30):
        """
        Initialize the downloader
        
        Args:
            server_url: ANYmal server URL (e.g., 'your-server.com')
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
        """
        # Clean up server URL
        server_url = server_url.strip().strip('/')
        if not server_url.startswith('http'):
            server_url = f"https://{server_url}"
        self.base_url = server_url.replace('api-', '')
        
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        
        # Configure session with retries
        self.session = requests.Session()
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
        """
        Authenticate with the ANYmal server
        
        Args:
            email: User email
            password: User password
            
        Returns:
            True if authentication successful, False otherwise
        """
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
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                data = response.json()
                self.access_token = data.get("accessToken")
                
                # Calculate token expiration (assume 1 hour if not provided)
                expires_in = data.get("expiresIn", 3600)
                self.token_expires_at = time.time() + expires_in - 300  # 5 min buffer
                
                # Set default authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication request failed: {e}")
            return False
    
    def _is_token_expired(self) -> bool:
        """Check if the access token is expired"""
        if not self.token_expires_at:
            return False
        return time.time() >= self.token_expires_at
    
    def download_inspection_file(self, filename: str, output_dir: str = "./downloads") -> Optional[str]:
        """
        Download a specific inspection data file
        
        Args:
            filename: Name of the file to download
            output_dir: Directory to save the downloaded file
            
        Returns:
            Path to downloaded file if successful, None otherwise
        """
        if not self.access_token:
            logger.error("Not authenticated. Call authenticate() first.")
            return None
            
        if self._is_token_expired():
            logger.warning("Access token expired. Please re-authenticate.")
            return None
            
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # URL encode filename to handle special characters
        encoded_filename = quote(filename, safe='')
        download_url = f"{self.base_url}/data-navigator-api/inspections/raw-data/{encoded_filename}"
        output_path = os.path.join(output_dir, filename)
        
        try:
            logger.info(f"Downloading {filename}...")
            
            response = self.session.get(
                download_url, 
                verify=self.verify_ssl, 
                stream=True,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                # Download file in chunks to handle large files
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(output_path)
                logger.info(f"Successfully downloaded {filename} ({file_size} bytes) to {output_path}")
                return output_path
                
            elif response.status_code == 404:
                logger.warning(f"File {filename} not found (may not be uploaded yet)")
                return None
                
            elif response.status_code == 401:
                logger.error("Authentication token expired or invalid")
                return None
                
            else:
                logger.error(f"Download failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Download request failed: {e}")
            return None
    
    def download_multiple_files(self, filenames: list, output_dir: str = "./downloads") -> Dict[str, Optional[str]]:
        """
        Download multiple inspection files
        
        Args:
            filenames: List of filenames to download
            output_dir: Directory to save downloaded files
            
        Returns:
            Dictionary mapping filename to downloaded path (or None if failed)
        """
        results = {}
        
        for filename in filenames:
            result = self.download_inspection_file(filename, output_dir)
            results[filename] = result
            
        return results
    
    def batch_download_with_pattern(self, asset_id: str, file_extensions: list = None, output_dir: str = "./downloads") -> Dict[str, Optional[str]]:
        """
        Download files matching a pattern (simulated batch download)
        
        Args:
            asset_id: Asset ID to search for
            file_extensions: List of file extensions to try (e.g., ['.jpg', '.png', '.mp4'])
            output_dir: Directory to save downloaded files
            
        Returns:
            Dictionary of successful downloads
        """
        if file_extensions is None:
            file_extensions = ['.jpg', '.png', '.mp4', '.wav', '.json']
            
        results = {}
        
        for ext in file_extensions:
            # Try common naming patterns
            patterns = [
                f"{asset_id}{ext}",
                f"{asset_id}_thermal{ext}",
                f"{asset_id}_visual{ext}",
                f"{asset_id}_audio{ext}",
                f"inspection_{asset_id}{ext}"
            ]
            
            for pattern in patterns:
                result = self.download_inspection_file(pattern, output_dir)
                if result:
                    results[pattern] = result
                    
        return results
    
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Get file information without downloading (HEAD request)
        
        Args:
            filename: Name of the file to check
            
        Returns:
            Dictionary with file info if exists, None otherwise
        """
        if not self.access_token or self._is_token_expired():
            logger.error("Not authenticated or token expired")
            return None
            
        encoded_filename = quote(filename, safe='')
        download_url = f"{self.base_url}/data-navigator-api/inspections/raw-data/{encoded_filename}"
        
        try:
            response = self.session.head(download_url, verify=self.verify_ssl, timeout=self.timeout)
            
            if response.status_code == 200:
                return {
                    'filename': filename,
                    'size': response.headers.get('Content-Length'),
                    'content_type': response.headers.get('Content-Type'),
                    'last_modified': response.headers.get('Last-Modified'),
                    'exists': True
                }
            elif response.status_code == 404:
                return {'filename': filename, 'exists': False}
            else:
                logger.error(f"File info request failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"File info request failed: {e}")
            return None
    
    def close(self):
        """Clean up resources"""
        if self.session:
            self.session.close()


def main():
    """Example usage of the ANYmal data downloader"""
    
    # Configuration - Use environment variables for security
    SERVER_URL = os.getenv("ANYMAL_SERVER_URL")
    EMAIL = os.getenv("ANYMAL_EMAIL") 
    PASSWORD = os.getenv("ANYMAL_PASSWORD")
    
    # Validate configuration
    if not all([SERVER_URL, EMAIL, PASSWORD]):
        logger.error("Missing required environment variables:")
        logger.error("Please set: ANYMAL_SERVER_URL, ANYMAL_EMAIL, ANYMAL_PASSWORD")
        logger.error("Example: export ANYMAL_SERVER_URL='your-server.com'")
        return
    
    # Initialize downloader
    downloader = ANYmalDataDownloader(SERVER_URL, verify_ssl=True, timeout=60)
    
    try:
        # Authenticate
        if not downloader.authenticate(EMAIL, PASSWORD):
            logger.error("Failed to authenticate")
            return
        
        # Example 1: Check if file exists before downloading
        filename = "bab90e5a-8e0b-4c6d-a022-34b42f5917ce_Inspect UNIT_01_THERMAL_1T001_interpretation_0.jpg"
        file_info = downloader.get_file_info(filename)
        
        if file_info and file_info.get('exists'):
            logger.info(f"File {filename} exists (size: {file_info.get('size')} bytes)")
            downloaded_path = downloader.download_inspection_file(filename)
            
            if downloaded_path:
                logger.info(f"File downloaded to: {downloaded_path}")
        else:
            logger.warning(f"File {filename} does not exist on server")
        
        # Example 2: Download multiple files with progress tracking
        filenames = [
            "0e3934eb-c4c7-4273-8c38-c5dcaf522f4a_UNIT_01_THERMAL_1T001_measurement.json",
            "bab90e5a-8e0b-4c6d-a022-34b42f5917ce_Inspect UNIT_01_THERMAL_1T001_interpretation_0.jpg", 
            "asset_001_audio.wav"
        ]
        
        logger.info(f"Starting download of {len(filenames)} files...")
        results = downloader.download_multiple_files(filenames, "./inspection_data")
        
        successful = sum(1 for path in results.values() if path)
        logger.info(f"Download completed: {successful}/{len(filenames)} files successful")
        
        for filename, path in results.items():
            if path:
                logger.info(f"✓ {filename} -> {path}")
            else:
                logger.warning(f"✗ {filename} - Download failed")
        
        # Example 3: Batch download by asset ID
        asset_id = "asset_12345"
        batch_results = downloader.batch_download_with_pattern(asset_id, ['.jpg', '.png', '.mp4'])
        
        logger.info(f"Batch download completed. Downloaded {len(batch_results)} files.")
        
    finally:
        # Clean up resources
        downloader.close()


# Utility functions for different use cases

def download_single_file_simple(server_url: str, email: str, password: str, filename: str) -> bool:
    """
    Simple function to download a single file
    
    Returns:
        True if successful, False otherwise
    """
    downloader = ANYmalDataDownloader(server_url)
    
    if downloader.authenticate(email, password):
        result = downloader.download_inspection_file(filename)
        return result is not None
    
    return False


def download_with_retry(server_url: str, email: str, password: str, filename: str, max_retries: int = 3) -> Optional[str]:
    """
    Download file with retry logic
    
    Args:
        server_url: ANYmal server URL
        email: User email
        password: User password  
        filename: File to download
        max_retries: Maximum number of retry attempts
        
    Returns:
        Path to downloaded file if successful, None otherwise
    """
    downloader = ANYmalDataDownloader(server_url)
    
    if not downloader.authenticate(email, password):
        return None
    
    for attempt in range(max_retries):
        try:
            result = downloader.download_inspection_file(filename)
            if result:
                return result
                
            logger.info(f"Retry attempt {attempt + 1}/{max_retries}")
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            
    logger.error(f"Failed to download {filename} after {max_retries} attempts")
    return None


if __name__ == "__main__":
    main()
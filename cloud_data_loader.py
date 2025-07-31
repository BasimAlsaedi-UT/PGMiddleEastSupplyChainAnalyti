"""
Cloud Data Loader for Streamlit Deployment
Handles loading data from various cloud sources
"""

import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import os
import requests
from typing import Tuple, Optional

def load_from_url(url: str) -> pd.DataFrame:
    """Load Excel file from URL"""
    try:
        # Add headers to avoid bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check if we got an HTML error page instead of Excel file
        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            st.error("Received HTML instead of Excel file. The file might not be publicly accessible.")
            st.error("Please ensure the Google Sheets is shared with 'Anyone with the link can view'")
            return None
            
        return pd.read_excel(BytesIO(response.content))
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            st.error("403 Forbidden: The file is not publicly accessible. Please check sharing settings.")
        else:
            st.error(f"HTTP Error {e.response.status_code}: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error loading from URL: {str(e)}")
        return None

def load_from_base64(encoded_string: str) -> pd.DataFrame:
    """Load Excel file from base64 encoded string"""
    try:
        decoded = base64.b64decode(encoded_string)
        return pd.read_excel(BytesIO(decoded))
    except Exception as e:
        st.error(f"Error loading from base64: {str(e)}")
        return None

def load_from_google_drive(file_id: str) -> pd.DataFrame:
    """Load Excel file from Google Drive or Google Sheets"""
    try:
        # Clean up the file ID first
        file_id = file_id.strip()
        
        # Handle both full URLs and just IDs
        if file_id.startswith('http'):
            # Check if it's a Google Sheets URL
            if 'spreadsheets' in file_id:
                # Extract sheet ID from Google Sheets URL
                if '/d/' in file_id:
                    file_id = file_id.split('/d/')[1].split('/')[0]
                    # Remove any query parameters or trailing characters
                    file_id = file_id.split('?')[0].split('&')[0].rstrip('-/')
                # Convert to Excel export URL
                url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
            else:
                # Regular Google Drive file
                if '/d/' in file_id:
                    file_id = file_id.split('/d/')[1].split('/')[0]
                elif 'id=' in file_id:
                    file_id = file_id.split('id=')[1].split('&')[0]
                url = f"https://drive.google.com/uc?id={file_id}&export=download"
        else:
            # Just an ID - clean it up
            # Remove any trailing dash or special characters
            file_id = file_id.rstrip('-/').strip()
            # Try Google Sheets export format
            url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
        
        st.info(f"Attempting to load from: {url}")
        result = load_from_url(url)
        
        if result is None:
            # If Google Sheets failed, try regular Google Drive format
            if not file_id.startswith('http'):
                st.warning("Google Sheets format failed, trying Google Drive format...")
                url = f"https://drive.google.com/uc?id={file_id}&export=download"
                result = load_from_url(url)
        
        return result
    except Exception as e:
        st.error(f"Error loading from Google Drive: {str(e)}")
        st.error(f"File ID used: {file_id}")
        return None

def get_cloud_file_paths() -> Tuple[Optional[str], Optional[str]]:
    """Get file paths from Streamlit secrets"""
    
    # Check if running on Streamlit Cloud
    if not hasattr(st, 'secrets'):
        return None, None
    
    shipping_path = None
    sales_path = None
    
    # Try different secret configurations
    if 'data_files' in st.secrets:
        if 'shipping_file' in st.secrets.data_files:
            shipping_path = st.secrets.data_files.shipping_file
        if 'sales_file' in st.secrets.data_files:
            sales_path = st.secrets.data_files.sales_file
    
    return shipping_path, sales_path

def save_cloud_data_locally(shipping_data: pd.DataFrame, sales_data: pd.DataFrame, 
                           parent_dir: str) -> bool:
    """Save cloud data to local files for processing"""
    try:
        # Save with expected file names
        shipping_path = os.path.join(parent_dir, "2-JPG shipping tracking - July 2025.xlsx")
        sales_path = os.path.join(parent_dir, "3-DSR-PG- 2025 July.xlsx")
        
        # Save to Excel files
        shipping_data.to_excel(shipping_path, index=False)
        sales_data.to_excel(sales_path, index=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving cloud data: {str(e)}")
        return False

def load_cloud_data() -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Main function to load data from cloud sources"""
    
    # Check if running on Streamlit Cloud
    if not hasattr(st, 'secrets'):
        return None, None
    
    shipping_data = None
    sales_data = None
    
    try:
        # Log available secrets for debugging
        st.info(f"Available secret sections: {list(st.secrets.keys())}")
        
        # Option 1: Direct file paths/URLs
        if 'data_files' in st.secrets:
            secrets = st.secrets.data_files
            st.info(f"Available keys in data_files: {list(secrets.keys())}")
            
            # URLs
            if 'shipping_url' in secrets and 'sales_url' in secrets:
                st.info("Loading from URLs...")
                shipping_data = load_from_url(secrets.shipping_url)
                sales_data = load_from_url(secrets.sales_url)
            
            # Base64
            elif 'shipping_base64' in secrets and 'sales_base64' in secrets:
                st.info("Loading from Base64...")
                shipping_data = load_from_base64(secrets.shipping_base64)
                sales_data = load_from_base64(secrets.sales_base64)
            
            # Google Drive/Sheets
            elif 'shipping_drive_id' in secrets and 'sales_drive_id' in secrets:
                st.info("Loading from Google Drive (drive_id)...")
                shipping_data = load_from_google_drive(secrets.shipping_drive_id)
                sales_data = load_from_google_drive(secrets.sales_drive_id)
            
            # Alternative naming: file_id instead of drive_id
            elif 'shipping_file_id' in secrets and 'sales_file_id' in secrets:
                st.info("Loading from Google Drive (file_id)...")
                shipping_data = load_from_google_drive(secrets.shipping_file_id)
                sales_data = load_from_google_drive(secrets.sales_file_id)
            else:
                st.error("No recognized data source configuration found in secrets")
                st.error(f"Available keys: {list(secrets.keys())}")
        
        # Option 2: Alternative secret structure - direct file_id at root level
        elif 'shipping_file_id' in st.secrets and 'sales_file_id' in st.secrets:
            st.info("Loading from root-level file_id secrets...")
            shipping_data = load_from_google_drive(st.secrets.shipping_file_id)
            sales_data = load_from_google_drive(st.secrets.sales_file_id)
        
        # Option 3: Alternative secret structure
        elif 'shipping_data' in st.secrets and 'sales_data' in st.secrets:
            # Direct data storage in secrets (for small files)
            shipping_data = pd.DataFrame(st.secrets.shipping_data)
            sales_data = pd.DataFrame(st.secrets.sales_data)
        
        else:
            st.error("No data configuration found in secrets")
            st.error("Please add either [data_files] section or shipping_file_id/sales_file_id directly")
        
    except Exception as e:
        st.error(f"Error loading cloud data: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None, None
    
    # Log success
    if shipping_data is not None:
        st.success(f"✅ Shipping data loaded: {shipping_data.shape}")
    else:
        st.error("❌ Failed to load shipping data")
        
    if sales_data is not None:
        st.success(f"✅ Sales data loaded: {sales_data.shape}")
    else:
        st.error("❌ Failed to load sales data")
    
    return shipping_data, sales_data

# Example secrets.toml structure:
"""
# Option 1: URLs
[data_files]
shipping_url = "https://your-storage.com/shipping.xlsx"
sales_url = "https://your-storage.com/sales.xlsx"

# Option 2: Google Drive
[data_files]
shipping_drive_id = "1ABC...XYZ"
sales_drive_id = "2DEF...UVW"

# Option 3: Base64 (for smaller files)
[data_files]
shipping_base64 = "UEsDBAoAAA..."
sales_base64 = "UEsDBAoAAA..."
"""
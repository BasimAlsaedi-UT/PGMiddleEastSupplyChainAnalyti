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
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_excel(BytesIO(response.content))
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
    """Load Excel file from Google Drive"""
    try:
        url = f"https://drive.google.com/uc?id={file_id}&export=download"
        return load_from_url(url)
    except Exception as e:
        st.error(f"Error loading from Google Drive: {str(e)}")
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
        # Option 1: Direct file paths/URLs
        if 'data_files' in st.secrets:
            secrets = st.secrets.data_files
            
            # URLs
            if 'shipping_url' in secrets and 'sales_url' in secrets:
                shipping_data = load_from_url(secrets.shipping_url)
                sales_data = load_from_url(secrets.sales_url)
            
            # Base64
            elif 'shipping_base64' in secrets and 'sales_base64' in secrets:
                shipping_data = load_from_base64(secrets.shipping_base64)
                sales_data = load_from_base64(secrets.sales_base64)
            
            # Google Drive
            elif 'shipping_drive_id' in secrets and 'sales_drive_id' in secrets:
                shipping_data = load_from_google_drive(secrets.shipping_drive_id)
                sales_data = load_from_google_drive(secrets.sales_drive_id)
        
        # Option 2: Alternative secret structure
        elif 'shipping_data' in st.secrets and 'sales_data' in st.secrets:
            # Direct data storage in secrets (for small files)
            shipping_data = pd.DataFrame(st.secrets.shipping_data)
            sales_data = pd.DataFrame(st.secrets.sales_data)
        
    except Exception as e:
        st.error(f"Error loading cloud data: {str(e)}")
        return None, None
    
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
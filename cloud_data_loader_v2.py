"""
Enhanced Cloud Data Loader that preserves Excel sheet structure
"""

import streamlit as st
import pandas as pd
import os
import requests
from io import BytesIO
from typing import Tuple, Optional

def download_excel_file(url: str) -> Optional[bytes]:
    """Download Excel file from URL and return bytes"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            st.error("Received HTML instead of Excel file")
            return None
            
        return response.content
    except Exception as e:
        st.error(f"Error downloading: {str(e)}")
        return None

def save_excel_from_bytes(file_bytes: bytes, file_path: str) -> bool:
    """Save Excel file from bytes"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write bytes directly to file
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
        
        # Verify it's a valid Excel file
        pd.ExcelFile(file_path)
        return True
    except Exception as e:
        st.error(f"Error saving Excel file: {str(e)}")
        return False

def load_cloud_data_v2() -> bool:
    """Load data from cloud and save as Excel files preserving structure"""
    
    if not hasattr(st, 'secrets'):
        return False
    
    try:
        st.info("Downloading files from Dropbox...")
        
        # Get URLs from secrets
        if 'data_files' not in st.secrets:
            st.error("No data_files section in secrets")
            return False
            
        secrets = st.secrets.data_files
        
        if 'shipping_url' not in secrets or 'sales_url' not in secrets:
            st.error("Missing shipping_url or sales_url in secrets")
            return False
        
        # Download files
        col1, col2 = st.columns(2)
        
        with col1:
            with st.spinner("Downloading shipping file..."):
                shipping_bytes = download_excel_file(secrets.shipping_url)
                if shipping_bytes:
                    st.success("✅ Downloaded shipping file")
                else:
                    st.error("❌ Failed to download shipping file")
                    return False
        
        with col2:
            with st.spinner("Downloading sales file..."):
                sales_bytes = download_excel_file(secrets.sales_url)
                if sales_bytes:
                    st.success("✅ Downloaded sales file")
                else:
                    st.error("❌ Failed to download sales file")
                    return False
        
        # Save files
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        shipping_path = os.path.join(parent_dir, "2-JPG shipping tracking - July 2025.xlsx")
        sales_path = os.path.join(parent_dir, "3-DSR-PG- 2025 July.xlsx")
        
        if save_excel_from_bytes(shipping_bytes, shipping_path):
            st.success(f"✅ Saved shipping file: {shipping_path}")
        else:
            return False
            
        if save_excel_from_bytes(sales_bytes, sales_path):
            st.success(f"✅ Saved sales file: {sales_path}")
        else:
            return False
        
        # Verify files
        st.info("Verifying saved files...")
        
        # Check shipping file
        try:
            xl = pd.ExcelFile(shipping_path)
            st.success(f"✅ Shipping file has sheets: {xl.sheet_names}")
        except Exception as e:
            st.error(f"❌ Error reading shipping file: {str(e)}")
            return False
        
        # Check sales file  
        try:
            xl = pd.ExcelFile(sales_path)
            st.success(f"✅ Sales file has sheets: {xl.sheet_names}")
        except Exception as e:
            st.error(f"❌ Error reading sales file: {str(e)}")
            return False
            
        return True
        
    except Exception as e:
        st.error(f"Error in cloud data loader: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return False
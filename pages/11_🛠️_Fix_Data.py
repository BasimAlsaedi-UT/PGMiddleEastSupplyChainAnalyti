"""
Fix data loading issues by forcing a proper reload
"""
import streamlit as st
import os
import shutil
import pandas as pd
from io import BytesIO
import requests

st.set_page_config(page_title="Fix Data", layout="wide")

st.title("🛠️ Fix Data Loading")

st.warning("This page will fix data loading issues by downloading and extracting data properly")

# Clear cache button
if st.button("1. Clear All Cached Data", type="primary"):
    try:
        # Clear extracted data
        extracted_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'extracted')
        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)
            st.success("✅ Cleared extracted data")
        
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ Cleared session state")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")

# Download and extract button
if st.button("2. Download and Extract Data", type="primary"):
    try:
        # Get URLs from secrets
        if not hasattr(st, 'secrets') or 'data_files' not in st.secrets:
            st.error("No secrets configured")
            st.stop()
            
        shipping_url = st.secrets.data_files.shipping_url
        sales_url = st.secrets.data_files.sales_url
        
        # Download files
        st.info("Downloading files from Dropbox...")
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Download shipping file
        with st.spinner("Downloading shipping file..."):
            resp = requests.get(shipping_url, headers=headers)
            resp.raise_for_status()
            shipping_bytes = resp.content
            st.success(f"✅ Downloaded shipping file ({len(shipping_bytes)} bytes)")
        
        # Download sales file
        with st.spinner("Downloading sales file..."):
            resp = requests.get(sales_url, headers=headers)
            resp.raise_for_status()
            sales_bytes = resp.content
            st.success(f"✅ Downloaded sales file ({len(sales_bytes)} bytes)")
        
        # Save files temporarily
        temp_dir = "/tmp/excel_files"
        os.makedirs(temp_dir, exist_ok=True)
        
        shipping_path = os.path.join(temp_dir, "shipping.xlsx")
        sales_path = os.path.join(temp_dir, "sales.xlsx")
        
        with open(shipping_path, 'wb') as f:
            f.write(shipping_bytes)
        with open(sales_path, 'wb') as f:
            f.write(sales_bytes)
        
        st.success("✅ Saved temporary files")
        
        # Extract data
        st.info("Extracting data (using lightweight extractor)...")
        
        # Import and use lightweight extractor
        from utils.lightweight_extractor import LightweightExtractor
        
        extractor = LightweightExtractor(shipping_file=shipping_path, sales_file=sales_path)
        
        # Create output directory
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'extracted')
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract and save
        success = extractor.extract_and_save(output_dir=output_dir)
        
        st.success("✅ Data extracted successfully!")
        
        # Show what was extracted
        st.subheader("Extracted Files:")
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            for f in sorted(files):
                size = os.path.getsize(os.path.join(output_dir, f))
                st.write(f"- {f} ({size:,} bytes)")
        
        # Verify data
        st.subheader("Data Verification:")
        
        # Check shipping
        shipping_file = os.path.join(output_dir, 'shipping_main_data.csv')
        if os.path.exists(shipping_file):
            df = pd.read_csv(shipping_file)
            st.success(f"✅ Shipping data: {df.shape[0]:,} rows, {df.shape[1]} columns")
        else:
            st.error("❌ Shipping data not found")
        
        # Check sales
        sales_files = ['sales_Data.csv', 'sales_TOP_10.csv', 'sales_Pivot.csv']
        for f in sales_files:
            path = os.path.join(output_dir, f)
            if os.path.exists(path):
                df = pd.read_csv(path)
                st.success(f"✅ {f}: {df.shape[0]:,} rows, {df.shape[1]} columns")
            else:
                st.error(f"❌ {f} not found")
        
        st.balloons()
        st.success("🎉 Data loading fixed! Go back to Overview page.")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

st.markdown("---")
st.info("After fixing, go back to the Overview page and the app should work properly.")
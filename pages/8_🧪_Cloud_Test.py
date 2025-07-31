"""
Simple test to verify cloud data loading
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cloud Data Test", layout="wide")

st.title("🧪 Cloud Data Loading Test")

# Check if we have secrets
st.header("1. Checking Secrets")
if hasattr(st, 'secrets'):
    st.success("✅ Secrets are available")
    st.write("Secret sections:", list(st.secrets.keys()))
    
    if 'data_files' in st.secrets:
        st.write("data_files keys:", list(st.secrets.data_files.keys()))
        
        if 'shipping_url' in st.secrets.data_files:
            st.code(f"Shipping URL: {st.secrets.data_files.shipping_url[:50]}...")
        if 'sales_url' in st.secrets.data_files:
            st.code(f"Sales URL: {st.secrets.data_files.sales_url[:50]}...")
else:
    st.error("❌ No secrets found")

# Try to load data directly
st.header("2. Testing Direct Data Load")

try:
    from cloud_data_loader import load_cloud_data
    st.success("✅ Cloud data loader imported")
    
    with st.spinner("Loading data from cloud..."):
        shipping_data, sales_data = load_cloud_data()
    
    if shipping_data is not None:
        st.success(f"✅ Shipping data loaded: {shipping_data.shape[0]} rows, {shipping_data.shape[1]} columns")
        st.write("First 5 rows:")
        st.dataframe(shipping_data.head())
    else:
        st.error("❌ Failed to load shipping data")
    
    if sales_data is not None:
        st.success(f"✅ Sales data loaded: {sales_data.shape[0]} rows, {sales_data.shape[1]} columns")
        st.write("First 5 rows:")
        st.dataframe(sales_data.head())
    else:
        st.error("❌ Failed to load sales data")
        
except Exception as e:
    st.error(f"Error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

# Show file structure
st.header("3. File Structure")
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
st.write(f"Current directory: {current_dir}")

data_dir = os.path.join(current_dir, 'data', 'extracted')
if os.path.exists(data_dir):
    st.write(f"Extracted data directory exists: {data_dir}")
    files = os.listdir(data_dir)
    st.write(f"Files in extracted directory: {files}")
else:
    st.warning("Extracted data directory does not exist yet")
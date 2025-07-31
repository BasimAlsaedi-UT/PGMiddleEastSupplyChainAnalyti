"""
Debug data loading to see what's in the Excel files
"""
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Debug Data", layout="wide")

st.title("🔍 Debug Data Loading")

# Load data from cloud
try:
    from cloud_data_loader import load_cloud_data
    
    with st.spinner("Loading data from Dropbox..."):
        shipping_data, sales_data = load_cloud_data()
    
    st.header("1. Raw Data from Dropbox")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if shipping_data is not None:
            st.success(f"✅ Shipping data: {shipping_data.shape}")
            st.write("Columns:", list(shipping_data.columns)[:10], "...")
            with st.expander("First 5 rows"):
                st.dataframe(shipping_data.head())
        else:
            st.error("❌ No shipping data")
    
    with col2:
        if sales_data is not None:
            st.success(f"✅ Sales data: {sales_data.shape}")
            st.write("Columns:", list(sales_data.columns)[:10], "...")
            with st.expander("First 5 rows"):
                st.dataframe(sales_data.head())
        else:
            st.error("❌ No sales data")
    
    st.header("2. Check Excel Files on Disk")
    
    # Get parent directory
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if Excel files exist
    file1_path = os.path.join(parent_dir, "2-JPG shipping tracking - July 2025.xlsx")
    file2_path = os.path.join(parent_dir, "3-DSR-PG- 2025 July.xlsx")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Shipping File")
        if os.path.exists(file1_path):
            st.success(f"✅ File exists: {file1_path}")
            try:
                xl = pd.ExcelFile(file1_path)
                st.write("Sheet names:", xl.sheet_names)
                
                # Show preview of Sheet1
                if 'Sheet1' in xl.sheet_names:
                    df = pd.read_excel(file1_path, sheet_name='Sheet1', nrows=5)
                    st.write("Sheet1 preview (first 5 rows):")
                    st.dataframe(df)
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        else:
            st.error("❌ File not found")
    
    with col2:
        st.subheader("Sales File")
        if os.path.exists(file2_path):
            st.success(f"✅ File exists: {file2_path}")
            try:
                xl = pd.ExcelFile(file2_path)
                st.write("Sheet names:", xl.sheet_names)
                
                # Show info about each sheet
                for sheet in xl.sheet_names:
                    df = pd.read_excel(file2_path, sheet_name=sheet, nrows=2)
                    st.write(f"\n**{sheet}**: {df.shape[1]} columns")
                    if st.checkbox(f"Show columns for {sheet}", key=f"cols_{sheet}"):
                        st.write(list(df.columns))
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        else:
            st.error("❌ File not found")
    
    st.header("3. Check Extracted Data")
    
    extracted_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'extracted')
    if os.path.exists(extracted_dir):
        files = os.listdir(extracted_dir)
        st.info(f"Files in extracted directory: {files}")
        
        # Check for sales files
        sales_files = [f for f in files if f.startswith('sales_')]
        if sales_files:
            st.success(f"Found sales files: {sales_files}")
        else:
            st.error("No sales files found (files starting with 'sales_')")
    else:
        st.warning("Extracted directory doesn't exist")
        
except Exception as e:
    st.error(f"Error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
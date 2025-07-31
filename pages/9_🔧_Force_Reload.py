"""
Force reload data from cloud
"""
import streamlit as st
import os
import shutil

st.set_page_config(page_title="Force Reload", layout="wide")

st.title("🔧 Force Data Reload")

st.warning("This page will clear all cached data and force a reload from Dropbox")

# Show current status
extracted_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'extracted')
if os.path.exists(extracted_dir):
    files = os.listdir(extracted_dir)
    st.info(f"Currently cached files: {files}")
else:
    st.info("No cached data found")

# Clear data button
if st.button("🗑️ Clear All Cached Data", type="primary"):
    try:
        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)
            st.success("✅ Cleared all cached data")
        else:
            st.warning("No cached data to clear")
    except Exception as e:
        st.error(f"Error clearing data: {str(e)}")

st.markdown("---")

# Test cloud loading
if st.button("🌐 Test Cloud Loading"):
    try:
        from cloud_data_loader import load_cloud_data
        
        with st.spinner("Loading from Dropbox..."):
            shipping_data, sales_data = load_cloud_data()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if shipping_data is not None:
                st.success(f"✅ Shipping: {shipping_data.shape}")
                st.dataframe(shipping_data.head(3))
            else:
                st.error("❌ Failed to load shipping data")
        
        with col2:
            if sales_data is not None:
                st.success(f"✅ Sales: {sales_data.shape}")
                st.dataframe(sales_data.head(3))
            else:
                st.error("❌ Failed to load sales data")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")
st.info("After clearing cached data, go back to the Overview page and it should reload from Dropbox")
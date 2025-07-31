"""
Minimal test app for Streamlit deployment
Use this to test if basic deployment works
"""

import streamlit as st

st.title("🚀 Deployment Test")

st.write("If you can see this, basic deployment is working!")

# Test if secrets are accessible
if hasattr(st, 'secrets'):
    st.success("✅ Secrets are accessible")
    st.write("Available sections:", list(st.secrets.keys()))
    
    if 'data_files' in st.secrets:
        st.write("data_files keys:", list(st.secrets.data_files.keys()))
else:
    st.error("❌ No secrets found")

# Test basic imports
try:
    import pandas as pd
    st.success("✅ Pandas imported successfully")
except:
    st.error("❌ Failed to import pandas")

try:
    import plotly.express as px
    st.success("✅ Plotly imported successfully")
except:
    st.error("❌ Failed to import plotly")

try:
    from cloud_data_loader import load_cloud_data
    st.success("✅ Cloud data loader imported successfully")
    
    # Try to load data
    with st.spinner("Loading data from Dropbox..."):
        shipping, sales = load_cloud_data()
    
    if shipping is not None:
        st.success(f"✅ Shipping data loaded: {shipping.shape}")
    else:
        st.error("❌ Failed to load shipping data")
    
    if sales is not None:
        st.success(f"✅ Sales data loaded: {sales.shape}")
    else:
        st.error("❌ Failed to load sales data")
        
except Exception as e:
    st.error(f"❌ Error with cloud data loader: {str(e)}")
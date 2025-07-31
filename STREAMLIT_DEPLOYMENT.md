# Streamlit Cloud Deployment Guide

## Prerequisites
- GitHub repository with the code
- Streamlit Cloud account (free at streamlit.io)
- Excel data files

## Step 1: Prepare Repository

1. Ensure all code is pushed to GitHub
2. Verify `requirements.txt` includes all dependencies
3. Check that `.streamlit/config.toml` exists

## Step 2: Create Streamlit Cloud Account

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign up with your GitHub account
3. Authorize Streamlit to access your repositories

## Step 3: Deploy the App

1. Click "New app" in Streamlit Cloud
2. Select repository: `BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti`
3. Branch: `main`
4. Main file path: `Overview.py`
5. Click "Deploy"

## Step 4: Configure Secrets for Data Files

Since we can't commit Excel files to GitHub, use Streamlit secrets:

1. In Streamlit Cloud dashboard, click on your app
2. Go to Settings → Secrets
3. Add the following configuration:

```toml
[data_files]
shipping_file_url = "YOUR_CLOUD_STORAGE_URL_FOR_SHIPPING_FILE"
sales_file_url = "YOUR_CLOUD_STORAGE_URL_FOR_SALES_FILE"

# Or use base64 encoded files (for smaller files)
[data_files_base64]
shipping_file = "BASE64_ENCODED_STRING"
sales_file = "BASE64_ENCODED_STRING"
```

## Step 5: Modify Code for Cloud Data

Create a file `cloud_data_loader.py`:

```python
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import requests
import os

def load_cloud_data():
    """Load data from Streamlit secrets"""
    
    # Check if running on Streamlit Cloud
    if 'data_files' in st.secrets:
        # Option 1: Load from URLs
        if 'shipping_file_url' in st.secrets.data_files:
            shipping_data = pd.read_excel(st.secrets.data_files.shipping_file_url)
            sales_data = pd.read_excel(st.secrets.data_files.sales_file_url)
            return shipping_data, sales_data
    
    # Option 2: Load from base64
    if 'data_files_base64' in st.secrets:
        shipping_bytes = base64.b64decode(st.secrets.data_files_base64.shipping_file)
        sales_bytes = base64.b64decode(st.secrets.data_files_base64.sales_file)
        
        shipping_data = pd.read_excel(BytesIO(shipping_bytes))
        sales_data = pd.read_excel(BytesIO(sales_bytes))
        return shipping_data, sales_data
    
    # Fallback to local files
    return None, None
```

## Step 6: Update Overview.py

Add cloud data loading to the `load_data()` function:

```python
# At the top of Overview.py
try:
    from cloud_data_loader import load_cloud_data
except ImportError:
    load_cloud_data = None

# In load_data() function, add:
if load_cloud_data:
    cloud_shipping, cloud_sales = load_cloud_data()
    if cloud_shipping is not None:
        # Use cloud data instead of local files
        # Process and save to extracted folder
```

## Alternative: Using Google Drive

1. Upload Excel files to Google Drive
2. Make them publicly readable (or use service account)
3. Use the sharing link in secrets:

```toml
[google_drive]
shipping_file_id = "https://docs.google.com/spreadsheets/d/1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59-/edit?usp=sharing&ouid=108224533927157750418&rtpof=true&sd=true"
sales_file_id = "https://docs.google.com/spreadsheets/d/1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi/edit?usp=sharing&ouid=108224533927157750418&rtpof=true&sd=true"
```

## Environment Variables

Set these in Streamlit Cloud settings:

- `STREAMLIT_SERVER_HEADLESS`: true
- `STREAMLIT_SERVER_PORT`: 80

## Monitoring

1. Check logs in Streamlit Cloud dashboard
2. Monitor resource usage (free tier: 1GB RAM)
3. Set up error notifications

## Updating the Deployed App

1. Push changes to GitHub
2. Streamlit Cloud automatically redeploys
3. For data updates, update the secrets

## Custom Domain (Optional)

1. In app settings, add custom domain
2. Configure DNS CNAME to point to Streamlit

## Performance Tips

1. Use `st.cache_data` for data loading
2. Minimize data file sizes
3. Consider using Parquet format for large datasets
4. Use session state for expensive computations

## Troubleshooting

### App crashes on startup
- Check logs for memory errors
- Reduce data size or upgrade to paid tier

### Data not loading
- Verify secrets are properly formatted
- Check file permissions if using cloud storage

### Slow performance
- Enable caching
- Reduce visualization complexity
- Consider data sampling for large datasets
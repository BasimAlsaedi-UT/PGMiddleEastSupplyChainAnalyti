# Streamlit Deployment Troubleshooting Guide

## Common Deployment Issues and Solutions

### 1. "Error installing requirements" Issue

This is the most common error when deploying to Streamlit Cloud. Here's how to diagnose and fix it:

#### Check the Deployment Logs
1. Go to your Streamlit Cloud dashboard
2. Click on your app
3. Click "Manage app" → "Logs"
4. Look for specific error messages

#### Common Causes and Solutions:

**a) Package Version Conflicts**
- Solution: Use compatible versions in requirements.txt
- Already fixed in your requirements.txt

**b) Missing System Dependencies**
- Some Python packages need system libraries
- Solution: Create a `packages.txt` file if needed

**c) Memory Limit Exceeded**
- Free tier has 1GB RAM limit
- Solution: Reduce package sizes or data

### 2. Google Sheets Access Issues

Your current secrets configuration:
```toml
shipping_file_id = '1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59-'
sales_file_id = '1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi'
```

#### Verify Google Sheets are Publicly Accessible:

1. **Test Direct Access:**
   Open these URLs in an incognito/private browser window:
   ```
   https://docs.google.com/spreadsheets/d/1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59-/export?format=xlsx
   https://docs.google.com/spreadsheets/d/1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi/export?format=xlsx
   ```
   
   If they download, great! If not, you need to fix sharing permissions.

2. **Fix Sharing Permissions:**
   - Open each Google Sheet
   - Click "Share" button (top right)
   - Click "Change to anyone with the link"
   - Make sure it says "Anyone with the link can view"
   - Click "Done"

3. **Correct File ID Format:**
   Remove any trailing dashes from file IDs:
   ```toml
   # Correct format in Streamlit secrets:
   [data_files]
   shipping_file_id = "1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59"
   sales_file_id = "1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi"
   ```

### 3. Secrets Configuration Issues

#### Proper Secrets Format:
1. Go to Streamlit Cloud → Your App → Settings → Secrets
2. Clear all content and paste exactly this:

```toml
[data_files]
shipping_file_id = "1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59"
sales_file_id = "1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi"
```

**Important:** 
- No quotes around the section name [data_files]
- Use double quotes for the values
- No trailing dashes in file IDs
- No extra spaces or tabs

### 4. Quick Debugging Steps

1. **Check if Secrets are Loaded:**
   Add this to your Overview.py temporarily:
   ```python
   import streamlit as st
   st.write("Secrets loaded:", hasattr(st, 'secrets'))
   if hasattr(st, 'secrets'):
       st.write("Available secrets:", list(st.secrets.keys()))
   ```

2. **Test Data Loading:**
   Create a simple test page to verify data loads:
   ```python
   # pages/test_data.py
   import streamlit as st
   from cloud_data_loader import load_cloud_data
   
   st.title("Data Loading Test")
   
   shipping, sales = load_cloud_data()
   
   if shipping is not None:
       st.success("✅ Shipping data loaded successfully!")
       st.write(f"Shape: {shipping.shape}")
   else:
       st.error("❌ Failed to load shipping data")
   
   if sales is not None:
       st.success("✅ Sales data loaded successfully!")
       st.write(f"Shape: {sales.shape}")
   else:
       st.error("❌ Failed to load sales data")
   ```

### 5. Alternative Solutions

#### Option A: Use Direct Export URLs
Instead of file IDs, use the full export URLs:
```toml
[data_files]
shipping_url = "https://docs.google.com/spreadsheets/d/1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59/export?format=xlsx"
sales_url = "https://docs.google.com/spreadsheets/d/1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi/export?format=xlsx"
```

#### Option B: Convert to Regular Google Drive Files
1. Download the Google Sheets as Excel files
2. Upload the Excel files to Google Drive (not as Google Sheets)
3. Share and use those file IDs instead

#### Option C: Use GitHub Releases
1. Download your Google Sheets as Excel files
2. Create a release on your GitHub repo
3. Upload the Excel files as release assets
4. Use the direct download URLs from the release

### 6. Error Messages and Solutions

| Error Message | Likely Cause | Solution |
|--------------|--------------|----------|
| "Error installing requirements" | Package conflict | Check logs for specific package |
| "No module named 'xlsxwriter'" | Missing dependency | Already handled in code |
| "403 Forbidden" | Google Sheets not public | Fix sharing permissions |
| "File not found" | Wrong file ID | Check ID format, remove dashes |
| "JSONDecodeError" | Corrupted download | Check if URL returns Excel file |

### 7. Step-by-Step Deployment Checklist

- [ ] Google Sheets are shared with "Anyone with the link can view"
- [ ] File IDs extracted correctly (no trailing dashes)
- [ ] Secrets added to Streamlit Cloud in correct TOML format
- [ ] App deployed from correct branch (main)
- [ ] Main file path set to "Overview.py"
- [ ] Requirements.txt is minimal (no heavy packages)
- [ ] Test data loads in incognito browser

### 8. If All Else Fails

1. **Use the Manual Upload Method:**
   - Download Google Sheets as Excel files
   - Create a `data` folder in your repo
   - Upload the Excel files
   - Remove from .gitignore temporarily
   - Push to GitHub
   - Deploy
   - Add back to .gitignore after first successful run

2. **Contact Streamlit Support:**
   - Go to discuss.streamlit.io
   - Post your deployment logs
   - They're very responsive!

### 9. Testing Locally First

Before deploying, test the cloud data loading locally:

```bash
# Create a test secrets file
mkdir -p .streamlit
echo '[data_files]' > .streamlit/secrets.toml
echo 'shipping_file_id = "1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59"' >> .streamlit/secrets.toml
echo 'sales_file_id = "1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi"' >> .streamlit/secrets.toml

# Run the app
streamlit run Overview.py
```

### 10. Monitor After Deployment

Once deployed successfully:
1. Check memory usage (should be under 1GB)
2. Monitor for timeout errors (large files may timeout)
3. Set up error notifications in Streamlit Cloud

Remember: The free tier of Streamlit Cloud has limitations. If your data files are large, consider:
- Sampling the data for demo purposes
- Using data compression
- Upgrading to a paid tier
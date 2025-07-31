# Quick Fix Guide for Streamlit Deployment

## Your Current Issue
You're getting "Error installing requirements" when deploying to Streamlit Cloud.

## Immediate Steps to Fix

### 1. Run the Test Script First
```bash
python test_google_sheets.py
```

This will tell you if your Google Sheets are accessible. If they fail, fix the sharing permissions first.

### 2. Fix Your Streamlit Secrets

Go to your Streamlit app → Settings → Secrets and use EXACTLY this format:

```toml
[data_files]
shipping_file_id = "1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59"
sales_file_id = "1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi"
```

**Important:** Remove the trailing dash from the first ID!

### 3. If Still Failing, Try This Alternative Format

Clear all secrets and use just this (no section header):

```toml
shipping_file_id = "1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59"
sales_file_id = "1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi"
```

### 4. Check Deployment Logs

1. Go to your Streamlit app
2. Click "Manage app"
3. Look at the logs
4. Find the ACTUAL error (not just "Error installing requirements")

Common errors:
- **"403 Forbidden"** → Google Sheets not public
- **"No module named..."** → Package issue
- **"Memory limit exceeded"** → Data files too large

### 5. Emergency Workaround

If nothing works, here's a quick workaround:

1. Download your Google Sheets as Excel files
2. Upload to GitHub Releases:
   ```bash
   # Create a release on GitHub
   # Go to: https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti/releases/new
   # Upload the Excel files there
   ```
3. Update secrets with the release URLs:
   ```toml
   [data_files]
   shipping_url = "https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti/releases/download/v1.0/shipping.xlsx"
   sales_url = "https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti/releases/download/v1.0/sales.xlsx"
   ```

### 6. Test Locally with Secrets

Create `.streamlit/secrets.toml` locally:
```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'EOF'
[data_files]
shipping_file_id = "1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59"
sales_file_id = "1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi"
EOF
```

Then run:
```bash
streamlit run Overview.py
```

If it works locally with secrets, it should work on Streamlit Cloud.

## Still Not Working?

The updated `cloud_data_loader.py` now shows detailed debug information. Deploy it and check what it says:

- "Available secret sections: ..." → Shows what secrets Streamlit sees
- "Attempting to load from: ..." → Shows the URL it's trying
- "403 Forbidden" → File not public
- "Received HTML instead of Excel" → File not accessible

## Final Resort

If absolutely nothing works:

1. Fork this simpler approach:
   - Remove cloud_data_loader.py imports from Overview.py
   - Upload Excel files directly to your repo (temporarily)
   - Deploy
   - Once it works, implement cloud loading

2. Contact Streamlit support at discuss.streamlit.io with:
   - Your app URL
   - The error logs
   - This message: "Google Sheets export URLs returning 403 despite public sharing"

## Success Checklist

- [ ] Google Sheets shared with "Anyone with link can view"
- [ ] Test script confirms files are accessible
- [ ] Secrets formatted correctly (TOML syntax)
- [ ] No trailing dashes in file IDs
- [ ] Deployment logs checked for real error
- [ ] Local test with secrets.toml works

Remember: The free Streamlit tier has a 1GB memory limit. If your Excel files are huge, they might cause memory errors even if everything else works!
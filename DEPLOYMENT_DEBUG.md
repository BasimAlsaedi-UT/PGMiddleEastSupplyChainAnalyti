# Streamlit Deployment Debugging Guide

## How to Check the Real Error

1. **Click "Manage App"** in your Streamlit dashboard
2. Look for the **terminal/logs** section
3. Find the actual error message (not just "Error installing requirements")

## Common Errors and Solutions

### 1. Memory Error During Package Installation
**Error:** "Killed" or memory-related messages
**Solution:** Try this minimal requirements.txt:
```
streamlit
pandas
numpy
plotly
openpyxl
requests
```

### 2. Specific Package Version Conflict
**Error:** "Could not find a version that satisfies..."
**Solution:** Remove version numbers:
```
streamlit
pandas
numpy
plotly
scikit-learn
openpyxl
xlrd
scipy
statsmodels
matplotlib
requests
```

### 3. Missing System Dependencies
**Error:** "error: Microsoft Visual C++ 14.0 is required"
**Solution:** Some packages need compilation. Try removing:
- statsmodels
- scipy
- scikit-learn

Then add them back one by one.

## Emergency Minimal Requirements

If nothing else works, use this absolute minimum:

```
streamlit
pandas
plotly
openpyxl
requests
```

Then create a simplified version of your app that doesn't use the other packages.

## Step-by-Step Debug Process

1. **Check logs** - What's the exact error?
2. **Simplify requirements** - Start minimal
3. **Test locally** with exact versions:
   ```bash
   pip freeze > requirements_exact.txt
   ```
4. **Deploy with minimal app** - Just test data loading:
   ```python
   import streamlit as st
   from cloud_data_loader import load_cloud_data
   
   st.title("Test Data Loading")
   shipping, sales = load_cloud_data()
   
   if shipping is not None:
       st.success(f"Shipping data: {shipping.shape}")
   else:
       st.error("Failed to load shipping data")
   
   if sales is not None:
       st.success(f"Sales data: {sales.shape}")
   else:
       st.error("Failed to load sales data")
   ```

## What to Look for in Logs

1. **Package name** causing the issue
2. **Version conflicts**
3. **Memory errors** (common on free tier)
4. **Missing dependencies**

## Quick Actions

1. **Push the packages.txt file** I created (even if empty)
2. **Try the minimal requirements**
3. **Check the actual error in logs**
4. **Share the error message** so I can help further

The logs will tell us exactly what's wrong!
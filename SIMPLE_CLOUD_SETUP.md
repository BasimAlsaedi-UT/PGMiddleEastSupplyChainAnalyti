# Simple Cloud Setup Guide

## Using Google Drive (Easiest Method)

### Step 1: Upload Your Excel Files to Google Drive

1. Go to [drive.google.com](https://drive.google.com)
2. Upload these two files:
   - `2-JPG shipping tracking - July 2025.xlsx`
   - `3-DSR-PG- 2025 July.xlsx`

### Step 2: Get Shareable Links

For EACH file:
1. Right-click the file
2. Click "Share"
3. Click "Change to anyone with the link"
4. Click "Copy link"

You'll get links like this:
```
https://drive.google.com/file/d/1ABC123xyz/view?usp=sharing
```

### Step 3: Extract the File IDs

From each link, copy the ID part (the random string):
- Link: `https://drive.google.com/file/d/1ABC123xyz/view?usp=sharing`
- ID: `1ABC123xyz`

### Step 4: Add to Streamlit Secrets

1. Go to your Streamlit app dashboard
2. Click Settings → Secrets
3. Add this configuration (replace with your actual IDs):

```toml
[data_files]
shipping_drive_id = "1ABC123xyz"
sales_drive_id = "2DEF456abc"
```

That's it! Your app will now load data from Google Drive.

## Using Dropbox (Alternative)

### Step 1: Upload to Dropbox
1. Upload your Excel files to Dropbox
2. Click "Share" → "Create link"

### Step 2: Modify the Links
Change the ending from `?dl=0` to `?dl=1`:
- Original: `https://www.dropbox.com/s/abc123/file.xlsx?dl=0`
- Modified: `https://www.dropbox.com/s/abc123/file.xlsx?dl=1`

### Step 3: Add to Streamlit Secrets
```toml
[data_files]
shipping_url = "https://www.dropbox.com/s/abc123/shipping.xlsx?dl=1"
sales_url = "https://www.dropbox.com/s/xyz789/sales.xlsx?dl=1"
```

## Quick Test

To test if your links work:
1. Open a new incognito/private browser window
2. Paste the link
3. The file should download automatically

If it opens a preview instead of downloading, the link format is wrong.

## Common Issues

### "File not found" error
- Make sure the file is shared with "Anyone with the link"
- Check that you copied the ID correctly

### "Download failed" error
- File might be too large (>100MB)
- Try compressing the Excel file first

### App still looking for local files
- Clear the `data/extracted/` folder in your app
- Restart the app

## Need Help?

If you're stuck, the app will show helpful error messages telling you exactly what's wrong!
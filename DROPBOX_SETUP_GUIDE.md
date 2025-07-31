# Dropbox Setup Guide for Streamlit Deployment

## Step-by-Step Instructions

### 1. Download Your Google Sheets as Excel Files

Since your Google Sheets are giving errors, first download them:

1. Open each Google Sheet
2. File → Download → Microsoft Excel (.xlsx)
3. Save with these exact names:
   - `2-JPG shipping tracking - July 2025.xlsx`
   - `3-DSR-PG- 2025 July.xlsx`

### 2. Upload to Dropbox

1. Go to [dropbox.com](https://www.dropbox.com)
2. Upload both Excel files
3. Keep them in any folder you like

### 3. Get Shareable Links

For **each** file:

1. Click the "Share" button next to the file
2. Click "Create link" (if not already created)
3. Click "Copy link"

You'll get links that look like:
```
https://www.dropbox.com/scl/fi/abc123xyz/filename.xlsx?rlkey=def456&dl=0
```

### 4. Convert to Direct Download Links

**IMPORTANT:** Change `?dl=0` to `?dl=1` at the end of each URL

Example:
- Sharing link: `https://www.dropbox.com/scl/fi/abc123/shipping.xlsx?rlkey=xyz789&dl=0`
- Direct link: `https://www.dropbox.com/scl/fi/abc123/shipping.xlsx?rlkey=xyz789&dl=1`

### 5. Update Your Streamlit Secrets

Go to your Streamlit app → Settings → Secrets

Clear everything and add:

```toml
[data_files]
shipping_url = "YOUR_DROPBOX_SHIPPING_URL_WITH_dl=1"
sales_url = "YOUR_DROPBOX_SALES_URL_WITH_dl=1"
```

Real example:
```toml
[data_files]
shipping_url = "https://www.dropbox.com/scl/fi/abc123/2-JPG shipping tracking - July 2025.xlsx?rlkey=xyz789&dl=1"
sales_url = "https://www.dropbox.com/scl/fi/def456/3-DSR-PG- 2025 July.xlsx?rlkey=uvw012&dl=1"
```

### 6. Test Your Links First

Before deploying, test each link:

1. Open a new incognito/private browser window
2. Paste the direct link (with `?dl=1`)
3. The file should download immediately
4. If it shows a preview page instead, the link is wrong

### 7. Redeploy Your App

After updating secrets:
1. Go to your Streamlit app
2. Click "Reboot app" or it should auto-redeploy

## Why Dropbox Works Better

1. **Simpler URLs** - No complex ID extraction needed
2. **More reliable** - No 404 or 432 errors
3. **Direct downloads** - Just change dl=0 to dl=1
4. **No permission issues** - Dropbox links always work when created

## Quick Checklist

- [ ] Downloaded both Google Sheets as .xlsx files
- [ ] Uploaded to Dropbox
- [ ] Got sharing links for both files
- [ ] Changed `?dl=0` to `?dl=1` in both URLs
- [ ] Tested links download files directly
- [ ] Updated Streamlit secrets with new URLs
- [ ] Redeployed the app

## Still Having Issues?

If you get errors after switching to Dropbox:

1. Make sure the URLs end with `?dl=1` (not `?dl=0`)
2. Check that file names don't have special characters
3. Verify the links work in an incognito browser
4. Look at Streamlit logs for the actual error

Dropbox is much more reliable than Google Sheets for this use case, so this should resolve your deployment issues!
# Cloud Storage Options for Excel Files

## Option 1: Google Drive (Recommended)

### Step 1: Upload Files to Google Drive
1. Upload your Excel files to Google Drive
2. Right-click each file → "Get link"
3. Change permission to "Anyone with the link can view"

### Step 2: Get Direct Download Links
For each file, convert the sharing link to a direct download link:

**Original Google Drive link format:**
```
https://drive.google.com/file/d/FILE_ID/view?usp=sharing
```

**Convert to direct download format:**
```
https://drive.google.com/uc?export=download&id=FILE_ID
```

### Example:
If your sharing link is:
```
https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view?usp=sharing
```

The direct download link would be:
```
https://drive.google.com/uc?export=download&id=1a2b3c4d5e6f7g8h9i0j
```

### Step 3: Add to Streamlit Secrets
In Streamlit Cloud settings → Secrets, add:
```toml
[data_files]
shipping_url = "https://drive.google.com/uc?export=download&id=YOUR_SHIPPING_FILE_ID"
sales_url = "https://drive.google.com/uc?export=download&id=YOUR_SALES_FILE_ID"
```

## Option 2: Dropbox

### Step 1: Upload to Dropbox
1. Upload files to Dropbox
2. Click "Share" → "Create link"
3. Copy the sharing link

### Step 2: Convert to Direct Download
Change the URL ending from `?dl=0` to `?dl=1`

**Original Dropbox link:**
```
https://www.dropbox.com/s/abc123xyz/filename.xlsx?dl=0
```

**Direct download link:**
```
https://www.dropbox.com/s/abc123xyz/filename.xlsx?dl=1
```

### Step 3: Add to Streamlit Secrets
```toml
[data_files]
shipping_url = "https://www.dropbox.com/s/YOUR_ID/shipping.xlsx?dl=1"
sales_url = "https://www.dropbox.com/s/YOUR_ID/sales.xlsx?dl=1"
```

## Option 3: GitHub Releases (For Public Data)

### Step 1: Create a Release
1. Go to your GitHub repo → Releases → "Create a new release"
2. Upload Excel files as release assets
3. Publish the release

### Step 2: Get Download URLs
Right-click on each asset → "Copy link address"

### Step 3: Add to Streamlit Secrets
```toml
[data_files]
shipping_url = "https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti/releases/download/v1.0/shipping.xlsx"
sales_url = "https://github.com/BasimAlsaedi-UT/PGMiddleEastSupplyChainAnalyti/releases/download/v1.0/sales.xlsx"
```

## Option 4: OneDrive

### Step 1: Upload to OneDrive
1. Upload files to OneDrive
2. Right-click → "Share"
3. Click "Copy link"

### Step 2: Convert to Direct Download
The URL needs to be converted using OneDrive's embedding format:
```
https://onedrive.live.com/download?resid=RESID&authkey=AUTHKEY
```

### Step 3: Add to Streamlit Secrets
```toml
[data_files]
shipping_url = "https://onedrive.live.com/download?resid=YOUR_RESID&authkey=YOUR_AUTHKEY"
sales_url = "https://onedrive.live.com/download?resid=YOUR_RESID&authkey=YOUR_AUTHKEY"
```

## Option 5: AWS S3 (For Production)

### Step 1: Upload to S3
1. Create an S3 bucket
2. Upload files
3. Make files public or use pre-signed URLs

### Step 2: Get Public URLs
```
https://your-bucket.s3.amazonaws.com/shipping.xlsx
https://your-bucket.s3.amazonaws.com/sales.xlsx
```

### Step 3: Add to Streamlit Secrets
```toml
[data_files]
shipping_url = "https://your-bucket.s3.amazonaws.com/shipping.xlsx"
sales_url = "https://your-bucket.s3.amazonaws.com/sales.xlsx"
```

## Option 6: Alternative - Using File IDs

Instead of full URLs, you can store just the file IDs:

```toml
[google_drive]
shipping_file_id = "1a2b3c4d5e6f7g8h9i0j"
sales_file_id = "2k3l4m5n6o7p8q9r0s1t"
```

The `cloud_data_loader.py` already supports this format!

## Testing Your URLs

Before adding to Streamlit, test that your URLs work:

1. Open a new browser tab (incognito/private mode)
2. Paste the URL
3. It should download the file directly (not open a preview)

## Security Notes

- **Public Links**: The methods above create publicly accessible links
- **Private Data**: For sensitive data, consider:
  - Using authentication tokens
  - Implementing OAuth flow
  - Using private S3 buckets with IAM roles
  - Encrypting files before uploading

## Troubleshooting

### "Access Denied" Error
- Check file permissions are set to "Anyone with link"
- Verify the URL format is correct for direct download

### "File Too Large" Error
- Google Drive: Files over 100MB may require confirmation
- Consider compressing files or using chunked loading

### Slow Download
- Large files may timeout on Streamlit's free tier
- Consider using smaller sample data for demo
- Upgrade to Streamlit's paid tier for better performance

## Example Complete Configuration

Here's a complete example using Google Drive:

```toml
# In Streamlit Cloud → App Settings → Secrets

[data_files]
shipping_url = "https://drive.google.com/uc?export=download&id=1ABC123DEF456GHI"
sales_url = "https://drive.google.com/uc?export=download&id=2JKL789MNO012PQR"

[app]
environment = "production"
```

After adding these secrets, redeploy your app and it will automatically download the files from Google Drive!
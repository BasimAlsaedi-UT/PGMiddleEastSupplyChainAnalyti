"""
Test script for Dropbox as an alternative to Google Sheets
"""

import requests
from io import BytesIO
import pandas as pd

def test_dropbox_url(url, file_name):
    """Test if a Dropbox file can be accessed"""
    print(f"\n{'='*50}")
    print(f"Testing {file_name}...")
    print(f"URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'Not specified')}")
        
        if response.status_code == 200:
            # Try to load as Excel
            try:
                df = pd.read_excel(BytesIO(response.content))
                print(f"✅ SUCCESS: Loaded Excel file with shape {df.shape}")
                return True
            except Exception as e:
                print(f"❌ ERROR: Could not parse as Excel: {str(e)}")
                return False
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        return False

def check_google_sheets_actual_urls():
    """Check the actual Google Sheets URLs you provided"""
    print("\nChecking your actual Google Sheets URLs...")
    
    urls = {
        "Shipping": "https://docs.google.com/spreadsheets/d/1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59-?rtpof=true&usp=drive_fs",
        "Sales": "https://docs.google.com/spreadsheets/d/1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi?rtpof=true&usp=drive_fs"
    }
    
    for name, url in urls.items():
        print(f"\n{name} URL: {url}")
        
        # Extract the ID correctly
        if '/d/' in url:
            file_id = url.split('/d/')[1].split('?')[0].rstrip('-')
            print(f"Extracted ID: {file_id}")
            
            # Note the dash in the shipping URL
            if name == "Shipping" and url.count('-') > 0:
                print("⚠️  WARNING: This URL has a dash before the ? mark")
                print("   The actual file ID might be different")

def main():
    print("="*70)
    print("DROPBOX vs GOOGLE SHEETS COMPARISON")
    print("="*70)
    
    # Check Google Sheets issues
    check_google_sheets_actual_urls()
    
    print("\n" + "="*70)
    print("DROPBOX ADVANTAGES:")
    print("="*70)
    print("✅ More reliable direct download links")
    print("✅ No complex URL parsing needed")
    print("✅ Better handling of Excel files")
    print("✅ Simpler sharing mechanism")
    print("✅ No 404/432 errors like Google Sheets")
    
    print("\n" + "="*70)
    print("HOW TO USE DROPBOX:")
    print("="*70)
    print("1. Upload your Excel files to Dropbox")
    print("2. Click 'Share' → 'Create link' → 'Copy link'")
    print("3. Change the URL ending from '?dl=0' to '?dl=1'")
    print("   Example:")
    print("   Original: https://www.dropbox.com/s/abc123/file.xlsx?dl=0")
    print("   Direct:   https://www.dropbox.com/s/abc123/file.xlsx?dl=1")
    print("\n4. Update your Streamlit secrets:")
    print("   [data_files]")
    print("   shipping_url = \"https://www.dropbox.com/s/YOUR_ID/shipping.xlsx?dl=1\"")
    print("   sales_url = \"https://www.dropbox.com/s/YOUR_ID/sales.xlsx?dl=1\"")
    
    print("\n" + "="*70)
    print("IMMEDIATE SOLUTION:")
    print("="*70)
    print("Since your Google Sheets are giving 404/432 errors, I recommend:")
    print("1. Download the Google Sheets as Excel files")
    print("2. Upload to Dropbox")
    print("3. Use Dropbox links in Streamlit")
    
    print("\n" + "="*70)
    print("TEST A DROPBOX URL:")
    print("="*70)
    test_url = input("Paste a Dropbox sharing link to test (or press Enter to skip): ").strip()
    
    if test_url:
        # Convert to direct download
        if '?dl=0' in test_url:
            direct_url = test_url.replace('?dl=0', '?dl=1')
            print(f"Converted to direct download: {direct_url}")
            test_dropbox_url(direct_url, "Test File")
        else:
            print("⚠️  Make sure to change ?dl=0 to ?dl=1 in the URL")

if __name__ == "__main__":
    main()
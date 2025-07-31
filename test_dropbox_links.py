"""
Test your specific Dropbox links
"""

import requests
from io import BytesIO
import pandas as pd

# Your Dropbox links converted to direct download
SHIPPING_URL = "https://www.dropbox.com/scl/fi/ntdmnsnk8z8y5trp53a0a/2-JPG-shipping-tracking-July-2025.xlsx?rlkey=m83v6mfeevnrtyg45mdrshuty&st=gw4t113u&dl=1"
SALES_URL = "https://www.dropbox.com/scl/fi/gxoa0u42h7phtb8c81c4k/3-DSR-PG-2025-July.xlsx?rlkey=jsfkrlm1n3lhb8iuemo00brkc&st=dx5j5bfw&dl=1"

def test_dropbox_url(url, file_name):
    """Test if a Dropbox file can be accessed"""
    print(f"\n{'='*70}")
    print(f"Testing {file_name}...")
    print(f"URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'Not specified')}")
        print(f"Content Length: {response.headers.get('content-length', 'Not specified')} bytes")
        
        if response.status_code == 200:
            # Try to load as Excel
            try:
                df = pd.read_excel(BytesIO(response.content))
                print(f"✅ SUCCESS: Loaded Excel file")
                print(f"   Shape: {df.shape}")
                print(f"   Columns: {list(df.columns)[:5]}...")
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

def main():
    print("="*70)
    print("TESTING YOUR DROPBOX LINKS")
    print("="*70)
    
    # Test both files
    shipping_ok = test_dropbox_url(SHIPPING_URL, "Shipping File")
    sales_ok = test_dropbox_url(SALES_URL, "Sales File")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY:")
    print(f"Shipping File: {'✅ OK' if shipping_ok else '❌ FAILED'}")
    print(f"Sales File: {'✅ OK' if sales_ok else '❌ FAILED'}")
    
    if shipping_ok and sales_ok:
        print("\n✅ Both files are accessible! Here's your Streamlit secrets configuration:")
        print("\n" + "="*70)
        print("Copy and paste this EXACTLY into Streamlit Cloud → Settings → Secrets:")
        print("="*70)
        print("""[data_files]
shipping_url = "https://www.dropbox.com/scl/fi/ntdmnsnk8z8y5trp53a0a/2-JPG-shipping-tracking-July-2025.xlsx?rlkey=m83v6mfeevnrtyg45mdrshuty&st=gw4t113u&dl=1"
sales_url = "https://www.dropbox.com/scl/fi/gxoa0u42h7phtb8c81c4k/3-DSR-PG-2025-July.xlsx?rlkey=jsfkrlm1n3lhb8iuemo00brkc&st=dx5j5bfw&dl=1"
""")
        print("="*70)
    else:
        print("\n❌ One or more files failed. Check the errors above.")

if __name__ == "__main__":
    main()
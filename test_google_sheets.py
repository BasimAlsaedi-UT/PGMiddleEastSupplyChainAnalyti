"""
Test script to verify Google Sheets access
Run this locally to test your Google Sheets configuration
"""

import requests
from io import BytesIO
import pandas as pd

# Your Google Sheets IDs
SHIPPING_ID = "1ZqnJ0db0p1RwOjMikCQL9R4c1mZ2G59"
SALES_ID = "1b61GNkB3VW37hVJFG7pt0lPetbvP3xKi"

def test_google_sheets_access(file_id, file_name):
    """Test if a Google Sheet can be accessed and downloaded"""
    print(f"\n{'='*50}")
    print(f"Testing {file_name}...")
    print(f"File ID: {file_id}")
    
    # Clean the ID
    clean_id = file_id.rstrip('-/').strip()
    print(f"Cleaned ID: {clean_id}")
    
    # Build the export URL
    url = f"https://docs.google.com/spreadsheets/d/{clean_id}/export?format=xlsx"
    print(f"Export URL: {url}")
    
    try:
        # Try to download
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'Not specified')}")
        
        if response.status_code == 200:
            # Check if it's actually an Excel file
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                print("❌ ERROR: Received HTML instead of Excel file")
                print("   The file is likely not shared publicly")
                print("   Solution: Share the Google Sheet with 'Anyone with the link can view'")
                return False
            
            # Try to load as Excel
            try:
                df = pd.read_excel(BytesIO(response.content))
                print(f"✅ SUCCESS: Loaded Excel file with shape {df.shape}")
                print(f"   Columns: {list(df.columns)[:5]}...")  # Show first 5 columns
                return True
            except Exception as e:
                print(f"❌ ERROR: Could not parse as Excel: {str(e)}")
                return False
                
        elif response.status_code == 403:
            print("❌ ERROR: 403 Forbidden - File is not publicly accessible")
            print("   Solution: Change sharing to 'Anyone with the link can view'")
            return False
        elif response.status_code == 404:
            print("❌ ERROR: 404 Not Found - Invalid file ID")
            print("   Solution: Check that the file ID is correct")
            return False
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Google Sheets Access Test")
    print("=" * 50)
    
    # Test both files
    shipping_ok = test_google_sheets_access(SHIPPING_ID, "Shipping File")
    sales_ok = test_google_sheets_access(SALES_ID, "Sales File")
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY:")
    print(f"Shipping File: {'✅ OK' if shipping_ok else '❌ FAILED'}")
    print(f"Sales File: {'✅ OK' if sales_ok else '❌ FAILED'}")
    
    if not (shipping_ok and sales_ok):
        print("\n⚠️  IMPORTANT: Fix the issues above before deploying to Streamlit")
        print("\nTo fix sharing permissions:")
        print("1. Open the Google Sheet")
        print("2. Click 'Share' button (top right)")
        print("3. Click 'Change to anyone with the link'")
        print("4. Make sure it says 'Anyone with the link can view'")
        print("5. Click 'Done'")
    else:
        print("\n✅ All tests passed! Your files are ready for Streamlit deployment.")
        print("\nStreamlit secrets.toml format:")
        print("[data_files]")
        print(f'shipping_file_id = "{SHIPPING_ID}"')
        print(f'sales_file_id = "{SALES_ID}"')

if __name__ == "__main__":
    main()
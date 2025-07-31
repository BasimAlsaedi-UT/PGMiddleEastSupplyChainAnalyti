"""
Script to run the Streamlit app with data extraction
"""

import os
import sys
import subprocess

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_extractor import DataExtractor

def setup_data():
    """Extract data from Excel files if not already done"""
    data_dir = "data/extracted"
    
    if not os.path.exists(f"{data_dir}/shipping_main_data.csv"):
        print("First time setup: Extracting data from Excel files...")
        
        # Create data directories
        os.makedirs(data_dir, exist_ok=True)
        
        # Extract data
        try:
            extractor = DataExtractor(
                file1_path="../2-JPG shipping tracking - July 2025.xlsx",
                file2_path="../3-DSR-PG- 2025 July.xlsx"
            )
            extractor.save_extracted_data()
            print("✅ Data extraction completed successfully!")
        except Exception as e:
            print(f"❌ Error extracting data: {str(e)}")
            print("\nPlease ensure the Excel files are in the parent directory:")
            print("  - ../2-JPG shipping tracking - July 2025.xlsx")
            print("  - ../3-DSR-PG- 2025 July.xlsx")
            return False
    else:
        print("✅ Data already extracted, skipping extraction step")
    
    return True

def run_streamlit():
    """Run the Streamlit application"""
    print("\n🚀 Starting P&G Supply Chain Analytics Dashboard...")
    print("=" * 50)
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    # Setup data
    if setup_data():
        # Run app
        run_streamlit()
    else:
        print("\n❌ Failed to setup data. Please fix the issues and try again.")
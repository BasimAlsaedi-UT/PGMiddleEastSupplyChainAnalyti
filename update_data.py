"""
Data Update Script for P&G Supply Chain Analytics Dashboard
This script helps update the dashboard with new Excel data files
"""

import os
import shutil
import sys
from datetime import datetime
import argparse

def backup_old_files(parent_dir):
    """Create backup of existing data files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(parent_dir, f'backup_{timestamp}')
    
    # Files to backup
    shipping_file = os.path.join(parent_dir, "2-JPG shipping tracking - July 2025.xlsx")
    sales_file = os.path.join(parent_dir, "3-DSR-PG- 2025 July.xlsx")
    
    if os.path.exists(shipping_file) or os.path.exists(sales_file):
        os.makedirs(backup_dir, exist_ok=True)
        
        if os.path.exists(shipping_file):
            shutil.copy2(shipping_file, backup_dir)
            print(f"✓ Backed up shipping file to {backup_dir}")
            
        if os.path.exists(sales_file):
            shutil.copy2(sales_file, backup_dir)
            print(f"✓ Backed up sales file to {backup_dir}")
    
    return backup_dir

def update_data_files(new_shipping_file, new_sales_file, keep_names=False):
    """Update dashboard data files"""
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    extracted_dir = os.path.join(script_dir, 'data', 'extracted')
    
    print(f"\n🔄 P&G Dashboard Data Update Script")
    print(f"{'='*50}")
    
    # Validate input files exist
    if not os.path.exists(new_shipping_file):
        print(f"❌ Error: Shipping file not found: {new_shipping_file}")
        return False
        
    if not os.path.exists(new_sales_file):
        print(f"❌ Error: Sales file not found: {new_sales_file}")
        return False
    
    # Create backup
    print("\n📦 Creating backup of existing files...")
    backup_dir = backup_old_files(parent_dir)
    
    # Copy new files
    print("\n📥 Copying new data files...")
    
    if keep_names:
        # Keep original file names - need to update app_fixed.py
        dest_shipping = os.path.join(parent_dir, os.path.basename(new_shipping_file))
        dest_sales = os.path.join(parent_dir, os.path.basename(new_sales_file))
        
        print(f"\n⚠️  Note: Using original file names. You need to update Overview.py with:")
        print(f"   Shipping file: {os.path.basename(new_shipping_file)}")
        print(f"   Sales file: {os.path.basename(new_sales_file)}")
    else:
        # Use standard names
        dest_shipping = os.path.join(parent_dir, "2-JPG shipping tracking - July 2025.xlsx")
        dest_sales = os.path.join(parent_dir, "3-DSR-PG- 2025 July.xlsx")
    
    # Copy files
    shutil.copy2(new_shipping_file, dest_shipping)
    print(f"✓ Copied shipping file to: {dest_shipping}")
    
    shutil.copy2(new_sales_file, dest_sales)
    print(f"✓ Copied sales file to: {dest_sales}")
    
    # Remove extracted data to force refresh
    if os.path.exists(extracted_dir):
        print("\n🗑️  Removing old extracted data...")
        shutil.rmtree(extracted_dir)
        print("✓ Cleared extracted data cache")
    
    print(f"\n{'='*50}")
    print("✅ Data update completed successfully!")
    print("\n📌 Next steps:")
    print("1. Restart the Streamlit application")
    print("2. The app will automatically extract data from new files")
    print("3. Verify data in the dashboard")
    
    if backup_dir and os.path.exists(backup_dir):
        print(f"\n💾 Backup location: {backup_dir}")
    
    return True

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description='Update P&G Dashboard data files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_data.py shipping.xlsx sales.xlsx
  python update_data.py --keep-names new_shipping_2025.xlsx new_sales_2025.xlsx
  
For more information, see DATA_UPDATE_GUIDE.md
        """
    )
    
    parser.add_argument('shipping_file', help='Path to new shipping Excel file')
    parser.add_argument('sales_file', help='Path to new sales Excel file')
    parser.add_argument('--keep-names', action='store_true', 
                       help='Keep original file names (requires updating Overview.py)')
    
    args = parser.parse_args()
    
    # Run update
    success = update_data_files(
        args.shipping_file, 
        args.sales_file,
        keep_names=args.keep_names
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
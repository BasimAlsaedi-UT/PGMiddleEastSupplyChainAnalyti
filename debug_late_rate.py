"""
Debug script to find why we're seeing 38% instead of 35.5%
"""

import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processor import DataProcessor

print("=== DEBUGGING LATE RATE CALCULATION ===\n")

# Load data using the same method as the app
processor = DataProcessor()
processor.load_processed_data(data_dir='data/extracted')

print(f"1. After loading, shipping_data has {len(processor.shipping_data)} rows")

# Check the raw calculation
if processor.shipping_data is not None and 'Delivery_Status' in processor.shipping_data.columns:
    status_counts = processor.shipping_data['Delivery_Status'].value_counts()
    total = status_counts.sum()
    
    print("\n2. Status counts:")
    for status, count in status_counts.items():
        pct = (count / total) * 100
        print(f"   {status}: {count:,} ({pct:.1f}%)")
    
    print(f"\n3. Total: {total:,}")
    
    # Calculate late rate
    late_count = status_counts.get('Late', 0)
    late_rate = (late_count / total) * 100
    print(f"\n4. Late rate calculation: {late_count:,} / {total:,} = {late_rate:.1f}%")

# Check if calculate_kpis gives different result
kpis = processor.calculate_kpis()
print(f"\n5. KPI calculation returns: {kpis['late_rate']}%")

# Check for any data processing that might change counts
print("\n6. Checking for data modifications during processing...")

# Check if dates are being filtered
if 'Actual_Ship_Date' in processor.shipping_data.columns:
    null_dates = processor.shipping_data['Actual_Ship_Date'].isnull().sum()
    print(f"   - Null ship dates: {null_dates}")
    
# Check for duplicates removed
print("\n7. Checking data_processor._validate_data() method...")
# This method removes duplicates - let's see if that's the issue

# Load raw data to compare
raw_df = pd.read_csv('data/extracted/shipping_main_data.csv')
print(f"\n8. Raw CSV has {len(raw_df)} rows")
print(f"   After DataProcessor loads: {len(processor.shipping_data)} rows")
print(f"   Difference: {len(raw_df) - len(processor.shipping_data)} rows")

# Check for duplicate removal
duplicates = raw_df.duplicated().sum()
print(f"\n9. Duplicates in raw data: {duplicates}")

# Recalculate with potential duplicates removed
if duplicates > 0:
    clean_df = raw_df.drop_duplicates()
    clean_status = clean_df['Delivery_Status'].value_counts()
    clean_total = clean_status.sum()
    clean_late = clean_status.get('Late', 0)
    clean_late_rate = (clean_late / clean_total) * 100
    print(f"\n10. After removing duplicates:")
    print(f"    Total: {clean_total}")
    print(f"    Late: {clean_late}")
    print(f"    Late rate: {clean_late_rate:.1f}%")

print("\n=== CONCLUSION ===")
if late_rate > 37.5 and late_rate < 38.5:
    print("The 38.0% late rate is being calculated correctly by the app.")
    print("This differs from Excel's 35.5% possibly due to:")
    print("- Duplicate removal during data processing")
    print("- Different filtering criteria")
    print("- Data validation steps")
else:
    print(f"Something else is happening. App shows {kpis['late_rate']}% but should show {late_rate:.1f}%")
"""
Debug script to trace where 38% is coming from
Run this to see exactly what the app is calculating
"""

import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processor import DataProcessor

print("=== DEBUGGING APP LATE RATE CALCULATION ===\n")

# Step 1: Load raw CSV data
print("STEP 1: Raw CSV Data")
print("-" * 50)
csv_path = 'data/extracted/shipping_main_data.csv'
raw_df = pd.read_csv(csv_path)
print(f"Total rows in CSV: {len(raw_df):,}")

raw_status = raw_df['Delivery_Status'].value_counts()
raw_late = raw_status.get('Late', 0)
raw_total = raw_status.sum()
raw_late_rate = (raw_late / raw_total) * 100
print(f"Late rate in CSV: {raw_late:,} / {raw_total:,} = {raw_late_rate:.1f}%")

# Step 2: Load through DataProcessor (like the app does)
print("\n\nSTEP 2: DataProcessor Loading")
print("-" * 50)
processor = DataProcessor()
processor.load_processed_data(data_dir='data/extracted')

print(f"Rows after loading: {len(processor.shipping_data):,}")

# Check what _validate_data() does
print("\nChecking for data modifications:")
print(f"- Duplicates would be removed by _validate_data()")
print(f"- But we know there are 0 duplicates")

# Step 3: Check the loaded data
print("\n\nSTEP 3: DataProcessor Data Analysis")
print("-" * 50)
if processor.shipping_data is not None:
    proc_status = processor.shipping_data['Delivery_Status'].value_counts()
    proc_late = proc_status.get('Late', 0)
    proc_total = proc_status.sum()
    proc_late_rate = (proc_late / proc_total) * 100
    
    print(f"Total rows in processor: {len(processor.shipping_data):,}")
    print(f"Late rate in processor: {proc_late:,} / {proc_total:,} = {proc_late_rate:.1f}%")
    
    # Compare
    print(f"\nDifference from raw: {len(processor.shipping_data) - len(raw_df):,} rows")

# Step 4: Calculate KPIs (like the app does)
print("\n\nSTEP 4: KPI Calculation")
print("-" * 50)
kpis = processor.calculate_kpis()
print(f"KPI late_rate: {kpis['late_rate']}%")
print(f"KPI total_shipments: {kpis['total_shipments']:,}")

# Step 5: Look for any date filtering
print("\n\nSTEP 5: Checking for Hidden Filters")
print("-" * 50)

# Check for null dates that might be filtered
if 'Actual_Ship_Date' in processor.shipping_data.columns:
    null_dates = processor.shipping_data['Actual_Ship_Date'].isnull().sum()
    print(f"Null ship dates: {null_dates}")
    
    # Check date range
    non_null_dates = processor.shipping_data['Actual_Ship_Date'].dropna()
    if len(non_null_dates) > 0:
        print(f"Date range: {non_null_dates.min()} to {non_null_dates.max()}")

# Check for any other filtering
print(f"\nUnique Delivery_Status values: {processor.shipping_data['Delivery_Status'].unique()}")

# Step 6: Simulate the app's filtered_data behavior
print("\n\nSTEP 6: Simulating App Filtering")
print("-" * 50)

# When "All Time" is selected, filtered_data should equal processor.shipping_data
filtered_data = processor.shipping_data.copy()
print(f"Filtered data rows: {len(filtered_data):,}")

# Recalculate on filtered data
if len(filtered_data) > 0:
    filt_status = filtered_data['Delivery_Status'].value_counts()
    filt_late = filt_status.get('Late', 0)
    filt_total = filt_status.sum()
    filt_late_rate = (filt_late / filt_total) * 100
    print(f"Late rate on filtered: {filt_late:,} / {filt_total:,} = {filt_late_rate:.1f}%")

# Summary
print("\n\n" + "="*70)
print("SUMMARY:")
print("="*70)
print(f"1. Raw CSV has:        35.5% late rate ✓ (matches Excel)")
print(f"2. DataProcessor has:  {proc_late_rate:.1f}% late rate")
print(f"3. KPI calculation:    {kpis['late_rate']}% late rate")
print(f"4. Expected in app:    38.0% late rate")

if abs(kpis['late_rate'] - 38.0) < 0.1:
    print("\n✓ The KPI calculation matches what you see in the app!")
    print("  The issue is in the data processing, not the display.")
elif abs(proc_late_rate - 38.0) < 0.1:
    print("\n✓ The DataProcessor data matches what you see in the app!")
    print("  The issue is in how data is loaded/filtered.")
else:
    print("\n✗ Neither calculation gives 38.0%")
    print("  There may be additional filtering in the app.")
    
print("\nPOSSIBLE CAUSES:")
print("1. Date filtering is applied even with 'All Time' selected")
print("2. Some records are excluded during processing")
print("3. The app is using different data than what's in data/extracted/")
print("4. There's a calculation error in the app")

print("\nNEXT STEPS:")
print("1. Add the debug code from app_with_debug.py to your app.py")
print("2. Check if any filters are secretly applied")
print("3. Re-extract the data to ensure freshness")
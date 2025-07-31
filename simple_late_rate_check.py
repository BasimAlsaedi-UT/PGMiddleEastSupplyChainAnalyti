"""
Simple script to check the late rate without any processing
Run this to see the raw calculation
"""

import pandas as pd
import os

print("=== SIMPLE LATE RATE CHECK ===\n")

# Check if extracted data exists
csv_path = 'data/extracted/shipping_main_data.csv'
if not os.path.exists(csv_path):
    print(f"ERROR: No extracted data found at {csv_path}")
    print("Please run the Streamlit app first to extract data from Excel files")
    exit(1)

# Load data
print(f"Loading data from: {csv_path}")
df = pd.read_csv(csv_path)
print(f"Loaded {len(df):,} rows\n")

# Count statuses
print("Delivery Status Counts:")
status_counts = df['Delivery_Status'].value_counts()
total = 0
for status in ['Late', 'On Time', 'Advanced', 'Not Due']:
    count = status_counts.get(status, 0)
    total += count
    pct = (count / len(df)) * 100
    print(f"  {status:12}: {count:6,} ({pct:5.1f}%)")

print(f"  {'TOTAL':12}: {total:6,}\n")

# Calculate late rate
late_count = status_counts.get('Late', 0)
late_rate = (late_count / total) * 100

print(f"Late Rate Calculation:")
print(f"  {late_count:,} Late / {total:,} Total = {late_rate:.1f}%\n")

# Show extraction date
metadata_path = 'data/extracted/extraction_metadata.json'
if os.path.exists(metadata_path):
    import json
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    print(f"Data extracted on: {metadata.get('extraction_date', 'Unknown')}")
else:
    print("Extraction date unknown")

print("\n" + "="*50)
print("RESULT:")
if late_rate < 36:
    print(f"✓ Late rate is {late_rate:.1f}% (matches Excel's 35.5%)")
elif late_rate > 37.5 and late_rate < 38.5:
    print(f"✗ Late rate is {late_rate:.1f}% (not matching Excel's 35.5%)")
    print("  This suggests the data has changed since the Excel analysis")
else:
    print(f"? Late rate is {late_rate:.1f}% (unexpected value)")
print("="*50)
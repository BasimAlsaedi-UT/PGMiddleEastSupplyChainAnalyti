"""
Verify the late delivery rate calculation
Compare with expected 35.5% from Excel
"""

import pandas as pd
import os

# Load the extracted shipping data
data_path = 'data/extracted/shipping_main_data.csv'
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    
    print("=== DATA VERIFICATION ===")
    print(f"Total rows in CSV: {len(df)}")
    
    # Check for Delivery_Status column
    if 'Delivery_Status' in df.columns:
        print("\nDelivery Status Distribution:")
        status_counts = df['Delivery_Status'].value_counts()
        print(status_counts)
        
        total = status_counts.sum()
        print(f"\nTotal records with status: {total}")
        
        print("\nPercentage Breakdown:")
        for status, count in status_counts.items():
            percentage = (count / total) * 100
            print(f"{status}: {count:,} ({percentage:.1f}%)")
        
        # Expected from Excel
        print("\n=== EXCEL COMPARISON ===")
        print("Expected from Excel Sheet 2:")
        print("- Advanced: 3,262 (13.3%)")
        print("- On Time: 9,860 (40.2%)")  
        print("- Late: 8,706 (35.5%)")
        print("- Not Due: 2,693 (11.0%)")
        print("- Total: 24,521")
        
        print("\n=== DIFFERENCES ===")
        excel_late_count = 8706
        excel_total = 24521
        excel_late_rate = 35.5
        
        actual_late_count = status_counts.get('Late', 0)
        actual_late_rate = (actual_late_count / total) * 100
        
        print(f"Excel Late Count: {excel_late_count:,}")
        print(f"Actual Late Count: {actual_late_count:,}")
        print(f"Difference: {actual_late_count - excel_late_count:,}")
        
        print(f"\nExcel Total: {excel_total:,}")
        print(f"Actual Total: {total:,}")
        print(f"Difference: {total - excel_total:,}")
        
        print(f"\nExcel Late Rate: {excel_late_rate}%")
        print(f"Actual Late Rate: {actual_late_rate:.1f}%")
        print(f"Difference: {actual_late_rate - excel_late_rate:.1f} percentage points")
        
        # Check for duplicates
        print("\n=== DUPLICATE CHECK ===")
        duplicates = df.duplicated().sum()
        print(f"Duplicate rows: {duplicates}")
        
        # Check for nulls in key columns
        print("\n=== NULL VALUES CHECK ===")
        null_status = df['Delivery_Status'].isnull().sum()
        print(f"Null Delivery_Status: {null_status}")
        
        # Check unique values
        print("\n=== UNIQUE STATUS VALUES ===")
        unique_statuses = df['Delivery_Status'].unique()
        print(f"Unique statuses: {unique_statuses}")
        
    else:
        print("ERROR: Delivery_Status column not found!")
        print(f"Available columns: {df.columns.tolist()}")
else:
    print(f"ERROR: File not found at {data_path}")

# Also check if we're filtering anything during extraction
print("\n=== EXTRACTION ANALYSIS ===")
print("The data extractor applies these filters:")
print("1. Removes rows where Delivery_Status is null")
print("2. Removes rows where Delivery_Status is 'Status' or 'Delivery Status' (header rows)")
print("3. Keeps only valid statuses: ['Advanced', 'Late', 'On Time', 'Not Due']")
print("\nThis filtering might be removing some records that Excel includes.")
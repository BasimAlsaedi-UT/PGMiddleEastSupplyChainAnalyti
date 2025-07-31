"""
Verify IOUs Analysis calculations step by step
"""

import pandas as pd
import numpy as np
from utils.data_processor import DataProcessor

# Load data
processor = DataProcessor()
processor.load_processed_data()

print("=== VERIFYING IOUs ANALYSIS CALCULATIONS ===\n")

# Check sales data
print("1. SALES DATA CHECK")
print("-" * 50)
print(f"Total sales records: {len(processor.sales_data)}")
print(f"Columns: {list(processor.sales_data.columns)}")
print()

# Basic IOU metrics
print("2. BASIC IOU METRICS")
print("-" * 50)
total_ious = processor.sales_data['IOUs'].sum()
total_sales = processor.sales_data['Sales'].sum()
iou_rate = (total_ious / total_sales * 100) if total_sales > 0 else 0
avg_iou = processor.sales_data['IOUs'].mean()
products_with_ious = (processor.sales_data['IOUs'] > 0).sum()

print(f"Total IOUs: {total_ious:,.0f}")
print(f"Total Sales: {total_sales:,.0f}")
print(f"IOU Rate: {iou_rate:.1f}%")
print(f"Average IOU per SKU: {avg_iou:.1f}")
print(f"Products with IOUs > 0: {products_with_ious}")
print()

# Check IOUs distribution
print("3. IOUs DISTRIBUTION")
print("-" * 50)
iou_distribution = processor.sales_data['IOUs'].describe()
print(iou_distribution)
print(f"\nProducts with IOU = 0: {(processor.sales_data['IOUs'] == 0).sum()}")
print(f"Products with IOU > 0: {(processor.sales_data['IOUs'] > 0).sum()}")
print()

# Channel Analysis
print("4. CHANNEL ANALYSIS")
print("-" * 50)
channel_ious = processor.sales_data.groupby('Channel').agg({
    'IOUs': 'sum',
    'Sales': 'sum',
    'Target': 'sum'
}).round(0)
channel_ious['IOU_Rate'] = (channel_ious['IOUs'] / channel_ious['Sales'] * 100).round(1)
channel_ious = channel_ious.sort_values('IOUs', ascending=False)
print(channel_ious)
print()

# Category Analysis
print("5. CATEGORY ANALYSIS")
print("-" * 50)
category_ious = processor.sales_data.groupby('Category').agg({
    'IOUs': ['sum', 'count', 'mean'],
    'Sales': 'sum'
}).round(0)
category_ious.columns = ['IOU_Total', 'Product_Count', 'Avg_IOU', 'Sales']
category_ious['IOU_Rate'] = (category_ious['IOU_Total'] / category_ious['Sales'] * 100).round(1)
category_ious = category_ious.sort_values('IOU_Total', ascending=False)
print(category_ious.head())
print()

# Top Products Analysis
print("6. TOP PRODUCTS WITH IOUs")
print("-" * 50)
top_products = processor.sales_data.nlargest(20, 'IOUs')[
    ['Planning Level', 'Category', 'Master Brand', 'IOUs', 'Sales', 'Target']
].copy()

print(f"Top 5 products by IOUs:")
print(top_products.head())
print()

# Products Needing Attention Logic
print("7. PRODUCTS NEEDING ATTENTION LOGIC")
print("-" * 50)
top_products['Achievement'] = (top_products['Sales'] / top_products['Target'] * 100).round(1)
top_products['IOU_vs_Sales'] = (top_products['IOUs'] / top_products['Sales'] * 100).round(1)

print("Criteria: IOU_vs_Sales > 50% AND Achievement < 80%")
print()

# Check for division by zero issues
print("Checking for potential division issues:")
print(f"Products with Sales = 0: {(top_products['Sales'] == 0).sum()}")
print(f"Products with Target = 0: {(top_products['Target'] == 0).sum()}")
print()

# Replace inf values if any
top_products['IOU_vs_Sales'] = top_products['IOU_vs_Sales'].replace([np.inf, -np.inf], 0)
top_products['Achievement'] = top_products['Achievement'].replace([np.inf, -np.inf], 0)

critical_products = top_products[
    (top_products['IOU_vs_Sales'] > 50) & 
    (top_products['Achievement'] < 80)
].head(3)

print(f"Critical products found: {len(critical_products)}")
if len(critical_products) > 0:
    print("\nCritical products details:")
    for idx, product in critical_products.iterrows():
        print(f"\nProduct: {product['Planning Level']}")
        print(f"  IOUs: {product['IOUs']:,.0f}")
        print(f"  Sales: {product['Sales']:,.0f}")
        print(f"  Target: {product['Target']:,.0f}")
        print(f"  Achievement: {product['Achievement']:.1f}%")
        print(f"  IOU vs Sales: {product['IOU_vs_Sales']:.1f}%")
else:
    print("\nNo products meet the critical criteria")
    print("\nLet's check products with high IOU_vs_Sales:")
    high_iou_ratio = top_products[top_products['IOU_vs_Sales'] > 20].head(5)
    print(high_iou_ratio[['Planning Level', 'IOUs', 'Sales', 'IOU_vs_Sales', 'Achievement']])

# Check what "400mlSH..." might be
print("\n8. CHECKING FOR '400mlSH...' PRODUCTS")
print("-" * 50)
products_400ml = processor.sales_data[processor.sales_data['Planning Level'].str.contains('400ml', na=False)]
print(f"Products containing '400ml': {len(products_400ml)}")
if len(products_400ml) > 0:
    print("\nSample '400ml' products:")
    print(products_400ml[['Planning Level', 'IOUs', 'Sales', 'Target']].head())

# Check if there are products with 0 IOUs in top products
print("\n9. CHECKING TOP PRODUCTS WITH 0 IOUs")
print("-" * 50)
zero_iou_in_top = top_products[top_products['IOUs'] == 0]
print(f"Products with 0 IOUs in top 20: {len(zero_iou_in_top)}")
if len(zero_iou_in_top) > 0:
    print("This shouldn't happen - top products should have IOUs > 0")
    print(zero_iou_in_top[['Planning Level', 'IOUs', 'Sales']])
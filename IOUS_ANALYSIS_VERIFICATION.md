# IOUs Analysis Verification Report

## Calculations Verified

### 1. Basic IOU Metrics (KPI Cards) ✅
- **Total Outstanding Orders**: Sum of all IOUs in sales data
- **IOU Rate**: (Total IOUs / Total Sales) × 100
- **Average IOU per SKU**: Mean of IOUs column
- **Products with IOUs**: Count where IOUs > 0

### 2. Channel Analysis ✅
- Groups data by Channel
- Calculates sum of IOUs, Sales, and Target per channel
- IOU_Rate = (IOUs / Sales) × 100 for each channel
- Bar chart colored by IOU_Rate (red scale for urgency)

### 3. Category Analysis ✅
- Groups data by Category
- Calculates:
  - IOU_Total: Sum of IOUs
  - Product_Count: Number of products
  - Avg_IOU: Mean IOU per product
  - IOU_Rate: (IOU_Total / Sales) × 100
- Pie chart shows distribution of IOUs
- Scatter plot shows IOUs vs Sales relationship

### 4. Top Products ✅
- Selects top 20 products by IOU value
- Calculates Achievement and IOU_vs_Sales ratios
- Bar chart shows top 10 products

## Issues Found and Fixed

### 1. Division by Zero Errors
**Problem**: Some products have Target=0 or Sales=0, causing division errors

**Fix**: Added safe division using numpy.where:
```python
top_products['Achievement'] = np.where(
    top_products['Target'] > 0,
    (top_products['Sales'] / top_products['Target'] * 100).round(1),
    0
)
```

### 2. Products Needing Attention Logic
**Original Issue**: Showing "400mlSH...: 0 IOUs"

**Root Cause**: 
- The logic was looking for products with IOU_vs_Sales > 50% AND Achievement < 80%
- Some products with 0 sales/target were causing invalid calculations
- The "400mlSH" shown was likely a product meeting criteria but with display issues

**Fix**:
- Filter out products with Sales=0 or Target=0 first
- Show more details (IOU rate and achievement) for context
- If no products meet criteria, show top 3 products by IOU value instead

### 3. Data Insights from Analysis

From the sales data sample:
- Many products have IOUs < 1.0 (fractional values)
- Top IOU products include:
  - 30kg: 1.29 IOUs
  - 15Kg: 1.12 IOUs  
  - 400mlSH: 0.96 IOUs
- Products with high IOU_vs_Sales ratio (>50%) often have very low sales volumes
- Some products have Target=0, indicating new or discontinued items

## Visualizations Verified

1. **Channel Bar Chart** ✅ - Shows IOUs by channel, colored by IOU rate
2. **Category Pie Chart** ✅ - Shows IOU distribution across categories
3. **Category Scatter** ✅ - IOUs vs Sales with bubble size for product count
4. **Top Products Bar** ✅ - Top 10 products by IOU value
5. **IOU vs Achievement Scatter** ✅ - Shows relationship between IOUs and sales achievement

## Recommendations

1. Consider filtering out products with very low sales/target values for cleaner analysis
2. The IOU values being fractional (< 1.0) suggests they might be in different units than expected
3. Products with Target=0 should be handled separately as "unplanned" items
4. Consider adding time-based analysis when historical data is available
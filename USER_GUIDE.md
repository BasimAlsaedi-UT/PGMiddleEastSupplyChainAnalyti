# P&G Supply Chain Analytics Dashboard - Complete User Guide

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Navigation](#navigation)
4. [Filters Section](#filters-section)
5. [Dashboard Pages](#dashboard-pages)
   - [Executive Summary](#executive-summary)
   - [Shipping Performance](#shipping-performance)
   - [Sales Analytics](#sales-analytics)
   - [Product Analysis](#product-analysis)
   - [Predictive Insights](#predictive-insights)
   - [Data Quality](#data-quality)
6. [Additional Pages](#additional-pages)
   - [Statistical Analysis](#statistical-analysis)
   - [ML Predictions](#ml-predictions)
7. [Features Reference](#features-reference)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The P&G Supply Chain Analytics Dashboard is a comprehensive tool for analyzing shipping performance, sales metrics, and supply chain efficiency. It processes data from two Excel files containing shipping tracking and sales information for the Middle East region.

### Key Metrics Tracked
- **35.5% Late Delivery Rate** - Critical business issue identified
- **Shipping Performance** - On-time, late, advanced, and not due shipments
- **Sales Achievement** - Actual vs target sales performance
- **Product Analysis** - Brand and SKU level performance

---

## Getting Started

### First Time Setup
When you run the dashboard for the first time:
1. The app automatically extracts data from Excel files
2. You'll see "First time setup: Extracting data from Excel files..."
3. This process takes 30-60 seconds
4. Data is cached for future use

### Data Sources
- **File 1**: `2-JPG shipping tracking - July 2025.xlsx` - Shipping and delivery data
- **File 2**: `3-DSR-PG- 2025 July.xlsx` - Sales and target data

---

## Navigation

### Sidebar Components

#### 1. **P&G Logo**
- Displays the P&G company logo
- Falls back to text if image fails to load

#### 2. **Dashboard Selector (Dropdown)**
Main navigation dropdown with six options:
- Executive Summary
- Shipping Performance
- Sales Analytics
- Product Analysis
- Predictive Insights
- Data Quality

#### 3. **Refresh Data Button** 🔄
- **Purpose**: Reload data from source files
- **When to use**: 
  - After updating Excel files
  - If data seems stale
  - To clear any cached calculations
- **Note**: This will re-extract data from Excel files

#### 4. **Last Update Timestamp**
- Shows when data was last loaded
- Format: "Last updated: YYYY-MM-DD HH:MM"

#### 5. **Additional Pages** (Below main content)
- 📊 Statistical Analysis
- 🤖 ML Predictions

---

## Filters Section

### Overview
The filters section appears at the top of every dashboard page with an expandable panel labeled "Filter Options".

### Date Range Filter

#### **Date Selection**
- **Type**: Date range picker
- **Default**: Full data range (all available dates)
- **Format**: MM/DD/YYYY
- **How it works**:
  - Select start date and end date
  - Filters all data to only show shipments within this range
  - Affects all charts and metrics

### Multi-Select Filters

#### 1. **Category Filter**
- **Type**: Multi-select dropdown
- **Options**: Product categories from the data
- **Examples**: "FAMILY CARE", "FABRIC CARE", "HAIR CARE", etc.
- **Default**: All categories selected
- **Usage**: Click to open, check/uncheck categories

#### 2. **Master Brand Filter**
- **Type**: Multi-select dropdown
- **Options**: Major P&G brands
- **Examples**: "PAMPERS", "ARIEL", "HEAD & SHOULDERS", etc.
- **Default**: All brands selected
- **Cascading**: Filters update based on selected categories

#### 3. **Source/Plant Filter**
- **Type**: Multi-select dropdown
- **Options**: Manufacturing plants/sources
- **Examples**: "GEBZE", "CAIRO", "RAKONA", etc.
- **Default**: All sources selected
- **Purpose**: Analyze performance by manufacturing location

#### 4. **Delivery Status Filter**
- **Type**: Multi-select dropdown
- **Options**: 
  - "On Time" - Delivered as scheduled
  - "Late" - Delivered after requested date
  - "Advanced" - Delivered before requested date
  - "Not Due" - Not yet due for delivery
- **Default**: All statuses selected
- **Critical**: Use to focus on problem shipments

#### 5. **Channel Filter** (if available)
- **Type**: Multi-select dropdown
- **Options**: Sales channels
- **Examples**: "MODERN TRADE", "TRADITIONAL TRADE", "E-COMMERCE"
- **Default**: All channels selected

### Filter Summary
- **Location**: Bottom of filter panel
- **Shows**: Active filters and date range
- **Format**: "Showing data from [start] to [end] with [X] filters applied"

---

## Dashboard Pages

### Executive Summary

#### Purpose
High-level overview of supply chain performance with key metrics and alerts.

#### Components

##### 1. **Alert Section**
- **Critical Alert** (Red): Shows when late rate > 40%
- **Warning Alert** (Yellow): Shows when late rate > 35%
- **Success Alert** (Green): Shows when performance is good

##### 2. **Primary KPI Cards** (Top Row)
- **Total Shipments**
  - Shows: Total number of shipments
  - Format: Numeric (e.g., "12,345")
  
- **Late Delivery Rate**
  - Shows: Percentage of late shipments
  - Format: Percentage with 1 decimal (e.g., "35.5%")
  - Color coding: Red if > 35%, Yellow if > 30%, Green otherwise
  
- **On-Time Rate**
  - Shows: Percentage delivered on schedule
  - Format: Percentage (e.g., "45.2%")
  
- **Avg Delay (Late Only)**
  - Shows: Average days late for late shipments
  - Format: Days with 1 decimal (e.g., "5.3 days")

##### 3. **Secondary KPI Cards** (Second Row)
- **Advanced Shipments**: Delivered early percentage
- **Not Due**: Pending deliveries percentage
- **Total Sales**: Sum of all sales
- **Sales Achievement**: Actual/Target percentage

##### 4. **Charts**

**Delivery Status Distribution (Pie Chart)**
- **Type**: Pie chart
- **Shows**: Breakdown of delivery statuses
- **Colors**: 
  - Late: Red
  - On Time: Green
  - Advanced: Blue
  - Not Due: Orange
- **Interactive**: Hover for exact numbers

**Sales Achievement Gauge**
- **Type**: Gauge chart
- **Range**: 0-150%
- **Zones**:
  - Red: 0-80% (Below target)
  - Yellow: 80-95% (Near target)
  - Green: 95%+ (On/above target)
- **Pointer**: Shows current achievement

**Daily Late Rate Trend**
- **Type**: Line chart
- **X-axis**: Date
- **Y-axis**: Late delivery percentage
- **Features**: 
  - 7-day moving average line
  - Hover for daily details
  - Zoom and pan capabilities

**Category Performance**
- **Type**: Horizontal bar chart
- **Shows**: Late rate by product category
- **Sorted**: Worst performing at top
- **Color**: Gradient from green (good) to red (bad)

---

### Shipping Performance

#### Purpose
Detailed analysis of shipping and delivery performance with multiple analytical views.

#### Tabs

##### 1. **Overview Tab**

**Waterfall Chart**
- **Shows**: Flow from total shipments to each delivery status
- **Colors**: 
  - Green: Positive (On Time)
  - Red: Negative (Late)
  - Blue: Other statuses
- **Values**: Number of shipments in each category

**Delay Distribution**
- **Type**: Histogram
- **Shows**: Distribution of delay days for late shipments
- **X-axis**: Days delayed (bins)
- **Y-axis**: Number of shipments
- **Insight**: Identifies if delays are systematic or random

##### 2. **Plant Analysis Tab**

**Plant Performance Table**
- **Columns**:
  - Source (Plant name)
  - Late shipments count
  - On Time count
  - Total shipments
  - Late Rate %
- **Sorting**: By late rate (worst first)
- **Color coding**: Heat map on late rate column

**Plant Performance Heatmap**
- **Type**: 2D heatmap
- **X-axis**: Delivery Status
- **Y-axis**: Plant/Source
- **Color intensity**: Number of shipments
- **Purpose**: Quick visual of problem plants

##### 3. **Time Analysis Tab**

**Shipping by Day of Week**
- **Type**: Grouped bar chart
- **Shows**: Shipment volumes by weekday
- **Groups**: Each delivery status
- **Insight**: Identifies weekly patterns

**Monthly Trends**
- **Type**: Multi-line chart
- **Lines**: One per delivery status
- **X-axis**: Month-Year
- **Y-axis**: Number of shipments
- **Purpose**: Seasonal pattern identification

##### 4. **Pivot Recreation Tab**

**Original Excel Pivot Structure**
- **Recreates**: Pivot table from source Excel
- **Index**: Category > Master Brand > Brand
- **Columns**: Source/Plant
- **Values**: Quantity shipped
- **Format**: Numbers with thousand separators

---

### Sales Analytics

#### Purpose
Analysis of sales performance against targets and forecast accuracy.

#### Components

##### 1. **Channel Performance Section**

**Channel Performance Table**
- **Columns**:
  - Channel name
  - Sales (actual)
  - Target
  - Achievement %
  - Late Rate %
- **Color coding**: Achievement gradient

**Sales vs Target Bar Chart**
- **Type**: Grouped bar chart
- **Groups**: Sales (blue) vs Target (orange)
- **X-axis**: Channel
- **Y-axis**: Value
- **Shows**: Performance gaps visually

##### 2. **Forecast Accuracy**

**Accuracy by Category Chart**
- **Type**: Bar chart
- **Shows**: Forecast accuracy percentage
- **Target line**: 90% accuracy
- **Color**: Below target in red, above in green

##### 3. **Top Products**

**Top 10 Products by Late Deliveries**
- **Table showing**:
  - Product/SKU name
  - Late shipment count
  - Total shipments
  - Late rate %
  - Total quantity
- **Sorted**: Most problematic first

---

### Product Analysis

#### Purpose
Deep dive into brand and SKU level performance.

#### Components

##### 1. **Brand Performance Sunburst**
- **Type**: Hierarchical sunburst chart
- **Levels**: 
  - Center: Total
  - Ring 1: Categories
  - Ring 2: Master Brands
  - Ring 3: Individual brands
- **Size**: Represents volume
- **Color**: Performance metric
- **Interactive**: Click to zoom into segments

##### 2. **Brand Performance Table**
- **Shows**: Top 20 brands
- **Metrics**:
  - Total shipments
  - Late shipments
  - Late rate %
- **Sorting**: By volume (highest first)
- **Color**: Heat map on late rate

##### 3. **SKU Level Analysis**

**Controls**:
- **Metric Selector**: Choose between "Late", "Quantity", or "Late Rate"
- **Product Count Slider**: Select 5-50 products to display

**SKU Performance Table**
- **Dynamic columns** based on selected metric
- **Shows**: Top/bottom performers
- **Use cases**:
  - "Late": Find most problematic SKUs
  - "Quantity": Find highest volume SKUs
  - "Late Rate": Find worst performing SKUs

---

### Predictive Insights

#### Purpose
Forward-looking analytics and trend projections (requires ML features).

#### Components

##### 1. **Late Delivery Risk Prediction**
- **Status**: "Coming soon" placeholder
- **Purpose**: ML model to predict at-risk shipments
- **Future**: Will show risk scores for pending shipments

##### 2. **Trend Projection**

**Late Rate Trend Analysis**
- **Type**: Multi-line chart
- **Lines**:
  - Actual late rate (blue)
  - 7-day moving average (orange)
  - 30-day moving average (green)
- **Purpose**: Smooth out daily variations
- **Insight**: Identify improving/worsening trends

---

### Data Quality

#### Purpose
Monitor data completeness and validation checks.

#### Components

##### 1. **Data Completeness Table**
- **Columns**:
  - Column name
  - Non-null count
  - Null count
  - Completeness %
- **Color**: Gradient on completeness
- **Purpose**: Identify missing data issues

##### 2. **Data Validation Checks**

**Automated Checks**:

1. **No Future Ship Dates**
   - Checks: Ship dates are not in future
   - Status: ✅ Pass or ❌ Fail
   - Severity: High

2. **No Extreme Delays**
   - Checks: No delays < -30 days
   - Status: ✅ Pass or ⚠️ Warning
   - Severity: Medium

3. **Valid Delivery Status**
   - Checks: All statuses are valid
   - Status: ✅ Pass or ❌ Fail
   - Severity: High

4. **No Duplicate Shipments**
   - Checks: No duplicate records
   - Status: ✅ Pass or ⚠️ Warning
   - Severity: Medium

##### 3. **Data Freshness**
- **Shows**: How old the data is
- **Status indicators**:
  - ✅ Current: < 2 days old
  - ⚠️ Warning: 2-7 days old
  - ❌ Error: > 7 days old
- **Display**: Last shipment date

---

## Additional Pages

### Statistical Analysis

#### Access
Click "📊 Statistical Analysis" in the sidebar (below main content).

#### Features
- Statistical tests on shipping data
- Correlation analysis
- Distribution analysis
- Hypothesis testing capabilities

### ML Predictions

#### Access
Click "🤖 ML Predictions" in the sidebar.

#### Requirements
- Requires scikit-learn installation
- Optional: prophet for advanced forecasting

#### Features

##### 1. **Model Training**
- Click "🚀 Train All Models" to start
- Trains three model types:
  - Late delivery prediction
  - Demand forecasting
  - Anomaly detection

##### 2. **Late Delivery Prediction**
- **Accuracy metrics**: Model performance
- **ROC curve**: Classification quality
- **Feature importance**: What drives late deliveries
- **Risk assessment**: Current shipments at risk

##### 3. **Demand Forecasting**
- **30-day forecast**: Future shipment volumes
- **Seasonality patterns**: Weekly/monthly trends
- **Confidence intervals**: Uncertainty ranges

##### 4. **Anomaly Detection**
- **Unusual patterns**: Outlier shipments
- **Anomaly rate**: Percentage of anomalies
- **Detail table**: Specific anomalous records

##### 5. **Route Optimization**
- **Route scoring**: Worst performing routes
- **Optimization priorities**: Where to focus
- **Recommendations**: Specific actions

---

## Features Reference

### Interactive Elements

#### 1. **Hover Information**
- All charts show details on hover
- Tables show full text on hover
- Metrics show additional context

#### 2. **Zoom and Pan**
- Line charts: Click and drag to zoom
- Reset: Double-click
- Pan: Shift + drag

#### 3. **Download Options**
- Charts: Camera icon to download as PNG
- Tables: Can be copied to clipboard

### Performance Features

#### 1. **Data Caching**
- Processed data cached for 1 hour
- Reduces reload time
- Clear cache with Refresh button

#### 2. **Lazy Loading**
- Charts load as you scroll
- Improves initial page load

#### 3. **Responsive Design**
- Adapts to screen size
- Works on tablets and large monitors

---

## Troubleshooting

### Common Issues

#### 1. **"No data matches filters"**
- **Cause**: Filters too restrictive
- **Solution**: Reset filters or select more options

#### 2. **Empty charts**
- **Cause**: No data for that metric
- **Solution**: Check data quality page

#### 3. **Slow loading**
- **Cause**: Large dataset
- **Solution**: Use date filters to reduce data

#### 4. **ML features not working**
- **Cause**: Missing dependencies
- **Solution**: Install scikit-learn

### Data Issues

#### 1. **High late rate (35.5%)**
- This is a real issue in the data
- Focus on worst categories/plants
- Use filters to investigate

#### 2. **Missing values**
- Check Data Quality page
- Some calculations may be affected
- Completeness % shows impact

### Getting Help

#### Error Messages
- Read the specific error shown
- Check the terminal for details
- Most errors include solutions

#### Feature Requests
- The dashboard is extensible
- New charts can be added
- Additional metrics possible

---

## Best Practices

### 1. **Start with Executive Summary**
- Get overall picture first
- Note problem areas
- Then dive into details

### 2. **Use Filters Effectively**
- Start broad, then narrow
- Compare filtered vs overall
- Save interesting filter combinations

### 3. **Cross-Reference Pages**
- Sales issues → Check shipping
- Late deliveries → Check plants
- Use multiple views for insights

### 4. **Regular Monitoring**
- Check daily/weekly
- Watch trend changes
- Set up alerts for thresholds

### 5. **Data Quality First**
- Always check data quality
- Address issues before analysis
- Document data problems

---

## Keyboard Shortcuts

- **F5**: Refresh page
- **Ctrl+F**: Search in page
- **Esc**: Close popups
- **Tab**: Navigate elements

---

## Export Options

### Charts
1. Hover over chart
2. Click camera icon
3. Download as PNG

### Data
1. Select table data
2. Copy (Ctrl+C)
3. Paste into Excel

### Full Report
- Use browser print (Ctrl+P)
- Save as PDF
- Adjust layout as needed
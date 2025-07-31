# Advanced Features Guide - Statistical Analysis & ML Predictions

## Table of Contents
1. [Statistical Analysis Page](#statistical-analysis-page)
   - [Overview](#overview-statistical-analysis)
   - [Descriptive Statistics](#descriptive-statistics)
   - [Distribution Analysis](#distribution-analysis)
   - [Correlation Analysis](#correlation-analysis)
   - [Hypothesis Testing](#hypothesis-testing)
   - [Time Series Analysis](#time-series-analysis)
   - [Advanced Analytics](#advanced-analytics)
2. [ML Predictions Page](#ml-predictions-page)
   - [Overview](#overview-ml-predictions)
   - [Model Training](#model-training)
   - [Late Delivery Prediction](#late-delivery-prediction)
   - [Demand Forecasting](#demand-forecasting)
   - [Anomaly Detection](#anomaly-detection)
   - [Route Optimization](#route-optimization)
   - [Model Insights](#model-insights)
3. [Technical Requirements](#technical-requirements)
4. [Best Practices](#best-practices)

---

# Statistical Analysis Page

## Overview (Statistical Analysis)

### Purpose
The Statistical Analysis page provides advanced statistical tools to analyze shipping and sales data, uncover patterns, test hypotheses, and generate insights beyond basic descriptive statistics.

### Access
- **Location**: Sidebar below main content
- **Icon**: 📊
- **Label**: "Statistical Analysis"
- **Requirements**: scipy, matplotlib (optional but recommended)

### Page Layout
The page is organized into tabs for different types of statistical analysis:
1. Descriptive Stats
2. Distribution Analysis
3. Correlation Analysis
4. Hypothesis Testing
5. Time Series Analysis
6. Advanced Analytics

---

## Descriptive Statistics

### Overview Section
Comprehensive statistical summary of numerical columns in the dataset.

#### **Summary Statistics Table**
- **Metrics Included**:
  - **Count**: Number of non-null values
  - **Mean**: Average value
  - **Std Dev**: Standard deviation
  - **Min**: Minimum value
  - **25%**: First quartile
  - **50%**: Median (second quartile)
  - **75%**: Third quartile
  - **Max**: Maximum value
  - **Skewness**: Measure of asymmetry
  - **Kurtosis**: Measure of tail heaviness

#### **Key Insights Panel**
- **Automatic Detection**:
  - Most variable metric (highest CV)
  - Most skewed distribution
  - Potential outliers (using IQR method)
  - Missing data summary

#### **Categorical Variables Summary**
- **For Each Category**:
  - Unique values count
  - Most frequent value (mode)
  - Frequency of top value
  - Distribution chart

---

## Distribution Analysis

### Features

#### **1. Variable Selector**
- **Type**: Dropdown menu
- **Options**: All numerical columns
- **Default**: "Delay_Days" or first numerical column

#### **2. Distribution Plots**

**Histogram with KDE**
- **Components**:
  - Histogram bars (blue)
  - Kernel Density Estimation curve (red)
  - Normal distribution overlay (green dashed)
- **Customization**:
  - Bin size slider (10-100 bins)
  - Show/hide normal curve toggle
  - Log scale option for skewed data

**Q-Q Plot (Quantile-Quantile)**
- **Purpose**: Test for normality
- **Interpretation**:
  - Points on diagonal line = normal distribution
  - S-shaped curve = heavy tails
  - Inverted S = light tails
- **Features**:
  - Reference line (red)
  - Confidence bands (95%)

**Box Plot with Outliers**
- **Shows**:
  - Median (center line)
  - IQR (box)
  - Whiskers (1.5 * IQR)
  - Outliers (individual points)
- **Options**:
  - Group by category
  - Show violin plot overlay

#### **3. Statistical Tests Panel**

**Normality Tests**:
- **Shapiro-Wilk Test**
  - Null hypothesis: Data is normal
  - p < 0.05: Reject normality
  - Best for n < 5000

- **Anderson-Darling Test**
  - More sensitive to tails
  - Multiple significance levels
  - Better for larger samples

**Distribution Fit Tests**:
- Tests against multiple distributions:
  - Normal
  - Exponential
  - Log-normal
  - Gamma
  - Weibull
- **Output**: Best fit distribution with parameters

---

## Correlation Analysis

### Features

#### **1. Correlation Matrix**

**Heatmap Display**
- **Color Scale**: 
  - Dark red: Strong negative (-1)
  - White: No correlation (0)
  - Dark blue: Strong positive (+1)
- **Options**:
  - Pearson correlation (default)
  - Spearman rank correlation
  - Kendall's tau
- **Annotations**: Show correlation values
- **Mask**: Upper/lower triangle options

#### **2. Variable Relationship Explorer**

**Scatter Plot Matrix**
- **Purpose**: Pairwise relationships
- **Features**:
  - Diagonal: Distribution plots
  - Off-diagonal: Scatter plots
  - Color coding by category
  - Regression lines option

**Interactive Correlation Explorer**
- **Select two variables**:
  - X-axis variable dropdown
  - Y-axis variable dropdown
- **Plot includes**:
  - Scatter points
  - Regression line
  - Confidence interval
  - R² value
  - Correlation coefficient

#### **3. Top Correlations Table**
- **Shows**: Strongest correlations (absolute value)
- **Columns**:
  - Variable 1
  - Variable 2
  - Correlation coefficient
  - p-value
  - Significance stars
- **Filter**: Minimum correlation threshold

#### **4. Partial Correlation Analysis**
- **Purpose**: Control for confounding variables
- **Process**:
  1. Select primary variables
  2. Select control variables
  3. Calculate partial correlations
- **Output**: Adjusted correlation matrix

---

## Hypothesis Testing

### Features

#### **1. Test Selection Panel**

**Available Tests**:

**T-Tests**:
- **One-sample t-test**
  - Compare mean to hypothesized value
  - Example: Is average delay > 5 days?
  
- **Two-sample t-test**
  - Compare means between groups
  - Example: Late rate Plant A vs Plant B
  
- **Paired t-test**
  - Before/after comparisons
  - Example: Performance pre/post intervention

**ANOVA Tests**:
- **One-way ANOVA**
  - Compare means across multiple groups
  - Example: Delay by category
  
- **Two-way ANOVA**
  - Two factor analysis
  - Example: Category × Plant interaction

**Chi-Square Tests**:
- **Independence Test**
  - Relationship between categoricals
  - Example: Status vs Category
  
- **Goodness of Fit**
  - Compare to expected distribution
  - Example: Uniform delivery across days

#### **2. Test Configuration**

**Parameters**:
- **Significance Level**: α slider (0.01, 0.05, 0.10)
- **Alternative Hypothesis**: Two-tailed, greater, less
- **Effect Size**: Calculate Cohen's d, η²
- **Power Analysis**: Sample size requirements

#### **3. Results Display**

**Test Output Panel**:
- **Test Statistic**: Value and distribution
- **p-value**: With interpretation
- **Confidence Intervals**: For differences
- **Effect Size**: With interpretation guidelines
- **Assumptions Check**: 
  - Normality
  - Equal variances
  - Independence

**Visualization**:
- Distribution plots with test regions
- Means with error bars
- Effect size forest plots

#### **4. Multiple Comparisons**
- **Bonferroni Correction**: Adjusted p-values
- **Tukey HSD**: Post-hoc for ANOVA
- **False Discovery Rate**: Benjamini-Hochberg

---

## Time Series Analysis

### Features

#### **1. Trend Analysis**

**Decomposition Plot**
- **Components**:
  - **Observed**: Original time series
  - **Trend**: Long-term direction
  - **Seasonal**: Repeating patterns
  - **Residual**: Random variation
- **Methods**:
  - Additive decomposition
  - Multiplicative decomposition
  - STL decomposition

**Moving Averages**:
- **Options**:
  - Simple MA (7, 14, 30 days)
  - Exponential MA
  - Weighted MA
- **Display**: Original + smoothed lines

#### **2. Seasonality Detection**

**Autocorrelation Function (ACF)**
- **Shows**: Correlation at different lags
- **Interpretation**:
  - Significant spikes = seasonality
  - Lag number = period length
- **Confidence bands**: 95% significance

**Periodogram**
- **Purpose**: Frequency domain analysis
- **Peaks**: Indicate seasonal frequencies
- **Annotation**: Major periods labeled

#### **3. Stationarity Tests**

**Augmented Dickey-Fuller Test**
- **Null**: Series has unit root (non-stationary)
- **Alternative**: Series is stationary
- **Output**: Test statistic, p-value, critical values

**KPSS Test**
- **Null**: Series is stationary
- **Complementary** to ADF test
- **Both pass**: Likely stationary

#### **4. Forecasting (Simple)**

**Methods Available**:
- **Naive**: Last value carries forward
- **Seasonal Naive**: Last season's value
- **Drift Method**: Linear trend
- **Simple Exponential Smoothing**

**Forecast Display**:
- Historical data (solid line)
- Forecast (dashed line)
- Confidence intervals (shaded)
- Forecast horizon selector (7-90 days)

---

## Advanced Analytics

### Features

#### **1. Outlier Detection**

**Methods**:
- **IQR Method**: 1.5 × IQR from quartiles
- **Z-Score Method**: |z| > 3
- **Isolation Forest**: ML-based
- **Local Outlier Factor**: Density-based

**Outlier Report**:
- Count by variable
- Percentage of total
- Most extreme values
- Outlier visualization

#### **2. Clustering Analysis**

**Customer/Product Segmentation**:
- **Variables**: Select features for clustering
- **Methods**:
  - K-means clustering
  - Hierarchical clustering
  - DBSCAN
- **Optimal Clusters**: Elbow method plot
- **Results**: 
  - Cluster assignments
  - Centroid characteristics
  - Cluster profiles

#### **3. Feature Engineering Suggestions**

**Automatic Detection**:
- High cardinality categoricals
- Datetime features to extract
- Interaction terms to create
- Transformations needed

**Generated Features**:
- Day of week/month
- Lag features
- Rolling statistics
- Categorical encodings

#### **4. Statistical Report Generator**

**One-Click Report**:
- Executive summary
- Key findings
- Statistical test results
- Visualizations
- Recommendations

**Export Options**:
- PDF report
- HTML interactive
- CSV data tables

---

# ML Predictions Page

## Overview (ML Predictions)

### Purpose
The ML Predictions page provides machine learning models for predictive analytics, enabling proactive decision-making in supply chain management.

### Access
- **Location**: Sidebar below main content
- **Icon**: 🤖
- **Label**: "ML Predictions"
- **Requirements**: scikit-learn, optionally prophet for advanced forecasting

### Page Structure
- **Sidebar**: Model training controls and status
- **Main Area**: Four tabs for different ML applications
- **Bottom**: Insights and recommendations summary

---

## Model Training

### Training Panel (Sidebar)

#### **Train All Models Button** 🚀
- **Purpose**: Train all available ML models
- **Process**:
  1. Late Delivery Model (~30 seconds)
  2. Demand Forecast Model (~20 seconds)
  3. Anomaly Detection Model (~15 seconds)
- **Total Time**: ~1-2 minutes depending on data size

#### **Model Status Indicators**
After training, shows status for each model:
- ✅ **Green Check**: Model trained successfully
- ⚠️ **Yellow Warning**: Model trained with warnings
- ❌ **Red X**: Model training failed

#### **Training Progress**
- **Spinner**: Shows during training
- **Status Messages**: Updates for each model
- **Error Messages**: Specific failure reasons

### Data Requirements
- **Minimum Records**: 100 shipments
- **Required Columns**: Varies by model
- **Data Quality**: Missing values handled automatically

---

## Late Delivery Prediction

### Model Overview
Predicts probability of shipments being delivered late using historical patterns.

### Features Used
The model automatically selects from:
- **Temporal Features**:
  - Day of week
  - Month
  - Quarter
  - Days since order
- **Categorical Features**:
  - Category
  - Source/Plant
  - Master Brand
  - Channel
- **Numerical Features**:
  - Historical plant performance
  - Distance/route metrics
  - Order size/quantity

### Model Performance Section

#### **1. Performance Metrics**

**Accuracy Score**
- **Display**: Large metric card
- **Format**: Percentage (e.g., "85.3%")
- **Interpretation**:
  - >90%: Excellent
  - 80-90%: Good
  - 70-80%: Acceptable
  - <70%: Needs improvement

**AUC Score (Area Under Curve)**
- **Range**: 0.5 to 1.0
- **Interpretation**:
  - 0.5: No better than random
  - 0.7-0.8: Acceptable
  - 0.8-0.9: Good
  - >0.9: Excellent

**Baseline Late Rate**
- **Shows**: Actual late percentage in data
- **Purpose**: Context for model performance
- **Comparison**: Model should beat naive baseline

#### **2. ROC Curve**

**Interactive Plot**:
- **X-axis**: False Positive Rate
- **Y-axis**: True Positive Rate
- **Diagonal Line**: Random classifier reference
- **Area Fill**: AUC visualization
- **Hover**: Shows threshold values

**Interpretation**:
- Curve closer to top-left = better
- More area under curve = better

#### **3. Feature Importance**

**Horizontal Bar Chart**:
- **Top 10 Features**: Most important for predictions
- **Score**: Relative importance (0-100%)
- **Color Coding**: 
  - Dark blue: Very important
  - Light blue: Less important

**Common Important Features**:
1. Plant/Source (historical performance)
2. Category (product type patterns)
3. Day of week (operational patterns)
4. Month (seasonal effects)
5. Route distance

#### **4. Confusion Matrix**

**2×2 Grid Display**:
```
                 Predicted
              On Time    Late
Actual  On Time  TN      FP
        Late     FN      TP
```

**Metrics Shown**:
- True Negatives (TN): Correctly predicted on-time
- False Positives (FP): Wrongly predicted late
- False Negatives (FN): Missed late deliveries
- True Positives (TP): Correctly predicted late

**Color Intensity**: Higher numbers = darker blue

### Current Shipments Risk Assessment

#### **Risk Scoring Process**
1. Filters recent/pending shipments
2. Applies trained model
3. Generates risk scores (0-1)
4. Flags high-risk shipments (>0.7)

#### **High-Risk Shipments Table**

**Columns**:
- **Category**: Product category
- **Master Brand**: Brand name
- **Source**: Shipping plant
- **SLS Plant**: Destination
- **Late Risk Score**: 0.0-1.0 (color-coded)
- **Delivery Status**: Current status

**Sorting**: Highest risk first
**Display Limit**: Top 20 shipments
**Color Scale**: Green (low) → Yellow → Red (high)

#### **Risk Interpretation**
- **0.0-0.3**: Low risk (green)
- **0.3-0.5**: Moderate risk (yellow)
- **0.5-0.7**: High risk (orange)
- **0.7-1.0**: Critical risk (red)

---

## Demand Forecasting

### Model Overview
Forecasts future shipment volumes using time series analysis and machine learning.

### Forecasting Methods

#### **Primary Method (Prophet)**
If available, uses Facebook Prophet for:
- Trend detection
- Seasonality modeling
- Holiday effects
- Uncertainty intervals

#### **Fallback Method**
Simple exponential smoothing for basic forecasting.

### Forecast Display

#### **1. Forecast Plot**

**Interactive Time Series Chart**:
- **Historical Data**: Solid blue line
- **Forecast**: Dashed blue line
- **Confidence Interval**: Light blue shaded area
- **Components**:
  - X-axis: Date
  - Y-axis: Number of shipments
  - Zoom: Click and drag
  - Pan: Shift + drag

**Interpretation**:
- Wider confidence bands = more uncertainty
- Trend direction indicates growth/decline
- Seasonal patterns visible as waves

#### **2. 30-Day Forecast Summary**

**Three Key Metrics**:

**Average Daily Forecast**
- **Calculation**: Mean of next 30 days
- **Format**: "245 shipments"
- **Use**: Capacity planning baseline

**Peak Day**
- **Shows**: Highest forecast day
- **Format**: "312 shipments on 2025-08-15"
- **Use**: Maximum capacity needs

**Total 30-Day Forecast**
- **Calculation**: Sum of 30 days
- **Format**: "7,350 shipments"
- **Use**: Total volume planning

#### **3. Weekly Forecast Breakdown**

**Table Format**:
| Week | Forecast | Lower Bound | Upper Bound |
|------|----------|-------------|-------------|
| 32   | 1,750    | 1,650       | 1,850       |
| 33   | 1,820    | 1,700       | 1,940       |
| 34   | 1,695    | 1,550       | 1,840       |
| 35   | 1,885    | 1,720       | 2,050       |

**Use Cases**:
- Staff scheduling
- Inventory planning
- Capacity allocation

#### **4. Seasonality Patterns**

**Weekly Seasonality**
- **Bar Chart**: Effect by day of week
- **Y-axis**: Impact on demand (± shipments)
- **Insights**:
  - Monday: Often higher (catch-up)
  - Friday: May be lower
  - Weekends: Depends on operations

**Monthly Seasonality**
- **Bar Chart**: Effect by month
- **Y-axis**: Impact on demand
- **Patterns**:
  - Ramadan effects
  - Summer variations
  - Year-end peaks

---

## Anomaly Detection

### Model Overview
Identifies unusual patterns and outliers in shipment data using unsupervised learning.

### Detection Methods

**Isolation Forest Algorithm**:
- Isolates anomalies instead of profiling normal points
- Works well with high-dimensional data
- No assumptions about data distribution

### Anomaly Statistics

#### **Summary Metrics**

**Total Anomalies Detected**
- **Count**: Absolute number
- **Updates**: After each training

**Anomaly Rate**
- **Calculation**: Anomalies / Total × 100
- **Normal Range**: 1-5%
- **Alert**: If > 5%

**Features Used**
- **Count**: Number of variables analyzed
- **Examples**: Delay days, quantity, route

#### **Anomaly Visualization**

**Scatter Plot**
- **Points**: Each shipment
- **Color**: 
  - Blue: Normal
  - Red: Anomaly
- **Size**: Anomaly score
- **Axes**: Principal components
- **Interactive**: Hover for details

### Anomaly Analysis

#### **1. Anomaly Summary by Category**

**Table Columns**:
- **Category**: Product category
- **Count**: Number of anomalies
- **Avg Delay Days**: For anomalous shipments
- **Avg Quantity**: For anomalous shipments

**Insights**:
- Categories with most anomalies
- Common characteristics
- Potential issues

#### **2. Sample Anomalous Shipments**

**Detailed Table** (Top 20 by anomaly score):
- **Category**: Product type
- **Master Brand**: Brand affected
- **Source**: Origin location
- **Delivery Status**: Current state
- **Delay Days**: Actual delay
- **Quantity**: Shipment size
- **Anomaly Score**: 0-1 scale

**Common Anomaly Patterns**:
- Extremely early deliveries
- Unusually large quantities
- Rare source-destination pairs
- Atypical delay patterns

#### **Use Cases**
1. **Quality Control**: Flag for review
2. **Fraud Detection**: Unusual patterns
3. **Process Issues**: Systematic problems
4. **Data Errors**: Impossible values

---

## Route Optimization

### Model Overview
Analyzes route performance to identify optimization opportunities.

### Optimization Scoring

**Score Calculation**:
```
Score = (Late Rate × 40) + (Avg Delay × 30) + (Volume Impact × 30)
```

**Components**:
- **Late Rate**: Percentage of late deliveries
- **Avg Delay**: Average days delayed
- **Volume Impact**: Total shipments affected

### Route Analysis Display

#### **1. Summary Metrics**

**Worst Performing Route**
- **Format**: "GEBZE → RIYADH"
- **Highlights**: Most problematic route

**Optimization Score**
- **Range**: 0-100
- **Interpretation**:
  - 0-30: Good performance
  - 30-50: Needs attention
  - 50-70: High priority
  - 70-100: Critical

**High Priority Routes**
- **Count**: Routes scoring > 50
- **Use**: Focus areas

#### **2. Route Optimization Heatmap**

**Matrix Visualization**:
- **Rows**: Source locations
- **Columns**: Destinations
- **Color**: Optimization score
- **Scale**: Green (good) to Red (poor)
- **Interactive**: Hover for details

**Patterns to Look For**:
- Red rows: Problematic sources
- Red columns: Difficult destinations
- Hot spots: Specific problem routes

#### **3. Top 10 Routes for Optimization**

**Detailed Table**:
| Route | Late Rate | Avg Delay | Volume | Score |
|-------|-----------|-----------|---------|--------|
| A → B | 68.5%     | 8.2 days  | 1,250   | 78.3   |
| C → D | 55.2%     | 6.5 days  | 2,100   | 65.7   |

**Formatting**:
- Percentages for rates
- Days for delays
- Comma-separated volumes
- Color-coded scores

#### **4. Optimization Recommendations**

**Automated Insights**:

**Priority 1 - Critical Routes** 🚨
- Routes with >50% late rate
- Specific source-destination pairs
- Suggested actions:
  - Alternative routing
  - Capacity increase
  - Express lanes

**Priority 2 - High Volume Impact** 📦
- High-volume routes with >30% late rate
- Affects most shipments
- Actions:
  - Dedicated resources
  - Schedule optimization
  - Load balancing

**Priority 3 - Persistent Delays** ⏱️
- Routes with average delay >5 days
- Consistent pattern
- Actions:
  - Transit time analysis
  - Stop reduction
  - Route redesign

---

## Model Insights

### Key Insights & Actions Section

Located at bottom of page after training models.

#### **Automated Insights Generation**

**Late Delivery Insights**:
- Model accuracy achievement
- Top predictive factors
- Risk concentration areas

**Demand Forecast Insights**:
- Trend direction (increasing/decreasing)
- Seasonal patterns detected
- Capacity requirements

**Anomaly Detection Insights**:
- Anomaly rate assessment
- Common anomaly types
- Investigation priorities

#### **Actionable Recommendations**

**Format**: Each insight includes:
- ✅ Success indicators
- 📈 Trend observations
- ⚠️ Warning conditions
- 💡 Suggested actions

**Examples**:
- "✅ Late delivery model 87% accurate - reliable for planning"
- "📈 Demand increasing 15% over next 30 days - prepare capacity"
- "⚠️ 6.2% anomaly rate detected - investigate unusual patterns"

---

# Technical Requirements

## Statistical Analysis Page

### Required Packages
```python
pandas >= 1.0.0
numpy >= 1.18.0
scipy >= 1.4.0  # For statistical tests
matplotlib >= 3.1.0  # For static plots (optional)
```

### Optional Enhancements
```python
seaborn >= 0.10.0  # Better statistical plots
statsmodels >= 0.11.0  # Advanced statistics
pingouin >= 0.3.0  # Statistical tests
```

## ML Predictions Page

### Required Packages
```python
scikit-learn >= 0.22.0  # Core ML functionality
pandas >= 1.0.0
numpy >= 1.18.0
```

### Optional Enhancements
```python
prophet >= 1.0  # Advanced forecasting
imbalanced-learn >= 0.7.0  # Handle imbalanced data
xgboost >= 1.0.0  # Better predictions
shap >= 0.35.0  # Model interpretability
```

## Performance Considerations

### Data Size Limits
- **Optimal**: < 100,000 records
- **Maximum**: ~ 1 million records
- **Training Time**: Increases with size

### Memory Usage
- **Base**: ~500 MB
- **With ML**: ~1-2 GB
- **Large datasets**: Up to 4 GB

### Browser Requirements
- **Chrome/Edge**: Recommended
- **Firefox**: Supported
- **Safari**: Basic support
- **RAM**: 4GB minimum, 8GB recommended

---

# Best Practices

## Statistical Analysis

### 1. **Start with Descriptive Stats**
- Understand data distribution
- Check for outliers
- Identify missing patterns

### 2. **Validate Assumptions**
- Test normality before t-tests
- Check independence
- Verify equal variances

### 3. **Multiple Testing Correction**
- Use Bonferroni for few tests
- FDR for many tests
- Report adjusted p-values

### 4. **Effect Size Matters**
- Statistical vs practical significance
- Report confidence intervals
- Consider sample size impact

## ML Predictions

### 1. **Regular Retraining**
- Weekly/monthly updates
- Monitor performance degradation
- Adjust for seasonality

### 2. **Validate Predictions**
- Compare to baselines
- Check on holdout data
- Monitor in production

### 3. **Interpret with Caution**
- Correlation ≠ causation
- Consider business context
- Validate surprising results

### 4. **Act on Insights**
- High-risk shipments: Proactive contact
- Demand spikes: Capacity planning
- Anomalies: Investigation triggers
- Route issues: Optimization projects

## Common Pitfalls to Avoid

### Statistical Analysis
1. **P-hacking**: Testing until significant
2. **Ignoring assumptions**: Invalid results
3. **Small sample conclusions**: Unreliable
4. **Missing confounders**: Wrong causation

### ML Predictions
1. **Overfitting**: Too complex models
2. **Data leakage**: Future information
3. **Class imbalance**: Biased predictions
4. **Blind trust**: Not validating

## Integration with Business Process

### Daily Operations
1. Check high-risk shipments
2. Review anomalies
3. Monitor KPIs

### Weekly Planning
1. Demand forecast review
2. Capacity adjustments
3. Route optimization

### Monthly Analysis
1. Retrain models
2. Statistical deep dives
3. Process improvements

### Quarterly Reviews
1. Model performance audit
2. Feature engineering
3. Strategy adjustments
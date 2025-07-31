"""
P&G Middle East Supply Chain Analytics Dashboard
Main Streamlit Application - FINAL FIXED VERSION
All critical and medium priority issues resolved
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
from utils.data_extractor import DataExtractor
from utils.data_processor import DataProcessor
from components.kpi_cards import display_kpi_row, display_secondary_kpis, create_alert_box
from components.charts import (
    create_delivery_status_pie, create_daily_trend_chart,
    create_category_performance_bar, create_plant_heatmap,
    create_brand_performance_sunburst, create_delay_distribution,
    create_sales_vs_target_gauge, create_waterfall_chart
)
import plotly.express as px
import plotly.graph_objects as go
from components.filters import (
    create_date_filter, create_multiselect_filters,
    apply_filters_to_data, create_filter_summary
)

# Configuration
class Config:
    LATE_RATE_WARNING = 35
    LATE_RATE_CRITICAL = 40
    MAX_DELAY_DAYS = 30
    DEFAULT_PAGE_SIZE = 20
    CACHE_TTL = 3600  # 1 hour

# Page configuration
st.set_page_config(
    page_title="P&G Supply Chain Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 0rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #666;
    }
    div[data-testid="metric-container"] > div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: bold;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.processor = None
    st.session_state.last_update = None

@st.cache_data(ttl=Config.CACHE_TTL)
def load_csv_data(file_path):
    """Cache CSV file reads"""
    return pd.read_csv(file_path)

def load_data():
    """Load and process data with proper error handling"""
    with st.spinner("Loading data..."):
        try:
            # Fixed: Check for directory and file separately
            extracted_dir = os.path.join(os.path.dirname(__file__), 'data', 'extracted')
            extracted_file = os.path.join(extracted_dir, 'shipping_main_data.csv')
            
            if not os.path.exists(extracted_file):
                st.info("First time setup: Extracting data from Excel files...")
                logger.info("Extracting data from Excel files")
                
                # Get parent directory (ExcelProblem)
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                # Validate Excel files exist
                excel_file1 = os.path.join(parent_dir, "2-JPG shipping tracking - July 2025.xlsx")
                excel_file2 = os.path.join(parent_dir, "3-DSR-PG- 2025 July.xlsx")
                
                if not os.path.exists(excel_file1) or not os.path.exists(excel_file2):
                    st.error("Excel files not found in parent directory")
                    st.error("Please ensure these files exist:")
                    st.error(f"- {excel_file1}")
                    st.error(f"- {excel_file2}")
                    return False
                
                # Extract data
                extractor = DataExtractor(
                    file1_path=excel_file1,
                    file2_path=excel_file2
                )
                
                # Create directory if it doesn't exist
                os.makedirs(extracted_dir, exist_ok=True)
                extractor.save_extracted_data(output_dir=extracted_dir)
                logger.info("Data extraction completed")
            
            # Load processed data
            processor = DataProcessor()
            processor.load_processed_data(data_dir=extracted_dir)
            
            st.session_state.processor = processor
            st.session_state.data_loaded = True
            st.session_state.last_update = datetime.now()
            
            logger.info("Data loaded successfully")
            return True
            
        except FileNotFoundError as e:
            st.error(f"File not found: {str(e)}")
            logger.error(f"File not found: {str(e)}")
            return False
        except PermissionError as e:
            st.error("Permission denied. Please check file permissions.")
            logger.error(f"Permission error: {str(e)}")
            return False
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            logger.error(f"Error loading data: {str(e)}")
            return False

def safe_datetime_comparison(date1, date2):
    """Safely compare two datetime objects handling timezone issues"""
    # Convert to timezone-naive if needed
    if hasattr(date1, 'tz_localize'):
        date1 = date1.tz_localize(None)
    if hasattr(date2, 'tz_localize'):
        date2 = date2.tz_localize(None)
    
    # Handle pandas Timestamp
    if isinstance(date1, pd.Timestamp):
        date1 = date1.to_pydatetime().replace(tzinfo=None)
    if isinstance(date2, pd.Timestamp):
        date2 = date2.to_pydatetime().replace(tzinfo=None)
    
    return date1, date2

def main():
    """Main application function with error boundary"""
    try:
        # Header with dynamic date
        st.title("🚚 P&G Middle East Supply Chain Analytics")
        current_month = datetime.now().strftime("%B %Y")
        st.markdown(f"### Real-time Performance Dashboard - {current_month}")
        
        # Sidebar
        with st.sidebar:
            # Fixed: Specific exception handling for logo
            try:
                st.image("https://www.pg.com/assets/images/Header_P&G_Logo.svg", width=150)
            except Exception as e:
                st.markdown("### P&G")
                logger.warning(f"Could not load P&G logo: {str(e)}")
            
            st.markdown("---")
            
            # Navigation
            page = st.selectbox(
                "Select Dashboard",
                ["Executive Summary", "Shipping Performance", "Sales Analytics", 
                 "Product Analysis", "Predictive Insights", "Data Quality"]
            )
            
            st.markdown("---")
            
            # Data refresh
            if st.button("🔄 Refresh Data"):
                st.session_state.data_loaded = False
                st.cache_data.clear()  # Clear cache on refresh
                st.rerun()
            
            if st.session_state.last_update:
                st.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}")
        
        # Load data if not loaded
        if not st.session_state.data_loaded:
            if not load_data():
                st.stop()
        
        processor = st.session_state.processor
        
        # Validate processor has data
        if processor is None or processor.shipping_data is None:
            st.error("No data available. Please check your data files.")
            st.stop()
        
        # Filters section
        st.markdown("### 🔍 Filters")
        with st.expander("Filter Options", expanded=True):
            # Date filter
            date_range = create_date_filter(processor.shipping_data)
            
            # Other filters
            filters = create_multiselect_filters(processor.shipping_data)
            
            # Apply filters
            filtered_data = apply_filters_to_data(processor.shipping_data, filters, date_range)
            
            # Filter summary
            create_filter_summary(filters, date_range)
        
        # Calculate KPIs on filtered data
        # Create a temporary processor for filtered data
        filtered_processor = DataProcessor()
        filtered_processor.shipping_data = filtered_data.copy()  # Use copy to avoid mutations
        filtered_processor.sales_data = processor.sales_data
        
        # Check if we have data before calculating KPIs
        if len(filtered_data) == 0:
            st.warning("No data matches the selected filters. Please adjust your filters.")
            st.stop()
        
        kpis = filtered_processor.calculate_kpis()
        
        # Page content based on selection
        if page == "Executive Summary":
            show_executive_summary(filtered_processor, kpis)
        elif page == "Shipping Performance":
            show_shipping_performance(filtered_processor, filtered_data)
        elif page == "Sales Analytics":
            show_sales_analytics(filtered_processor)
        elif page == "Product Analysis":
            show_product_analysis(filtered_processor, filtered_data)
        elif page == "Predictive Insights":
            show_predictive_insights(filtered_processor, filtered_data)
        elif page == "Data Quality":
            show_data_quality(processor, filtered_data)
            
    except Exception as e:
        st.error("An unexpected error occurred. Please refresh the page.")
        logger.error(f"Unexpected error in main: {str(e)}", exc_info=True)
        if st.button("Show Error Details"):
            st.exception(e)

def show_executive_summary(processor, kpis):
    """Display executive summary dashboard with proper error handling"""
    st.markdown("## 📊 Executive Summary")
    
    # Alerts section using configuration
    if kpis.get('late_rate', 0) > Config.LATE_RATE_CRITICAL:
        create_alert_box(
            "Critical Alert",
            f"Late delivery rate ({kpis['late_rate']}%) exceeds critical threshold of {Config.LATE_RATE_CRITICAL}%",
            "error"
        )
    elif kpis.get('late_rate', 0) > Config.LATE_RATE_WARNING:
        create_alert_box(
            "Warning",
            f"Late delivery rate ({kpis['late_rate']}%) is above target of 30%",
            "warning"
        )
    
    # KPI Cards
    st.markdown("### Key Performance Indicators")
    display_kpi_row(kpis)
    
    st.markdown("### Secondary Metrics")
    display_secondary_kpis(kpis)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Fixed: Use filtered data for pie chart
        if not processor.shipping_data.empty:
            fig = create_delivery_status_pie(processor.shipping_data)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sales achievement gauge
        fig = create_sales_vs_target_gauge(kpis.get('sales_achievement', 0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Daily trend
    daily_data = processor.get_time_series_data()
    if not daily_data.empty:
        fig = create_daily_trend_chart(daily_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Category performance
    category_data = processor.get_category_analysis()
    if not category_data.empty:
        fig = create_category_performance_bar(category_data)
        st.plotly_chart(fig, use_container_width=True)

def show_shipping_performance(processor, data):
    """Display shipping performance dashboard with validation"""
    st.markdown("## 🚚 Shipping Performance Analysis")
    
    # Validate data
    if data.empty:
        st.warning("No shipping data available")
        return
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Plant Analysis", "Time Analysis", "Pivot Recreation"])
    
    with tab1:
        # Waterfall chart
        try:
            fig = create_waterfall_chart(data)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error("Could not create waterfall chart")
            logger.error(f"Waterfall chart error: {str(e)}")
        
        # Delay distribution
        if 'Delay_Days' in data.columns and len(data[data['Delivery_Status'] == 'Late']) > 0:
            try:
                fig = create_delay_distribution(data)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error("Could not create delay distribution")
                logger.error(f"Delay distribution error: {str(e)}")
    
    with tab2:
        # Plant performance
        plant_perf = processor.get_plant_performance() if hasattr(processor, 'get_plant_performance') else pd.DataFrame()
        if not plant_perf.empty:
            try:
                st.dataframe(plant_perf.style.background_gradient(subset=['Late_Rate'], cmap='RdYlGn_r'))
            except ImportError:
                st.dataframe(plant_perf)
            except Exception as e:
                st.dataframe(plant_perf)
                logger.warning(f"Could not apply styling: {str(e)}")
        
        # Plant heatmap
        if len(data) > 0:
            try:
                fig = create_plant_heatmap(data)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error("Could not create plant heatmap")
                logger.error(f"Plant heatmap error: {str(e)}")
    
    with tab3:
        # Time-based analysis
        st.markdown("### Shipping Patterns by Day of Week")
        if 'Actual_Ship_Date' in data.columns:
            try:
                data_copy = data.copy()
                # Fixed: Check if datetime conversion needed
                if not pd.api.types.is_datetime64_any_dtype(data_copy['Actual_Ship_Date']):
                    data_copy['Actual_Ship_Date'] = pd.to_datetime(data_copy['Actual_Ship_Date'], errors='coerce')
                
                # Remove any NaT values
                data_copy = data_copy.dropna(subset=['Actual_Ship_Date'])
                
                if not data_copy.empty:
                    data_copy['Day_of_Week'] = data_copy['Actual_Ship_Date'].dt.day_name()
                    dow_analysis = data_copy.groupby(['Day_of_Week', 'Delivery_Status']).size().unstack(fill_value=0)
                    if not dow_analysis.empty:
                        st.bar_chart(dow_analysis)
                    else:
                        st.info("No data available for day of week analysis")
            except Exception as e:
                st.error("Could not create day of week analysis")
                logger.error(f"Day of week analysis error: {str(e)}")
        
        st.markdown("### Monthly Trends")
        if 'Actual_Ship_Date' in data.columns:
            try:
                data_copy = data.copy()
                if not pd.api.types.is_datetime64_any_dtype(data_copy['Actual_Ship_Date']):
                    data_copy['Actual_Ship_Date'] = pd.to_datetime(data_copy['Actual_Ship_Date'], errors='coerce')
                
                data_copy = data_copy.dropna(subset=['Actual_Ship_Date'])
                
                if not data_copy.empty:
                    # Fixed: Handle timezone-aware dates
                    data_copy['Month_Year'] = data_copy['Actual_Ship_Date'].dt.to_period('M').astype(str)
                    monthly_trend = data_copy.groupby(['Month_Year', 'Delivery_Status']).size().unstack(fill_value=0)
                    if not monthly_trend.empty:
                        st.line_chart(monthly_trend)
                    else:
                        st.info("No data available for monthly trends")
            except Exception as e:
                st.error("Could not create monthly trends")
                logger.error(f"Monthly trends error: {str(e)}")
    
    with tab4:
        # Recreate original pivot structure
        st.markdown("### Original Excel Pivot Recreation")
        st.info("This recreates the pivot table structure from columns P-U in the original file")
        
        # Create pivot with validation
        required_cols = ['Category', 'Master_Brand', 'Brand', 'Source', 'Quantity']
        if len(data) > 0 and all(col in data.columns for col in required_cols):
            try:
                pivot = pd.pivot_table(
                    data,
                    index=['Category', 'Master_Brand', 'Brand'],
                    columns='Source',
                    values='Quantity',
                    aggfunc='sum',
                    fill_value=0
                )
                
                # Fixed: Wrap style operation in try-except
                try:
                    st.dataframe(pivot.style.format("{:,.0f}"))
                except Exception:
                    st.dataframe(pivot)
            except Exception as e:
                st.error("Could not create pivot table")
                logger.error(f"Pivot table error: {str(e)}")
        else:
            missing_cols = [col for col in required_cols if col not in data.columns]
            st.warning(f"Cannot create pivot table. Missing columns: {missing_cols}")

def show_sales_analytics(processor):
    """Display sales analytics dashboard with proper validation"""
    st.markdown("## 💰 Sales Analytics")
    
    # Channel analysis
    if hasattr(processor, 'get_sales_channel_analysis'):
        try:
            channel_analysis = processor.get_sales_channel_analysis()
            if not channel_analysis.empty:
                st.markdown("### Channel Performance")
                
                col1, col2 = st.columns(2)
                with col1:
                    try:
                        st.dataframe(channel_analysis.style.background_gradient(subset=['Achievement'], cmap='RdYlGn'))
                    except ImportError:
                        st.dataframe(channel_analysis)
                    except Exception:
                        st.dataframe(channel_analysis)
                
                with col2:
                    # Channel comparison chart
                    fig = px.bar(
                        channel_analysis.reset_index(),
                        x='Channel',
                        y=['Sales', 'Target'],
                        barmode='group',
                        title="Sales vs Target by Channel"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error("Could not load channel analysis")
            logger.error(f"Channel analysis error: {str(e)}")
    
    # Forecast accuracy
    if hasattr(processor, 'calculate_forecast_accuracy'):
        try:
            forecast_accuracy = processor.calculate_forecast_accuracy()
            if not forecast_accuracy.empty:
                st.markdown("### Forecast Accuracy by Category")
                fig = px.bar(
                    x=forecast_accuracy.index,
                    y=forecast_accuracy.values,
                    title="Forecast Accuracy %",
                    labels={'x': 'Category', 'y': 'Accuracy %'}
                )
                fig.add_hline(y=90, line_dash="dash", annotation_text="Target: 90%")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error("Could not calculate forecast accuracy")
            logger.error(f"Forecast accuracy error: {str(e)}")
    
    # Top products
    if hasattr(processor, 'get_top_products'):
        try:
            st.markdown("### Top 10 Products by Late Deliveries")
            top_products = processor.get_top_products(n=10, metric='Late')
            if not top_products.empty:
                st.dataframe(top_products)
            else:
                st.info("No product data available")
        except Exception as e:
            st.error("Could not load top products")
            logger.error(f"Top products error: {str(e)}")

def show_product_analysis(processor, data):
    """Display product analysis dashboard with validation"""
    st.markdown("## 📦 Product Analysis")
    
    # Validate data
    if data.empty:
        st.warning("No product data available")
        return
    
    # Brand performance sunburst
    if len(data) > 0:
        try:
            fig = create_brand_performance_sunburst(data)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error("Could not create brand performance chart")
            logger.error(f"Brand sunburst error: {str(e)}")
    
    # Brand analysis table
    if hasattr(processor, 'get_brand_analysis'):
        try:
            brand_analysis = processor.get_brand_analysis()
            if not brand_analysis.empty:
                st.markdown("### Brand Performance Metrics")
                try:
                    st.dataframe(
                        brand_analysis.head(20).style.background_gradient(subset=['Late_Rate'], cmap='RdYlGn_r')
                    )
                except ImportError:
                    st.dataframe(brand_analysis.head(20))
                except Exception:
                    st.dataframe(brand_analysis.head(20))
        except Exception as e:
            st.error("Could not load brand analysis")
            logger.error(f"Brand analysis error: {str(e)}")
    
    # SKU level analysis
    st.markdown("### SKU Level Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox("Select Metric", ["Late", "Quantity", "Late Rate"])
    with col2:
        # Fixed: Validate slider max value
        max_products = min(50, len(data['Planning_Level'].unique()) if 'Planning_Level' in data.columns else 50)
        n_products = st.slider("Number of Products", 5, max_products, min(20, max_products))
    
    if hasattr(processor, 'get_top_products'):
        try:
            top_skus = processor.get_top_products(n=n_products, metric=metric)
            if not top_skus.empty:
                st.dataframe(top_skus)
            else:
                st.info("No SKU data available")
        except Exception as e:
            st.error("Could not load SKU analysis")
            logger.error(f"SKU analysis error: {str(e)}")

def show_predictive_insights(processor, data):
    """Display predictive insights dashboard with validation"""
    st.markdown("## 🔮 Predictive Insights")
    
    st.info("This section contains predictive analytics and ML models")
    
    # Placeholder for ML predictions
    st.markdown("### Late Delivery Risk Prediction")
    st.markdown("Coming soon: ML model to predict shipments at risk of being late")
    
    # Simple trend projection
    st.markdown("### Trend Projection")
    try:
        daily_trend = processor.get_time_series_data()
        if not daily_trend.empty and 'Late_Rate' in daily_trend.columns:
            # Filter out NaN values
            daily_trend = daily_trend[daily_trend['Late_Rate'].notna()]
            
            if len(daily_trend) > 7:  # Need at least 7 days for MA
                # Simple moving average projection
                ma_7 = daily_trend['Late_Rate'].rolling(7, min_periods=1).mean()
                ma_30 = daily_trend['Late_Rate'].rolling(30, min_periods=1).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=daily_trend.index, y=daily_trend['Late_Rate'], 
                                        name='Actual', mode='lines'))
                fig.add_trace(go.Scatter(x=daily_trend.index, y=ma_7, 
                                        name='7-day MA', mode='lines'))
                if len(daily_trend) > 30:
                    fig.add_trace(go.Scatter(x=daily_trend.index, y=ma_30, 
                                            name='30-day MA', mode='lines'))
                
                fig.update_layout(title="Late Rate Trend Analysis", 
                                 xaxis_title="Date", yaxis_title="Late Rate %")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient data for trend analysis (need at least 7 days)")
        else:
            st.info("No time series data available for trend analysis")
    except Exception as e:
        st.error("Could not create trend projection")
        logger.error(f"Trend projection error: {str(e)}")

def show_data_quality(processor, filtered_data):
    """Display data quality monitoring dashboard with improved validation"""
    st.markdown("## 🔍 Data Quality Monitoring")
    
    # Validate input
    if filtered_data.empty:
        st.warning("No data available for quality analysis")
        return
    
    # Data completeness
    st.markdown("### Data Completeness")
    
    try:
        # Fixed: Handle division by zero
        total_rows = max(len(filtered_data), 1)
        completeness = pd.DataFrame({
            'Column': filtered_data.columns,
            'Non_Null_Count': filtered_data.count(),
            'Null_Count': filtered_data.isnull().sum(),
            'Completeness_%': (filtered_data.count() / total_rows * 100).round(1)
        })
        
        try:
            st.dataframe(
                completeness.style.background_gradient(subset=['Completeness_%'], cmap='RdYlGn')
            )
        except ImportError:
            st.dataframe(completeness)
        except Exception:
            st.dataframe(completeness)
    except Exception as e:
        st.error("Could not calculate data completeness")
        logger.error(f"Data completeness error: {str(e)}")
    
    # Data validation checks
    st.markdown("### Data Validation Checks")
    
    checks = []
    
    # Check 1: Future dates
    if 'Actual_Ship_Date' in filtered_data.columns:
        try:
            # Ensure datetime format
            ship_dates = pd.to_datetime(filtered_data['Actual_Ship_Date'], errors='coerce')
            future_dates = (ship_dates > datetime.now()).sum()
            checks.append({
                'Check': 'No future ship dates',
                'Status': '✅ Pass' if future_dates == 0 else f'❌ Fail ({future_dates} found)',
                'Severity': 'High'
            })
        except Exception as e:
            logger.error(f"Future date check error: {str(e)}")
    
    # Check 2: Negative delays
    if 'Delay_Days' in filtered_data.columns:
        try:
            extreme_negative = filtered_data[filtered_data['Delay_Days'] < -Config.MAX_DELAY_DAYS].shape[0]
            checks.append({
                'Check': f'No extreme negative delays (< -{Config.MAX_DELAY_DAYS} days)',
                'Status': '✅ Pass' if extreme_negative == 0 else f'⚠️ Warning ({extreme_negative} found)',
                'Severity': 'Medium'
            })
        except Exception as e:
            logger.error(f"Negative delay check error: {str(e)}")
    
    # Check 3: Valid delivery status
    if 'Delivery_Status' in filtered_data.columns:
        try:
            valid_statuses = ['Advanced', 'Late', 'On Time', 'Not Due']
            invalid_status = filtered_data[~filtered_data['Delivery_Status'].isin(valid_statuses)].shape[0]
            checks.append({
                'Check': 'All delivery statuses are valid',
                'Status': '✅ Pass' if invalid_status == 0 else f'❌ Fail ({invalid_status} invalid)',
                'Severity': 'High'
            })
        except Exception as e:
            logger.error(f"Delivery status check error: {str(e)}")
    
    # Check 4: Duplicate records
    try:
        duplicate_cols = ['Planning_Level', 'Actual_Ship_Date', 'Source']
        if all(col in filtered_data.columns for col in duplicate_cols):
            duplicates = filtered_data.duplicated(subset=duplicate_cols).sum()
            checks.append({
                'Check': 'No duplicate shipments',
                'Status': '✅ Pass' if duplicates == 0 else f'⚠️ Warning ({duplicates} duplicates)',
                'Severity': 'Medium'
            })
    except Exception as e:
        logger.error(f"Duplicate check error: {str(e)}")
    
    if checks:
        checks_df = pd.DataFrame(checks)
        st.dataframe(checks_df)
    
    # Data freshness
    st.markdown("### Data Freshness")
    if 'Actual_Ship_Date' in filtered_data.columns and len(filtered_data) > 0:
        try:
            # Fixed: Handle timezone-aware dates properly
            ship_dates = pd.to_datetime(filtered_data['Actual_Ship_Date'], errors='coerce')
            valid_dates = ship_dates.dropna()
            
            if len(valid_dates) > 0:
                latest_date = valid_dates.max()
                
                # Safe datetime comparison
                current_time, latest_time = safe_datetime_comparison(datetime.now(), latest_date)
                days_old = (current_time - latest_time).days
                
                if days_old < 2:
                    st.success(f"✅ Data is current (last shipment: {latest_time.strftime('%Y-%m-%d')})")
                elif days_old < 7:
                    st.warning(f"⚠️ Data is {days_old} days old (last shipment: {latest_time.strftime('%Y-%m-%d')})")
                else:
                    st.error(f"❌ Data is {days_old} days old (last shipment: {latest_time.strftime('%Y-%m-%d')})")
            else:
                st.warning("No valid dates found in the data")
        except Exception as e:
            st.error("Could not determine data freshness")
            logger.error(f"Data freshness error: {str(e)}")

if __name__ == "__main__":
    main()
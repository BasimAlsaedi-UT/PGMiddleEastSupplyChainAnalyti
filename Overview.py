"""
P&G Middle East Supply Chain Analytics Dashboard
Main Streamlit Application - FIXED VERSION
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
from utils.data_extractor import DataExtractor
from utils.data_processor import DataProcessor

# Try to import cloud data loader for Streamlit deployment
try:
    from cloud_data_loader import load_cloud_data, save_cloud_data_locally
    CLOUD_DEPLOYMENT = True
except ImportError:
    CLOUD_DEPLOYMENT = False
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

def load_data():
    """Load and process data"""
    with st.spinner("Loading data..."):
        try:
            # Check if we need to extract data first
            extracted_file = os.path.join(os.path.dirname(__file__), 'data', 'extracted', 'shipping_main_data.csv')
            if not os.path.exists(extracted_file):
                st.info("First time setup: Extracting data from Excel files...")
                
                # Get parent directory
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                # Try cloud deployment first
                if CLOUD_DEPLOYMENT and hasattr(st, 'secrets'):
                    shipping_data, sales_data = load_cloud_data()
                    if shipping_data is not None and sales_data is not None:
                        # Save cloud data as local Excel files
                        if save_cloud_data_locally(shipping_data, sales_data, parent_dir):
                            st.success("Loaded data from cloud storage")
                
                # Extract data from Excel files
                file1_path = os.path.join(parent_dir, "2-JPG shipping tracking - July 2025.xlsx")
                file2_path = os.path.join(parent_dir, "3-DSR-PG- 2025 July.xlsx")
                
                # Check if files exist
                if not os.path.exists(file1_path) or not os.path.exists(file2_path):
                    if CLOUD_DEPLOYMENT:
                        st.error("Data files not found. Please configure data in Streamlit secrets.")
                        st.stop()
                    else:
                        st.error("Excel files not found in parent directory.")
                        st.stop()
                
                extractor = DataExtractor(file1_path=file1_path, file2_path=file2_path)
                extractor.save_extracted_data(output_dir=os.path.join(os.path.dirname(__file__), 'data', 'extracted'))
            
            # Load processed data
            processor = DataProcessor()
            processor.load_processed_data(data_dir=os.path.join(os.path.dirname(__file__), 'data', 'extracted'))
            
            st.session_state.processor = processor
            st.session_state.data_loaded = True
            st.session_state.last_update = datetime.now()
            
            return True
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.error("Please ensure the Excel files are in the parent directory.")
            return False

def main():
    # Header
    st.title("🚚 P&G Middle East Supply Chain Analytics")
    st.markdown("### Real-time Performance Dashboard - July 2025")
    
    # Sidebar
    with st.sidebar:
        # Try to load P&G logo, fallback to text if fails
        try:
            st.image("https://www.pg.com/assets/images/Header_P&G_Logo.svg", width=150)
        except Exception:
            st.markdown("### P&G")
        
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
            st.rerun()
        
        if st.session_state.last_update:
            st.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M')}")
    
    # Load data if not loaded
    if not st.session_state.data_loaded:
        if not load_data():
            st.stop()
    
    processor = st.session_state.processor
    
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
    filtered_processor.shipping_data = filtered_data
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

def show_executive_summary(processor, kpis):
    """Display executive summary dashboard"""
    st.markdown("## 📊 Executive Summary")
    
    # Alerts section
    if kpis['late_rate'] > 40:
        create_alert_box(
            "Critical Alert",
            f"Late delivery rate ({kpis['late_rate']}%) exceeds critical threshold of 40%",
            "error"
        )
    elif kpis['late_rate'] > 35:
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
        # Delivery status pie chart
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
    """Display shipping performance dashboard"""
    st.markdown("## 🚚 Shipping Performance Analysis")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Plant Analysis", "Time Analysis", "Pivot Recreation"])
    
    with tab1:
        # Waterfall chart
        fig = create_waterfall_chart(data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Delay distribution
        if 'Delay_Days' in data.columns and len(data[data['Delivery_Status'] == 'Late']) > 0:
            fig = create_delay_distribution(data)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Plant performance
        plant_perf = processor.get_plant_performance()
        if not plant_perf.empty:
            try:
                st.dataframe(plant_perf.style.background_gradient(subset=['Late_Rate'], cmap='RdYlGn_r'))
            except (ImportError, AttributeError):
                st.dataframe(plant_perf)
        
        # Plant heatmap
        if len(data) > 0:
            fig = create_plant_heatmap(data)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Time-based analysis
        st.markdown("### Shipping Patterns by Day of Week")
        if 'Actual_Ship_Date' in data.columns:
            data_copy = data.copy()
            data_copy['Day_of_Week'] = pd.to_datetime(data_copy['Actual_Ship_Date']).dt.day_name()
            dow_analysis = data_copy.groupby(['Day_of_Week', 'Delivery_Status']).size().unstack(fill_value=0)
            if not dow_analysis.empty:
                st.bar_chart(dow_analysis)
        
        st.markdown("### Monthly Trends")
        if 'Actual_Ship_Date' in data.columns:
            data_copy = data.copy()
            data_copy['Month_Year'] = pd.to_datetime(data_copy['Actual_Ship_Date']).dt.to_period('M')
            monthly_trend = data_copy.groupby(['Month_Year', 'Delivery_Status']).size().unstack(fill_value=0)
            if not monthly_trend.empty:
                st.line_chart(monthly_trend)
    
    with tab4:
        # Recreate original pivot structure
        st.markdown("### Original Excel Pivot Recreation")
        st.info("This recreates the pivot table structure from columns P-U in the original file")
        
        # Create pivot - FIXED: Using pandas pivot_table directly
        if len(data) > 0 and all(col in data.columns for col in ['Category', 'Master_Brand', 'Brand', 'Source', 'Quantity']):
            pivot = pd.pivot_table(
                data,
                index=['Category', 'Master_Brand', 'Brand'],
                columns='Source',
                values='Quantity',
                aggfunc='sum',
                fill_value=0
            )
            
            st.dataframe(pivot.style.format("{:,.0f}"))
        else:
            st.warning("Insufficient data for pivot table creation")

def show_sales_analytics(processor):
    """Display sales analytics dashboard"""
    st.markdown("## 💰 Sales Analytics")
    
    # Channel analysis
    channel_analysis = processor.get_sales_channel_analysis()
    if not channel_analysis.empty:
            st.markdown("### Channel Performance")
            
            col1, col2 = st.columns(2)
            with col1:
                try:
                    st.dataframe(channel_analysis.style.background_gradient(subset=['Achievement'], cmap='RdYlGn'))
                except (ImportError, AttributeError):
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
    
    # Forecast accuracy
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
    
    # Top products
    st.markdown("### Top 10 Products by Late Deliveries")
    top_products = processor.get_top_products(n=10, metric='Late')
    if not top_products.empty:
        st.dataframe(top_products)

def show_product_analysis(processor, data):
    """Display product analysis dashboard"""
    st.markdown("## 📦 Product Analysis")
    
    # Brand performance sunburst
    if len(data) > 0:
        fig = create_brand_performance_sunburst(data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Brand analysis table
    brand_analysis = processor.get_brand_analysis()
    if not brand_analysis.empty:
            st.markdown("### Brand Performance Metrics")
            try:
                st.dataframe(
                    brand_analysis.head(20).style.background_gradient(subset=['Late_Rate'], cmap='RdYlGn_r')
                )
            except (ImportError, AttributeError):
                st.dataframe(brand_analysis.head(20))
    
    # SKU level analysis
    st.markdown("### SKU Level Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox("Select Metric", ["Late", "Quantity", "Late Rate"])
    with col2:
        n_products = st.slider("Number of Products", 5, 50, 20)
    
    top_skus = processor.get_top_products(n=n_products, metric=metric)
    if not top_skus.empty:
        st.dataframe(top_skus)

def show_predictive_insights(processor, data):
    """Display predictive insights dashboard"""
    st.markdown("## 🔮 Predictive Insights")
    
    st.info("This section contains predictive analytics and ML models")
    
    # Placeholder for ML predictions
    st.markdown("### Late Delivery Risk Prediction")
    st.markdown("Coming soon: ML model to predict shipments at risk of being late")
    
    # Simple trend projection
    st.markdown("### Trend Projection")
    daily_trend = processor.get_time_series_data()
    if not daily_trend.empty and 'Late_Rate' in daily_trend.columns:
        # Simple moving average projection
        ma_7 = daily_trend['Late_Rate'].rolling(7).mean()
        ma_30 = daily_trend['Late_Rate'].rolling(30).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_trend.index, y=daily_trend['Late_Rate'], 
                                name='Actual', mode='lines'))
        fig.add_trace(go.Scatter(x=daily_trend.index, y=ma_7, 
                                name='7-day MA', mode='lines'))
        fig.add_trace(go.Scatter(x=daily_trend.index, y=ma_30, 
                                name='30-day MA', mode='lines'))
        
        fig.update_layout(title="Late Rate Trend Analysis", 
                         xaxis_title="Date", yaxis_title="Late Rate %")
        st.plotly_chart(fig, use_container_width=True)

def show_data_quality(processor, filtered_data):
    """Display data quality monitoring dashboard"""
    st.markdown("## 🔍 Data Quality Monitoring")
    
    # Data completeness
    st.markdown("### Data Completeness")
    
    completeness = pd.DataFrame({
        'Column': filtered_data.columns,
        'Non_Null_Count': filtered_data.count(),
        'Null_Count': filtered_data.isnull().sum(),
        'Completeness_%': (filtered_data.count() / len(filtered_data) * 100).round(1)
    })
    
    try:
        st.dataframe(
            completeness.style.background_gradient(subset=['Completeness_%'], cmap='RdYlGn')
        )
    except (ImportError, AttributeError):
        st.dataframe(completeness)
    
    # Data validation checks
    st.markdown("### Data Validation Checks")
    
    checks = []
    
    # Check 1: Future dates
    if 'Actual_Ship_Date' in filtered_data.columns:
        future_dates = filtered_data[filtered_data['Actual_Ship_Date'] > datetime.now()].shape[0]
        checks.append({
            'Check': 'No future ship dates',
            'Status': '✅ Pass' if future_dates == 0 else f'❌ Fail ({future_dates} found)',
            'Severity': 'High'
        })
    
    # Check 2: Negative delays
    if 'Delay_Days' in filtered_data.columns:
        negative_delays = filtered_data[filtered_data['Delay_Days'] < -30].shape[0]
        checks.append({
            'Check': 'No extreme negative delays (< -30 days)',
            'Status': '✅ Pass' if negative_delays == 0 else f'⚠️ Warning ({negative_delays} found)',
            'Severity': 'Medium'
        })
    
    # Check 3: Valid delivery status
    if 'Delivery_Status' in filtered_data.columns:
        valid_statuses = ['Advanced', 'Late', 'On Time', 'Not Due']
        invalid_status = filtered_data[~filtered_data['Delivery_Status'].isin(valid_statuses)].shape[0]
        checks.append({
            'Check': 'All delivery statuses are valid',
            'Status': '✅ Pass' if invalid_status == 0 else f'❌ Fail ({invalid_status} invalid)',
            'Severity': 'High'
        })
    
    if checks:
        checks_df = pd.DataFrame(checks)
        st.dataframe(checks_df)
    
    # Data freshness - FIXED: Removed unnecessary pd.to_datetime conversion
    st.markdown("### Data Freshness")
    if 'Actual_Ship_Date' in filtered_data.columns and len(filtered_data) > 0:
        latest_date = filtered_data['Actual_Ship_Date'].max()
        if pd.notna(latest_date):
            days_old = (datetime.now() - latest_date).days
            
            if days_old < 2:
                st.success(f"✅ Data is current (last shipment: {latest_date.strftime('%Y-%m-%d')})")
            elif days_old < 7:
                st.warning(f"⚠️ Data is {days_old} days old (last shipment: {latest_date.strftime('%Y-%m-%d')})")
            else:
                st.error(f"❌ Data is {days_old} days old (last shipment: {latest_date.strftime('%Y-%m-%d')})")

if __name__ == "__main__":
    main()
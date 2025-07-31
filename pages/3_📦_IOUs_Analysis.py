"""
IOUs (Outstanding Orders) Analysis Page
Implements the missing Excel feature for tracking outstanding orders
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import DataProcessor

st.set_page_config(
    page_title="IOUs Analysis - P&G Analytics",
    page_icon="📦",
    layout="wide"
)

st.title("📦 IOUs (Outstanding Orders) Analysis")
st.markdown("Track and analyze outstanding orders across channels and categories")

# Load data
@st.cache_resource
def load_data():
    processor = DataProcessor()
    processor.load_processed_data()
    return processor

processor = load_data()

# Check if IOUs data is available
if processor.sales_data is None or 'IOUs' not in processor.sales_data.columns:
    st.error("IOUs data not available. Please ensure the sales data contains IOUs column.")
    st.stop()

# Calculate IOU metrics
total_ious = processor.sales_data['IOUs'].sum()
total_sales = processor.sales_data['Sales'].sum()
iou_rate = (total_ious / total_sales * 100) if total_sales > 0 else 0

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Outstanding Orders",
        f"{total_ious:,.0f}",
        help="Total IOUs across all channels"
    )

with col2:
    st.metric(
        "IOU Rate",
        f"{iou_rate:.1f}%",
        delta=f"of total sales",
        help="IOUs as percentage of total sales"
    )

with col3:
    avg_iou = processor.sales_data['IOUs'].mean()
    st.metric(
        "Average IOU per SKU",
        f"{avg_iou:,.1f}",
        help="Average outstanding orders per product"
    )

with col4:
    products_with_ious = (processor.sales_data['IOUs'] > 0).sum()
    st.metric(
        "Products with IOUs",
        f"{products_with_ious:,}",
        help="Number of products with outstanding orders"
    )

# Analysis Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Channel Analysis", "Category Analysis", "Top Products", "Trends"])

with tab1:
    st.markdown("### Outstanding Orders by Channel")
    
    # Channel summary
    channel_ious = processor.sales_data.groupby('Channel').agg({
        'IOUs': 'sum',
        'Sales': 'sum',
        'Target': 'sum'
    }).round(0)
    
    channel_ious['IOU_Rate'] = channel_ious['IOUs'].div(channel_ious['Sales'].replace(0, 1)).mul(100).round(1)
    channel_ious = channel_ious.sort_values('IOUs', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bar chart
        fig = px.bar(
            channel_ious.reset_index(),
            x='Channel',
            y='IOUs',
            title="IOUs by Sales Channel",
            color='IOU_Rate',
            color_continuous_scale='Reds',
            labels={'IOUs': 'Outstanding Orders', 'IOU_Rate': 'IOU Rate %'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Table
        st.dataframe(
            channel_ious.style.format({
                'IOUs': '{:,.0f}',
                'Sales': '{:,.0f}',
                'IOU_Rate': '{:.1f}%'
            }).background_gradient(subset=['IOU_Rate'], cmap='Reds')
        )

with tab2:
    st.markdown("### Outstanding Orders by Category")
    
    # Category analysis
    category_ious = processor.sales_data.groupby('Category').agg({
        'IOUs': ['sum', 'count', 'mean'],
        'Sales': 'sum'
    }).round(0)
    
    category_ious.columns = ['IOU_Total', 'Product_Count', 'Avg_IOU', 'Sales']
    category_ious['IOU_Rate'] = category_ious['IOU_Total'].div(category_ious['Sales'].replace(0, 1)).mul(100).round(1)
    category_ious = category_ious.sort_values('IOU_Total', ascending=False)
    
    # Pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            category_ious.reset_index(),
            values='IOU_Total',
            names='Category',
            title="IOU Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter plot - IOU vs Sales
        fig = px.scatter(
            category_ious.reset_index(),
            x='Sales',
            y='IOU_Total',
            size='Product_Count',
            color='IOU_Rate',
            hover_data=['Category'],
            title="IOUs vs Sales by Category",
            labels={'IOU_Total': 'Total IOUs', 'Sales': 'Total Sales'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.markdown("### Category Details")
    st.dataframe(
        category_ious.style.format({
            'IOU_Total': '{:,.0f}',
            'Product_Count': '{:,}',
            'Avg_IOU': '{:,.1f}',
            'Sales': '{:,.0f}',
            'IOU_Rate': '{:.1f}%'
        }).background_gradient(subset=['IOU_Rate'], cmap='Reds')
    )

with tab3:
    st.markdown("### Top Products with Outstanding Orders")
    
    # Top products by IOUs
    # Use correct column names from sales data
    # Also include Channel and Brand to distinguish products with same Planning Level
    top_products = processor.sales_data.nlargest(20, 'IOUs')[
        ['Channel', 'Planning Level', 'Brand', 'Category', 'Master Brand', 'IOUs', 'Sales', 'Target']
    ].copy()
    
    # Calculate achievement and IOU vs Sales with safe division
    top_products['Achievement'] = np.where(
        top_products['Target'] > 0,
        top_products['Sales'].div(top_products['Target'].replace(0, 1)).mul(100).round(1),
        0
    )
    top_products['IOU_vs_Sales'] = np.where(
        top_products['Sales'] > 0,
        top_products['IOUs'].div(top_products['Sales'].replace(0, 1)).mul(100).round(1),
        0
    )
    
    # Create a unique product identifier for display
    top_products['Product_Display'] = top_products.apply(
        lambda row: f"{row['Planning Level']} ({row['Brand']}, {row['Channel']})", 
        axis=1
    )
    
    # Bar chart of top 10
    fig = px.bar(
        top_products.head(10),
        x='Product_Display',
        y='IOUs',
        color='Category',
        hover_data=['Channel', 'Brand', 'Master Brand'],
        title="Top 10 Products by Outstanding Orders",
        labels={'IOUs': 'Outstanding Orders', 'Product_Display': 'Product (Brand, Channel)'}
    )
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table - show unique product info
    st.markdown("### Product Details")
    # Select columns to display in a more readable format
    table_data = top_products[['Product_Display', 'Category', 'IOUs', 'Sales', 'Target', 'Achievement', 'IOU_vs_Sales']].copy()
    table_data.columns = ['Product (Brand, Channel)', 'Category', 'IOUs', 'Sales', 'Target', 'Achievement %', 'IOU vs Sales %']
    
    st.dataframe(
        table_data.style.format({
            'IOUs': '{:,.2f}',
            'Sales': '{:,.2f}',
            'Target': '{:,.2f}',
            'Achievement %': '{:.1f}',
            'IOU vs Sales %': '{:.1f}'
        }).background_gradient(subset=['IOU vs Sales %'], cmap='Reds')
    )

with tab4:
    st.markdown("### IOU Trends Analysis")
    
    # If we have date information, show trends
    st.info("Trend analysis requires historical IOU data. Currently showing current snapshot only.")
    
    # IOU vs Achievement scatter
    iou_analysis = processor.sales_data[processor.sales_data['IOUs'] > 0].copy()
    # Safe division for achievement
    iou_analysis['Achievement'] = np.where(
        iou_analysis['Target'] > 0,
        iou_analysis['Sales'].div(iou_analysis['Target'].replace(0, 1)).mul(100).round(1),
        0
    )
    
    fig = px.scatter(
        iou_analysis,
        x='Achievement',
        y='IOUs',
        color='Category',
        size='Sales',
        hover_data=['Planning Level', 'Master Brand'],
        title="IOUs vs Sales Achievement",
        labels={'Achievement': 'Sales Achievement %', 'IOUs': 'Outstanding Orders'}
    )
    
    # Add reference lines
    fig.add_hline(y=iou_analysis['IOUs'].median(), line_dash="dash", 
                  annotation_text="Median IOU", annotation_position="bottom right")
    fig.add_vline(x=100, line_dash="dash", 
                  annotation_text="Target", annotation_position="top left")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary insights
    st.markdown("### Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### High IOU Categories")
        high_iou_categories = category_ious.head(3)
        for idx, row in high_iou_categories.iterrows():
            st.write(f"- **{idx}**: {row['IOU_Total']:,.0f} IOUs ({row['IOU_Rate']:.1f}% of sales)")
    
    with col2:
        st.markdown("#### Products Needing Attention")
        # Products with high IOU rate and low achievement
        # Exclude products with 0 sales or target to avoid division issues
        # First add Product_Display to top_products if not already there
        if 'Product_Display' not in top_products.columns:
            top_products['Product_Display'] = top_products.apply(
                lambda row: f"{row['Planning Level']} ({row['Brand']}, {row['Channel']})", 
                axis=1
            )
        
        products_with_valid_data = top_products[
            (top_products['Sales'] > 0) & 
            (top_products['Target'] > 0)
        ].copy()
        
        critical_products = products_with_valid_data[
            (products_with_valid_data['IOU_vs_Sales'] > 50) & 
            (products_with_valid_data['Achievement'] < 80)
        ].head(3)
        
        if len(critical_products) > 0:
            for _, product in critical_products.iterrows():
                # Show more details for clarity with unique identifier
                product_name = f"{product['Planning Level']} ({product['Brand']}, {product['Channel']})"
                if len(product_name) > 50:
                    product_name = product_name[:50] + "..."
                st.write(f"- **{product_name}**: {product['IOUs']:,.1f} IOUs ({product['IOU_vs_Sales']:.0f}% of sales, {product['Achievement']:.0f}% of target)")
        else:
            # If no critical products, show products with highest IOUs
            st.write("No products meeting critical criteria (IOU>50% of sales & Achievement<80%)")
            st.write("\n**Products with highest IOUs:**")
            for i, (_, product) in enumerate(top_products.head(3).iterrows()):
                product_name = f"{product['Planning Level']} ({product['Brand']}, {product['Channel']})"
                if len(product_name) > 50:
                    product_name = product_name[:50] + "..."
                st.write(f"- **{product_name}**: {product['IOUs']:,.1f} IOUs")

# Export functionality
st.markdown("---")
st.markdown("### Export IOU Data")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Download Channel Summary"):
        csv = channel_ious.to_csv()
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"iou_channel_summary_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📥 Download Category Summary"):
        csv = category_ious.to_csv()
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"iou_category_summary_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col3:
    if st.button("📥 Download Top Products"):
        csv = top_products.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"iou_top_products_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
"""
TOP 10 Executive Dashboard for P&G Supply Chain Analytics
High-level view of top performers and problem areas
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import DataProcessor
from components.filters import create_multiselect_filters, apply_filters_to_data

st.set_page_config(
    page_title="TOP 10 Executive View - P&G Analytics",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 TOP 10 Executive Dashboard")
st.markdown("Quick insights into top performers and critical areas")

# Load data
@st.cache_resource
def load_data():
    processor = DataProcessor()
    processor.load_processed_data()
    return processor

processor = load_data()

# Filters
st.sidebar.markdown("### Filters")
filters = create_multiselect_filters(processor.shipping_data)
filtered_data = apply_filters_to_data(processor.shipping_data, filters)

# Create a temporary processor for filtered data
filtered_processor = DataProcessor()
filtered_processor.shipping_data = filtered_data
filtered_processor.sales_data = processor.sales_data

# Executive Summary Cards
st.markdown("## 📊 Executive Summary")

col1, col2, col3, col4 = st.columns(4)

# Calculate key metrics
total_shipments = len(filtered_data)
late_shipments = (filtered_data['Delivery_Status'] == 'Late').sum()
late_rate = round((late_shipments / total_shipments * 100), 1) if total_shipments > 0 else 0
on_time_deliveries = (filtered_data['Delivery_Status'] == 'On Time').sum()

with col1:
    st.metric(
        "Total Shipments",
        f"{total_shipments:,}",
        help="Total number of shipments in selected period"
    )

with col2:
    st.metric(
        "Late Delivery Rate",
        f"{late_rate:.1f}%",
        delta=f"{late_rate - 30:.1f}% vs target",
        delta_color="inverse",
        help="Target: 30%"
    )

with col3:
    st.metric(
        "On-Time Deliveries",
        f"{on_time_deliveries:,}",
        f"{on_time_deliveries/total_shipments*100:.1f}%" if total_shipments > 0 else "0%"
    )

with col4:
    if 'Quantity' in filtered_data.columns:
        # Ensure Quantity is numeric
        filtered_data['Quantity'] = pd.to_numeric(filtered_data['Quantity'], errors='coerce').fillna(0)
        total_volume = filtered_data['Quantity'].sum()
        st.metric(
            "Total Volume",
            f"{total_volume:,.0f}",
            help="Total quantity shipped"
        )

# Prepare category performance data for reuse across tabs
category_perf = filtered_data.groupby('Category').agg({
    'Delivery_Status': [
        lambda x: (x == 'On Time').sum(),
        lambda x: (x == 'Late').sum(),
        'count'
    ]
})
category_perf.columns = ['On_Time', 'Late', 'Total']
category_perf['On_Time_Rate'] = category_perf['On_Time'].div(category_perf['Total'].replace(0, 1)).mul(100).round(1)
category_perf['Late_Rate'] = category_perf['Late'].div(category_perf['Total'].replace(0, 1)).mul(100).round(1)
category_perf = category_perf[category_perf['Total'] >= 10]  # Min 10 shipments

# Create tabs for different TOP 10 views
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏆 Best Performers", 
    "⚠️ Problem Areas", 
    "📦 Top Products", 
    "🏭 Plant Rankings",
    "💰 Sales Leaders",
    "📈 Trend Analysis"
])

with tab1:
    st.markdown("## 🏆 Best Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 Categories with Best On-Time Performance
        st.markdown("### Top 10 Categories - Best On-Time Rate")
        
        top_categories = category_perf.nlargest(10, 'On_Time_Rate')
        
        fig = px.bar(
            top_categories.reset_index(),
            x='On_Time_Rate',
            y='Category',
            orientation='h',
            title="Categories with Best On-Time Performance",
            color='On_Time_Rate',
            color_continuous_scale='Greens',
            text='On_Time_Rate'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top 10 Brands with Best Performance
        st.markdown("### Top 10 Brands - Lowest Late Rate")
        
        brand_perf = filtered_data.groupby('Master_Brand').agg({
            'Delivery_Status': [
                lambda x: (x == 'Late').sum(),
                'count'
            ]
        })
        brand_perf.columns = ['Late', 'Total']
        brand_perf['Late_Rate'] = brand_perf['Late'].div(brand_perf['Total'].replace(0, 1)).mul(100).round(1)
        brand_perf = brand_perf[brand_perf['Total'] >= 20]  # Min 20 shipments
        
        best_brands = brand_perf.nsmallest(10, 'Late_Rate')
        
        fig = px.bar(
            best_brands.reset_index(),
            x='Late_Rate',
            y='Master_Brand',
            orientation='h',
            title="Brands with Lowest Late Rate",
            color='Late_Rate',
            color_continuous_scale='Greens_r',
            text='Late_Rate'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("## ⚠️ Problem Areas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 Categories with Worst Performance
        st.markdown("### Bottom 10 Categories - Highest Late Rate")
        
        worst_categories = category_perf.nlargest(10, 'Late_Rate')
        
        fig = px.bar(
            worst_categories.reset_index(),
            x='Late_Rate',
            y='Category',
            orientation='h',
            title="Categories Needing Immediate Attention",
            color='Late_Rate',
            color_continuous_scale='Reds',
            text='Late_Rate'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.add_vline(x=30, line_dash="dash", annotation_text="Target: 30%")
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top 10 Products with Most Late Shipments
        st.markdown("### Top 10 Products - Most Late Shipments")
        
        product_late = filtered_data[filtered_data['Delivery_Status'] == 'Late'].groupby('Planning_Level').size()
        top_late_products = product_late.nlargest(10)
        
        fig = px.bar(
            x=top_late_products.values,
            y=top_late_products.index,
            orientation='h',
            title="Products with Most Late Deliveries",
            color=top_late_products.values,
            color_continuous_scale='Reds',
            labels={'x': 'Late Shipments', 'y': 'Product'}
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("## 📦 Top Products Analysis")
    
    # Top 10 Products by Volume
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top 10 Products by Volume")
        
        if 'Quantity' in filtered_data.columns:
            product_volume = filtered_data.groupby('Planning_Level')['Quantity'].sum().nlargest(10)
            
            fig = px.pie(
                values=product_volume.values,
                names=product_volume.index,
                title="Top 10 Products by Total Volume"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Top 10 Products by Order Count")
        
        product_orders = filtered_data.groupby('Planning_Level').size().nlargest(10)
        
        fig = px.bar(
            x=product_orders.values,
            y=product_orders.index,
            orientation='h',
            title="Most Frequently Ordered Products",
            color=product_orders.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Product Performance Table
    st.markdown("### Product Performance Metrics")
    
    product_metrics = filtered_data.groupby('Planning_Level').agg({
        'Transaction_ID': 'count',
        'Delivery_Status': lambda x: (x == 'Late').sum(),
        'Quantity': 'sum' if 'Quantity' in filtered_data.columns else lambda x: 0,
        'Delay_Days': lambda x: x[filtered_data.loc[x.index, 'Delivery_Status'] == 'Late'].mean()
    }).rename(columns={
        'Transaction_ID': 'Orders',
        'Delivery_Status': 'Late_Orders',
        'Quantity': 'Total_Volume',
        'Delay_Days': 'Avg_Delay'
    })
    
    product_metrics['Late_Rate'] = product_metrics['Late_Orders'].div(product_metrics['Orders'].replace(0, 1)).mul(100).round(1)
    product_metrics = product_metrics.nlargest(10, 'Orders')
    
    st.dataframe(
        product_metrics.style.background_gradient(subset=['Late_Rate'], cmap='RdYlGn_r')
        .format({
            'Orders': '{:,.0f}',
            'Late_Orders': '{:,.0f}',
            'Total_Volume': '{:,.0f}',
            'Avg_Delay': '{:.1f}',
            'Late_Rate': '{:.1f}%'
        })
    )

with tab4:
    st.markdown("## 🏭 Plant/Source Rankings")
    
    # Plant performance metrics
    plant_metrics = filtered_data.groupby('Source').agg({
        'Transaction_ID': 'count',
        'Delivery_Status': [
            lambda x: (x == 'Late').sum(),
            lambda x: (x == 'On Time').sum()
        ],
        'Delay_Days': lambda x: x[filtered_data.loc[x.index, 'Delivery_Status'] == 'Late'].mean()
    })
    
    plant_metrics.columns = ['Total_Orders', 'Late_Orders', 'OnTime_Orders', 'Avg_Delay']
    plant_metrics['Late_Rate'] = plant_metrics['Late_Orders'].div(plant_metrics['Total_Orders'].replace(0, 1)).mul(100).round(1)
    plant_metrics['OnTime_Rate'] = plant_metrics['OnTime_Orders'].div(plant_metrics['Total_Orders'].replace(0, 1)).mul(100).round(1)
    
    # Ranking visualization
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Plant Performance by Late Rate", "Plant Volume Distribution"),
        specs=[[{"type": "bar"}, {"type": "pie"}]]
    )
    
    # Late rate ranking
    plant_sorted = plant_metrics.sort_values('Late_Rate')
    
    fig.add_trace(
        go.Bar(
            x=plant_sorted['Late_Rate'],
            y=plant_sorted.index,
            orientation='h',
            marker_color=['green' if x < 30 else 'red' for x in plant_sorted['Late_Rate']],
            text=plant_sorted['Late_Rate'],
            name='Late Rate %'
        ),
        row=1, col=1
    )
    
    # Volume distribution
    fig.add_trace(
        go.Pie(
            labels=plant_metrics.index,
            values=plant_metrics['Total_Orders'],
            name='Order Volume'
        ),
        row=1, col=2
    )
    
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside', row=1, col=1)
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed plant metrics
    st.markdown("### Detailed Plant Metrics")
    st.dataframe(
        plant_metrics.sort_values('Total_Orders', ascending=False)
        .style.background_gradient(subset=['Late_Rate'], cmap='RdYlGn_r')
        .background_gradient(subset=['OnTime_Rate'], cmap='RdYlGn')
        .format({
            'Total_Orders': '{:,.0f}',
            'Late_Orders': '{:,.0f}',
            'OnTime_Orders': '{:,.0f}',
            'Late_Rate': '{:.1f}%',
            'OnTime_Rate': '{:.1f}%',
            'Avg_Delay': '{:.1f} days'
        })
    )

with tab5:
    st.markdown("## 💰 Sales Performance Leaders")
    
    if processor.sales_data is not None and not processor.sales_data.empty:
        # Top 10 by Sales Achievement
        sales_by_category = processor.sales_data.groupby('Category').agg({
            'Sales': 'sum',
            'Target': 'sum'
        })
        sales_by_category['Achievement'] = sales_by_category['Sales'].div(sales_by_category['Target'].replace(0, 1)).mul(100).round(1)
        sales_by_category['Gap'] = sales_by_category['Sales'] - sales_by_category['Target']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Top 10 - Sales Achievement %")
            
            top_achievers = sales_by_category.nlargest(10, 'Achievement')
            
            fig = px.bar(
                top_achievers.reset_index(),
                x='Achievement',
                y='Category',
                orientation='h',
                title="Categories with Highest Sales Achievement",
                color='Achievement',
                color_continuous_scale='Viridis',
                text='Achievement'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.add_vline(x=100, line_dash="dash", annotation_text="Target: 100%")
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Top 10 - Absolute Sales Value")
            
            top_sales = sales_by_category.nlargest(10, 'Sales')
            
            fig = px.bar(
                top_sales.reset_index(),
                x='Sales',
                y='Category',
                orientation='h',
                title="Categories with Highest Sales",
                color='Sales',
                color_continuous_scale='Blues',
                text='Sales'
            )
            fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Sales vs Target comparison
        st.markdown("### Sales vs Target - Top 10 Categories")
        
        top_categories_sales = sales_by_category.nlargest(10, 'Sales').reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top_categories_sales['Category'],
            y=top_categories_sales['Sales'],
            name='Actual Sales',
            marker_color='lightblue'
        ))
        fig.add_trace(go.Bar(
            x=top_categories_sales['Category'],
            y=top_categories_sales['Target'],
            name='Target',
            marker_color='lightcoral'
        ))
        
        fig.update_layout(
            title="Sales Performance vs Target",
            barmode='group',
            height=400,
            yaxis_title="Sales Value ($)"
        )
        st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.markdown("## 📈 Trend Analysis - Top 10 Insights")
    
    # Time-based analysis
    if 'Actual_Ship_Date' in filtered_data.columns:
        # Weekly trend for top 5 categories
        st.markdown("### Weekly Late Rate Trend - Top 5 Categories")
        
        top_5_categories = filtered_data['Category'].value_counts().head(5).index
        
        weekly_data = filtered_data[filtered_data['Category'].isin(top_5_categories)].copy()
        weekly_data['Week'] = weekly_data['Actual_Ship_Date'].dt.to_period('W')
        
        weekly_trend = weekly_data.groupby(['Week', 'Category']).agg({
            'Delivery_Status': [
                lambda x: (x == 'Late').sum(),
                'count'
            ]
        })
        weekly_trend.columns = ['Late', 'Total']
        weekly_trend['Late_Rate'] = weekly_trend['Late'].div(weekly_trend['Total'].replace(0, 1)).mul(100).round(1)
        weekly_trend = weekly_trend.reset_index()
        weekly_trend['Week'] = weekly_trend['Week'].astype(str)
        
        fig = px.line(
            weekly_trend,
            x='Week',
            y='Late_Rate',
            color='Category',
            title="Weekly Late Rate Trend by Top Categories",
            markers=True
        )
        fig.add_hline(y=30, line_dash="dash", annotation_text="Target: 30%")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Daily volume trend
        st.markdown("### Daily Shipment Volume - Last 30 Days")
        
        last_30_days = filtered_data['Actual_Ship_Date'].max() - pd.Timedelta(days=30)
        recent_data = filtered_data[filtered_data['Actual_Ship_Date'] >= last_30_days]
        
        daily_volume = recent_data.groupby(recent_data['Actual_Ship_Date'].dt.date).agg({
            'Transaction_ID': 'count',
            'Delivery_Status': lambda x: (x == 'Late').sum()
        }).rename(columns={'Transaction_ID': 'Total', 'Delivery_Status': 'Late'})
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_volume.index,
            y=daily_volume['Total'],
            mode='lines+markers',
            name='Total Shipments',
            line=dict(width=2)
        ))
        fig.add_trace(go.Bar(
            x=daily_volume.index,
            y=daily_volume['Late'],
            name='Late Shipments',
            marker_color='red',
            opacity=0.7
        ))
        
        fig.update_layout(
            title="Daily Shipment Volume Trend",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

# Executive Actions Section
st.markdown("---")
st.markdown("## 🎯 Recommended Executive Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🚨 Immediate Actions")
    if late_rate > 40:
        st.error("• **Critical**: Late rate exceeds 40% - Initiate emergency response")
    # Get worst category if exists
    if 'Late_Rate' in category_perf.columns and len(category_perf) > 0:
        worst_cat = category_perf['Late_Rate'].idxmax()
        worst_rate = category_perf['Late_Rate'].max()
        if worst_rate > 50:
            st.warning(f"• Review {worst_cat} category - {worst_rate:.1f}% late rate")
    st.info("• Focus on top 3 problem categories")

with col2:
    st.markdown("### 📊 Performance Review")
    st.success("• Recognize top performing plants")
    st.info("• Share best practices from top categories")
    st.warning("• Address bottom 10% performers")

with col3:
    st.markdown("### 📈 Strategic Focus")
    st.info("• Invest in capacity for top 10 products")
    st.warning("• Review routing for high-delay plants")
    st.success("• Expand successful category strategies")
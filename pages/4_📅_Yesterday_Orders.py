"""
Yesterday Orders Comparison Page for P&G Supply Chain Analytics
Compares today's orders with yesterday's performance
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import DataProcessor
from components.filters import create_multiselect_filters, apply_filters_to_data

st.set_page_config(
    page_title="Yesterday Orders - P&G Analytics",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Yesterday Orders Comparison")
st.markdown("Compare daily order performance and identify trends")

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

# Get the latest date in the data
if 'Actual_Ship_Date' in filtered_data.columns:
    latest_date = filtered_data['Actual_Ship_Date'].max()
    yesterday = latest_date - timedelta(days=1)
    two_days_ago = latest_date - timedelta(days=2)
    
    # Today's data (latest date)
    today_data = filtered_data[filtered_data['Actual_Ship_Date'].dt.date == latest_date.date()]
    yesterday_data = filtered_data[filtered_data['Actual_Ship_Date'].dt.date == yesterday.date()]
    
    # Summary metrics
    st.markdown("### 📊 Daily Comparison")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        today_count = len(today_data)
        yesterday_count = len(yesterday_data)
        change = today_count - yesterday_count
        change_pct = (change / yesterday_count * 100) if yesterday_count > 0 else 0
        
        st.metric(
            f"Orders on {latest_date.strftime('%Y-%m-%d')}",
            f"{today_count:,}",
            f"{change:+,} ({change_pct:+.1f}%)"
        )
    
    with col2:
        today_late = (today_data['Delivery_Status'] == 'Late').sum()
        yesterday_late = (yesterday_data['Delivery_Status'] == 'Late').sum()
        late_change = today_late - yesterday_late
        
        st.metric(
            "Late Orders",
            f"{today_late:,}",
            f"{late_change:+,}"
        )
    
    with col3:
        today_late_rate = (today_late / today_count * 100) if today_count > 0 else 0
        yesterday_late_rate = (yesterday_late / yesterday_count * 100) if yesterday_count > 0 else 0
        rate_change = today_late_rate - yesterday_late_rate
        
        st.metric(
            "Late Rate",
            f"{today_late_rate:.1f}%",
            f"{rate_change:+.1f}%"
        )
    
    with col4:
        if 'Quantity' in today_data.columns:
            # Ensure Quantity is numeric
            today_data['Quantity'] = pd.to_numeric(today_data['Quantity'], errors='coerce').fillna(0)
            yesterday_data['Quantity'] = pd.to_numeric(yesterday_data['Quantity'], errors='coerce').fillna(0)
            
            today_volume = today_data['Quantity'].sum()
            yesterday_volume = yesterday_data['Quantity'].sum()
            volume_change = today_volume - yesterday_volume
            volume_change_pct = (volume_change / yesterday_volume * 100) if yesterday_volume > 0 else 0
            
            st.metric(
                "Total Volume",
                f"{today_volume:,.0f}",
                f"{volume_change:+,.0f} ({volume_change_pct:+.1f}%)"
            )
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Hourly Comparison", "Category Analysis", "Source Performance", "Weekly Trend"
    ])
    
    with tab1:
        st.markdown("### ⏰ Hourly Order Distribution")
        
        # Create hourly comparison if we have timestamp data
        if pd.api.types.is_datetime64_any_dtype(filtered_data['Actual_Ship_Date']):
            # Add hour column
            today_data_copy = today_data.copy()
            yesterday_data_copy = yesterday_data.copy()
            
            today_data_copy['Hour'] = today_data_copy['Actual_Ship_Date'].dt.hour
            yesterday_data_copy['Hour'] = yesterday_data_copy['Actual_Ship_Date'].dt.hour
            
            # Aggregate by hour
            today_hourly = today_data_copy.groupby('Hour').size()
            yesterday_hourly = yesterday_data_copy.groupby('Hour').size()
            
            # Create comparison chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=list(range(24)),
                y=[today_hourly.get(h, 0) for h in range(24)],
                name=f'Today ({latest_date.strftime("%m/%d")})',
                marker_color='lightblue'
            ))
            
            fig.add_trace(go.Bar(
                x=list(range(24)),
                y=[yesterday_hourly.get(h, 0) for h in range(24)],
                name=f'Yesterday ({yesterday.strftime("%m/%d")})',
                marker_color='lightcoral'
            ))
            
            fig.update_layout(
                title="Hourly Order Distribution Comparison",
                xaxis_title="Hour of Day",
                yaxis_title="Number of Orders",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Hourly analysis requires timestamp data")
    
    with tab2:
        st.markdown("### 📦 Category Performance Comparison")
        
        # Category comparison
        today_category = today_data.groupby('Category').agg({
            'Transaction_ID': 'count',
            'Delivery_Status': lambda x: (x == 'Late').sum()
        }).rename(columns={'Transaction_ID': 'Total_Today', 'Delivery_Status': 'Late_Today'})
        
        yesterday_category = yesterday_data.groupby('Category').agg({
            'Transaction_ID': 'count',
            'Delivery_Status': lambda x: (x == 'Late').sum()
        }).rename(columns={'Transaction_ID': 'Total_Yesterday', 'Delivery_Status': 'Late_Yesterday'})
        
        # Combine data
        category_comp = pd.concat([today_category, yesterday_category], axis=1).fillna(0)
        category_comp['Change'] = category_comp['Total_Today'] - category_comp['Total_Yesterday']
        
        # Safe division for late rates
        category_comp['Late_Rate_Today'] = np.where(
            category_comp['Total_Today'] > 0,
            (category_comp['Late_Today'] / category_comp['Total_Today'] * 100).round(1),
            0
        )
        category_comp['Late_Rate_Yesterday'] = np.where(
            category_comp['Total_Yesterday'] > 0,
            (category_comp['Late_Yesterday'] / category_comp['Total_Yesterday'] * 100).round(1),
            0
        )
        category_comp['Late_Rate_Change'] = category_comp['Late_Rate_Today'] - category_comp['Late_Rate_Yesterday']
        
        # Sort by total volume
        category_comp = category_comp.sort_values('Total_Today', ascending=False)
        
        # Display table
        st.dataframe(
            category_comp[['Total_Today', 'Total_Yesterday', 'Change', 
                          'Late_Rate_Today', 'Late_Rate_Yesterday', 'Late_Rate_Change']]
            .style.background_gradient(subset=['Change'], cmap='RdYlGn')
            .background_gradient(subset=['Late_Rate_Change'], cmap='RdYlGn_r')
            .format({
                'Total_Today': '{:,.0f}',
                'Total_Yesterday': '{:,.0f}',
                'Change': '{:+,.0f}',
                'Late_Rate_Today': '{:.1f}%',
                'Late_Rate_Yesterday': '{:.1f}%',
                'Late_Rate_Change': '{:+.1f}%'
            })
        )
        
        # Visualization
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Order Volume by Category", "Late Rate by Category")
        )
        
        # Volume comparison
        fig.add_trace(
            go.Bar(x=category_comp.index, y=category_comp['Total_Today'], 
                   name='Today', marker_color='blue'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=category_comp.index, y=category_comp['Total_Yesterday'], 
                   name='Yesterday', marker_color='lightblue'),
            row=1, col=1
        )
        
        # Late rate comparison
        fig.add_trace(
            go.Bar(x=category_comp.index, y=category_comp['Late_Rate_Today'], 
                   name='Today', marker_color='red', showlegend=False),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=category_comp.index, y=category_comp['Late_Rate_Yesterday'], 
                   name='Yesterday', marker_color='lightcoral', showlegend=False),
            row=1, col=2
        )
        
        fig.update_layout(height=400, barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 🏭 Source/Warehouse Performance")
        
        # Source comparison
        today_source = today_data.groupby('Source').agg({
            'Transaction_ID': 'count',
            'Delivery_Status': lambda x: (x == 'Late').sum()
        }).rename(columns={'Transaction_ID': 'Total', 'Delivery_Status': 'Late'})
        
        yesterday_source = yesterday_data.groupby('Source').agg({
            'Transaction_ID': 'count',
            'Delivery_Status': lambda x: (x == 'Late').sum()
        }).rename(columns={'Transaction_ID': 'Total', 'Delivery_Status': 'Late'})
        
        # Create comparison
        source_metrics = []
        for source in set(today_source.index) | set(yesterday_source.index):
            today_total = today_source.loc[source, 'Total'] if source in today_source.index else 0
            yesterday_total = yesterday_source.loc[source, 'Total'] if source in yesterday_source.index else 0
            today_late = today_source.loc[source, 'Late'] if source in today_source.index else 0
            yesterday_late = yesterday_source.loc[source, 'Late'] if source in yesterday_source.index else 0
            
            source_metrics.append({
                'Source': source,
                'Orders Today': today_total,
                'Orders Yesterday': yesterday_total,
                'Change': today_total - yesterday_total,
                'Late Today': today_late,
                'Late Yesterday': yesterday_late,
                'Late Change': today_late - yesterday_late
            })
        
        source_df = pd.DataFrame(source_metrics)
        
        # Show the data table first for transparency
        st.markdown("#### Source Performance Data")
        st.dataframe(
            source_df.style.format({
                'Orders Today': '{:,.0f}',
                'Orders Yesterday': '{:,.0f}',
                'Change': '{:+,.0f}',
                'Late Today': '{:,.0f}',
                'Late Yesterday': '{:,.0f}',
                'Late Change': '{:+,.0f}'
            }).background_gradient(subset=['Change'], cmap='RdYlGn')
            .background_gradient(subset=['Late Change'], cmap='RdYlGn_r')
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Order volume chart
            fig = px.bar(
                source_df,
                x='Source',
                y=['Orders Today', 'Orders Yesterday'],
                title="Order Volume by Source",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Late orders chart
            # Check if there are any late orders
            total_late_today = source_df['Late Today'].sum()
            total_late_yesterday = source_df['Late Yesterday'].sum()
            
            if total_late_today == 0 and total_late_yesterday == 0:
                st.info("No late orders recorded for any source on these days")
                # Show a placeholder chart with zero values
                fig = px.bar(
                    source_df,
                    x='Source',
                    y=['Late Today', 'Late Yesterday'],
                    title="Late Orders by Source (No Late Orders)",
                    barmode='group',
                    color_discrete_map={
                        'Late Today': 'red',
                        'Late Yesterday': 'lightcoral'
                    }
                )
                fig.update_yaxes(range=[0, 1])  # Set a minimum range so axes show
            else:
                fig = px.bar(
                    source_df,
                    x='Source',
                    y=['Late Today', 'Late Yesterday'],
                    title="Late Orders by Source",
                    barmode='group',
                    color_discrete_map={
                        'Late Today': 'red',
                        'Late Yesterday': 'lightcoral'
                    }
                )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show summary statistics below the chart
            st.markdown("##### Late Orders Summary")
            summary_cols = st.columns(2)
            with summary_cols[0]:
                st.metric("Total Late Today", f"{total_late_today:,.0f}")
            with summary_cols[1]:
                st.metric("Total Late Yesterday", f"{total_late_yesterday:,.0f}")
    
    with tab4:
        st.markdown("### 📈 7-Day Rolling Trend")
        
        # Get last 7 days of data
        week_ago = latest_date - timedelta(days=7)
        week_data = filtered_data[filtered_data['Actual_Ship_Date'] >= week_ago]
        
        # Daily aggregation
        daily_stats = week_data.groupby(week_data['Actual_Ship_Date'].dt.date).agg({
            'Transaction_ID': 'count',
            'Delivery_Status': lambda x: (x == 'Late').sum(),
            'Quantity': 'sum' if 'Quantity' in week_data.columns else lambda x: 0
        }).rename(columns={
            'Transaction_ID': 'Total_Orders',
            'Delivery_Status': 'Late_Orders'
        })
        
        daily_stats['Late_Rate'] = daily_stats['Late_Orders'].div(daily_stats['Total_Orders'].replace(0, 1)).mul(100).round(1)
        
        # Create trend chart
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=("Daily Order Volume", "Daily Late Rate %"),
            vertical_spacing=0.1
        )
        
        # Order volume
        fig.add_trace(
            go.Scatter(
                x=daily_stats.index,
                y=daily_stats['Total_Orders'],
                mode='lines+markers',
                name='Total Orders',
                line=dict(color='blue', width=2),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=daily_stats.index,
                y=daily_stats['Late_Orders'],
                name='Late Orders',
                marker_color='red',
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # Late rate
        fig.add_trace(
            go.Scatter(
                x=daily_stats.index,
                y=daily_stats['Late_Rate'],
                mode='lines+markers',
                name='Late Rate %',
                line=dict(color='red', width=2),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        # Add target line
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                      annotation_text="Target: 30%", row=2, col=1)
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Orders", row=1, col=1)
        fig.update_yaxes(title_text="Late Rate %", row=2, col=1)
        
        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        st.markdown("### 📊 7-Day Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_daily_orders = daily_stats['Total_Orders'].mean()
            st.metric("Average Daily Orders", f"{avg_daily_orders:,.0f}")
        
        with col2:
            avg_late_rate = daily_stats['Late_Rate'].mean()
            st.metric("Average Late Rate", f"{avg_late_rate:.1f}%")
        
        with col3:
            trend = "📈 Increasing" if daily_stats['Late_Rate'].iloc[-1] > daily_stats['Late_Rate'].iloc[0] else "📉 Decreasing"
            st.metric("Late Rate Trend", trend)

else:
    st.error("No date column found in the data")
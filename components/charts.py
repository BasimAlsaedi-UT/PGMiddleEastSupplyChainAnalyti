"""
Charts Component for Streamlit Dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_delivery_status_pie(data):
    """Create pie chart for delivery status distribution"""
    status_counts = data['Delivery_Status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Delivery Status Distribution",
        color_discrete_map={
            'Late': '#FF4B4B',
            'On Time': '#00CC88',
            'Advanced': '#1F77B4',
            'Not Due': '#FFA500'
        },
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )
    
    # Add annotation in the center
    late_pct = (status_counts.get('Late', 0) / status_counts.sum() * 100) if status_counts.sum() > 0 else 0
    fig.add_annotation(
        text=f"Late<br>{late_pct:.1f}%",
        x=0.5, y=0.5,
        font_size=20,
        showarrow=False
    )
    
    return fig

def create_daily_trend_chart(daily_data):
    """Create daily trend chart for late deliveries"""
    fig = go.Figure()
    
    # Add traces for each status
    for status in ['Late', 'On Time', 'Advanced', 'Not Due']:
        if status in daily_data.columns:
            fig.add_trace(go.Scatter(
                x=daily_data.index,
                y=daily_data[status],
                mode='lines+markers',
                name=status,
                line=dict(width=2),
                marker=dict(size=6)
            ))
    
    # Add late rate as secondary y-axis
    if 'Late_Rate' in daily_data.columns:
        fig.add_trace(go.Scatter(
            x=daily_data.index,
            y=daily_data['Late_Rate'],
            mode='lines',
            name='Late Rate %',
            yaxis='y2',
            line=dict(color='red', width=3, dash='dash')
        ))
    
    fig.update_layout(
        title="Daily Delivery Performance Trend",
        xaxis_title="Date",
        yaxis_title="Number of Shipments",
        yaxis2=dict(
            title="Late Rate %",
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_category_performance_bar(category_data):
    """Create bar chart for category performance"""
    # Sort by late rate
    category_data = category_data.sort_values('Late_Rate', ascending=True)
    
    fig = px.bar(
        category_data,
        x='Late_Rate',
        y=category_data.index,
        orientation='h',
        title="Late Delivery Rate by Category",
        labels={'Late_Rate': 'Late Rate (%)', 'index': 'Category'},
        color='Late_Rate',
        color_continuous_scale=['green', 'yellow', 'red'],
        range_color=[0, 50]
    )
    
    # Add target line at 30%
    fig.add_vline(x=30, line_dash="dash", line_color="red", 
                  annotation_text="Target: 30%", annotation_position="top")
    
    fig.update_layout(height=400)
    
    return fig

def create_plant_heatmap(data):
    """Create heatmap for plant performance"""
    pivot = data.pivot_table(
        index='Category',
        columns='Source',
        values='Delivery_Status',
        aggfunc=lambda x: (x == 'Late').sum() / len(x) * 100 if len(x) > 0 else 0
    )
    
    fig = px.imshow(
        pivot,
        title="Late Delivery Heatmap: Category vs Plant",
        labels=dict(x="Plant/Source", y="Category", color="Late Rate (%)"),
        color_continuous_scale='RdYlGn_r',
        aspect='auto'
    )
    
    fig.update_traces(
        text=pivot.round(1),
        texttemplate='%{text}%',
        textfont_size=10
    )
    
    return fig

def create_brand_performance_sunburst(data):
    """Create sunburst chart for brand hierarchy performance"""
    # Aggregate data by category and brand
    brand_data = data.groupby(['Category', 'Master_Brand', 'Brand']).agg({
        'Delivery_Status': lambda x: (x == 'Late').sum() / len(x) * 100 if len(x) > 0 else 0
    }).reset_index()
    brand_data.columns = ['Category', 'Master_Brand', 'Brand', 'Late_Rate']
    brand_data['Count'] = data.groupby(['Category', 'Master_Brand', 'Brand']).size().values
    
    fig = px.sunburst(
        brand_data,
        path=['Category', 'Master_Brand', 'Brand'],
        values='Count',
        color='Late_Rate',
        color_continuous_scale='RdYlGn_r',
        title="Product Hierarchy Performance",
        hover_data={'Late_Rate': ':.1f'}
    )
    
    fig.update_traces(
        textinfo="label+percent parent",
        hovertemplate='<b>%{label}</b><br>Late Rate: %{color:.1f}%<br>Count: %{value}<extra></extra>'
    )
    
    return fig

def create_delay_distribution(data):
    """Create histogram of delay days"""
    late_data = data[data['Delivery_Status'] == 'Late']['Delay_Days'].dropna()
    
    fig = px.histogram(
        late_data,
        x='Delay_Days',
        nbins=30,
        title="Distribution of Delay Days (Late Shipments Only)",
        labels={'Delay_Days': 'Days Delayed', 'count': 'Number of Shipments'}
    )
    
    # Add average line
    avg_delay = late_data.mean()
    fig.add_vline(x=avg_delay, line_dash="dash", line_color="red",
                  annotation_text=f"Avg: {avg_delay:.1f} days")
    
    return fig

def create_sales_vs_target_gauge(sales_achievement):
    """Create gauge chart for sales achievement"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sales_achievement,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Sales vs Target Achievement"},
        delta={'reference': 100, 'relative': True},
        gauge={
            'axis': {'range': [None, 120]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 80], 'color': "lightgray"},
                {'range': [80, 100], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig

def create_waterfall_chart(data):
    """Create waterfall chart for delivery performance breakdown"""
    # Calculate percentages
    total = len(data)
    advanced = (data['Delivery_Status'] == 'Advanced').sum()
    on_time = (data['Delivery_Status'] == 'On Time').sum()
    not_due = (data['Delivery_Status'] == 'Not Due').sum()
    late = (data['Delivery_Status'] == 'Late').sum()
    
    fig = go.Figure(go.Waterfall(
        name="Delivery Performance",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Total Shipments", "Advanced", "On Time", "Not Due", "Late"],
        y=[total, -advanced, -on_time, -not_due, late],
        text=[f"{total:,}", f"-{advanced:,}", f"-{on_time:,}", f"-{not_due:,}", f"{late:,}"],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title="Delivery Performance Waterfall",
        showlegend=False,
        height=400
    )
    
    return fig

def create_forecast_chart(historical_data, forecast_data=None):
    """Create time series forecast chart"""
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=historical_data.index,
        y=historical_data['Late_Rate'],
        mode='lines+markers',
        name='Historical',
        line=dict(color='blue', width=2)
    ))
    
    # Add forecast if provided
    if forecast_data is not None:
        fig.add_trace(go.Scatter(
            x=forecast_data.index,
            y=forecast_data['Forecast'],
            mode='lines',
            name='Forecast',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Add confidence interval
        if 'Lower_Bound' in forecast_data.columns:
            fig.add_trace(go.Scatter(
                x=forecast_data.index,
                y=forecast_data['Upper_Bound'],
                fill=None,
                mode='lines',
                line_color='rgba(0,100,80,0)',
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_data.index,
                y=forecast_data['Lower_Bound'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(0,100,80,0)',
                name='Confidence Interval'
            ))
    
    fig.update_layout(
        title="Late Delivery Rate Forecast",
        xaxis_title="Date",
        yaxis_title="Late Rate (%)",
        hovermode='x unified',
        height=400
    )
    
    return fig
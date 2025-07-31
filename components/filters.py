"""
Fixed Filters Component for Streamlit Dashboard
Fixes the date range issue that was causing 38% instead of 35.5%
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def create_date_filter(data, key="date_filter"):
    """Create date range filter - FIXED to handle future dates"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        date_option = st.selectbox(
            "Date Range",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom"],
            index=0,  # Default to "All Time"
            key=f"{key}_option"
        )
    
    if date_option == "Custom":
        with col2:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=30),
                key=f"{key}_start"
            )
        with col3:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                key=f"{key}_end"
            )
    else:
        # FIXED: Calculate date range based on actual data, not current date
        if 'Actual_Ship_Date' in data.columns:
            # Get actual min and max dates from data
            data_min_date = data['Actual_Ship_Date'].min()
            data_max_date = data['Actual_Ship_Date'].max()
            
            # Convert to date objects if they're timestamps
            if hasattr(data_min_date, 'date'):
                data_min_date = data_min_date.date()
            if hasattr(data_max_date, 'date'):
                data_max_date = data_max_date.date()
                
            if date_option == "All Time":
                # Use the actual data range
                start_date = data_min_date
                end_date = data_max_date
            else:
                # For relative ranges, use the data's max date as reference
                # This handles cases where data is from the future
                end_date = data_max_date
                
                if date_option == "Last 7 Days":
                    start_date = end_date - timedelta(days=7)
                elif date_option == "Last 30 Days":
                    start_date = end_date - timedelta(days=30)
                elif date_option == "Last 90 Days":
                    start_date = end_date - timedelta(days=90)
                
                # Ensure start date isn't before data begins
                start_date = max(start_date, data_min_date)
        else:
            # Fallback if no date column
            end_date = datetime.now().date()
            if date_option == "Last 7 Days":
                start_date = end_date - timedelta(days=7)
            elif date_option == "Last 30 Days":
                start_date = end_date - timedelta(days=30)
            elif date_option == "Last 90 Days":
                start_date = end_date - timedelta(days=90)
            else:  # All Time
                start_date = end_date - timedelta(days=365)
    
    return start_date, end_date

def create_multiselect_filters(data):
    """Create multiselect filters for various dimensions"""
    filters = {}
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Plant filter
        if 'SLS_Plant' in data.columns:
            plants = data['SLS_Plant'].dropna().unique()
            selected_plants = st.multiselect(
                "Plant",
                options=sorted(plants),
                default=None,
                key="filter_plant"
            )
            if selected_plants:
                filters['SLS_Plant'] = selected_plants
        
        # Source filter
        if 'Source' in data.columns:
            sources = data['Source'].dropna().unique()
            selected_sources = st.multiselect(
                "Source/Warehouse",
                options=sorted(sources),
                default=None,
                key="filter_source"
            )
            if selected_sources:
                filters['Source'] = selected_sources
    
    with col2:
        # Category filter
        if 'Category' in data.columns:
            categories = data['Category'].dropna().unique()
            selected_categories = st.multiselect(
                "Category",
                options=sorted(categories),
                default=None,
                key="filter_category"
            )
            if selected_categories:
                filters['Category'] = selected_categories
    
    with col3:
        # Master Brand filter
        if 'Master_Brand' in data.columns:
            brands = data['Master_Brand'].dropna().unique()
            selected_brands = st.multiselect(
                "Master Brand",
                options=sorted(brands),
                default=None,
                key="filter_brand"
            )
            if selected_brands:
                filters['Master_Brand'] = selected_brands
    
    with col4:
        # Delivery Status filter
        if 'Delivery_Status' in data.columns:
            statuses = data['Delivery_Status'].dropna().unique()
            selected_statuses = st.multiselect(
                "Delivery Status",
                options=sorted(statuses),
                default=None,
                key="filter_status"
            )
            if selected_statuses:
                filters['Delivery_Status'] = selected_statuses
    
    return filters

def create_channel_filter(data):
    """Create filter for sales channels"""
    if 'Channel' in data.columns:
        channels = data['Channel'].dropna().unique()
        selected_channel = st.selectbox(
            "Sales Channel",
            options=["All Channels"] + list(sorted(channels)),
            key="filter_channel"
        )
        return None if selected_channel == "All Channels" else selected_channel
    return None

def apply_filters_to_data(data, filters, date_range=None):
    """Apply all filters to the dataframe"""
    filtered_data = data.copy()
    
    # Apply date filter
    if date_range and 'Actual_Ship_Date' in filtered_data.columns:
        start_date, end_date = date_range
        filtered_data = filtered_data[
            (filtered_data['Actual_Ship_Date'].dt.date >= start_date) & 
            (filtered_data['Actual_Ship_Date'].dt.date <= end_date)
        ]
    
    # Apply other filters
    for column, values in filters.items():
        if column in filtered_data.columns and values:
            filtered_data = filtered_data[filtered_data[column].isin(values)]
    
    return filtered_data

def create_filter_summary(filters, date_range=None):
    """Display a summary of applied filters"""
    filter_parts = []
    
    if date_range:
        filter_parts.append(f"Date: {date_range[0]} to {date_range[1]}")
    
    for column, values in filters.items():
        if values:
            if len(values) == 1:
                filter_parts.append(f"{column}: {values[0]}")
            else:
                filter_parts.append(f"{column}: {len(values)} selected")
    
    if filter_parts:
        st.info(f"Active filters: {' | '.join(filter_parts)}")
    else:
        st.info("No filters applied - showing all data")

def save_filter_preset(filters, preset_name):
    """Save current filter configuration as a preset"""
    if 'filter_presets' not in st.session_state:
        st.session_state.filter_presets = {}
    
    st.session_state.filter_presets[preset_name] = filters
    st.success(f"Filter preset '{preset_name}' saved!")

def load_filter_preset(preset_name):
    """Load a saved filter preset"""
    if 'filter_presets' in st.session_state and preset_name in st.session_state.filter_presets:
        return st.session_state.filter_presets[preset_name]
    return {}

def create_filter_preset_controls():
    """Create controls for saving and loading filter presets"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if 'filter_presets' in st.session_state and st.session_state.filter_presets:
            selected_preset = st.selectbox(
                "Load Filter Preset",
                options=["None"] + list(st.session_state.filter_presets.keys()),
                key="selected_preset"
            )
        else:
            selected_preset = None
    
    with col2:
        preset_name = st.text_input("Preset Name", key="new_preset_name")
    
    with col3:
        if st.button("Save Current Filters", key="save_preset_btn"):
            if preset_name:
                # Get current filters from session state
                current_filters = {}
                for key in st.session_state:
                    if key.startswith("filter_"):
                        current_filters[key] = st.session_state[key]
                save_filter_preset(current_filters, preset_name)
    
    return selected_preset
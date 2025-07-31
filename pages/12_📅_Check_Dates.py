"""
Check date ranges in the data
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Check Dates", layout="wide")

st.title("📅 Check Date Ranges")

# Load shipping data
try:
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'extracted')
    shipping_file = os.path.join(data_dir, 'shipping_main_data.csv')
    
    if os.path.exists(shipping_file):
        df = pd.read_csv(shipping_file)
        st.success(f"Loaded {len(df)} shipping records")
        
        # Check date columns
        date_cols = ['Actual_Ship_Date', 'Requested_Ship_Date', 'Requested_Delivery_Date']
        
        for col in date_cols:
            if col in df.columns:
                st.subheader(f"{col} Analysis")
                
                # Convert to datetime
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # Get stats
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Min Date", df[col].min().strftime('%Y-%m-%d') if pd.notna(df[col].min()) else "N/A")
                
                with col2:
                    st.metric("Max Date", df[col].max().strftime('%Y-%m-%d') if pd.notna(df[col].max()) else "N/A")
                
                with col3:
                    st.metric("Null Count", df[col].isna().sum())
                
                # Show date distribution
                if df[col].notna().any():
                    date_counts = df[col].dt.date.value_counts().sort_index()
                    st.line_chart(date_counts)
        
        # Current date vs data dates
        st.subheader("Date Comparison")
        st.write(f"**Current Date:** {datetime.now().date()}")
        st.write(f"**Data Date Range:** {df['Actual_Ship_Date'].min().date()} to {df['Actual_Ship_Date'].max().date()}")
        
        if df['Actual_Ship_Date'].max().date() > datetime.now().date():
            st.warning("⚠️ Data contains future dates! This is why filters might not work with 'Last 7 Days' etc.")
            st.info("💡 Use 'All Time' filter option to see all data")
        
    else:
        st.error(f"Shipping data not found at {shipping_file}")
        
except Exception as e:
    st.error(f"Error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
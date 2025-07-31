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
        
        # First show raw data sample
        st.subheader("Raw Data Sample")
        st.dataframe(df.head())
        
        # Check what columns actually exist
        st.write("Available columns:", list(df.columns))
        
        # Check date columns
        date_cols = ['Actual_Ship_Date', 'Requested_Ship_Date', 'Requested_Delivery_Date']
        
        for col in date_cols:
            if col in df.columns:
                st.subheader(f"{col} Analysis")
                
                # Show raw values first
                st.write("Sample raw values:", df[col].head(10).tolist())
                
                # Check data type
                st.write(f"Data type: {df[col].dtype}")
                
                # Try to convert to datetime
                df[f'{col}_converted'] = pd.to_datetime(df[col], errors='coerce')
                
                # If all NaT, try Excel serial number conversion
                if df[f'{col}_converted'].isna().all() and pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        df[f'{col}_converted'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df[col], unit='D')
                        st.info(f"Converted {col} from Excel serial numbers")
                    except:
                        pass
                
                # Get stats
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Min Date", df[f'{col}_converted'].min().strftime('%Y-%m-%d') if pd.notna(df[f'{col}_converted'].min()) else "N/A")
                
                with col2:
                    st.metric("Max Date", df[f'{col}_converted'].max().strftime('%Y-%m-%d') if pd.notna(df[f'{col}_converted'].max()) else "N/A")
                
                with col3:
                    st.metric("Null Count", df[f'{col}_converted'].isna().sum())
        
        # Current date vs data dates
        st.subheader("Date Comparison")
        st.write(f"**Current Date:** {datetime.now().date()}")
        
        # Try to show date range if we have converted dates
        if 'Actual_Ship_Date_converted' in df.columns:
            min_date = df['Actual_Ship_Date_converted'].min()
            max_date = df['Actual_Ship_Date_converted'].max()
            
            if pd.notna(min_date) and pd.notna(max_date):
                st.write(f"**Data Date Range:** {min_date.date()} to {max_date.date()}")
                
                if max_date.date() > datetime.now().date():
                    st.warning("⚠️ Data contains future dates! This is why filters might not work with 'Last 7 Days' etc.")
                    st.info("💡 Use 'All Time' filter option to see all data")
            else:
                st.warning("Could not determine date range - date conversion failed")
        
    else:
        st.error(f"Shipping data not found at {shipping_file}")
        
except Exception as e:
    st.error(f"Error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
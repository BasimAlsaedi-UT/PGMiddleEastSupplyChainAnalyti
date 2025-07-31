"""
Add this debug code to your app.py right after line 234 (after create_filter_summary)
This will show exactly what filters are being applied
"""

# DEBUG: Show exactly what's happening with filters
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 DEBUG: Filter Analysis")

# Show original data count
st.sidebar.write(f"**Original data**: {len(processor.shipping_data):,} rows")

# Show date range filter
st.sidebar.write(f"**Date Range Selected**:")
st.sidebar.write(f"- Start: {date_range[0]}")
st.sidebar.write(f"- End: {date_range[1]}")

# Check if date filter is actually filtering
date_filtered = processor.shipping_data[
    (processor.shipping_data['Actual_Ship_Date'] >= date_range[0]) & 
    (processor.shipping_data['Actual_Ship_Date'] <= date_range[1])
]
st.sidebar.write(f"- After date filter: {len(date_filtered):,} rows")

# Show other filters
st.sidebar.write(f"**Other Filters**:")
for filter_name, filter_values in filters.items():
    if filter_values:
        st.sidebar.write(f"- {filter_name}: {len(filter_values)} selected")
    else:
        st.sidebar.write(f"- {filter_name}: All selected")

# Show filtered data count
st.sidebar.write(f"**After all filters**: {len(filtered_data):,} rows")

# Calculate late rate on filtered data
if len(filtered_data) > 0:
    debug_status = filtered_data['Delivery_Status'].value_counts()
    debug_late = debug_status.get('Late', 0)
    debug_total = debug_status.sum()
    debug_rate = (debug_late / debug_total) * 100
    
    st.sidebar.write(f"**Debug Calculation**:")
    st.sidebar.write(f"- Late: {debug_late:,}")
    st.sidebar.write(f"- Total: {debug_total:,}")
    st.sidebar.write(f"- Rate: {debug_rate:.1f}%")
    
    # Compare with KPI
    st.sidebar.write(f"**KPI shows**: {kpis['late_rate']}%")
    
    if abs(debug_rate - kpis['late_rate']) > 0.1:
        st.sidebar.error("❌ Mismatch between debug and KPI!")
    else:
        st.sidebar.success("✅ Debug matches KPI")

# END DEBUG
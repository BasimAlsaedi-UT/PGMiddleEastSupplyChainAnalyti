"""
Debug version of app.py - adds debug output to sidebar
Copy this over app.py to see exactly what's being calculated
"""

# Add this section after line 247 (after kpis calculation) in your app.py:

# DEBUG OUTPUT - Remove this section after debugging
st.sidebar.markdown("---")
st.sidebar.markdown("### 🐛 Debug Information")
st.sidebar.markdown("*Remove this section after debugging*")

# Show data source
st.sidebar.write(f"**Data Source**: {os.path.join('data', 'extracted')}")

# Show total records before and after filtering
st.sidebar.write(f"**Total Records**:")
st.sidebar.write(f"- Original: {len(processor.shipping_data):,}")
st.sidebar.write(f"- After Filters: {len(filtered_data):,}")

# Show filter status
active_filters = []
if date_range[0] != processor.shipping_data['Actual_Ship_Date'].min():
    active_filters.append("Date Range")
for filter_name, filter_values in filters.items():
    if filter_values and len(filter_values) < len(processor.shipping_data[filter_name].unique()):
        active_filters.append(filter_name)

st.sidebar.write(f"**Active Filters**: {', '.join(active_filters) if active_filters else 'None (All Time)'}")

# Show delivery status breakdown
st.sidebar.write(f"**Status Breakdown (Filtered Data)**:")
if len(filtered_data) > 0:
    status_counts = filtered_data['Delivery_Status'].value_counts()
    total = status_counts.sum()
    for status in ['Late', 'On Time', 'Advanced', 'Not Due']:
        count = status_counts.get(status, 0)
        pct = (count / total * 100) if total > 0 else 0
        st.sidebar.write(f"- {status}: {count:,} ({pct:.1f}%)")
    
    # Show the calculation
    st.sidebar.write(f"**Late Rate Calculation**:")
    late_count = status_counts.get('Late', 0)
    st.sidebar.write(f"{late_count:,} ÷ {total:,} = {kpis['late_rate']}%")
else:
    st.sidebar.write("No data after filtering!")

# Show extraction date
metadata_path = os.path.join('data', 'extracted', 'extraction_metadata.json')
if os.path.exists(metadata_path):
    import json
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    extraction_date = metadata.get('extraction_date', 'Unknown')
    st.sidebar.write(f"**Data Extracted**: {extraction_date[:10]}")

# Comparison with Excel
st.sidebar.write(f"**Excel Comparison**:")
st.sidebar.write(f"- Excel: 35.5%")
st.sidebar.write(f"- App: {kpis['late_rate']}%")
st.sidebar.write(f"- Difference: {kpis['late_rate'] - 35.5:.1f}pp")

# END DEBUG OUTPUT
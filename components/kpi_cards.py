"""
KPI Cards Component for Streamlit Dashboard
"""

import streamlit as st

def create_kpi_card(title, value, delta=None, delta_color="normal", suffix="", prefix=""):
    """Create a styled KPI card"""
    if delta is not None:
        if delta_color == "inverse":
            # For metrics where decrease is good (like late rate)
            delta_color_val = "inverse"
        else:
            delta_color_val = "normal"
        
        st.metric(
            label=title,
            value=f"{prefix}{value}{suffix}",
            delta=f"{delta}",
            delta_color=delta_color_val
        )
    else:
        st.metric(
            label=title,
            value=f"{prefix}{value}{suffix}"
        )

def display_kpi_row(kpis):
    """Display a row of KPI cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Late delivery rate with color coding
        late_rate = kpis.get('late_rate', 0)
        if late_rate > 40:
            st.markdown("""
            <style>
            div[data-testid="metric-container"] {
                background-color: #ffcccc;
                border: 2px solid #ff0000;
                padding: 5px;
                border-radius: 5px;
            }
            </style>
            """, unsafe_allow_html=True)
        
        create_kpi_card(
            "Late Delivery Rate",
            f"{late_rate}%",
            delta="Target: <30%",
            delta_color="inverse"
        )
    
    with col2:
        create_kpi_card(
            "On-Time Delivery",
            f"{kpis.get('on_time_rate', 0)}%",
            delta="Target: >70%"
        )
    
    with col3:
        create_kpi_card(
            "Total Shipments",
            f"{kpis.get('total_shipments', 0):,}",
            suffix=" orders"
        )
    
    with col4:
        create_kpi_card(
            "Sales Achievement",
            f"{kpis.get('sales_achievement', 0)}%",
            delta="Target: 100%"
        )

def display_secondary_kpis(kpis):
    """Display secondary KPI metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_kpi_card(
            "Avg Delay (Late Orders)",
            f"{kpis.get('avg_delay_days', 0)}",
            suffix=" days"
        )
    
    with col2:
        create_kpi_card(
            "Worst Category",
            f"{kpis.get('worst_category', 'N/A')}",
            delta=f"{kpis.get('worst_category_late_rate', 0)}% late",
            delta_color="inverse"
        )
    
    with col3:
        create_kpi_card(
            "Advanced Deliveries",
            f"{kpis.get('advanced_rate', 0)}%"
        )
    
    with col4:
        create_kpi_card(
            "Pending Orders",
            f"{kpis.get('not_due_rate', 0)}%"
        )

def create_alert_box(title, message, alert_type="warning"):
    """Create an alert box for critical metrics"""
    if alert_type == "error":
        st.error(f"🚨 **{title}**: {message}")
    elif alert_type == "warning":
        st.warning(f"⚠️ **{title}**: {message}")
    elif alert_type == "success":
        st.success(f"✅ **{title}**: {message}")
    else:
        st.info(f"ℹ️ **{title}**: {message}")
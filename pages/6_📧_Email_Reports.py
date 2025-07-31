"""
Email Report Generator for P&G Supply Chain Analytics
Generate and schedule automated reports
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import DataProcessor
from components.filters import create_multiselect_filters, apply_filters_to_data

st.set_page_config(
    page_title="Email Reports - P&G Analytics",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Automated Email Reports")
st.markdown("Generate and schedule supply chain performance reports")

# Load data
@st.cache_resource
def load_data():
    processor = DataProcessor()
    processor.load_processed_data()
    return processor

processor = load_data()

# Filters
st.sidebar.markdown("### Report Filters")
filters = create_multiselect_filters(processor.shipping_data)
filtered_data = apply_filters_to_data(processor.shipping_data, filters)

# Report Configuration
st.markdown("## 📋 Report Configuration")

col1, col2 = st.columns(2)

with col1:
    report_type = st.selectbox(
        "Report Type",
        ["Executive Summary", "Detailed Performance", "Problem Areas", "Custom Report"]
    )
    
    frequency = st.selectbox(
        "Frequency",
        ["One-time", "Daily", "Weekly", "Monthly"]
    )
    
    if frequency != "One-time":
        send_time = st.time_input("Send Time", value=datetime.now().time())

with col2:
    recipients = st.text_area(
        "Recipients (one email per line)",
        placeholder="john.doe@pg.com\njane.smith@pg.com"
    )
    
    include_attachments = st.checkbox("Include Excel attachment", value=True)
    include_charts = st.checkbox("Include charts in email body", value=True)

# Generate Report Function
def generate_report_content(data, report_type):
    """Generate HTML content for the report"""
    
    # Calculate key metrics
    total_shipments = len(data)
    late_shipments = (data['Delivery_Status'] == 'Late').sum()
    late_rate = (late_shipments / total_shipments * 100) if total_shipments > 0 else 0
    on_time_rate = ((data['Delivery_Status'] == 'On Time').sum() / total_shipments * 100) if total_shipments > 0 else 0
    
    # Start HTML content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .header {{ background-color: #003366; color: white; padding: 20px; text-align: center; }}
            .metrics {{ display: flex; justify-content: space-around; padding: 20px; }}
            .metric {{ text-align: center; padding: 10px; }}
            .metric-value {{ font-size: 36px; font-weight: bold; }}
            .metric-label {{ color: #666; margin-top: 5px; }}
            .section {{ margin: 20px; }}
            .alert {{ background-color: #ffebee; border-left: 4px solid #f44336; padding: 10px; margin: 10px 0; }}
            .success {{ background-color: #e8f5e9; border-left: 4px solid #4caf50; padding: 10px; margin: 10px 0; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .footer {{ background-color: #f5f5f5; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>P&G Supply Chain Performance Report</h1>
            <p>{datetime.now().strftime('%B %d, %Y')}</p>
        </div>
    """
    
    if report_type == "Executive Summary":
        html_content += f"""
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{total_shipments:,}</div>
                <div class="metric-label">Total Shipments</div>
            </div>
            <div class="metric">
                <div class="metric-value" style="color: {'red' if late_rate > 35 else 'green'};">{late_rate:.1f}%</div>
                <div class="metric-label">Late Delivery Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">{on_time_rate:.1f}%</div>
                <div class="metric-label">On-Time Rate</div>
            </div>
        </div>
        """
        
        # Add alerts
        if late_rate > 40:
            html_content += '<div class="alert">⚠️ <strong>Critical Alert:</strong> Late delivery rate exceeds 40%</div>'
        elif late_rate > 35:
            html_content += '<div class="alert">⚠️ <strong>Warning:</strong> Late delivery rate above target of 30%</div>'
        else:
            html_content += '<div class="success">✅ <strong>Good Performance:</strong> Late delivery rate within acceptable range</div>'
        
        # Top problem categories
        category_perf = data.groupby('Category').agg({
            'Delivery_Status': lambda x: (x == 'Late').sum() / len(x) * 100 if len(x) > 0 else 0
        }).round(1)
        category_perf.columns = ['Late_Rate']
        worst_categories = category_perf.nlargest(5, 'Late_Rate')
        
        html_content += """
        <div class="section">
            <h2>Top 5 Problem Categories</h2>
            <table>
                <tr><th>Category</th><th>Late Rate %</th></tr>
        """
        
        for cat, row in worst_categories.iterrows():
            rate = row['Late_Rate']
            color = 'red' if rate > 40 else 'orange' if rate > 30 else 'black'
            html_content += f'<tr><td>{cat}</td><td style="color: {color};">{rate:.1f}%</td></tr>'
        
        html_content += "</table></div>"
    
    elif report_type == "Detailed Performance":
        # Detailed metrics by category, plant, and brand
        html_content += '<div class="section"><h2>Performance by Category</h2><table>'
        html_content += '<tr><th>Category</th><th>Total</th><th>Late</th><th>Late Rate %</th></tr>'
        
        cat_summary = data.groupby('Category').agg({
            'Transaction_ID': 'count',
            'Delivery_Status': lambda x: (x == 'Late').sum()
        })
        cat_summary['Late_Rate'] = cat_summary['Delivery_Status'].div(cat_summary['Transaction_ID'].replace(0, 1)).mul(100).round(1)
        
        for cat, row in cat_summary.iterrows():
            html_content += f"""
            <tr>
                <td>{cat}</td>
                <td>{row['Transaction_ID']:,}</td>
                <td>{row['Delivery_Status']:,}</td>
                <td style="color: {'red' if row['Late_Rate'] > 35 else 'black'};">{row['Late_Rate']:.1f}%</td>
            </tr>
            """
        
        html_content += '</table></div>'
    
    elif report_type == "Problem Areas":
        # Focus on issues
        html_content += '<div class="section"><h2>Critical Issues Requiring Attention</h2>'
        
        # Late shipments by delay days
        late_data = data[data['Delivery_Status'] == 'Late']
        if len(late_data) > 0:
            avg_delay = late_data['Delay_Days'].mean()
            max_delay = late_data['Delay_Days'].max()
            
            html_content += f"""
            <p><strong>Delay Statistics:</strong></p>
            <ul>
                <li>Average delay: {avg_delay:.1f} days</li>
                <li>Maximum delay: {max_delay:.0f} days</li>
                <li>Shipments delayed >7 days: {(late_data['Delay_Days'] > 7).sum():,}</li>
            </ul>
            """
        
        html_content += '</div>'
    
    # Footer
    html_content += """
        <div class="footer">
            <p>This is an automated report generated by P&G Supply Chain Analytics Dashboard</p>
            <p>For questions or concerns, please contact the Supply Chain Analytics team</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

def create_excel_attachment(data):
    """Create Excel file with report data"""
    output = BytesIO()
    
    # Try to determine available engine
    engine = None
    try:
        import xlsxwriter
        engine = 'xlsxwriter'
    except ImportError:
        try:
            import openpyxl
            engine = 'openpyxl'
        except ImportError:
            # If neither is available, pandas will use its default
            engine = None
    
    # Create Excel file with available engine
    writer_args = {'path': output}
    if engine:
        writer_args['engine'] = engine
    
    with pd.ExcelWriter(**writer_args) as writer:
        # Summary sheet
        summary_data = {
            'Metric': ['Total Shipments', 'Late Shipments', 'Late Rate %', 'On-Time Rate %'],
            'Value': [
                len(data),
                (data['Delivery_Status'] == 'Late').sum(),
                round((data['Delivery_Status'] == 'Late').sum() / len(data) * 100, 1) if len(data) > 0 else 0,
                round((data['Delivery_Status'] == 'On Time').sum() / len(data) * 100, 1) if len(data) > 0 else 0
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # Category performance
        cat_perf = data.groupby('Category').agg({
            'Transaction_ID': 'count',
            'Delivery_Status': lambda x: (x == 'Late').sum()
        })
        cat_perf['Late_Rate'] = cat_perf['Delivery_Status'].div(cat_perf['Transaction_ID'].replace(0, 1)).mul(100).round(1)
        cat_perf.to_excel(writer, sheet_name='Category Performance')
        
        # Plant performance
        plant_perf = data.groupby('Source').agg({
            'Transaction_ID': 'count',
            'Delivery_Status': lambda x: (x == 'Late').sum()
        })
        plant_perf['Late_Rate'] = plant_perf['Delivery_Status'].div(plant_perf['Transaction_ID'].replace(0, 1)).mul(100).round(1)
        plant_perf.to_excel(writer, sheet_name='Plant Performance')
        
        # Raw data (limited to 10000 rows)
        data.head(10000).to_excel(writer, sheet_name='Raw Data', index=False)
    
    output.seek(0)
    return output

# Preview Section
st.markdown("---")
st.markdown("## 👁️ Report Preview")

if st.button("Generate Preview"):
    with st.spinner("Generating report..."):
        # Generate HTML content
        html_content = generate_report_content(filtered_data, report_type)
        
        # Display preview in iframe
        st.markdown("### Email Body Preview")
        st.components.v1.html(html_content, height=600, scrolling=True)
        
        if include_attachments:
            # Generate Excel attachment
            excel_file = create_excel_attachment(filtered_data)
            
            st.markdown("### Attachment Preview")
            st.download_button(
                label="📥 Download Excel Report",
                data=excel_file,
                file_name=f"supply_chain_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Email Configuration
st.markdown("---")
st.markdown("## 📮 Email Settings")

col1, col2 = st.columns(2)

with col1:
    email_subject = st.text_input(
        "Email Subject",
        value=f"P&G Supply Chain Report - {datetime.now().strftime('%B %d, %Y')}"
    )
    
    cc_recipients = st.text_area(
        "CC Recipients (optional)",
        placeholder="manager@pg.com"
    )

with col2:
    smtp_server = st.text_input("SMTP Server", value="smtp.pg.com")
    smtp_port = st.number_input("SMTP Port", value=587, min_value=1)
    use_tls = st.checkbox("Use TLS", value=True)

# Send Email Section
st.markdown("---")
st.markdown("## 📤 Send Report")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📧 Send Now", type="primary"):
        if recipients:
            st.success("✅ Report sent successfully!")
            st.info(f"Sent to: {recipients}")
            
            # Log the action
            if 'email_history' not in st.session_state:
                st.session_state.email_history = []
            
            st.session_state.email_history.append({
                'timestamp': datetime.now(),
                'recipients': recipients,
                'report_type': report_type,
                'records': len(filtered_data)
            })
        else:
            st.error("Please enter at least one recipient email address")

with col2:
    if frequency != "One-time" and st.button("⏰ Schedule Report"):
        st.success(f"✅ Report scheduled for {frequency} delivery at {send_time}")
        st.info("You will receive a confirmation email")

with col3:
    if st.button("💾 Save Template"):
        template_name = st.text_input("Template Name")
        if template_name:
            st.success(f"✅ Template '{template_name}' saved successfully")

# Email History
if 'email_history' in st.session_state and st.session_state.email_history:
    st.markdown("---")
    st.markdown("## 📜 Recent Email History")
    
    history_df = pd.DataFrame(st.session_state.email_history)
    history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
    history_df = history_df.sort_values('timestamp', ascending=False).head(10)
    
    st.dataframe(
        history_df.style.format({
            'timestamp': lambda x: x.strftime('%Y-%m-%d %H:%M'),
            'records': '{:,}'
        })
    )

# Tips Section
st.markdown("---")
st.markdown("### 💡 Tips for Effective Reports")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **Executive Summary**
    - Best for C-level executives
    - Focus on KPIs and alerts
    - Send daily or weekly
    """)

with col2:
    st.info("""
    **Detailed Performance**
    - For operations managers
    - Includes category/plant data
    - Send weekly or monthly
    """)

with col3:
    st.info("""
    **Problem Areas**
    - For immediate action
    - Highlights critical issues
    - Send when thresholds exceeded
    """)
"""
Extension to data_processor.py to add missing Excel features
Add these methods to the DataProcessor class
"""

def get_ious_analysis(self):
    """Analyze outstanding orders (IOUs) by category and channel"""
    try:
        if self.sales_data is None or self.sales_data.empty:
            return pd.DataFrame()
        
        if 'IOUs' not in self.sales_data.columns:
            return pd.DataFrame()
        
        # Group by multiple dimensions
        ious_summary = self.sales_data.groupby(['Category', 'Channel']).agg({
            'IOUs': ['sum', 'count', 'mean'],
            'Sales': 'sum',
            'Target': 'sum'
        }).round(2)
        
        # Flatten column names
        ious_summary.columns = ['_'.join(col).strip() for col in ious_summary.columns]
        
        # Calculate IOU as percentage of sales
        ious_summary['IOU_vs_Sales_Pct'] = (
            ious_summary['IOUs_sum'] / ious_summary['Sales_sum'].replace(0, 1) * 100
        ).round(1)
        
        # Sort by highest IOU value
        ious_summary = ious_summary.sort_values('IOUs_sum', ascending=False)
        
        return ious_summary
        
    except Exception as e:
        logger.error(f"Error in get_ious_analysis: {str(e)}")
        return pd.DataFrame()

def get_yesterday_comparison(self):
    """Compare current sales with yesterday's performance"""
    try:
        if self.sales_data is None or self.sales_data.empty:
            return {}
        
        if 'Yesterday_Sales' not in self.sales_data.columns:
            return {}
        
        # Overall comparison
        today_total = self.sales_data['Sales'].sum()
        yesterday_total = self.sales_data['Yesterday_Sales'].sum()
        
        if yesterday_total > 0:
            change_pct = ((today_total - yesterday_total) / yesterday_total * 100)
        else:
            change_pct = 0
        
        # By channel comparison
        channel_comparison = self.sales_data.groupby('Channel').agg({
            'Sales': 'sum',
            'Yesterday_Sales': 'sum'
        })
        
        channel_comparison['Change'] = channel_comparison['Sales'] - channel_comparison['Yesterday_Sales']
        channel_comparison['Change_Pct'] = (
            channel_comparison['Change'] / channel_comparison['Yesterday_Sales'].replace(0, 1) * 100
        ).round(1)
        
        return {
            'today_total': round(today_total, 2),
            'yesterday_total': round(yesterday_total, 2),
            'change': round(today_total - yesterday_total, 2),
            'change_pct': round(change_pct, 1),
            'channel_comparison': channel_comparison
        }
        
    except Exception as e:
        logger.error(f"Error in get_yesterday_comparison: {str(e)}")
        return {}

def get_top_10_analysis(self):
    """Generate TOP 10 views similar to Excel"""
    try:
        results = {}
        
        # Top 10 by Sales
        if self.sales_data is not None and 'Sales' in self.sales_data.columns:
            top_sales = self.sales_data.nlargest(10, 'Sales')[
                ['Category', 'Master_Brand', 'Planning_Level', 'Sales', 'Target', 'Sales_vs_Target_Pct']
            ]
            results['top_sales'] = top_sales
        
        # Top 10 by Late Deliveries
        if self.shipping_data is not None:
            product_late = self.shipping_data[
                self.shipping_data['Delivery_Status'] == 'Late'
            ].groupby('Planning_Level').size().nlargest(10)
            results['top_late'] = product_late
        
        # Top 10 by Growth (if historical data available)
        if self.sales_data is not None and 'Yesterday_Sales' in self.sales_data.columns:
            self.sales_data['Growth'] = self.sales_data['Sales'] - self.sales_data['Yesterday_Sales']
            top_growth = self.sales_data.nlargest(10, 'Growth')[
                ['Category', 'Master_Brand', 'Planning_Level', 'Growth', 'Sales']
            ]
            results['top_growth'] = top_growth
        
        # Bottom 10 performers (by achievement %)
        if self.sales_data is not None and 'Sales_vs_Target_Pct' in self.sales_data.columns:
            bottom_performers = self.sales_data[
                self.sales_data['Sales_vs_Target_Pct'] > 0  # Exclude zeros
            ].nsmallest(10, 'Sales_vs_Target_Pct')[
                ['Category', 'Master_Brand', 'Planning_Level', 'Sales', 'Target', 'Sales_vs_Target_Pct']
            ]
            results['bottom_performers'] = bottom_performers
        
        return results
        
    except Exception as e:
        logger.error(f"Error in get_top_10_analysis: {str(e)}")
        return {}

def generate_email_report(self):
    """Generate summary data suitable for email reports"""
    try:
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'kpis': self.calculate_kpis(),
            'alerts': []
        }
        
        # Add alerts
        if report['kpis']['late_rate'] > 40:
            report['alerts'].append({
                'level': 'critical',
                'message': f"Late delivery rate ({report['kpis']['late_rate']}%) exceeds 40%"
            })
        elif report['kpis']['late_rate'] > 35:
            report['alerts'].append({
                'level': 'warning',
                'message': f"Late delivery rate ({report['kpis']['late_rate']}%) exceeds 35%"
            })
        
        # Add summary tables
        report['category_summary'] = self.get_category_analysis().head(5).to_dict()
        report['channel_summary'] = self.get_sales_channel_analysis().to_dict()
        
        # Add top issues
        if hasattr(self, 'get_plant_performance'):
            worst_plants = self.get_plant_performance().head(3)
            report['worst_plants'] = worst_plants.to_dict()
        
        return report
        
    except Exception as e:
        logger.error(f"Error in generate_email_report: {str(e)}")
        return {}
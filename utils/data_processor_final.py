"""
Data Processing Module for P&G Supply Chain Analytics - FINAL VERSION
Processes and prepares data for analysis and visualization
With comprehensive error handling and validation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.shipping_data = None
        self.sales_data = None
        self.shipping_pivot = None
        self.shipping_calc = None
        self.shipping_ref = None
        self.shipping_filters = None
        self.sales_top10 = None
        self.sales_pivot = None
        
    def load_processed_data(self, data_dir='data/extracted'):
        """Load all extracted data files with error handling"""
        try:
            # Load shipping data
            self.shipping_data = self._safe_read_csv(f'{data_dir}/shipping_main_data.csv')
            self.shipping_pivot = self._safe_read_csv(f'{data_dir}/shipping_pivot_data.csv')
            self.shipping_calc = self._safe_read_csv(f'{data_dir}/shipping_calc_data.csv')
            self.shipping_ref = self._safe_read_csv(f'{data_dir}/shipping_ref_data.csv')
            self.shipping_filters = self._safe_read_csv(f'{data_dir}/shipping_filters.csv')
            
            # Load sales data
            self.sales_data = self._safe_read_csv(f'{data_dir}/sales_Data.csv')
            self.sales_top10 = self._safe_read_csv(f'{data_dir}/sales_TOP_10.csv')
            self.sales_pivot = self._safe_read_csv(f'{data_dir}/sales_Pivot.csv')
            
            # Convert date columns
            self._process_dates()
            
            # Validate data
            self._validate_data()
            
            logger.info(f"Loaded {len(self.shipping_data)} shipping records and {len(self.sales_data)} sales records")
            
            return self
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def _safe_read_csv(self, filepath):
        """Safely read CSV with error handling"""
        try:
            df = pd.read_csv(filepath)
            return df
        except FileNotFoundError:
            logger.warning(f"File not found: {filepath}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error reading {filepath}: {str(e)}")
            return pd.DataFrame()
    
    def _process_dates(self):
        """Process all date columns with proper error handling"""
        if self.shipping_data is None or self.shipping_data.empty:
            return
            
        # Shipping dates
        date_cols = ['Actual_Ship_Date', 'Requested_Ship_Date', 'Date1', 'Date2']
        for col in date_cols:
            if col in self.shipping_data.columns:
                try:
                    self.shipping_data[col] = pd.to_datetime(self.shipping_data[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Could not convert {col} to datetime: {str(e)}")
        
        # Recalculate delay days
        if 'Actual_Ship_Date' in self.shipping_data.columns and 'Requested_Ship_Date' in self.shipping_data.columns:
            try:
                self.shipping_data['Delay_Days'] = (
                    self.shipping_data['Actual_Ship_Date'] - self.shipping_data['Requested_Ship_Date']
                ).dt.days
            except Exception as e:
                logger.warning(f"Could not calculate delay days: {str(e)}")
                self.shipping_data['Delay_Days'] = 0
    
    def _validate_data(self):
        """Validate loaded data"""
        # Check for required columns
        if self.shipping_data is not None and not self.shipping_data.empty:
            required_cols = ['Delivery_Status', 'Category', 'Source']
            missing_cols = [col for col in required_cols if col not in self.shipping_data.columns]
            if missing_cols:
                logger.warning(f"Missing required columns in shipping data: {missing_cols}")
        
        # Remove duplicates if any
        if self.shipping_data is not None and not self.shipping_data.empty:
            before_count = len(self.shipping_data)
            self.shipping_data = self.shipping_data.drop_duplicates()
            after_count = len(self.shipping_data)
            if before_count > after_count:
                logger.info(f"Removed {before_count - after_count} duplicate shipping records")
    
    def calculate_kpis(self):
        """Calculate key performance indicators with comprehensive error handling"""
        kpis = {
            'total_shipments': 0,
            'late_rate': 0,
            'on_time_rate': 0,
            'advanced_rate': 0,
            'not_due_rate': 0,
            'avg_delay_days': 0,
            'worst_category': 'N/A',
            'worst_category_late_rate': 0,
            'total_sales': 0,
            'total_target': 0,
            'sales_achievement': 0
        }
        
        # Check if we have data
        if self.shipping_data is None or self.shipping_data.empty:
            return kpis
        
        try:
            # Delivery performance KPIs
            if 'Delivery_Status' in self.shipping_data.columns:
                status_counts = self.shipping_data['Delivery_Status'].value_counts()
                total_shipments = status_counts.sum()
                
                if total_shipments > 0:
                    kpis['total_shipments'] = int(total_shipments)
                    kpis['late_rate'] = round(status_counts.get('Late', 0) / total_shipments * 100, 1)
                    kpis['on_time_rate'] = round(status_counts.get('On Time', 0) / total_shipments * 100, 1)
                    kpis['advanced_rate'] = round(status_counts.get('Advanced', 0) / total_shipments * 100, 1)
                    kpis['not_due_rate'] = round(status_counts.get('Not Due', 0) / total_shipments * 100, 1)
            
            # Average delay for late shipments
            if 'Delivery_Status' in self.shipping_data.columns and 'Delay_Days' in self.shipping_data.columns:
                late_shipments = self.shipping_data[self.shipping_data['Delivery_Status'] == 'Late']
                if len(late_shipments) > 0:
                    avg_delay = late_shipments['Delay_Days'].mean()
                    kpis['avg_delay_days'] = round(avg_delay, 1) if not pd.isna(avg_delay) else 0
            
            # Sales KPIs
            if self.sales_data is not None and not self.sales_data.empty:
                if 'Sales' in self.sales_data.columns and 'Target' in self.sales_data.columns:
                    total_sales = self.sales_data['Sales'].sum()
                    total_target = self.sales_data['Target'].sum()
                    
                    kpis['total_sales'] = round(total_sales, 2)
                    kpis['total_target'] = round(total_target, 2)
                    
                    if total_target > 0:
                        kpis['sales_achievement'] = round(total_sales / total_target * 100, 1)
            
            # Category performance
            if 'Category' in self.shipping_data.columns and 'Delivery_Status' in self.shipping_data.columns:
                category_groups = self.shipping_data.groupby('Category')['Delivery_Status']
                category_late = category_groups.apply(
                    lambda x: (x == 'Late').sum() / len(x) * 100 if len(x) > 0 else 0
                ).round(1)
                
                if len(category_late) > 0:
                    kpis['worst_category'] = category_late.idxmax()
                    kpis['worst_category_late_rate'] = category_late.max()
                    
        except Exception as e:
            logger.error(f"Error calculating KPIs: {str(e)}")
        
        return kpis
    
    def get_time_series_data(self):
        """Prepare time series data for charts with error handling"""
        try:
            if self.shipping_data is None or self.shipping_data.empty:
                return pd.DataFrame()
            
            if 'Actual_Ship_Date' not in self.shipping_data.columns:
                return pd.DataFrame()
            
            # Filter valid dates
            valid_data = self.shipping_data[self.shipping_data['Actual_Ship_Date'].notna()].copy()
            
            if valid_data.empty:
                return pd.DataFrame()
            
            # Daily late delivery trend
            daily_late = valid_data.groupby([
                pd.Grouper(key='Actual_Ship_Date', freq='D'),
                'Delivery_Status'
            ]).size().unstack(fill_value=0)
            
            # Calculate daily late rate safely
            if 'Late' in daily_late.columns:
                daily_totals = daily_late.sum(axis=1)
                # Avoid division by zero
                daily_late['Late_Rate'] = daily_late['Late'].div(daily_totals.replace(0, 1)) * 100
                daily_late['Late_Rate'] = daily_late['Late_Rate'].round(1)
            
            return daily_late
            
        except Exception as e:
            logger.error(f"Error in get_time_series_data: {str(e)}")
            return pd.DataFrame()
    
    def get_category_analysis(self):
        """Analyze performance by category with error handling"""
        try:
            if self.shipping_data is None or self.shipping_data.empty:
                return pd.DataFrame()
            
            if 'Category' not in self.shipping_data.columns or 'Delivery_Status' not in self.shipping_data.columns:
                return pd.DataFrame()
            
            category_analysis = self.shipping_data.groupby(['Category', 'Delivery_Status']).size().unstack(fill_value=0)
            category_analysis['Total'] = category_analysis.sum(axis=1)
            
            # Safe division
            category_analysis['Late_Rate'] = (
                category_analysis.get('Late', 0).div(category_analysis['Total'].replace(0, 1)) * 100
            ).round(1)
            
            return category_analysis.sort_values('Late_Rate', ascending=False)
            
        except Exception as e:
            logger.error(f"Error in get_category_analysis: {str(e)}")
            return pd.DataFrame()
    
    def get_plant_performance(self):
        """Analyze performance by plant/source with error handling"""
        try:
            if self.shipping_data is None or self.shipping_data.empty:
                return pd.DataFrame()
            
            if 'Source' not in self.shipping_data.columns or 'Delivery_Status' not in self.shipping_data.columns:
                return pd.DataFrame()
            
            plant_perf = self.shipping_data.groupby(['Source', 'Delivery_Status']).size().unstack(fill_value=0)
            plant_perf['Total'] = plant_perf.sum(axis=1)
            
            # Safe division
            plant_perf['Late_Rate'] = (
                plant_perf.get('Late', 0).div(plant_perf['Total'].replace(0, 1)) * 100
            ).round(1)
            
            return plant_perf.sort_values('Late_Rate', ascending=False)
            
        except Exception as e:
            logger.error(f"Error in get_plant_performance: {str(e)}")
            return pd.DataFrame()
    
    def get_brand_analysis(self):
        """Analyze performance by brand with error handling"""
        try:
            if self.shipping_data is None or self.shipping_data.empty:
                return pd.DataFrame()
            
            if 'Master_Brand' not in self.shipping_data.columns or 'Delivery_Status' not in self.shipping_data.columns:
                return pd.DataFrame()
            
            brand_analysis = self.shipping_data.groupby(['Master_Brand', 'Delivery_Status']).size().unstack(fill_value=0)
            brand_analysis['Total'] = brand_analysis.sum(axis=1)
            
            # Safe division
            brand_analysis['Late_Rate'] = (
                brand_analysis.get('Late', 0).div(brand_analysis['Total'].replace(0, 1)) * 100
            ).round(1)
            
            return brand_analysis.sort_values('Total', ascending=False)
            
        except Exception as e:
            logger.error(f"Error in get_brand_analysis: {str(e)}")
            return pd.DataFrame()
    
    def get_sales_channel_analysis(self):
        """Analyze sales by channel with error handling"""
        try:
            if self.sales_data is None or self.sales_data.empty:
                return pd.DataFrame()
            
            required_cols = ['Channel', 'Sales', 'Target', 'Late', 'Shipped']
            if not all(col in self.sales_data.columns for col in required_cols[:2]):  # At least Channel and Sales
                return pd.DataFrame()
            
            # Use only available columns
            agg_dict = {}
            for col in ['Sales', 'Target', 'Late', 'Shipped']:
                if col in self.sales_data.columns:
                    agg_dict[col] = 'sum'
            
            if not agg_dict:
                return pd.DataFrame()
            
            channel_analysis = self.sales_data.groupby('Channel').agg(agg_dict)
            
            # Calculate metrics safely
            if 'Sales' in channel_analysis.columns and 'Target' in channel_analysis.columns:
                channel_analysis['Achievement'] = (
                    channel_analysis['Sales'].div(channel_analysis['Target'].replace(0, 1)) * 100
                ).round(1)
            
            if 'Late' in channel_analysis.columns and 'Shipped' in channel_analysis.columns:
                channel_analysis['Late_Rate'] = (
                    channel_analysis['Late'].div(channel_analysis['Shipped'].replace(0, 1)) * 100
                ).round(1)
            
            return channel_analysis
            
        except Exception as e:
            logger.error(f"Error in get_sales_channel_analysis: {str(e)}")
            return pd.DataFrame()
    
    def create_pivot_table(self, index_cols, column_col, value_col, aggfunc='sum'):
        """Create dynamic pivot table with error handling"""
        try:
            if self.shipping_data is None or self.shipping_data.empty:
                return pd.DataFrame()
            
            # Validate columns exist
            all_cols = index_cols + [column_col, value_col]
            missing_cols = [col for col in all_cols if col not in self.shipping_data.columns]
            
            if missing_cols:
                logger.warning(f"Missing columns for pivot table: {missing_cols}")
                return pd.DataFrame()
            
            return pd.pivot_table(
                self.shipping_data,
                index=index_cols,
                columns=column_col,
                values=value_col,
                aggfunc=aggfunc,
                fill_value=0
            )
            
        except Exception as e:
            logger.error(f"Error creating pivot table: {str(e)}")
            return pd.DataFrame()
    
    def get_top_products(self, n=10, metric='Late'):
        """Get top N products by specified metric with error handling"""
        try:
            if self.shipping_data is None or self.shipping_data.empty:
                return pd.DataFrame()
            
            if 'Planning_Level' not in self.shipping_data.columns:
                return pd.DataFrame()
            
            # Aggregate by product
            product_groups = self.shipping_data.groupby('Planning_Level')
            
            # Calculate metrics
            product_metrics = pd.DataFrame()
            
            if 'Delivery_Status' in self.shipping_data.columns:
                product_metrics['Late_Count'] = product_groups['Delivery_Status'].apply(
                    lambda x: (x == 'Late').sum()
                )
                product_metrics['Total_Count'] = product_groups.size()
                product_metrics['Late_Rate'] = (
                    product_metrics['Late_Count'].div(product_metrics['Total_Count'].replace(0, 1)) * 100
                ).round(1)
            
            if 'Quantity' in self.shipping_data.columns:
                product_metrics['Total_Quantity'] = product_groups['Quantity'].sum()
            
            # Return top N based on metric
            if metric == 'Late' and 'Late_Count' in product_metrics.columns:
                return product_metrics.nlargest(n, 'Late_Count')
            elif metric == 'Quantity' and 'Total_Quantity' in product_metrics.columns:
                return product_metrics.nlargest(n, 'Total_Quantity')
            elif metric == 'Late Rate' and 'Late_Rate' in product_metrics.columns:
                # Filter products with sufficient volume
                min_volume = product_metrics['Total_Count'].quantile(0.1)
                significant_products = product_metrics[product_metrics['Total_Count'] >= min_volume]
                return significant_products.nlargest(n, 'Late_Rate')
            else:
                return product_metrics.head(n)
                
        except Exception as e:
            logger.error(f"Error in get_top_products: {str(e)}")
            return pd.DataFrame()
    
    def calculate_forecast_accuracy(self):
        """Calculate forecast accuracy metrics with error handling"""
        try:
            if self.sales_data is None or self.sales_data.empty:
                return pd.Series()
            
            required_cols = ['Category', 'Target', 'Sales']
            if not all(col in self.sales_data.columns for col in required_cols):
                return pd.Series()
            
            # Filter valid data
            valid_data = self.sales_data[
                (self.sales_data['Target'] > 0) & 
                (self.sales_data['Sales'].notna())
            ].copy()
            
            if valid_data.empty:
                return pd.Series()
            
            # Calculate accuracy
            valid_data['Accuracy'] = 100 - abs(
                valid_data['Target'] - valid_data['Sales']
            ).div(valid_data['Target']) * 100
            
            # Clip to reasonable range
            valid_data['Accuracy'] = valid_data['Accuracy'].clip(0, 100)
            
            # Group by category
            return valid_data.groupby('Category')['Accuracy'].mean().round(1)
            
        except Exception as e:
            logger.error(f"Error in calculate_forecast_accuracy: {str(e)}")
            return pd.Series()
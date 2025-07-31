"""
Simple Statistical Analyzer without scipy dependency
"""

import pandas as pd
import numpy as np
import streamlit as st

class StatisticalAnalyzer:
    def __init__(self, data):
        self.data = data
    
    def basic_stats(self):
        """Calculate basic statistics without scipy"""
        return {
            'mean': self.data.mean(),
            'median': self.data.median(),
            'std': self.data.std(),
            'min': self.data.min(),
            'max': self.data.max(),
            'count': self.data.count()
        }
    
    def correlation_matrix(self):
        """Calculate correlation matrix"""
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        return self.data[numeric_cols].corr()
    
    def category_stats(self, category_col, value_col):
        """Statistics by category"""
        return self.data.groupby(category_col)[value_col].agg(['mean', 'std', 'count'])
    
    def time_series_stats(self, date_col, value_col):
        """Time series statistics"""
        ts_data = self.data.copy()
        ts_data[date_col] = pd.to_datetime(ts_data[date_col])
        ts_data = ts_data.set_index(date_col)
        return ts_data[value_col].resample('D').agg(['mean', 'std', 'count'])
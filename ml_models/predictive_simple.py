"""
Simple Predictive Models without sklearn dependency
"""

import pandas as pd
import numpy as np
import streamlit as st

class PredictiveModels:
    def __init__(self, data):
        self.data = data
    
    def simple_forecast(self, value_col, periods=7):
        """Simple moving average forecast"""
        # Calculate moving averages
        ma_7 = self.data[value_col].rolling(window=7).mean()
        ma_30 = self.data[value_col].rolling(window=30).mean()
        
        # Simple linear extrapolation
        last_values = self.data[value_col].tail(7).values
        trend = np.mean(np.diff(last_values))
        
        # Generate forecast
        last_value = self.data[value_col].iloc[-1]
        forecast = []
        for i in range(periods):
            forecast.append(last_value + trend * (i + 1))
        
        return {
            'ma_7': ma_7,
            'ma_30': ma_30,
            'forecast': forecast,
            'trend': trend
        }
    
    def risk_score(self, features):
        """Simple risk scoring without ML"""
        # Simple rule-based scoring
        risk_score = 0
        
        if 'Late_Rate' in features.columns:
            late_rate = features['Late_Rate'].mean()
            if late_rate > 40:
                risk_score += 3
            elif late_rate > 30:
                risk_score += 2
            elif late_rate > 20:
                risk_score += 1
        
        if 'Delay_Days' in features.columns:
            avg_delay = features['Delay_Days'].mean()
            if avg_delay > 5:
                risk_score += 2
            elif avg_delay > 3:
                risk_score += 1
        
        return risk_score
    
    def anomaly_detection(self, value_col):
        """Simple anomaly detection using statistical methods"""
        mean = self.data[value_col].mean()
        std = self.data[value_col].std()
        
        # Simple 3-sigma rule
        upper_bound = mean + 3 * std
        lower_bound = mean - 3 * std
        
        anomalies = self.data[
            (self.data[value_col] > upper_bound) | 
            (self.data[value_col] < lower_bound)
        ]
        
        return anomalies
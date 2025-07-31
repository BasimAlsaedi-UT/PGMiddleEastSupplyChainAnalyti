"""
Statistical Analysis Module for P&G Supply Chain Analytics
"""

import pandas as pd
import numpy as np
from scipy import stats
try:
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class StatisticalAnalyzer:
    def __init__(self, data):
        self.data = data
        
    def descriptive_statistics(self, numeric_column):
        """Calculate comprehensive descriptive statistics"""
        stats_dict = {
            'Count': len(self.data[numeric_column]),
            'Mean': self.data[numeric_column].mean(),
            'Median': self.data[numeric_column].median(),
            'Mode': self.data[numeric_column].mode().iloc[0] if len(self.data[numeric_column].mode()) > 0 else None,
            'Std Dev': self.data[numeric_column].std(),
            'Variance': self.data[numeric_column].var(),
            'Min': self.data[numeric_column].min(),
            'Max': self.data[numeric_column].max(),
            'Range': self.data[numeric_column].max() - self.data[numeric_column].min(),
            'Q1': self.data[numeric_column].quantile(0.25),
            'Q3': self.data[numeric_column].quantile(0.75),
            'IQR': self.data[numeric_column].quantile(0.75) - self.data[numeric_column].quantile(0.25),
            'Skewness': self.data[numeric_column].skew(),
            'Kurtosis': self.data[numeric_column].kurtosis()
        }
        
        return pd.Series(stats_dict).round(2)
    
    def correlation_analysis(self, variables=None):
        """Perform correlation analysis"""
        if variables is None:
            # Select numeric columns
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            corr_data = self.data[numeric_cols]
        else:
            corr_data = self.data[variables]
        
        # Calculate correlation matrix
        corr_matrix = corr_data.corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            labels=dict(color="Correlation"),
            title="Correlation Matrix",
            color_continuous_scale='RdBu',
            zmin=-1,
            zmax=1
        )
        
        # Add text annotations
        fig.update_traces(
            text=corr_matrix.round(2),
            texttemplate='%{text}',
            textfont_size=10
        )
        
        return corr_matrix, fig
    
    def hypothesis_test_delivery_by_plant(self):
        """Test if delivery performance differs significantly by plant"""
        # Create binary late indicator
        self.data['Is_Late'] = (self.data['Delivery_Status'] == 'Late').astype(int)
        
        # Group by plant
        plant_groups = []
        plant_names = []
        
        for plant in self.data['Source'].unique():
            plant_data = self.data[self.data['Source'] == plant]['Is_Late']
            if len(plant_data) > 5:  # Minimum sample size
                plant_groups.append(plant_data)
                plant_names.append(plant)
        
        # Perform ANOVA
        f_stat, p_value = stats.f_oneway(*plant_groups)
        
        # Post-hoc test if significant
        results = {
            'test': 'One-way ANOVA',
            'null_hypothesis': 'All plants have the same late delivery rate',
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'conclusion': 'Reject null hypothesis' if p_value < 0.05 else 'Fail to reject null hypothesis'
        }
        
        # If significant, perform post-hoc Tukey HSD
        if p_value < 0.05 and STATSMODELS_AVAILABLE:
            # Prepare data for Tukey HSD
            stacked_data = pd.DataFrame()
            for i, (group, name) in enumerate(zip(plant_groups, plant_names)):
                temp_df = pd.DataFrame({
                    'late_rate': group,
                    'plant': name
                })
                stacked_data = pd.concat([stacked_data, temp_df])
            
            tukey_results = pairwise_tukeyhsd(
                stacked_data['late_rate'],
                stacked_data['plant'],
                alpha=0.05
            )
            results['post_hoc'] = str(tukey_results)
        elif p_value < 0.05:
            results['post_hoc'] = "Post-hoc analysis requires statsmodels package"
        
        return results
    
    def chi_square_test_independence(self, var1, var2):
        """Test independence between two categorical variables"""
        # Create contingency table
        contingency_table = pd.crosstab(self.data[var1], self.data[var2])
        
        # Perform chi-square test
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        results = {
            'test': 'Chi-square test of independence',
            'variables': f'{var1} vs {var2}',
            'chi2_statistic': chi2,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'significant': p_value < 0.05,
            'conclusion': 'Variables are dependent' if p_value < 0.05 else 'Variables are independent'
        }
        
        # Create visualization
        fig = px.imshow(
            contingency_table,
            labels=dict(x=var2, y=var1, color="Count"),
            title=f"Contingency Table: {var1} vs {var2}",
            aspect='auto'
        )
        
        return results, fig
    
    def time_series_decomposition(self, date_column='Actual_Ship_Date', value_column='Late_Rate'):
        """Perform time series decomposition"""
        # Prepare time series data
        ts_data = self.data.groupby(pd.Grouper(key=date_column, freq='D')).agg({
            'Delivery_Status': lambda x: (x == 'Late').sum() / len(x) * 100 if len(x) > 0 else 0
        })
        ts_data.columns = [value_column]
        ts_data = ts_data.fillna(0)
        
        # Ensure we have enough data
        if len(ts_data) < 14:
            return None, None
        
        # Perform decomposition
        if not STATSMODELS_AVAILABLE:
            return None, None
            
        decomposition = seasonal_decompose(ts_data[value_column], model='additive', period=7)
        
        # Create visualization
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=('Original', 'Trend', 'Seasonal', 'Residual'),
            vertical_spacing=0.05
        )
        
        fig.add_trace(
            go.Scatter(x=ts_data.index, y=ts_data[value_column], name='Original'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=ts_data.index, y=decomposition.trend, name='Trend'),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=ts_data.index, y=decomposition.seasonal, name='Seasonal'),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=ts_data.index, y=decomposition.resid, name='Residual'),
            row=4, col=1
        )
        
        fig.update_layout(height=800, title_text="Time Series Decomposition")
        fig.update_xaxes(title_text="Date", row=4, col=1)
        
        return decomposition, fig
    
    def distribution_analysis(self, column):
        """Analyze distribution of a numeric column"""
        data = self.data[column].dropna()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Histogram', 'Box Plot', 'Q-Q Plot', 'Violin Plot'),
            specs=[[{'type': 'histogram'}, {'type': 'box'}],
                   [{'type': 'scatter'}, {'type': 'violin'}]]
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(x=data, name='Histogram', nbinsx=30),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=data, name='Box Plot'),
            row=1, col=2
        )
        
        # Q-Q plot
        theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(data)))
        sample_quantiles = np.sort(data)
        
        fig.add_trace(
            go.Scatter(x=theoretical_quantiles, y=sample_quantiles,
                      mode='markers', name='Q-Q Plot'),
            row=2, col=1
        )
        
        # Add diagonal line for Q-Q plot
        fig.add_trace(
            go.Scatter(x=theoretical_quantiles, y=theoretical_quantiles,
                      mode='lines', name='Normal Line', line=dict(dash='dash')),
            row=2, col=1
        )
        
        # Violin plot
        fig.add_trace(
            go.Violin(y=data, name='Violin Plot'),
            row=2, col=2
        )
        
        fig.update_layout(height=800, title_text=f"Distribution Analysis: {column}")
        
        # Normality tests
        shapiro_stat, shapiro_p = stats.shapiro(data[:5000])  # Shapiro-Wilk test
        ks_stat, ks_p = stats.kstest(data, 'norm', args=(data.mean(), data.std()))
        
        normality_results = {
            'Shapiro-Wilk Test': {'statistic': shapiro_stat, 'p_value': shapiro_p},
            'Kolmogorov-Smirnov Test': {'statistic': ks_stat, 'p_value': ks_p}
        }
        
        return fig, normality_results
    
    def confidence_intervals(self, column, confidence_level=0.95):
        """Calculate confidence intervals"""
        data = self.data[column].dropna()
        
        mean = np.mean(data)
        std_err = stats.sem(data)
        interval = stats.t.interval(confidence_level, len(data)-1, loc=mean, scale=std_err)
        
        return {
            'mean': mean,
            'confidence_level': confidence_level,
            'lower_bound': interval[0],
            'upper_bound': interval[1],
            'margin_of_error': interval[1] - mean
        }
    
    def anova_by_category(self):
        """Perform ANOVA to test if delay days differ by category"""
        # Filter for late shipments only
        late_data = self.data[self.data['Delivery_Status'] == 'Late'].copy()
        
        # Group by category
        category_groups = []
        category_names = []
        
        for category in late_data['Category'].unique():
            cat_data = late_data[late_data['Category'] == category]['Delay_Days'].dropna()
            if len(cat_data) > 5:  # Minimum sample size
                category_groups.append(cat_data)
                category_names.append(category)
        
        # Perform ANOVA
        f_stat, p_value = stats.f_oneway(*category_groups)
        
        # Create box plot
        fig = px.box(
            late_data,
            x='Category',
            y='Delay_Days',
            title='Delay Days Distribution by Category (Late Shipments Only)'
        )
        
        results = {
            'test': 'One-way ANOVA',
            'null_hypothesis': 'All categories have the same average delay days',
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'conclusion': 'Categories differ significantly' if p_value < 0.05 else 'No significant difference'
        }
        
        return results, fig
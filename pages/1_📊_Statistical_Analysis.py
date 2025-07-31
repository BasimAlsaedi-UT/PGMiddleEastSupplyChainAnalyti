"""
Statistical Analysis Page for P&G Supply Chain Analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from analytics.statistical import StatisticalAnalyzer
except ImportError:
    from analytics.statistical_simple import StatisticalAnalyzer
from utils.data_processor import DataProcessor
from components.filters import create_multiselect_filters, apply_filters_to_data

st.set_page_config(
    page_title="Statistical Analysis - P&G Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Statistical Analysis")
st.markdown("Advanced statistical analysis of supply chain performance")

# Load data
@st.cache_resource
def load_data():
    processor = DataProcessor()
    processor.load_processed_data()
    return processor

processor = load_data()

# Filters
st.sidebar.markdown("### Filters")
filters = create_multiselect_filters(processor.shipping_data)
filtered_data = apply_filters_to_data(processor.shipping_data, filters)

# Initialize analyzer
analyzer = StatisticalAnalyzer(filtered_data)

# Analysis tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Descriptive Statistics", 
    "Correlation Analysis", 
    "Hypothesis Testing", 
    "Time Series Analysis",
    "Distribution Analysis"
])

with tab1:
    st.markdown("### Descriptive Statistics")
    
    # Select numeric column
    numeric_cols = filtered_data.select_dtypes(include=['number']).columns
    selected_col = st.selectbox("Select column for analysis", numeric_cols)
    
    if selected_col:
        # Calculate statistics
        stats = analyzer.descriptive_statistics(selected_col)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Central Tendency")
            st.metric("Mean", f"{stats['Mean']:.2f}", 
                     help="Average value - sum of all values divided by count")
            st.metric("Median", f"{stats['Median']:.2f}",
                     help="Middle value when data is sorted - less affected by outliers than mean")
            if stats['Mode'] is not None:
                st.metric("Mode", f"{stats['Mode']:.2f}",
                         help="Most frequently occurring value in the dataset")
        
        with col2:
            st.markdown("#### Dispersion")
            st.metric("Standard Deviation", f"{stats['Std Dev']:.2f}",
                     help="Measure of spread - larger values indicate more variability")
            st.metric("Range", f"{stats['Range']:.2f}",
                     help="Difference between maximum and minimum values")
            st.metric("IQR", f"{stats['IQR']:.2f}",
                     help="Interquartile Range (Q3-Q1) - middle 50% of data spread")
        
        # Full statistics table
        st.markdown("#### Complete Statistics")
        st.dataframe(stats.to_frame(name='Value'))
        
        # Add interpretation
        st.markdown("#### 📊 Interpretation")
        
        # Compare mean and median
        if abs(stats['Mean'] - stats['Median']) > 0.1 * stats['Mean']:
            if stats['Mean'] > stats['Median']:
                st.info("📈 **Right-skewed distribution**: Mean > Median suggests data has a long tail on the right (some very high values)")
            else:
                st.info("📉 **Left-skewed distribution**: Mean < Median suggests data has a long tail on the left (some very low values)")
        else:
            st.info("📊 **Symmetric distribution**: Mean ≈ Median suggests data is relatively balanced")
        
        # Interpret skewness
        if stats['Skewness'] > 1:
            st.warning("⚠️ **Highly right-skewed**: Data is strongly skewed to the right")
        elif stats['Skewness'] < -1:
            st.warning("⚠️ **Highly left-skewed**: Data is strongly skewed to the left")
        elif abs(stats['Skewness']) < 0.5:
            st.success("✅ **Approximately symmetric**: Skewness is close to 0")
        
        # Interpret kurtosis
        if stats['Kurtosis'] > 3:
            st.info("📊 **Leptokurtic**: Distribution has heavy tails and sharp peak (more outliers than normal)")
        elif stats['Kurtosis'] < -1:
            st.info("📊 **Platykurtic**: Distribution has light tails and flat peak (fewer outliers than normal)")
        else:
            st.info("📊 **Mesokurtic**: Distribution is similar to normal in terms of tail weight")

with tab2:
    st.markdown("### Correlation Analysis")
    
    # Select variables for correlation
    numeric_cols = filtered_data.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) > 1:
        selected_vars = st.multiselect(
            "Select variables for correlation analysis",
            numeric_cols,
            default=numeric_cols[:5] if len(numeric_cols) > 5 else numeric_cols
        )
        
        if len(selected_vars) > 1:
            corr_matrix, fig = analyzer.correlation_analysis(selected_vars)
            
            # Display correlation matrix
            st.plotly_chart(fig, use_container_width=True)
            
            # Show strongest correlations
            st.markdown("#### Strongest Correlations")
            
            # Get upper triangle of correlation matrix
            upper_tri = corr_matrix.where(
                np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
            )
            
            # Find strongest correlations
            strong_corr = []
            for col in upper_tri.columns:
                for idx in upper_tri.index:
                    val = upper_tri.loc[idx, col]
                    if pd.notna(val) and abs(val) > 0.5:
                        strong_corr.append({
                            'Variable 1': idx,
                            'Variable 2': col,
                            'Correlation': val
                        })
            
            if strong_corr:
                st.dataframe(pd.DataFrame(strong_corr))
                
                # Add interpretation guide
                st.markdown("#### 📊 Correlation Interpretation Guide")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    **Correlation Strength:**
                    - 0.0 - 0.3: Weak
                    - 0.3 - 0.5: Moderate
                    - 0.5 - 0.7: Strong
                    - 0.7 - 1.0: Very Strong
                    """)
                with col2:
                    st.markdown("""
                    **Direction:**
                    - Positive (+): Variables move together
                    - Negative (-): Variables move oppositely
                    - Zero (0): No linear relationship
                    """)
                
                # Practical interpretation
                st.markdown("#### 💡 What This Means")
                for corr in strong_corr[:3]:  # Show top 3
                    if corr['Correlation'] > 0:
                        st.write(f"- **{corr['Variable 1']}** and **{corr['Variable 2']}** have a strong positive relationship ({corr['Correlation']:.2f}): "
                                f"When {corr['Variable 1']} increases, {corr['Variable 2']} tends to increase")
                    else:
                        st.write(f"- **{corr['Variable 1']}** and **{corr['Variable 2']}** have a strong negative relationship ({corr['Correlation']:.2f}): "
                                f"When {corr['Variable 1']} increases, {corr['Variable 2']} tends to decrease")
            else:
                st.info("No strong correlations (|r| > 0.5) found")
                st.markdown("**What this means**: The selected variables appear to be relatively independent of each other.")

with tab3:
    st.markdown("### Hypothesis Testing")
    
    # Test 1: Delivery performance by plant
    st.markdown("#### Test 1: Delivery Performance by Plant (ANOVA)")
    
    # Explanation
    with st.expander("ℹ️ What is ANOVA?"):
        st.markdown("""
        **Analysis of Variance (ANOVA)** tests whether there are statistically significant differences 
        in delivery performance across different plants/sources.
        
        - **Null Hypothesis (H₀)**: All plants have the same average late delivery rate
        - **Alternative Hypothesis (H₁)**: At least one plant has a different late delivery rate
        - **Significance Level**: α = 0.05 (5% chance of false positive)
        """)
    
    if st.button("Run ANOVA Test"):
        with st.spinner("Running analysis..."):
            results = analyzer.hypothesis_test_delivery_by_plant()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("F-Statistic", f"{results['f_statistic']:.4f}",
                         help="Ratio of between-group variance to within-group variance")
                st.metric("P-Value", f"{results['p_value']:.4f}",
                         help="Probability of seeing this result if all plants were truly equal")
            
            with col2:
                st.metric("Result", results['conclusion'])
                if results['significant']:
                    st.success("✅ Significant difference found")
                else:
                    st.info("❌ No significant difference")
            
            # Interpretation
            st.markdown("#### 📊 Interpretation")
            if results['significant']:
                st.warning(f"""
                **Result**: With p-value = {results['p_value']:.4f} < 0.05, we reject the null hypothesis.
                
                **What this means**: There IS a statistically significant difference in delivery performance 
                between plants. Some plants perform significantly better or worse than others.
                
                **Action Required**: Investigate the underperforming plants and share best practices from 
                high-performing plants.
                """)
            else:
                st.success(f"""
                **Result**: With p-value = {results['p_value']:.4f} > 0.05, we fail to reject the null hypothesis.
                
                **What this means**: There is NO statistically significant difference in delivery performance 
                between plants. All plants perform similarly.
                
                **Implication**: Performance issues (if any) are likely systemic rather than plant-specific.
                """)
            
            if 'post_hoc' in results:
                st.markdown("#### Post-hoc Analysis (Tukey HSD)")
                st.text(results['post_hoc'])
                st.info("Post-hoc tests show which specific pairs of plants differ significantly.")
    
    # Test 2: Chi-square test
    st.markdown("#### Test 2: Independence Test (Chi-Square)")
    
    with st.expander("ℹ️ What is Chi-Square Test?"):
        st.markdown("""
        **Chi-Square Test of Independence** determines whether two categorical variables are related.
        
        - **Null Hypothesis (H₀)**: The two variables are independent (not related)
        - **Alternative Hypothesis (H₁)**: The two variables are dependent (related)
        - **Example**: Is delivery status related to product category?
        """)
    
    cat_cols = filtered_data.select_dtypes(include=['object']).columns.tolist()
    col1, col2 = st.columns(2)
    
    with col1:
        var1 = st.selectbox("Select first variable", cat_cols)
    with col2:
        var2 = st.selectbox("Select second variable", 
                           [col for col in cat_cols if col != var1])
    
    if st.button("Run Chi-Square Test"):
        with st.spinner("Running analysis..."):
            results, fig = analyzer.chi_square_test_independence(var1, var2)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chi-Square Statistic", f"{results['chi2_statistic']:.4f}",
                         help="Measure of difference between observed and expected frequencies")
                st.metric("P-Value", f"{results['p_value']:.4f}",
                         help="Probability of seeing this association by chance")
            
            with col2:
                st.metric("Degrees of Freedom", results['degrees_of_freedom'],
                         help="(rows-1) × (columns-1)")
                if results['significant']:
                    st.success("✅ Variables are dependent")
                else:
                    st.info("❌ Variables are independent")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Interpretation
            st.markdown("#### 📊 Interpretation")
            if results['significant']:
                st.warning(f"""
                **Result**: With p-value = {results['p_value']:.4f} < 0.05, we reject the null hypothesis.
                
                **What this means**: **{var1}** and **{var2}** are statistically dependent. 
                The distribution of {var1} varies significantly across different levels of {var2}.
                
                **Business Insight**: Understanding this relationship can help in:
                - Targeted interventions for specific combinations
                - Better resource allocation
                - More accurate predictions
                """)
            else:
                st.success(f"""
                **Result**: With p-value = {results['p_value']:.4f} > 0.05, we fail to reject the null hypothesis.
                
                **What this means**: **{var1}** and **{var2}** are statistically independent. 
                Knowing the value of one variable doesn't help predict the other.
                
                **Business Insight**: These variables can be analyzed separately without considering 
                their interaction.
                """)
    
    # Test 3: ANOVA by category
    st.markdown("#### Test 3: Delay Days by Category (ANOVA)")
    if st.button("Run Category ANOVA"):
        with st.spinner("Running analysis..."):
            results, fig = analyzer.anova_by_category()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("F-Statistic", f"{results['f_statistic']:.4f}")
                st.metric("P-Value", f"{results['p_value']:.4f}")
            
            with col2:
                st.metric("Result", results['conclusion'])
            
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### Time Series Analysis")
    
    with st.expander("ℹ️ What is Time Series Decomposition?"):
        st.markdown("""
        **Time Series Decomposition** breaks down temporal data into components:
        - **Trend**: Long-term direction (improving or worsening)
        - **Seasonal**: Repeating patterns (weekly cycles)
        - **Residual**: Random fluctuations
        
        This helps identify patterns and predict future performance.
        """)
    
    if st.button("Run Time Series Decomposition"):
        with st.spinner("Performing decomposition..."):
            decomposition, fig = analyzer.time_series_decomposition()
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                # Key insights
                st.markdown("#### 📊 Component Analysis")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info("**Trend**: Shows the long-term direction of late delivery rates")
                
                with col2:
                    st.info("**Seasonal**: Weekly patterns in delivery performance")
                
                with col3:
                    st.info("**Residual**: Random variations after removing trend and seasonality")
                
                # Detailed interpretation
                st.markdown("#### 💡 Interpretation Guide")
                
                st.markdown("""
                **How to read the decomposition:**
                
                1. **Trend Component**:
                   - Upward trend → Performance is deteriorating over time
                   - Downward trend → Performance is improving over time
                   - Flat trend → Performance is stable
                
                2. **Seasonal Component**:
                   - Peaks indicate days/periods with typically worse performance
                   - Troughs indicate days/periods with typically better performance
                   - Regular patterns suggest predictable variations
                
                3. **Residual Component**:
                   - Large spikes indicate unusual events or outliers
                   - Small residuals indicate the model captures most variation
                   - Check for patterns - residuals should appear random
                
                **Business Applications:**
                - **Capacity Planning**: Allocate more resources during high-risk periods
                - **Performance Monitoring**: Distinguish between normal variations and real issues
                - **Forecasting**: Predict future performance based on trend and seasonality
                """)
            else:
                st.warning("Insufficient data for time series decomposition (need at least 14 days)")
                st.info("💡 **Tip**: Select a wider date range or 'All Time' to enable time series analysis")

with tab5:
    st.markdown("### Distribution Analysis")
    
    # Select column for distribution analysis
    numeric_cols = filtered_data.select_dtypes(include=['number']).columns
    selected_col = st.selectbox("Select column for distribution analysis", 
                               numeric_cols, key='dist_col')
    
    # Store analysis results in session state to persist them
    if 'dist_analysis_results' not in st.session_state:
        st.session_state.dist_analysis_results = {}
    
    # Store current column in session state
    if 'current_dist_col' not in st.session_state:
        st.session_state.current_dist_col = selected_col
    
    # Check if column changed
    if selected_col != st.session_state.current_dist_col:
        st.session_state.current_dist_col = selected_col
        # Clear previous results when column changes
        if selected_col in st.session_state.dist_analysis_results:
            del st.session_state.dist_analysis_results[selected_col]
    
    if selected_col:
        # Distribution Analysis Section
        st.markdown("#### 📊 Distribution Analysis")
        if st.button("Analyze Distribution", key="analyze_dist_btn"):
            with st.spinner("Analyzing distribution..."):
                fig, normality_results = analyzer.distribution_analysis(selected_col)
                
                # Store results in session state
                st.session_state.dist_analysis_results[selected_col] = {
                    'fig': fig,
                    'normality_results': normality_results,
                    'original_data': filtered_data[selected_col].dropna()
                }
        
        # Display results if they exist (either just analyzed or from previous analysis)
        if selected_col in st.session_state.dist_analysis_results:
            results = st.session_state.dist_analysis_results[selected_col]
            
            # Display plots
            st.plotly_chart(results['fig'], use_container_width=True)
            
            # Normality test results
            st.markdown("#### Normality Tests")
            
            normality_results = results['normality_results']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Shapiro-Wilk Test**")
                sw_p = normality_results['Shapiro-Wilk Test']['p_value']
                st.metric("P-Value", f"{sw_p:.4f}",
                         help="Tests if data comes from normal distribution")
                if sw_p > 0.05:
                    st.success("✅ Data appears normally distributed")
                else:
                    st.warning("❌ Data is not normally distributed")
            
            with col2:
                st.markdown("**Kolmogorov-Smirnov Test**")
                ks_p = normality_results['Kolmogorov-Smirnov Test']['p_value']
                st.metric("P-Value", f"{ks_p:.4f}",
                         help="Alternative test for normality")
                if ks_p > 0.05:
                    st.success("✅ Data appears normally distributed")
                else:
                    st.warning("❌ Data is not normally distributed")
                
            # Interpretation
            st.markdown("#### 📊 What This Means")
            
            if sw_p > 0.05 and ks_p > 0.05:
                st.success("""
                **Normal Distribution Confirmed** ✅
                
                Your data follows a bell curve pattern, which means:
                - Most values cluster around the mean
                - Extreme values are rare and balanced
                - Standard statistical methods (t-tests, ANOVA) are appropriate
                - Predictions using mean ± standard deviation are reliable
                """)
            else:
                st.warning("""
                **Non-Normal Distribution Detected** ⚠️
                
                Your data does NOT follow a bell curve, which means:
                - Data may be skewed (long tail on one side)
                - Outliers may be influencing results
                - Consider using:
                  - Median instead of mean for central tendency
                  - Non-parametric tests (Mann-Whitney, Kruskal-Wallis)
                  - Data transformation (log, square root) before analysis
                """)
                
                # Suggest transformations
                st.markdown("#### 🔧 Suggested Transformations")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Apply Log Transform", key="log_transform_btn"):
                        with st.spinner("Applying log transformation..."):
                            try:
                                # Get original data
                                original_data = results['original_data']
                                
                                # Apply log transformation (add small value to avoid log(0))
                                min_val = original_data.min()
                                if min_val <= 0:
                                    transformed_data = np.log(original_data - min_val + 1)
                                else:
                                    transformed_data = np.log(original_data)
                                
                                # Create new analyzer with transformed data
                                temp_df = filtered_data.copy()
                                temp_df[f'{selected_col}_log'] = transformed_data
                                temp_analyzer = StatisticalAnalyzer(temp_df)
                                
                                # Re-run analysis on transformed data
                                fig, new_normality_results = temp_analyzer.distribution_analysis(f'{selected_col}_log')
                                
                                # Update session state with transformed results
                                st.session_state.dist_analysis_results[f'{selected_col}_log_transformed'] = {
                                    'fig': fig,
                                    'normality_results': new_normality_results,
                                    'original_data': transformed_data,
                                    'transformation': 'log'
                                }
                                
                                st.success("✅ Log transformation applied!")
                                st.info("The transformed data analysis is shown below:")
                                
                                # Display transformed results
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Show new normality test results
                                st.markdown("##### Transformed Data Normality Tests")
                                new_sw_p = new_normality_results['Shapiro-Wilk Test']['p_value']
                                new_ks_p = new_normality_results['Kolmogorov-Smirnov Test']['p_value']
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("Shapiro-Wilk P-Value", f"{new_sw_p:.4f}")
                                with col_b:
                                    st.metric("K-S P-Value", f"{new_ks_p:.4f}")
                                
                                if new_sw_p > 0.05 and new_ks_p > 0.05:
                                    st.success("🎉 Transformation successful! Data is now normally distributed.")
                                else:
                                    st.info("Data is still non-normal after transformation. Try square root transform.")
                                    
                            except Exception as e:
                                st.error(f"Error applying log transformation: {str(e)}")
                
                with col2:
                    if st.button("Apply Square Root Transform", key="sqrt_transform_btn"):
                        with st.spinner("Applying square root transformation..."):
                            try:
                                # Get original data
                                original_data = results['original_data']
                                
                                # Apply square root transformation
                                min_val = original_data.min()
                                if min_val < 0:
                                    transformed_data = np.sqrt(original_data - min_val)
                                else:
                                    transformed_data = np.sqrt(original_data)
                                
                                # Create new analyzer with transformed data
                                temp_df = filtered_data.copy()
                                temp_df[f'{selected_col}_sqrt'] = transformed_data
                                temp_analyzer = StatisticalAnalyzer(temp_df)
                                
                                # Re-run analysis on transformed data
                                fig, new_normality_results = temp_analyzer.distribution_analysis(f'{selected_col}_sqrt')
                                
                                # Update session state with transformed results
                                st.session_state.dist_analysis_results[f'{selected_col}_sqrt_transformed'] = {
                                    'fig': fig,
                                    'normality_results': new_normality_results,
                                    'original_data': transformed_data,
                                    'transformation': 'sqrt'
                                }
                                
                                st.success("✅ Square root transformation applied!")
                                st.info("The transformed data analysis is shown below:")
                                
                                # Display transformed results
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Show new normality test results
                                st.markdown("##### Transformed Data Normality Tests")
                                new_sw_p = new_normality_results['Shapiro-Wilk Test']['p_value']
                                new_ks_p = new_normality_results['Kolmogorov-Smirnov Test']['p_value']
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("Shapiro-Wilk P-Value", f"{new_sw_p:.4f}")
                                with col_b:
                                    st.metric("K-S P-Value", f"{new_ks_p:.4f}")
                                
                                if new_sw_p > 0.05 and new_ks_p > 0.05:
                                    st.success("🎉 Transformation successful! Data is now normally distributed.")
                                else:
                                    st.info("Data is still non-normal after transformation. Consider other transformations or non-parametric methods.")
                                    
                            except Exception as e:
                                st.error(f"Error applying square root transformation: {str(e)}")
        
        # Confidence intervals section (separate from distribution analysis)
        st.markdown("---")  # Add separator
        st.markdown("#### Confidence Intervals")
        
        with st.expander("ℹ️ What are Confidence Intervals?"):
            st.markdown("""
            **Confidence Intervals** provide a range of plausible values for the true population mean.
            
            - **95% CI**: If we repeated this study 100 times, 95 would contain the true mean
            - **Wider interval** = More confidence but less precision
            - **Narrower interval** = Less confidence but more precision
            """)
        
        confidence_level = st.slider("Confidence Level", 0.90, 0.99, 0.95, 0.01)
        
        if st.button("Calculate Confidence Interval", key="calc_ci_btn"):
            with st.spinner("Calculating confidence interval..."):
                try:
                    ci_results = analyzer.confidence_intervals(selected_col, confidence_level)
                    
                    # Store CI results in session state
                    if 'ci_results' not in st.session_state:
                        st.session_state.ci_results = {}
                    st.session_state.ci_results[selected_col] = ci_results
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Sample Mean", f"{ci_results['mean']:.4f}",
                                 help="Average of your current data")
                    
                    with col2:
                        st.metric("Lower Bound", f"{ci_results['lower_bound']:.4f}",
                                 help="Minimum plausible value for true mean")
                    
                    with col3:
                        st.metric("Upper Bound", f"{ci_results['upper_bound']:.4f}",
                                 help="Maximum plausible value for true mean")
                    
                    # Visual representation
                    margin = ci_results['upper_bound'] - ci_results['mean']
                    st.info(f"""
                    📊 **Interpretation**: We are {confidence_level*100:.0f}% confident that the true mean 
                    of {selected_col} lies between **{ci_results['lower_bound']:.4f}** and 
                    **{ci_results['upper_bound']:.4f}**
                    
                    **Margin of Error**: ±{margin:.4f}
                    """)
                    
                    # Business interpretation
                    st.markdown("##### 💡 Business Application")
                    st.markdown(f"""
                    **How to use this information:**
                    
                    1. **Planning**: Use the upper bound for conservative estimates
                    2. **Target Setting**: The true average is likely within this range
                    3. **Sample Size**: Narrower intervals require larger samples
                    4. **Decision Making**: If the interval doesn't include a critical value, 
                       you can be {confidence_level*100:.0f}% confident the true value differs from it
                    
                    **Example**: If your target for {selected_col} is outside this interval, you can be 
                    {confidence_level*100:.0f}% confident you're not meeting the target.
                    """)
                except Exception as e:
                    st.error(f"Error calculating confidence interval: {str(e)}")
        
        # Display previous CI results if they exist
        elif 'ci_results' in st.session_state and selected_col in st.session_state.ci_results:
            ci_results = st.session_state.ci_results[selected_col]
            st.info("Showing previous confidence interval calculation. Click button above to recalculate.")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Sample Mean", f"{ci_results['mean']:.4f}")
            
            with col2:
                st.metric("Lower Bound", f"{ci_results['lower_bound']:.4f}")
            
            with col3:
                st.metric("Upper Bound", f"{ci_results['upper_bound']:.4f}")

# Summary insights
st.markdown("---")
st.markdown("### 💡 Statistical Insights Summary")

insights = []

# Check late rate
late_rate = (filtered_data['Delivery_Status'] == 'Late').mean() * 100
if late_rate > 35:
    insights.append(f"⚠️ High late delivery rate ({late_rate:.1f}%) requires immediate attention")

# Check for significant plant differences
if 'Source' in filtered_data.columns:
    plant_variance = filtered_data.groupby('Source')['Delivery_Status'].apply(
        lambda x: (x == 'Late').mean()
    ).var()
    if plant_variance > 0.01:
        insights.append("📍 Significant variation in performance across plants/sources")

# Check delay distribution
if 'Delay_Days' in filtered_data.columns:
    avg_delay = filtered_data[filtered_data['Delivery_Status'] == 'Late']['Delay_Days'].mean()
    if avg_delay > 3:
        insights.append(f"⏱️ Average delay for late shipments is {avg_delay:.1f} days")

if insights:
    for insight in insights:
        st.write(insight)
else:
    st.success("✅ No critical statistical issues identified")
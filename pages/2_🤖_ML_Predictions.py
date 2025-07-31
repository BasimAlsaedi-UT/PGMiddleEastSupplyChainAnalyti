"""
Machine Learning Predictions Page for P&G Supply Chain Analytics
FIXED VERSION - With comprehensive error handling and validation
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
import logging
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import with proper error handling
try:
    from ml_models.predictive import PredictiveModels
except ImportError:
    logger.warning("Advanced ML models not available, using simple version")
    try:
        from ml_models.predictive_simple import PredictiveModels
    except ImportError:
        logger.error("No ML models available")
        PredictiveModels = None

from utils.data_processor import DataProcessor
from components.filters import create_multiselect_filters, apply_filters_to_data

# Configuration
class Config:
    MIN_TRAINING_SAMPLES = 100
    HIGH_RISK_THRESHOLD = 0.7
    ANOMALY_RATE_WARNING = 5.0
    FORECAST_DAYS = 30
    MAX_DISPLAY_ROWS = 20

st.set_page_config(
    page_title="ML Predictions - P&G Analytics",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Machine Learning Predictions")
st.markdown("Advanced predictive analytics for proactive supply chain management")

# Check if ML models are available
if PredictiveModels is None:
    st.error("Machine Learning models are not available. Please install required dependencies.")
    st.info("Run: pip install scikit-learn prophet")
    st.stop()

# Load data with error handling
@st.cache_resource
def load_data():
    """Load data with comprehensive error handling"""
    try:
        processor = DataProcessor()
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'extracted')
        processor.load_processed_data(data_dir=data_dir)
        
        # Validate data
        if processor.shipping_data is None or processor.shipping_data.empty:
            raise ValueError("No shipping data available")
        
        logger.info(f"Loaded {len(processor.shipping_data)} shipping records")
        return processor
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return None

# Load data
processor = load_data()
if processor is None:
    st.error("Failed to load data. Please ensure data extraction has been completed.")
    st.stop()

# Validate minimum data requirements
if len(processor.shipping_data) < Config.MIN_TRAINING_SAMPLES:
    st.error(f"Insufficient data for ML models. Need at least {Config.MIN_TRAINING_SAMPLES} records.")
    st.stop()

# Initialize ML models
if 'ml_models' not in st.session_state:
    try:
        st.session_state.ml_models = PredictiveModels(processor.shipping_data)
        st.session_state.models_trained = False
    except Exception as e:
        st.error(f"Failed to initialize ML models: {str(e)}")
        logger.error(f"ML model initialization error: {str(e)}")
        st.stop()

ml_models = st.session_state.ml_models

# Sidebar for model training
with st.sidebar:
    st.markdown("### Model Training")
    
    if st.button("🚀 Train All Models"):
        with st.spinner("Training models..."):
            try:
                # Train late delivery model
                st.session_state.late_delivery_results = ml_models.train_late_delivery_model()
                
                # Validate results
                if not st.session_state.late_delivery_results:
                    st.warning("Late delivery model training returned no results")
                
                # Train demand forecast
                st.session_state.demand_model, st.session_state.demand_forecast = ml_models.train_demand_forecast()
                
                if st.session_state.demand_model is None:
                    st.warning("Demand forecast model training failed")
                
                # Train anomaly detection
                st.session_state.anomaly_stats = ml_models.train_anomaly_detection()
                
                if not st.session_state.anomaly_stats:
                    st.warning("Anomaly detection training returned no results")
                
                st.session_state.models_trained = True
                st.success("✅ Model training completed!")
                
            except Exception as e:
                st.error(f"Error during model training: {str(e)}")
                logger.error(f"Model training error: {str(e)}", exc_info=True)
                st.session_state.models_trained = False
    
    if st.session_state.get('models_trained', False):
        st.markdown("### Model Status")
        if st.session_state.get('late_delivery_results'):
            st.success("✅ Late Delivery Model")
        else:
            st.warning("⚠️ Late Delivery Model")
            
        if st.session_state.get('demand_model'):
            st.success("✅ Demand Forecast Model")
        else:
            st.warning("⚠️ Demand Forecast Model")
            
        if st.session_state.get('anomaly_stats'):
            st.success("✅ Anomaly Detection Model")
        else:
            st.warning("⚠️ Anomaly Detection Model")

# Main content
if not st.session_state.get('models_trained', False):
    st.info("👈 Click 'Train All Models' in the sidebar to get started")
else:
    # Model tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Late Delivery Prediction", 
        "Demand Forecasting", 
        "Anomaly Detection",
        "Route Optimization"
    ])
    
    with tab1:
        st.markdown("## 🚨 Late Delivery Risk Prediction")
        st.markdown("Predict which shipments are at risk of being delivered late")
        
        results = st.session_state.get('late_delivery_results', {})
        
        if results:
            # Model performance metrics with validation
            col1, col2, col3 = st.columns(3)
            
            with col1:
                accuracy = results.get('accuracy', 0)
                st.metric("Model Accuracy", f"{accuracy*100:.1f}%")
            
            with col2:
                auc_score = results.get('auc_score', 0)
                st.metric("AUC Score", f"{auc_score:.3f}")
            
            with col3:
                # Safe calculation of baseline late rate
                try:
                    if 'Delivery_Status' in processor.shipping_data.columns:
                        late_rate = (processor.shipping_data['Delivery_Status'] == 'Late').mean() * 100
                    else:
                        late_rate = 0
                except Exception:
                    late_rate = 0
                st.metric("Baseline Late Rate", f"{late_rate:.1f}%")
            
            # ROC Curve
            st.markdown("### Model Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # ROC Curve with error handling
                if 'y_test' in results and 'y_pred_proba' in results:
                    try:
                        roc_fig = ml_models.create_roc_curve(
                            results['y_test'], 
                            results['y_pred_proba']
                        )
                        if roc_fig:
                            st.plotly_chart(roc_fig, use_container_width=True)
                        else:
                            st.info("ROC curve not available")
                    except Exception as e:
                        st.error("Could not create ROC curve")
                        logger.error(f"ROC curve error: {str(e)}")
            
            with col2:
                # Feature importance
                st.markdown("#### Feature Importance")
                feature_imp = results.get('feature_importance', pd.DataFrame())
                
                if not feature_imp.empty:
                    try:
                        import plotly.express as px
                        fig = px.bar(
                            feature_imp.head(10),
                            x='importance',
                            y='feature',
                            orientation='h',
                            title="Top 10 Most Important Features"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error("Could not create feature importance chart")
                        logger.error(f"Feature importance chart error: {str(e)}")
                else:
                    st.info("Feature importance not available")
            
            # Confusion Matrix
            if 'confusion_matrix' in results:
                st.markdown("### Confusion Matrix")
                
                try:
                    cm = results['confusion_matrix']
                    cm_df = pd.DataFrame(
                        cm,
                        index=['Actual: On Time', 'Actual: Late'],
                        columns=['Predicted: On Time', 'Predicted: Late']
                    )
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.dataframe(cm_df.style.background_gradient(cmap='Blues'))
                except Exception as e:
                    st.error("Could not display confusion matrix")
                    logger.error(f"Confusion matrix error: {str(e)}")
            
            # Risk scoring for current shipments
            st.markdown("### Current Shipments Risk Assessment")
            
            try:
                # Filter for recent/upcoming shipments
                if 'Delivery_Status' in processor.shipping_data.columns:
                    recent_shipments = processor.shipping_data[
                        processor.shipping_data['Delivery_Status'].isin(['Not Due', 'On Time'])
                    ].head(100)
                    
                    if len(recent_shipments) > 0:
                        # Predict risk
                        risk_scored = ml_models.predict_late_risk(recent_shipments.copy())
                        
                        if risk_scored is not None and not risk_scored.empty:
                            # Show high-risk shipments
                            high_risk = risk_scored[
                                risk_scored['Late_Risk_Score'] > Config.HIGH_RISK_THRESHOLD
                            ].sort_values('Late_Risk_Score', ascending=False)
                            
                            if len(high_risk) > 0:
                                st.warning(f"⚠️ {len(high_risk)} shipments at high risk of being late!")
                                
                                # Display high-risk shipments
                                display_cols = ['Category', 'Master_Brand', 'Source', 'SLS_Plant', 
                                               'Late_Risk_Score', 'Delivery_Status']
                                available_cols = [col for col in display_cols if col in high_risk.columns]
                                
                                st.dataframe(
                                    high_risk[available_cols].head(Config.MAX_DISPLAY_ROWS).style.background_gradient(
                                        subset=['Late_Risk_Score'], cmap='Reds'
                                    )
                                )
                            else:
                                st.success("✅ No high-risk shipments identified")
                        else:
                            st.info("Risk scoring not available")
                    else:
                        st.info("No recent shipments to analyze")
                else:
                    st.warning("Delivery status column not found")
            except Exception as e:
                st.error("Error in risk assessment")
                logger.error(f"Risk assessment error: {str(e)}")
        else:
            st.warning("Late delivery model results not available")
    
    with tab2:
        st.markdown("## 📈 Demand Forecasting")
        st.markdown("Predict future demand to optimize inventory and capacity")
        
        model = st.session_state.get('demand_model')
        forecast = st.session_state.get('demand_forecast')
        
        if model and forecast is not None:
            try:
                # Forecast plot
                forecast_fig = ml_models.create_forecast_plot(model, forecast)
                if forecast_fig:
                    st.plotly_chart(forecast_fig, use_container_width=True)
                
                # Forecast summary
                st.markdown(f"### {Config.FORECAST_DAYS}-Day Forecast Summary")
                
                # Safe date comparison
                if hasattr(model, 'history') and 'ds' in model.history.columns:
                    max_history_date = model.history['ds'].max()
                    future_forecast = forecast[forecast['ds'] > max_history_date].copy()
                else:
                    future_forecast = forecast[forecast['ds'] > datetime.now()].copy()
                
                if len(future_forecast) > 0:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_forecast = future_forecast['yhat'].mean()
                        st.metric("Average Daily Forecast", f"{avg_forecast:.0f} shipments")
                    
                    with col2:
                        max_forecast = future_forecast['yhat'].max()
                        max_date_idx = future_forecast['yhat'].idxmax()
                        if pd.notna(max_date_idx):
                            max_date = future_forecast.loc[max_date_idx, 'ds']
                            st.metric("Peak Day", f"{max_forecast:.0f} shipments",
                                     delta=f"on {max_date.strftime('%Y-%m-%d')}")
                        else:
                            st.metric("Peak Day", f"{max_forecast:.0f} shipments")
                    
                    with col3:
                        total_forecast = future_forecast['yhat'].sum()
                        st.metric(f"Total {Config.FORECAST_DAYS}-Day Forecast", 
                                 f"{total_forecast:,.0f} shipments")
                    
                    # Weekly breakdown
                    st.markdown("### Weekly Forecast Breakdown")
                    
                    try:
                        future_forecast['Week'] = future_forecast['ds'].dt.isocalendar().week
                        weekly_forecast = future_forecast.groupby('Week').agg({
                            'yhat': 'sum',
                            'yhat_lower': 'sum',
                            'yhat_upper': 'sum'
                        }).round(0)
                        
                        weekly_forecast.columns = ['Forecast', 'Lower Bound', 'Upper Bound']
                        st.dataframe(weekly_forecast.style.format("{:,.0f}"))
                    except Exception as e:
                        st.error("Could not create weekly breakdown")
                        logger.error(f"Weekly breakdown error: {str(e)}")
                    
                    # Seasonality components
                    try:
                        if hasattr(model, 'predict') and hasattr(model, 'plot_components'):
                            st.markdown("### Seasonality Patterns")
                            
                            # Note about seasonality
                            st.info("📊 Seasonality patterns show how demand varies by day of week and time of year")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Weekly seasonality - using Prophet's internal components
                                st.markdown("#### Weekly Pattern")
                                
                                # Create a simple weekly pattern visualization
                                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                                
                                # Generate dates for one week
                                dates = pd.date_range(start='2025-01-06', periods=7, freq='D')  # Starting Monday
                                weekly_df = pd.DataFrame({'ds': dates})
                                
                                # Get predictions with components
                                weekly_forecast = model.predict(weekly_df)
                                
                                # Calculate weekly effect by comparing to trend
                                if 'trend' in weekly_forecast.columns and 'yhat' in weekly_forecast.columns:
                                    weekly_effect = weekly_forecast['yhat'] - weekly_forecast['trend']
                                    
                                    fig = go.Figure(go.Bar(
                                        x=days, 
                                        y=weekly_effect.values,
                                        marker_color=['green' if x > 0 else 'red' for x in weekly_effect.values]
                                    ))
                                    fig.update_layout(
                                        title="Weekly Seasonality Pattern",
                                        yaxis_title="Effect on Demand",
                                        showlegend=False
                                    )
                                    fig.add_hline(y=0, line_dash="dash", line_color="gray")
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.info("Weekly seasonality data not available in forecast")
                            
                            with col2:
                                # Monthly seasonality
                                st.markdown("#### Monthly Pattern")
                                
                                # Generate dates for each month
                                current_year = 2025
                                month_dates = []
                                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                                
                                # Get mid-month date for each month
                                for month in range(1, 13):
                                    month_dates.append(pd.Timestamp(f'{current_year}-{month:02d}-15'))
                                
                                monthly_df = pd.DataFrame({'ds': month_dates})
                                monthly_forecast = model.predict(monthly_df)
                                
                                # Calculate monthly effect
                                if 'trend' in monthly_forecast.columns and 'yhat' in monthly_forecast.columns:
                                    monthly_effect = monthly_forecast['yhat'] - monthly_forecast['trend']
                                    
                                    fig = go.Figure(go.Bar(
                                        x=month_names,
                                        y=monthly_effect.values,
                                        marker_color=['green' if x > 0 else 'red' for x in monthly_effect.values]
                                    ))
                                    fig.update_layout(
                                        title="Monthly Seasonality Pattern",
                                        yaxis_title="Effect on Demand",
                                        showlegend=False
                                    )
                                    fig.add_hline(y=0, line_dash="dash", line_color="gray")
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.info("Monthly seasonality data not available in forecast")
                        else:
                            st.info("Seasonality patterns require Prophet forecasting model. Please ensure Prophet is installed: pip install prophet")
                    except Exception as e:
                        st.error("Could not display seasonality patterns")
                        logger.error(f"Seasonality error: {str(e)}")
                else:
                    st.warning("No future forecast data available")
            except Exception as e:
                st.error("Error in demand forecasting display")
                logger.error(f"Demand forecast error: {str(e)}")
        else:
            st.warning("Demand forecast model not available")
    
    with tab3:
        st.markdown("## 🔍 Anomaly Detection")
        st.markdown("Identify unusual patterns and outliers in shipment data")
        
        anomaly_stats = st.session_state.get('anomaly_stats', {})
        
        if anomaly_stats:
            # Anomaly statistics with validation
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_anomalies = anomaly_stats.get('total_anomalies', 0)
                st.metric("Total Anomalies Detected", total_anomalies)
            
            with col2:
                anomaly_rate = anomaly_stats.get('anomaly_rate', 0)
                st.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
            
            with col3:
                features_used = anomaly_stats.get('features_used', [])
                st.metric("Features Used", len(features_used))
            
            # Anomaly scatter plot
            try:
                anomaly_fig = ml_models.create_anomaly_scatter()
                if anomaly_fig:
                    st.plotly_chart(anomaly_fig, use_container_width=True)
            except Exception as e:
                st.error("Could not create anomaly visualization")
                logger.error(f"Anomaly scatter error: {str(e)}")
            
            # Anomaly details
            st.markdown("### Anomaly Details")
            
            try:
                if 'Is_Anomaly' in processor.shipping_data.columns:
                    anomaly_data = processor.shipping_data[
                        processor.shipping_data['Is_Anomaly'] == 1
                    ].copy()
                    
                    if len(anomaly_data) > 0:
                        # Group anomalies by category
                        if 'Category' in anomaly_data.columns:
                            anomaly_summary = anomaly_data.groupby('Category').agg({
                                'Transaction_ID': 'count',
                                'Delay_Days': lambda x: x.mean() if len(x) > 0 else 0,
                                'Quantity': lambda x: x.mean() if len(x) > 0 else 0
                            }).round(2)
                            
                            anomaly_summary.columns = ['Count', 'Avg Delay Days', 'Avg Quantity']
                            anomaly_summary = anomaly_summary.sort_values('Count', ascending=False)
                            
                            st.dataframe(anomaly_summary.style.background_gradient(
                                subset=['Count'], cmap='Reds'
                            ))
                        
                        # Show sample anomalies
                        st.markdown("### Sample Anomalous Shipments")
                        
                        display_cols = ['Category', 'Master_Brand', 'Source', 'Delivery_Status',
                                       'Delay_Days', 'Quantity', 'Anomaly_Score']
                        available_cols = [col for col in display_cols if col in anomaly_data.columns]
                        
                        if 'Anomaly_Score' in anomaly_data.columns:
                            display_data = anomaly_data.nlargest(
                                Config.MAX_DISPLAY_ROWS, 'Anomaly_Score'
                            )[available_cols]
                        else:
                            display_data = anomaly_data.head(Config.MAX_DISPLAY_ROWS)[available_cols]
                        
                        st.dataframe(display_data.style.background_gradient(
                            subset=[col for col in ['Anomaly_Score'] if col in display_data.columns], 
                            cmap='Reds'
                        ))
                    else:
                        st.info("No anomalies detected in the data")
                else:
                    st.info("Anomaly detection has not been run on this data")
            except Exception as e:
                st.error("Error displaying anomaly details")
                logger.error(f"Anomaly details error: {str(e)}")
        else:
            st.warning("Anomaly detection results not available")
    
    with tab4:
        st.markdown("## 🗺️ Route Optimization Analysis")
        st.markdown("Identify routes with highest potential for improvement")
        
        try:
            # Calculate route optimization scores
            route_performance = ml_models.route_optimization_score()
            
            if route_performance is not None and not route_performance.empty:
                # Summary metrics with validation
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if len(route_performance) > 0:
                        worst_route = route_performance.index[0]
                        st.metric("Worst Performing Route", 
                                 f"{worst_route[0]} → {worst_route[1]}")
                
                with col2:
                    if 'Optimization_Score' in route_performance.columns:
                        worst_score = route_performance.iloc[0]['Optimization_Score']
                        st.metric("Optimization Score", f"{worst_score:.1f}")
                
                with col3:
                    if 'Optimization_Score' in route_performance.columns:
                        high_priority_routes = len(
                            route_performance[route_performance['Optimization_Score'] > 50]
                        )
                        st.metric("High Priority Routes", high_priority_routes)
                
                # Route optimization heatmap
                try:
                    route_heatmap = ml_models.create_route_optimization_heatmap(route_performance)
                    if route_heatmap:
                        st.plotly_chart(route_heatmap, use_container_width=True)
                        st.info("💡 Note: 'N/A' values indicate routes that don't exist in the data. MIC and MPC are smaller warehouses with limited plant connections.")
                except Exception as e:
                    st.error("Could not create route optimization heatmap")
                    logger.error(f"Route heatmap error: {str(e)}")
                
                # Top routes for optimization
                st.markdown("### Top 10 Routes for Optimization")
                
                top_routes = route_performance.head(10).copy()
                top_routes.index = top_routes.index.map(lambda x: f"{x[0]} → {x[1]}")
                
                # Format with available columns
                format_dict = {}
                if 'Late_Rate' in top_routes.columns:
                    format_dict['Late_Rate'] = '{:.1f}%'
                if 'Avg_Delay' in top_routes.columns:
                    format_dict['Avg_Delay'] = '{:.1f} days'
                if 'Total_Volume' in top_routes.columns:
                    format_dict['Total_Volume'] = '{:,.0f}'
                if 'Optimization_Score' in top_routes.columns:
                    format_dict['Optimization_Score'] = '{:.1f}'
                
                st.dataframe(
                    top_routes.style.background_gradient(
                        subset=[col for col in ['Optimization_Score', 'Late_Rate'] 
                               if col in top_routes.columns], 
                        cmap='Reds'
                    ).format(format_dict)
                )
                
                # Recommendations
                st.markdown("### 💡 Optimization Recommendations")
                
                recommendations = []
                
                # Check worst route
                if ('Late_Rate' in route_performance.columns and 
                    len(route_performance) > 0 and 
                    route_performance.iloc[0]['Late_Rate'] > 50):
                    recommendations.append(
                        f"🚨 **Priority 1**: Route {route_performance.index[0][0]} → "
                        f"{route_performance.index[0][1]} has {route_performance.iloc[0]['Late_Rate']:.1f}% "
                        f"late rate. Consider alternative routing or capacity increase."
                    )
                
                # Check high-volume routes
                if 'Total_Volume' in route_performance.columns and 'Late_Rate' in route_performance.columns:
                    volume_threshold = route_performance['Total_Volume'].quantile(0.75)
                    high_volume_poor = route_performance[
                        (route_performance['Total_Volume'] > volume_threshold) &
                        (route_performance['Late_Rate'] > 30)
                    ]
                    
                    if len(high_volume_poor) > 0:
                        recommendations.append(
                            f"📦 **Priority 2**: {len(high_volume_poor)} high-volume routes have "
                            f">30% late rate. These impact the most shipments."
                        )
                
                # Average delay check
                if 'Avg_Delay' in route_performance.columns:
                    high_delay_routes = route_performance[route_performance['Avg_Delay'] > 5]
                    if len(high_delay_routes) > 0:
                        recommendations.append(
                            f"⏱️ **Priority 3**: {len(high_delay_routes)} routes have average delays "
                            f">5 days. Focus on reducing transit times."
                        )
                
                if recommendations:
                    for rec in recommendations:
                        st.write(rec)
                else:
                    st.info("No specific optimization recommendations at this time")
            else:
                st.info("Route optimization analysis not available")
        except Exception as e:
            st.error("Error in route optimization analysis")
            logger.error(f"Route optimization error: {str(e)}")

# Model insights summary
if st.session_state.get('models_trained', False):
    st.markdown("---")
    st.markdown("### 🎯 Key Insights & Actions")
    
    insights = []
    
    # Late delivery insights
    if 'late_delivery_results' in st.session_state:
        results = st.session_state.late_delivery_results
        if isinstance(results, dict):
            accuracy = results.get('accuracy', 0)
            if accuracy > 0.8:
                insights.append(f"✅ Late delivery prediction model achieved {accuracy*100:.1f}% accuracy")
    
    # Demand forecast insights
    if 'demand_forecast' in st.session_state:
        forecast = st.session_state.demand_forecast
        if forecast is not None and not forecast.empty:
            try:
                future_forecast = forecast[forecast['ds'] > datetime.now()]
                if len(future_forecast) > 0 and 'yhat' in future_forecast.columns:
                    first_val = future_forecast['yhat'].iloc[0]
                    last_val = future_forecast['yhat'].iloc[-1]
                    trend = "increasing" if last_val > first_val else "decreasing"
                    insights.append(f"📈 Demand forecast shows {trend} trend over next {Config.FORECAST_DAYS} days")
            except Exception as e:
                logger.error(f"Forecast insight error: {str(e)}")
    
    # Anomaly insights
    if 'anomaly_stats' in st.session_state:
        stats = st.session_state.anomaly_stats
        if isinstance(stats, dict):
            anomaly_rate = stats.get('anomaly_rate', 0)
            if anomaly_rate > Config.ANOMALY_RATE_WARNING:
                insights.append(
                    f"⚠️ {anomaly_rate:.1f}% anomaly rate "
                    f"detected - investigate unusual patterns"
                )
    
    if insights:
        for insight in insights:
            st.write(insight)
    else:
        st.info("Train models to see insights and recommendations")
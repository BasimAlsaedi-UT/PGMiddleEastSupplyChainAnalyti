"""
Machine Learning Models for P&G Supply Chain Analytics
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PredictiveModels:
    def __init__(self, data):
        self.data = data
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        
    def prepare_features_for_late_prediction(self):
        """Prepare features for late delivery prediction"""
        # Create feature dataframe
        features_df = self.data.copy()
        
        # Create target variable (1 if Late, 0 otherwise)
        features_df['Is_Late'] = (features_df['Delivery_Status'] == 'Late').astype(int)
        
        # Extract time-based features
        features_df['Ship_DayOfWeek'] = pd.to_datetime(features_df['Actual_Ship_Date']).dt.dayofweek
        features_df['Ship_Month'] = pd.to_datetime(features_df['Actual_Ship_Date']).dt.month
        features_df['Ship_Quarter'] = pd.to_datetime(features_df['Actual_Ship_Date']).dt.quarter
        
        # Encode categorical variables
        categorical_cols = ['Category', 'Master_Brand', 'Source', 'SLS_Plant']
        
        for col in categorical_cols:
            if col in features_df.columns:
                le = LabelEncoder()
                # Ensure all values are strings before encoding
                features_df[f'{col}_Encoded'] = le.fit_transform(features_df[col].fillna('Unknown').astype(str))
                self.encoders[col] = le
        
        # Select features
        feature_cols = [
            'Ship_DayOfWeek', 'Ship_Month', 'Ship_Quarter',
            'Category_Encoded', 'Master_Brand_Encoded', 
            'Source_Encoded', 'SLS_Plant_Encoded'
        ]
        
        # Add quantity if available
        if 'Quantity' in features_df.columns:
            # Ensure Quantity is numeric
            features_df['Quantity'] = pd.to_numeric(features_df['Quantity'], errors='coerce').fillna(0)
            features_df['Quantity_Log'] = np.log1p(features_df['Quantity'])
            feature_cols.append('Quantity_Log')
        
        # Remove rows with missing values
        valid_features = [col for col in feature_cols if col in features_df.columns]
        X = features_df[valid_features].dropna()
        y = features_df.loc[X.index, 'Is_Late']
        
        return X, y, valid_features
    
    def train_late_delivery_model(self):
        """Train Random Forest model for late delivery prediction"""
        X, y, feature_names = self.prepare_features_for_late_prediction()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        rf_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = rf_model.predict(X_test)
        
        # Handle cases where we might have only one class
        y_pred_proba = rf_model.predict_proba(X_test)
        if y_pred_proba.shape[1] == 1:
            # Only one class present, can't calculate meaningful probabilities
            y_pred_proba_positive = np.zeros(len(y_test))
            auc_score = 0.5  # Random performance
        else:
            y_pred_proba_positive = y_pred_proba[:, 1]
            auc_score = roc_auc_score(y_test, y_pred_proba_positive)
        
        # Calculate metrics
        accuracy = rf_model.score(X_test, y_test)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Store model
        self.models['late_delivery'] = rf_model
        
        results = {
            'accuracy': accuracy,
            'auc_score': auc_score,
            'feature_importance': feature_importance,
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'model': rf_model,
            'X_test': X_test,
            'y_test': y_test,
            'y_pred_proba': y_pred_proba_positive  # Store only positive class probabilities
        }
        
        return results
    
    def create_roc_curve(self, y_true, y_pred_proba):
        """Create ROC curve visualization"""
        # y_pred_proba should already be 1D (positive class probabilities)
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        auc_score = roc_auc_score(y_true, y_pred_proba) if len(np.unique(y_true)) > 1 else 0.5
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=fpr, y=tpr,
            mode='lines',
            name=f'ROC curve (AUC = {auc_score:.3f})',
            line=dict(width=2)
        ))
        
        # Add diagonal line
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='lines',
            name='Random',
            line=dict(dash='dash', color='gray')
        ))
        
        fig.update_layout(
            title='ROC Curve - Late Delivery Prediction',
            xaxis_title='False Positive Rate',
            yaxis_title='True Positive Rate',
            width=600,
            height=500
        )
        
        return fig
    
    def predict_late_risk(self, new_data):
        """Predict late delivery risk for new shipments"""
        if 'late_delivery' not in self.models:
            return None
        
        model = self.models['late_delivery']
        
        # Prepare features (same as training)
        features_df = new_data.copy()
        
        # Extract time-based features
        features_df['Ship_DayOfWeek'] = pd.to_datetime(features_df['Actual_Ship_Date']).dt.dayofweek
        features_df['Ship_Month'] = pd.to_datetime(features_df['Actual_Ship_Date']).dt.month
        features_df['Ship_Quarter'] = pd.to_datetime(features_df['Actual_Ship_Date']).dt.quarter
        
        # Add quantity if available
        if 'Quantity' in features_df.columns:
            features_df['Quantity_Log'] = np.log1p(features_df['Quantity'].fillna(0))
        
        # Encode categorical variables using stored encoders
        for col, encoder in self.encoders.items():
            if col in features_df.columns:
                try:
                    # Handle unknown categories
                    known_categories = set(encoder.classes_)
                    features_df[f'{col}_Temp'] = features_df[col].fillna('Unknown')
                    features_df[f'{col}_Temp'] = features_df[f'{col}_Temp'].apply(
                        lambda x: x if x in known_categories else encoder.classes_[0]
                    )
                    features_df[f'{col}_Encoded'] = encoder.transform(features_df[f'{col}_Temp'])
                    features_df.drop(f'{col}_Temp', axis=1, inplace=True)
                except Exception as e:
                    features_df[f'{col}_Encoded'] = 0  # Default value if encoding fails
        
        # Prepare feature matrix
        feature_cols = model.feature_names_in_
        # Only use columns that exist in the new data
        available_cols = [col for col in feature_cols if col in features_df.columns]
        X_new = features_df[available_cols]
        
        # If columns are missing, add them with default values
        for col in feature_cols:
            if col not in X_new.columns:
                if 'Quantity_Log' in col:
                    X_new[col] = 0  # Default for missing quantity
                else:
                    X_new[col] = 0  # Default for other missing features
        
        # Reorder columns to match training
        X_new = X_new[feature_cols]
        
        # Predict
        risk_scores = model.predict_proba(X_new)[:, 1]
        predictions = model.predict(X_new)
        
        # Add to dataframe
        new_data['Late_Risk_Score'] = risk_scores
        new_data['Late_Prediction'] = predictions
        
        return new_data
    
    def train_demand_forecast(self, sales_data=None):
        """Train Prophet model for demand forecasting"""
        if not PROPHET_AVAILABLE:
            # Return simple forecast if Prophet not available
            return self._simple_forecast(sales_data)
            
        if sales_data is None:
            # Use shipping data as proxy for demand
            daily_demand = self.data.groupby(
                pd.Grouper(key='Actual_Ship_Date', freq='D')
            ).size().reset_index(name='y')
            daily_demand.columns = ['ds', 'y']
        else:
            # Use actual sales data
            daily_demand = sales_data.groupby(
                pd.Grouper(key='Date', freq='D')
            )['Sales'].sum().reset_index()
            daily_demand.columns = ['ds', 'y']
        
        # Initialize Prophet model
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05
        )
        
        # Add monthly seasonality
        model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # Fit model
        model.fit(daily_demand)
        
        # Make future predictions
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        
        # Store model
        self.models['demand_forecast'] = model
        
        return model, forecast
    
    def _simple_forecast(self, sales_data=None):
        """Simple forecast when Prophet is not available"""
        if sales_data is None:
            daily_demand = self.data.groupby(
                pd.Grouper(key='Actual_Ship_Date', freq='D')
            ).size().reset_index(name='y')
            daily_demand.columns = ['ds', 'y']
        else:
            daily_demand = sales_data.groupby(
                pd.Grouper(key='Date', freq='D')
            )['Sales'].sum().reset_index()
            daily_demand.columns = ['ds', 'y']
        
        # Simple moving average forecast
        last_30_days = daily_demand['y'].tail(30).mean()
        future_dates = pd.date_range(
            start=daily_demand['ds'].max() + timedelta(days=1),
            periods=30,
            freq='D'
        )
        
        forecast = pd.DataFrame({
            'ds': pd.concat([daily_demand['ds'], pd.Series(future_dates)]),
            'yhat': pd.concat([daily_demand['y'], pd.Series([last_30_days] * 30)]),
            'yhat_lower': pd.concat([daily_demand['y'] * 0.9, pd.Series([last_30_days * 0.8] * 30)]),
            'yhat_upper': pd.concat([daily_demand['y'] * 1.1, pd.Series([last_30_days * 1.2] * 30)])
        })
        
        # Create mock model object
        class SimpleModel:
            def __init__(self, history):
                self.history = history
            
            def predict(self, df):
                # Simple prediction for compatibility
                result = pd.DataFrame({
                    'ds': df['ds'],
                    'yhat': [last_30_days] * len(df),
                    'weekly': [0] * len(df),
                    'monthly': [0] * len(df)
                })
                return result
        
        model = SimpleModel(daily_demand)
        return model, forecast
    
    def create_forecast_plot(self, model, forecast):
        """Create forecast visualization"""
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=model.history['ds'],
            y=model.history['y'],
            mode='markers',
            name='Historical',
            marker=dict(color='blue', size=6)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            mode='lines',
            name='Forecast',
            line=dict(color='red', width=2)
        ))
        
        # Confidence intervals
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_upper'],
            fill=None,
            mode='lines',
            line_color='rgba(0,100,80,0)',
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_lower'],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,100,80,0)',
            name='Confidence Interval'
        ))
        
        fig.update_layout(
            title='Demand Forecast - Next 30 Days',
            xaxis_title='Date',
            yaxis_title='Demand',
            hovermode='x unified'
        )
        
        return fig
    
    def train_anomaly_detection(self):
        """Train Isolation Forest for anomaly detection"""
        # Prepare features
        features = []
        
        # Numeric features
        numeric_cols = ['Quantity', 'Delay_Days']
        for col in numeric_cols:
            if col in self.data.columns:
                features.append(col)
        
        # Create derived features
        if 'Delivery_Status' in self.data.columns:
            self.data['Late_Binary'] = (self.data['Delivery_Status'] == 'Late').astype(int)
            features.append('Late_Binary')
        
        # Select and scale features
        X = self.data[features].dropna()
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train Isolation Forest
        iso_forest = IsolationForest(
            contamination=0.05,  # Expect 5% anomalies
            random_state=42,
            n_estimators=100
        )
        
        iso_forest.fit(X_scaled)
        
        # Predict anomalies
        anomaly_scores = iso_forest.score_samples(X_scaled)
        anomaly_labels = iso_forest.predict(X_scaled)
        
        # Store results
        self.data.loc[X.index, 'Anomaly_Score'] = anomaly_scores
        self.data.loc[X.index, 'Is_Anomaly'] = (anomaly_labels == -1).astype(int)
        
        # Store model and scaler
        self.models['anomaly_detection'] = iso_forest
        self.scalers['anomaly_scaler'] = scaler
        
        # Calculate anomaly statistics
        anomaly_stats = {
            'total_anomalies': (anomaly_labels == -1).sum(),
            'anomaly_rate': (anomaly_labels == -1).mean() * 100,
            'features_used': features
        }
        
        return anomaly_stats
    
    def create_anomaly_scatter(self):
        """Create scatter plot of anomalies"""
        if 'Anomaly_Score' not in self.data.columns:
            return None
        
        anomaly_data = self.data[self.data['Anomaly_Score'].notna()].copy()
        
        fig = px.scatter(
            anomaly_data,
            x='Delay_Days',
            y='Quantity',
            color='Is_Anomaly',
            color_discrete_map={0: 'blue', 1: 'red'},
            labels={'Is_Anomaly': 'Anomaly'},
            title='Anomaly Detection Results',
            hover_data=['Category', 'Master_Brand', 'Delivery_Status']
        )
        
        fig.update_traces(
            marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')),
            selector=dict(mode='markers')
        )
        
        return fig
    
    def route_optimization_score(self):
        """Calculate route optimization potential"""
        # Group by source and destination (plant)
        route_performance = self.data.groupby(['Source', 'SLS_Plant']).agg({
            'Delivery_Status': lambda x: (x == 'Late').mean() * 100,
            'Delay_Days': 'mean',
            'Quantity': 'sum'
        }).round(2)
        
        route_performance.columns = ['Late_Rate', 'Avg_Delay', 'Total_Volume']
        
        # Calculate optimization score (higher score = more potential for improvement)
        max_volume = route_performance['Total_Volume'].max()
        if max_volume > 0:
            volume_component = (route_performance['Total_Volume'] / max_volume * 100) * 0.2
        else:
            volume_component = 0
        
        route_performance['Optimization_Score'] = (
            route_performance['Late_Rate'] * 0.5 +
            route_performance['Avg_Delay'] * 0.3 +
            volume_component
        )
        
        # Sort by optimization potential
        route_performance = route_performance.sort_values('Optimization_Score', ascending=False)
        
        return route_performance
    
    def create_route_optimization_heatmap(self, route_performance):
        """Create heatmap for route optimization"""
        # Pivot for heatmap
        pivot_data = route_performance.reset_index().pivot(
            index='Source',
            columns='SLS_Plant',
            values='Optimization_Score'
        )
        
        # Fill NaN values with 0 (no route exists = no optimization needed)
        pivot_data_filled = pivot_data.fillna(0)
        
        # Create text annotations - show "N/A" for non-existent routes
        text_data = pivot_data.round(1).fillna("N/A")
        
        fig = px.imshow(
            pivot_data_filled,
            labels=dict(x="Destination Plant", y="Source", color="Optimization Score"),
            title="Route Optimization Potential Heatmap",
            color_continuous_scale='Reds',
            aspect='auto'  # Adjust aspect ratio automatically
        )
        
        fig.update_traces(
            text=text_data,
            texttemplate='%{text}',
            textfont_size=10
        )
        
        # Update layout for better readability
        fig.update_xaxes(side="bottom")
        fig.update_layout(
            height=400,
            margin=dict(l=100, r=50, t=50, b=100)
        )
        
        return fig
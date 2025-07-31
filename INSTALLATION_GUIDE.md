# Installation Guide

## Quick Start

1. **Install core dependencies only** (recommended for first run):
```bash
pip install streamlit pandas numpy plotly openpyxl xlrd scipy
```

2. **Run the app**:
```bash
python run_app.py
```

The app will work with these core dependencies. Some advanced features will be disabled but all main functionality will work.

## Full Installation (Optional)

For all features including advanced statistical analysis and ML predictions:

```bash
# Windows
install_dependencies.bat

# Mac/Linux
pip install -r requirements.txt
```

## Troubleshooting

### If you get "ModuleNotFoundError"

The app is designed to work even if some packages fail to install:
- `statsmodels` - Required for advanced statistical tests
- `prophet` - Required for time series forecasting  
- `scikit-learn` - Required for ML predictions

Without these, the app will still run but those specific features will show a message.

### Python Version Issues

If you're using Python 3.11+, some packages like Prophet might not install. The app will automatically fall back to simpler methods.

## Minimal Dependencies

If you just want to see the dashboards and basic analytics:
```bash
pip install streamlit pandas plotly openpyxl
```

This will give you:
- All dashboards
- KPI calculations  
- Charts and visualizations
- Data quality monitoring
- Basic analytics

The app is designed to gracefully handle missing dependencies!
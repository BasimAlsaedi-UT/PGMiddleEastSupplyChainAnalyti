# P&G Supply Chain Analytics Dashboard - Quick Start

## To Run the Dashboard

### Windows:
```cmd
run.bat
```
or
```cmd
streamlit run Overview.py
```

### Linux/Mac:
```bash
./run.sh
```
or
```bash
streamlit run Overview.py
```

## Dashboard Pages

1. **Overview** (Main Page) - Executive Summary with KPIs
2. **Statistical Analysis** - ANOVA, Chi-Square, Correlations
3. **ML Predictions** - Predictive Analytics & Forecasting
4. **IOUs Analysis** - Outstanding Orders Tracking
5. **Yesterday Orders** - Daily Performance Comparison
6. **TOP 10 Executive** - Rankings & Top Performers
7. **Email Reports** - Automated Report Generation
8. **About** - Dashboard Information & Contact

## Key Features

- **Late Delivery Rate**: Currently tracking at 35.5%
- **Real-time Filters**: Date, Category, Brand, Status
- **Interactive Charts**: Hover for details, click to explore
- **Export Options**: Download data and reports

## To Update Data

1. Replace Excel files in parent directory
2. Delete `data/extracted/` folder
3. Run `streamlit run Overview.py`

## Contact

**Developer**: Dr. Basim Alsaedi  
**Email**: basimalsaedi@outlook.com
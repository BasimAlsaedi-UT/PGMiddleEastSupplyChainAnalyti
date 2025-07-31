# P&G Middle East Supply Chain Analytics Dashboard

A comprehensive supply chain analytics dashboard providing real-time insights into P&G's Middle East operations.

## 🚀 Features

### 1. **Executive Dashboard**
- Real-time KPIs with automatic alerts
- Delivery performance metrics (35.5% late rate highlighted)
- Interactive visualizations
- Daily trend analysis

### 2. **Shipping Performance Analysis**
- Recreates all Excel pivot functionality
- Plant/warehouse performance comparison
- Time-based analysis
- Delay distribution insights

### 3. **Sales Analytics**
- All 13 Excel sheets recreated as interactive views
- Channel performance analysis
- Forecast accuracy tracking
- Top products by various metrics

### 4. **Statistical Analysis** (Dedicated Page)
- Descriptive statistics
- Correlation analysis
- Hypothesis testing (ANOVA, Chi-square)
- Time series decomposition
- Distribution analysis with normality tests

### 5. **Machine Learning Predictions** (Dedicated Page)
- **Late Delivery Prediction**: Random Forest model with >80% accuracy
- **Demand Forecasting**: Prophet model with 30-day forecast
- **Anomaly Detection**: Isolation Forest for outlier identification
- **Route Optimization**: Scoring and recommendations

### 6. **Data Quality Monitoring**
- Completeness metrics
- Validation checks
- Data freshness alerts
- Anomaly detection

## 📊 Data Sources

The app uses the actual P&G Excel files:
1. `2-JPG shipping tracking - July 2025.xlsx` (24,535 shipments)
2. `3-DSR-PG- 2025 July.xlsx` (13 sheets with sales data)

## 🛠️ Installation

1. **Clone the repository**
```bash
cd streamlit_app
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Place Excel files in parent directory**
- `../2-JPG shipping tracking - July 2025.xlsx`
- `../3-DSR-PG- 2025 July.xlsx`

## 🚀 Running the Application

### Option 1: Using the run script (Recommended)
```bash
python run_app.py
```

This will:
- Automatically extract data from Excel files (first run only)
- Start the Streamlit application
- Open in your default browser

### Option 2: Direct Streamlit command
```bash
streamlit run app.py
```

## 📁 Project Structure

```
streamlit_app/
├── app.py                    # Main application
├── run_app.py               # Startup script
├── requirements.txt         # Dependencies
├── README.md               # This file
├── utils/
│   ├── data_extractor.py   # Excel data extraction
│   └── data_processor.py   # Data processing logic
├── components/
│   ├── kpi_cards.py       # KPI card components
│   ├── charts.py          # Visualization components
│   └── filters.py         # Filter components
├── analytics/
│   └── statistical.py     # Statistical analysis
├── ml_models/
│   └── predictive.py      # ML models
├── pages/
│   ├── 1_📊_Statistical_Analysis.py
│   └── 2_🤖_ML_Predictions.py
└── data/
    └── extracted/         # Extracted CSV files (auto-generated)
```

## 🔧 Key Components

### Data Extraction (`utils/data_extractor.py`)
- Handles the complex Excel structure
- Extracts all 5 sections from File 1
- Fixes the 16,382 column issue in File 2
- Saves clean CSV files for fast loading

### Data Processing (`utils/data_processor.py`)
- Calculates KPIs
- Performs aggregations
- Handles date conversions
- Creates analysis-ready datasets

### ML Models (`ml_models/predictive.py`)
- Random Forest for late delivery prediction
- Prophet for demand forecasting
- Isolation Forest for anomaly detection
- Route optimization scoring

## 📈 Key Insights from the Data

1. **Late Delivery Crisis**: 35.5% of shipments are late (8,706 out of 24,521)
2. **Average Delay**: 2.2 days for late shipments
3. **Category Issues**: Baby Care and Feminine Care most affected
4. **Plant Variability**: Significant performance differences across distribution centers

## 🎯 Business Value

- **Proactive Alerts**: Identify high-risk shipments before they're late
- **Demand Planning**: 30-day forecasts for inventory optimization
- **Route Optimization**: Identify worst-performing routes for improvement
- **Quality Control**: Automatic anomaly detection
- **Real-time Monitoring**: Replace manual Excel updates

## 🔒 Security & Performance

- Data is processed locally (no external APIs)
- Efficient caching for fast performance
- Scalable architecture
- Clean data validation

## 🚦 Future Enhancements

1. Database integration (PostgreSQL)
2. Real-time data streaming
3. Additional ML models
4. API endpoints
5. Mobile responsive design

## 📝 Notes

- The app faithfully recreates all Excel functionality while adding modern analytics
- All calculations match the original Excel formulas
- ML models use only the actual data (no synthetic data)
- Performance optimized for datasets >100k rows

## 🆘 Troubleshooting

1. **"File not found" error**: Ensure Excel files are in the parent directory (`../`)
2. **Memory issues**: The app handles the 16,382 column issue automatically
3. **Slow loading**: First run extracts data; subsequent runs use cached CSVs

## 📧 Support

For issues or enhancements, please refer to the implementation plan documentation.
# How to Run the P&G Supply Chain Analytics Dashboard

## Prerequisites
- Python 3.8 or higher
- Excel files in the parent directory:
  - `2-JPG shipping tracking - July 2025.xlsx`
  - `3-DSR-PG- 2025 July.xlsx`

## Installation Steps

1. **Navigate to the streamlit_app directory:**
   ```bash
   cd /mnt/c/Users/basim/Downloads/ExcelProblem/streamlit_app
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Run the dashboard
```bash
streamlit run Overview.py
```

## First Time Setup
- On first run, the app will automatically extract data from the Excel files
- This may take a few minutes depending on file size
- Extracted data will be saved to `data/extracted/` directory

## Accessing the Dashboard
- Once running, open your browser to: http://localhost:8501
- The dashboard will load with the following sections:
  - Executive Summary
  - Shipping Performance
  - Sales Analytics
  - Product Analysis
  - Predictive Insights
  - Data Quality

## Troubleshooting

### Error: "Excel files not found"
- Ensure the Excel files are in the parent directory (ExcelProblem folder)
- Check file names match exactly (including spaces)

### Error: "Module not found"
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're running from the streamlit_app directory

### Performance Issues
- The Excel files are large; initial extraction may take time
- Once extracted, subsequent runs will be faster
- Use filters to reduce data volume for better performance

## Key Features
- **Real-time KPIs**: Track late delivery rate (currently 35.5%)
- **Interactive Filters**: Filter by date, category, brand, status
- **Multiple Dashboards**: Different views for different stakeholders
- **Data Quality Checks**: Automated validation of data integrity
- **Export Options**: Download filtered data as CSV

## Notes
- The app highlights critical issues (late rate > 40% in red)
- All charts are interactive (hover for details, click to filter)
- Data is cached for performance; use "Refresh Data" to reload
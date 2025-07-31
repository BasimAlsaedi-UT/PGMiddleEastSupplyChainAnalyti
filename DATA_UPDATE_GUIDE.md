# Data Update Guide for P&G Supply Chain Analytics Dashboard

## Overview
The dashboard uses two Excel files as data sources. To update the dashboard with new data, you need to replace these files and refresh the application.

## Required Files
1. **Shipping Tracking File**: `2-JPG shipping tracking - July 2025.xlsx`
2. **Sales Data File**: `3-DSR-PG- 2025 July.xlsx`

## Update Methods

### Method 1: Simple File Replacement
1. **Locate the current files** in the parent directory (ExcelProblem folder)
2. **Backup the old files** (optional but recommended)
3. **Replace with new files** using the EXACT same names:
   - `2-JPG shipping tracking - July 2025.xlsx`
   - `3-DSR-PG- 2025 July.xlsx`
4. **Delete the extracted data folder**: `streamlit_app/data/extracted/`
5. **Restart the Streamlit app**
6. The app will automatically extract data from the new files on next run

### Method 2: Update with Different File Names
If your new files have different names, modify the file paths in `Overview.py`:

```python
# Around line 88-90 in Overview.py
extractor = DataExtractor(
    file1_path=os.path.join(parent_dir, "YOUR_NEW_SHIPPING_FILE.xlsx"),
    file2_path=os.path.join(parent_dir, "YOUR_NEW_SALES_FILE.xlsx")
)
```

### Method 3: Automated Monthly Updates
For regular monthly updates, you can rename your files to match the expected pattern:
- Shipping: `2-JPG shipping tracking - [Month] [Year].xlsx`
- Sales: `3-DSR-PG- [Year] [Month].xlsx`

## Important Notes

### File Format Requirements
The new Excel files must maintain the same structure:

#### Shipping File (File 1):
- Sheet name: `Sheet1`
- Data starts at row 13 (with headers at row 13)
- Columns A-O: Main shipping data
- Columns P-U: Pivot data
- Columns Y-AF: Calculations
- Columns AH-AM: Reference data
- Row 3, Columns B-D: Filter values

#### Sales File (File 2):
- Main sheet: Data starting at row 14
- Sheet `TOP 10`: TOP 10 products data
- Sheet `Pivot`: Sales pivot data

### Data Refresh Process
1. When you restart the app after updating files:
   - The app checks if extracted data exists
   - If not, it automatically extracts from the Excel files
   - Progress is shown in the UI

2. To force a data refresh:
   - Delete the `streamlit_app/data/extracted/` folder
   - Or click the "🔄 Refresh Data" button in the sidebar

### Troubleshooting

#### Error: "File not found"
- Ensure files are in the parent directory (ExcelProblem)
- Check file names match exactly (including spaces)

#### Error: "Column not found"
- New file structure doesn't match expected format
- Check that all required columns exist
- Verify data starts at the correct row

#### Performance Issues
- Large files may take time to process
- First load after update will be slower
- Subsequent loads use cached data

## Automated Update Script (Optional)

Create a Python script for easier updates:

```python
import os
import shutil
from datetime import datetime

def update_dashboard_data(new_shipping_file, new_sales_file):
    """Update dashboard with new data files"""
    
    # Define paths
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    extracted_dir = os.path.join(parent_dir, 'streamlit_app', 'data', 'extracted')
    
    # Backup old files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(parent_dir, f'backup_{timestamp}')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copy new files with correct names
    shutil.copy(new_shipping_file, 
                os.path.join(parent_dir, "2-JPG shipping tracking - July 2025.xlsx"))
    shutil.copy(new_sales_file, 
                os.path.join(parent_dir, "3-DSR-PG- 2025 July.xlsx"))
    
    # Remove extracted data to force refresh
    if os.path.exists(extracted_dir):
        shutil.rmtree(extracted_dir)
    
    print("Data files updated successfully!")
    print("Please restart the Streamlit app to see new data.")

# Usage
update_dashboard_data("path/to/new_shipping.xlsx", "path/to/new_sales.xlsx")
```

## Best Practices
1. **Test with sample data first** before production update
2. **Keep backups** of previous data files
3. **Document any changes** to file structure
4. **Update during off-hours** to minimize disruption
5. **Verify data integrity** after update using the Data Quality page
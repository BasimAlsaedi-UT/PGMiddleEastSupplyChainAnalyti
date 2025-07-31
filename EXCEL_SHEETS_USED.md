# Excel Sheets Used in P&G Dashboard

## File 1: 2-JPG shipping tracking - July 2025.xlsx

### Sheet Used: `Sheet1` (Only sheet used from this file)

From this single sheet, the following data sections are extracted:

1. **Main Shipping Data** (Columns A-O, starting row 14)
   - Date1, Date2
   - SLS_Plant
   - DLV_Shipping_Status
   - Category
   - Master_Brand
   - Brand
   - L_I
   - Planning_Level
   - Quantity
   - Source
   - Actual_Ship_Date
   - Month
   - Requested_Ship_Date
   - Delivery_Status

2. **Pivot Data** (Columns P-U, starting row 14)
   - Additional pivot table data

3. **Calculations Data** (Columns Y-AF, starting row 14)
   - Pre-calculated metrics and formulas

4. **Reference Data** (Columns AG-AM, rows 1-100)
   - Reference/lookup data

5. **Filter Settings** (Columns A-B, rows 4-11)
   - Pre-defined filter values

## File 2: 3-DSR-PG- 2025 July.xlsx

### Sheets Used: ALL sheets in the file

The system reads **all sheets** from this file dynamically:

1. **Data** (Main sheet)
   - Only first 25 columns are used
   - Contains sales data with columns like:
     - Channel
     - Market
     - Category
     - Target
     - Sales
     - IOUs
     - Yesterday_Sales
     - Planning Level
     - Brand

2. **TOP 10**
   - Contains TOP 10 products data
   - Used for executive summaries and rankings

3. **Pivot**
   - Sales pivot table data
   - Used for aggregated views

4. Any other sheets present in the file are also read and stored

## Important Notes

### For File 1 (Shipping):
- **Only `Sheet1` is used** - other sheets (if any) are ignored
- Data extraction starts at row 14 for most sections
- Different column ranges are used for different data types

### For File 2 (Sales):
- **All sheets are read dynamically**
- The system adapts to whatever sheets are present
- Sheet names are preserved and used in the application

### Data Structure Requirements

When updating with new files, ensure:

1. **File 1 must have**:
   - A sheet named `Sheet1`
   - Data starting at row 14 in the specified column ranges
   - Filter settings in rows 4-11

2. **File 2 must have**:
   - At minimum a sheet named `Data`
   - Sheets `TOP 10` and `Pivot` for full functionality
   - Column structure matching the original files

### Verification

To check which sheets are in your Excel files:
```python
import pandas as pd

# Check File 1 sheets
xl1 = pd.ExcelFile("2-JPG shipping tracking - July 2025.xlsx")
print("File 1 sheets:", xl1.sheet_names)

# Check File 2 sheets
xl2 = pd.ExcelFile("3-DSR-PG- 2025 July.xlsx")
print("File 2 sheets:", xl2.sheet_names)
```

Expected output:
- File 1: ['Sheet1', ...] (only Sheet1 is used)
- File 2: ['Data', 'TOP 10', 'Pivot', ...] (all sheets are used)
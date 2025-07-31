# Data Update Instructions

## Quick Update (Same File Names)

1. **Replace the Excel files** in the parent ExcelProblem folder:
   - `2-JPG shipping tracking - July 2025.xlsx`
   - `3-DSR-PG- 2025 July.xlsx`

2. **Delete cached data**:
   ```bash
   rm -rf streamlit_app/data/extracted/
   ```

3. **Restart the app**:
   ```bash
   streamlit run Overview.py
   ```

## Using the Update Script

### Basic Usage
```bash
cd streamlit_app
python update_data.py path/to/new_shipping.xlsx path/to/new_sales.xlsx
```

### Keep Original File Names
```bash
python update_data.py --keep-names path/to/shipping_aug_2025.xlsx path/to/sales_aug_2025.xlsx
```

Note: If you use `--keep-names`, you must update the file paths in `Overview.py` lines 89-90.

## Manual Update Process

### Step 1: Prepare New Files
Ensure your new Excel files have the same structure as the original files.

### Step 2: Backup Old Data (Optional)
```bash
mkdir backup_$(date +%Y%m%d)
cp *.xlsx backup_$(date +%Y%m%d)/
```

### Step 3: Copy New Files
```bash
cp /path/to/new/shipping.xlsx "2-JPG shipping tracking - July 2025.xlsx"
cp /path/to/new/sales.xlsx "3-DSR-PG- 2025 July.xlsx"
```

### Step 4: Clear Cache
```bash
rm -rf streamlit_app/data/extracted/
```

### Step 5: Restart Application
```bash
cd streamlit_app
streamlit run Overview.py
```

## Verification Steps

1. Check the **last update time** in the sidebar
2. Verify the **date range** in the data
3. Check **Data Quality** page for any issues
4. Compare **KPIs** with expected values

## Troubleshooting

### "File not found" Error
- Check file names match exactly (including spaces)
- Ensure files are in the parent directory

### "Column not found" Error
- New file structure doesn't match expected format
- Check DATA_UPDATE_GUIDE.md for required structure

### Performance Issues
- First load after update will be slower
- Large files may take 1-2 minutes to process

## Contact
For issues or questions:
- **Developer**: Basim Alsaedi
- **Email**: basim@example.com
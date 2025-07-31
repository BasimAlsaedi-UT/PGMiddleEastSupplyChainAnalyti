"""
Data Extraction Module for P&G Supply Chain Analytics
Extracts and cleans data from the two Excel files
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataExtractor:
    def __init__(self, file1_path, file2_path):
        self.file1_path = file1_path
        self.file2_path = file2_path
        
    def extract_file1_data(self):
        """Extract all data sections from File 1 (JPG Shipping)"""
        print("Extracting data from File 1...")
        
        # Extract main data (A-O, starting row 14)
        main_data = pd.read_excel(
            self.file1_path, 
            sheet_name='Sheet1',
            skiprows=12,
            usecols='A:O'
        )
        
        # Rename columns based on verified headers
        main_data.columns = [
            'Date1', 'Date2', 'SLS_Plant', 'DLV_Shipping_Status',
            'Category', 'Master_Brand', 'Brand', 'L_I', 'Planning_Level',
            'Quantity', 'Source', 'Actual_Ship_Date', 'Month',
            'Requested_Ship_Date', 'Delivery_Status'
        ]
        
        # Extract pivot data (P-U, starting row 14)
        pivot_data = pd.read_excel(
            self.file1_path,
            sheet_name='Sheet1',
            skiprows=12,
            usecols='P:U'
        )
        
        # Extract calculations (Y-AF, starting row 14)
        calc_data = pd.read_excel(
            self.file1_path,
            sheet_name='Sheet1',
            skiprows=12,
            usecols='Y:AF'
        )
        
        # Extract reference data (AG-AM, starting row 1)
        ref_data = pd.read_excel(
            self.file1_path,
            sheet_name='Sheet1',
            usecols='AG:AM',
            nrows=100
        )
        
        # Extract filter settings (rows 4-11)
        filter_settings = pd.read_excel(
            self.file1_path,
            sheet_name='Sheet1',
            skiprows=3,
            nrows=8,
            usecols='A:B',
            names=['Filter_Name', 'Filter_Value']
        )
        
        # Clean and process main data
        main_data = self._clean_main_data(main_data)
        
        return {
            'main_data': main_data,
            'pivot_data': pivot_data,
            'calc_data': calc_data,
            'ref_data': ref_data,
            'filter_settings': filter_settings
        }
    
    def extract_file2_data(self):
        """Extract data from File 2 (DSR-PG)"""
        print("Extracting data from File 2...")
        
        # Get all sheet names
        xl_file = pd.ExcelFile(self.file2_path)
        sheet_data = {}
        
        for sheet in xl_file.sheet_names:
            if sheet == 'Data':
                # Special handling for Data sheet - only first 25 columns
                df = pd.read_excel(
                    self.file2_path,
                    sheet_name=sheet,
                    usecols=range(25)
                )
            else:
                df = pd.read_excel(self.file2_path, sheet_name=sheet)
            
            sheet_data[sheet] = df
            print(f"  Loaded sheet: {sheet} - {df.shape}")
        
        # Clean the main data sheet
        if 'Data' in sheet_data:
            sheet_data['Data'] = self._clean_sales_data(sheet_data['Data'])
        
        return sheet_data
    
    def _clean_main_data(self, df):
        """Clean the main shipping data"""
        # Remove header rows if any
        df = df[df['Delivery_Status'].notna()]
        df = df[~df['Delivery_Status'].isin(['Status', 'Delivery Status'])]
        
        # Convert dates to datetime
        date_columns = ['Actual_Ship_Date', 'Requested_Ship_Date']
        for col in date_columns:
            if col in df.columns:
                # First check if it's already datetime
                if df[col].dtype == 'datetime64[ns]':
                    continue
                # Try to convert - it might be Excel serial numbers or date strings
                try:
                    # First try standard datetime conversion
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except (ValueError, TypeError):
                    # If that fails, try Excel serial number conversion
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce', origin='1899-12-30', unit='D')
                    except (ValueError, TypeError):
                        pass
        
        # Convert Date1 and Date2 if they're dates
        for col in ['Date1', 'Date2']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calculate delay days
        if 'Actual_Ship_Date' in df.columns and 'Requested_Ship_Date' in df.columns:
            try:
                df['Delay_Days'] = (df['Actual_Ship_Date'] - df['Requested_Ship_Date']).dt.days
            except (TypeError, AttributeError):
                df['Delay_Days'] = 0  # Default if calculation fails
        
        # Clean quantity column
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
        
        # Create unique ID
        df['Transaction_ID'] = range(1, len(df) + 1)
        
        # Filter valid delivery statuses
        valid_statuses = ['Advanced', 'Late', 'On Time', 'Not Due']
        df = df[df['Delivery_Status'].isin(valid_statuses)]
        
        return df
    
    def _clean_sales_data(self, df):
        """Clean the sales data from File 2"""
        # Rename columns if needed
        column_mapping = {
            'Column1': 'Channel1',
            'Column2': 'Channel2',
            'Column3': 'Code',
            'Column4': 'Principal',
            'Column5': 'Channel',
            'Column6': 'Category',
            'Column7': 'Master_Brand',
            'Column8': 'Brand',
            'Column9': 'L_I',
            'Column10': 'Planning_Level',
            'Column11': 'Target',
            'Column12': 'Sales',
            'Column13': 'Shipped',
            'Column14': 'Late',
            'Column15': 'Not_Due',
            'Column16': 'Yesterday_Sales',
            'Column17': 'IOUs'
        }
        
        # Apply mapping for unnamed columns
        for i, col in enumerate(df.columns):
            if col.startswith('Unnamed') or col.startswith('...'):
                if f'Column{i+1}' in column_mapping:
                    df.rename(columns={col: column_mapping[f'Column{i+1}']}, inplace=True)
        
        # Convert numeric columns
        numeric_cols = ['Target', 'Sales', 'Shipped', 'Late', 'Not_Due', 'Yesterday_Sales', 'IOUs']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Create Sales vs Target percentage
        if 'Sales' in df.columns and 'Target' in df.columns:
            df['Sales_vs_Target_Pct'] = (df['Sales'].div(df['Target'].replace(0, 1)) * 100).round(1)
        
        return df
    
    def save_extracted_data(self, output_dir='data/extracted'):
        """Save all extracted data to CSV files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract File 1
        file1_data = self.extract_file1_data()
        file1_data['main_data'].to_csv(f'{output_dir}/shipping_main_data.csv', index=False)
        file1_data['pivot_data'].to_csv(f'{output_dir}/shipping_pivot_data.csv', index=False)
        file1_data['calc_data'].to_csv(f'{output_dir}/shipping_calc_data.csv', index=False)
        file1_data['ref_data'].to_csv(f'{output_dir}/shipping_ref_data.csv', index=False)
        file1_data['filter_settings'].to_csv(f'{output_dir}/shipping_filters.csv', index=False)
        
        # Extract File 2
        file2_data = self.extract_file2_data()
        for sheet_name, df in file2_data.items():
            safe_name = sheet_name.replace(' ', '_').replace('-', '_')
            df.to_csv(f'{output_dir}/sales_{safe_name}.csv', index=False)
        
        print(f"All data extracted and saved to {output_dir}")
        
        # Save extraction metadata
        metadata = {
            'extraction_date': datetime.now().isoformat(),
            'file1_sheets': list(file1_data.keys()),
            'file2_sheets': list(file2_data.keys()),  # Fixed: was .items() which included DataFrames
            'total_shipping_records': len(file1_data['main_data']),
            'total_sales_records': len(file2_data.get('Data', pd.DataFrame()))
        }
        
        with open(f'{output_dir}/extraction_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return file1_data, file2_data

# Usage example
if __name__ == "__main__":
    extractor = DataExtractor(
        file1_path="../2-JPG shipping tracking - July 2025.xlsx",
        file2_path="../3-DSR-PG- 2025 July.xlsx"
    )
    
    # Extract and save all data
    file1_data, file2_data = extractor.save_extracted_data()
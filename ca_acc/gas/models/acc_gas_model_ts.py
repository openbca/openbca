"""
SQLMesh model for ACC Gas Model data.

This model scrapes data from the ACC Gas Model Excel file for all
Utilities, and outputs to DuckDB.
"""

from typing import Any
from pandas import DataFrame
from sqlmesh import model, ExecutionContext
import pandas as pd
import os
import time

try:
    import xlwings as xw
    #HAS_XLWINGS = True
except ImportError:
    #HAS_XLWINGS = False
    raise ImportError("xlwings is required. Install with: pip install xlwings")

# ID columns for the model grain
ID_COLUMNS = ["utility", "region", "year", "month", "quarter"]

BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "raw_acc_files"))  # adjust if needed

###SETUP START###
FILE_NAME = "2024 ACC Gas Model v1b_October Update_ver2.xlsx"

#Class: Total Core, End Use: Small Boiler, Emission Control: Uncontrolled
# First numeric data row in the Detailed Output sheet
user_dashboard_first_data_column = 'E'
user_dashboard_last_data_column = 'AJ'
user_dashboard_years_row = 58
emissions_sheet_marginal_ghg_cell = 'G6'
user_dashboard_utility_validation_cell = 'C5'

# Utilities
UTILITIES = ['PG&E', 'Socal Gas', 'SDG&E']

# Check cell ranges and value stream ordering in the User Dashboard sheet
value_stream_ranges_dict = {
    'total': 59,
    'market': 77,
    't_d': 91,
    'environment': 105,
    'upstream_methane': 119,
    'btm_methane': 133,
    'air_quality_adder': 147,
}

# Define the metadata and temporal columns for the output table
columns = {
            "utility": "string",
            "region": "string",
            "year": "int",
            "month": "int",
            "quarter": "int",
        }

###SETUP END###
        
# Add all value_stream columns as float
for value_stream in value_stream_ranges_dict.keys():
    columns[value_stream] = "float"

columns['marginal_ghg'] = "float"

@model(
    name="gas.acc_gas_model_ts",
    kind="FULL",
    grain=ID_COLUMNS,
    columns=columns
)

def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
    """
    Execute the model to scrape ACC Electric Model data.
    
    This function will:
    1. Generate all valid utility/climate zone combinations from UTILITY_CLIMATE_ZONES
    2. For each combination:
       - Prompt user to set utility in Excel
       - Prompt user to manually update macro (if needed) and save file
       - Scrape data after user confirms
    3. Return combined DataFrame with all combinations
    """

    return scrape_all_combinations(
        input_file=FILE_NAME
    )

def read_large_range_in_chunks(sheet, start_col, end_col, start_row, end_row, chunk_size=1000):
    """
    Read a large Excel range in chunks to avoid buffer overflow errors.
    
    Args:
        sheet: xlwings sheet object
        start_col: Starting column letter (e.g., 'P')
        end_col: Ending column letter (e.g., 'AU')
        start_row: Starting row number (e.g., 9)
        end_row: Ending row number (e.g., 8768)
        chunk_size: Number of rows to read per chunk
    
    Returns:
        List of lists representing the data
    """
    all_data = []
    current_row = start_row
    
    while current_row <= end_row:
        chunk_end_row = min(current_row + chunk_size - 1, end_row)
        range_str = f'{start_col}{current_row}:{end_col}{chunk_end_row}'
        
        try:
            chunk_data = sheet.range(range_str).value
            if chunk_data is None:
                break
            
            # Handle single row case
            if not isinstance(chunk_data, list):
                chunk_data = [chunk_data]
            elif len(chunk_data) > 0 and not isinstance(chunk_data[0], list):
                # Single row of data
                chunk_data = [chunk_data]
            
            all_data.extend(chunk_data)
            current_row = chunk_end_row + 1
        except Exception as e:
            print(f"Warning: Error reading chunk {range_str}: {e}")
            break
    
    return all_data


def scrape_all_combinations(input_file):
    """
    Iterate through all utility/climate zone combinations with interactive prompts
    for manual macro updates.
    
    Args:
        input_file: Name of the Excel file
        combinations: List of (utility, climate_zone) tuples to process
    
    Returns:
        DataFrame with all scraped data combined
    """
    file_path = os.path.join(DATA_DIR, input_file)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    
    # Open Excel in VISIBLE mode so user can update macros
    app = xw.App(visible=True)
    app.display_alerts = False
    app.screen_updating = True
    
    wb = None
    all_dfs = []
    
    try:
        # Open workbook
        wb = app.books.open(file_path)
        output_sheet = wb.sheets['User Dashboard']
        
        # Read years from row 6 (first range P6:AU6)
        years_raw = output_sheet.range(f'{user_dashboard_first_data_column}{user_dashboard_years_row}:{user_dashboard_last_data_column}{user_dashboard_years_row}').value
        years = [int(year) for year in years_raw]

        # Iterate through all combinations
        total_combinations = len(UTILITIES)
        combination_num = 0
        
        print(f"\n{'='*60}")
        print(f"Starting data scraping for {total_combinations} combinations")
        print(f"{'='*60}")
        for utility in UTILITIES:
            print(f"  {utility}")
        print(f"{'='*60}\n")
        
        # Iterate through all combinations
        for utility in UTILITIES:
            combination_num += 1
            
            print(f"\n{'='*60}")
            print(f"Combination {combination_num}/{total_combinations}: Utility={utility}")
            print(f"{'='*60}")
            
            # Interactive prompt for user to set values and update macro
            print(f"\n{'='*60}")
            print(f"MANUAL STEP REQUIRED - Combination {combination_num}/{total_combinations}:")
            print("!!!Ensure that the discount rate is set to 0 in the Dashboard Viewer sheet!!!\n")
            print(f"  1. In Excel, set the following filter values:")
            print(f"     - Utility = '{utility}'")
            print(f"  2. If needed, run the macro in Excel")
            print(f"  3. Save the Excel file")
            print(f"  4. Press ENTER here when ready to continue scraping...")
            print(f"{'='*60}")
            
            # Wait for user input
            input()
            
            # Verify the macro ran by checking H2/H3 of the Detailed Output sheet
            actual_utility = output_sheet.range(user_dashboard_utility_validation_cell).value
            
            print(f"\nVerified: {user_dashboard_utility_validation_cell}={actual_utility}")
            
            if str(actual_utility).strip() != str(utility).strip():
                print(f"WARNING: {user_dashboard_utility_validation_cell} shows '{actual_utility}' but expected '{utility}'")
                # Wait for user input
                input()

            print(f"\nScraping data...")
            
            # Scrape data for all value streams
            long_df = None
            for i, value_stream in enumerate(value_stream_ranges_dict.keys()):
                try:
                    avoided_costs = read_large_range_in_chunks(
                        output_sheet,
                        user_dashboard_first_data_column,
                        user_dashboard_last_data_column,
                        value_stream_ranges_dict[value_stream], 
                        value_stream_ranges_dict[value_stream]+11,
                        chunk_size=12
                    )
                    df = pd.DataFrame(avoided_costs, columns=years).reset_index(names='month')

                    df['utility'] = utility.replace('&', '').replace('Socal Gas', 'SCE')
                    df['region'] = None
                    
                    if i == 0:
                        long_df = df.melt(
                            id_vars=['utility', 'region', 'month'],
                            value_vars=years,
                            var_name="year",
                            value_name=value_stream
                        )
                    else:
                        long_df = pd.merge(
                            long_df,
                            df[['month'] + years].melt(
                                id_vars=['month'],
                                value_vars=years,
                                var_name="year",
                                value_name=value_stream
                            ),
                            on=['year', 'month']
                        )
                    print(f"  ✓ {value_stream}: {df.shape[0]} rows")
                except Exception as e:
                    print(f"  ✗ Error scraping {value_stream}: {e}")
                    continue
            
            if long_df is not None and not long_df.empty:
                all_dfs.append(long_df)
                print(f"\n✓ Successfully scraped {len(long_df)} rows for {utility}")
            else:
                print(f"\n✗ No data scraped for {utility}")
                
        # Combine all dataframes
        if not all_dfs:
            print("\nWARNING: No data was scraped!")
            return pd.DataFrame()
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df['month'] = combined_df['month'] + 1

        def month_quarter_map(month):
            if month in [1, 2, 3]:
                return 1
            elif month in [4, 5, 6]:
                return 2
            elif month in [7, 8, 9]:
                return 3
            elif month in [10, 11, 12]:
                return 4
            else:
                return None

        combined_df['quarter'] = combined_df['month'].apply(month_quarter_map)

        emissions_sheet = wb.sheets['Emissions']
        
        # Read emissions sheet marginal GHG cell
        marginal_ghg = emissions_sheet.range(emissions_sheet_marginal_ghg_cell).value
        combined_df['marginal_ghg'] = marginal_ghg 

        print(f"\n{'='*60}")
        print(f"SCRAPING COMPLETE!")
        print(f"Total rows: {len(combined_df)}")
        print(f"Total combinations: {len(all_dfs)}")
        print(f"{'='*60}\n")
        
        return combined_df
        
    finally:
        # Keep workbook open until user closes it, or close automatically
        print("\nClosing Excel...")
        if wb:
            try:
                wb.close()
            except:
                pass
        if app:
            try:
                app.quit()
            except:
                pass
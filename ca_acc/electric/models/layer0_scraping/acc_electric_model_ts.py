"""
SQLMesh model for ACC Electric Model data.

This model scrapes data from the ACC Electric Model Excel file for all
combinations of Utility and Climate Zone, and outputs to DuckDB.
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
ID_COLUMNS = ["utility", "region", "year", "hour_of_year", "month", "quarter"]

BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "raw_acc_files"))  # adjust if needed

###SETUP START###
FILE_NAME = "2024 ACC Electric Model v1b.xlsb"
OUTPUT_TABLE_NAME = f"full_ca_avoided_costs_acc"

# First numeric data row in the Detailed Output sheet
detailed_output_first_data_row = 9
detailed_output_utility_validation_cell = 'H2'
detailed_output_climate_zone_validation_cell = 'H3'

detialed_output_years_cell_initial = 'P6'
detialed_output_years_cell_final = 'AU6'

# Utility to Climate Zone mapping
UTILITY_CLIMATE_ZONES = {
    'PG&E': ['CZ1'],#, 'CZ2', 'CZ3A', 'CZ3B', 'CZ4', 'CZ5', 'CZ11', 'CZ12', 'CZ13', 'CZ16'],
    'SCE': ['CZ6'],# 'CZ8', 'CZ9', 'CZ10', 'CZ13', 'CZ14', 'CZ15', 'CZ16'],
    #'SDG&E': ['CZ7', 'CZ10', 'CZ14', 'CZ15']
}

# Check cell ranges and value stream ordering in the Detailed Output sheet
value_stream_ranges_dict = {
    'total': ['P', 'AU'],
    'cap_and_trade': ['AW', 'CB'],
    'ghg_adder': ['CD', 'DI'],
    'ghg_rebalancing': ['DK', 'EP'],
    'energy': ['ER', 'FW'],
    'capacity': ['FY', 'HD'],
    'transmission': ['HF', 'IK'],
    'distribution': ['IM', 'JR'],
    'ancillary_services': ['JT', 'KY'],
    'losses': ['LA', 'MF'],
    'methane_leakage': ['MH', 'NM'],
    'air_quality_adder': ['NO', 'OT'],
    'marginal_ghg': ['OW', 'QB']
}

# Define the metadata and temporal columns for the output table
columns = {
            "utility": "string",
            "region": "string",
            "year": "int",
            "month": "int",
            "quarter": "int",
            "hour_of_year": "int",
            "hour_of_day": "int",
        }

###SETUP END###
        
# Add all value_stream columns as float
for value_stream in value_stream_ranges_dict.keys():
    columns[value_stream] = "float"

columns['ghg_adder_rebalancing'] = "float"

@model(
    name="ca_acc_layer0_scraping.acc_electric_model_ts",
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
       - Prompt user to set utility and climate zone in Excel
       - Prompt user to manually update macro (if needed) and save file
       - Scrape data after user confirms
    3. Return combined DataFrame with all combinations
    """
    # Generate all valid combinations from the dictionary
    all_combinations = []
    for utility in ['PG&E', 'SCE', 'SDG&E']:
        if utility in UTILITY_CLIMATE_ZONES:
            for climate_zone in UTILITY_CLIMATE_ZONES[utility]:
                all_combinations.append((utility, climate_zone))
    
    return scrape_all_combinations(
        input_file=FILE_NAME, 
        combinations=all_combinations
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


def scrape_all_combinations(input_file, combinations):
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
    
    if not combinations:
        raise ValueError("No combinations provided to scrape")
    
    # Open Excel in VISIBLE mode so user can update macros
    app = xw.App(visible=True)
    app.display_alerts = False
    app.screen_updating = True
    
    wb = None
    all_dfs = []
    
    try:
        # Open workbook
        wb = app.books.open(file_path)
        output_sheet = wb.sheets['Detailed Output']
        
        # Read years from row 6 (first range P6:AU6)
        years_raw = output_sheet.range(f'{detialed_output_years_cell_initial}:{detialed_output_years_cell_final}').value
        years = [int(year) for year in years_raw]

        # Iterate through all combinations
        total_combinations = len(combinations)
        combination_num = 0
        
        print(f"\n{'='*60}")
        print(f"Starting data scraping for {total_combinations} combinations")
        print(f"{'='*60}")
        for utility, czs in UTILITY_CLIMATE_ZONES.items():
            print(f"  {utility}: {len(czs)} climate zones")
        print(f"{'='*60}\n")
        
        # Iterate through all combinations
        for utility, climate_zone in combinations:
            combination_num += 1
            
            print(f"\n{'='*60}")
            print(f"Combination {combination_num}/{total_combinations}: Utility={utility}, Climate Zone={climate_zone}")
            print(f"{'='*60}")
            
            # Interactive prompt for user to set values and update macro
            print(f"\n{'='*60}")
            print(f"MANUAL STEP REQUIRED - Combination {combination_num}/{total_combinations}:")
            print("!!!Ensure that the discount rate is set to 0 in the Dashboard Viewer sheet!!!\n")
            print(f"  1. In Excel, set the following filter values:")
            print(f"     - Utility = '{utility}'")
            print(f"     - Climate Zone = '{climate_zone}'")
            print(f"  2. If needed, run the macro in Excel")
            print(f"  3. Save the Excel file")
            print(f"  4. Press ENTER here when ready to continue scraping...")
            print(f"{'='*60}")
            
            # Wait for user input
            input()
            
            # Verify the macro ran by checking H2/H3 of the Detailed Output sheet
            actual_utility = output_sheet.range(detailed_output_utility_validation_cell).value
            actual_climate_zone = output_sheet.range(detailed_output_climate_zone_validation_cell).value
            
            print(f"\nVerified: {detailed_output_utility_validation_cell}={actual_utility}, {detailed_output_climate_zone_validation_cell}={actual_climate_zone}")
            
            if str(actual_utility).strip() != str(utility).strip():
                print(f"WARNING: {detailed_output_utility_validation_cell} shows '{actual_utility}' but expected '{utility}'")
                # Wait for user input
                input()
            if str(actual_climate_zone).strip() != str(climate_zone).strip():
                print(f"WARNING: {detailed_output_climate_zone_validation_cell} shows '{actual_climate_zone}' but expected '{climate_zone}'")
                # Wait for user input
                input()
            print(f"\nScraping data...")
            
            # Scrape data for all value streams
            long_df = None
            for i, value_stream in enumerate(value_stream_ranges_dict.keys()):
                try:
                    avoided_costs = read_large_range_in_chunks(
                        output_sheet,
                        value_stream_ranges_dict[value_stream][0],
                        value_stream_ranges_dict[value_stream][1],
                        detailed_output_first_data_row, detailed_output_first_data_row + 8759,
                        chunk_size=8760
                    )
                    df = pd.DataFrame(avoided_costs, columns=years).reset_index(names='hour_of_year')
                    df['utility'] = utility.replace('&', '')
                    df['region'] = climate_zone
                    
                    if i == 0:
                        long_df = df.melt(
                            id_vars=['utility', 'region', 'hour_of_year'],
                            value_vars=years,
                            var_name="year",
                            value_name=value_stream
                        )
                    else:
                        long_df = pd.merge(
                            long_df,
                            df[['hour_of_year'] + years].melt(
                                id_vars=['hour_of_year'],
                                value_vars=years,
                                var_name="year",
                                value_name=value_stream
                            ),
                            on=['year', 'hour_of_year']
                        )
                    print(f"  ✓ {value_stream}: {df.shape[0]} rows")
                except Exception as e:
                    print(f"  ✗ Error scraping {value_stream}: {e}")
                    continue
            
            if long_df is not None and not long_df.empty:
                all_dfs.append(long_df)
                print(f"\n✓ Successfully scraped {len(long_df)} rows for {utility}/{climate_zone}")
            else:
                print(f"\n✗ No data scraped for {utility}/{climate_zone}")
                
        # Combine all dataframes
        if not all_dfs:
            print("\nWARNING: No data was scraped!")
            return pd.DataFrame()
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df['ghg_adder_rebalancing'] = combined_df['ghg_adder'] + combined_df['ghg_rebalancing']
        combined_df['hour_of_day'] = combined_df['hour_of_year'] % 24
        combined_df['marginal_ghg'] = combined_df['marginal_ghg']*1000 

        # Map hour_of_year to month
        month_hod_hoy_map = pd.date_range('2023-01-01', periods=8760, freq='h')

        month_hod_hoy_map_df = pd.DataFrame({
            'month': month_hod_hoy_map.month,
            'hour_of_year': range(0, 8760)
        })
        
        combined_df = combined_df.merge(month_hod_hoy_map_df, on='hour_of_year')

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
"""
SQLMesh model for ACC Electric Model data.

This model scrapes data from the 2024 ACC Electric Model Excel file for all
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
ID_COLUMNS = ["utility", "climate_zone", "year", "hour_of_year"]

BASE_DIR = os.path.dirname(__file__)  # directory of the model file
DATA_DIR = os.path.join(BASE_DIR, "..", "raw_acc_files")  # adjust if needed

value_stream_ranges_dict = {
    'total': ['P', 'AU'],
    'cap_and_trade': ['AW', 'CB'],
    'ghg_adder': ['CD', 'DI'],
    'ghg_rebalancing': ['DK', 'EP'],
    'energy': ['ER', 'FW'],
    'capacity': ['FY', 'HD'],
    'transmission': ['HF', 'IK'],
    'distribution': ['IM', 'JR'],
    'procurement': ['JT', 'KY'],
    'losses': ['LA', 'MF'],
    'methane_leakage': ['MH', 'NM'],
    'air_quality_adder': ['NO', 'OT'],
    'marginal_ghg': ['OW', 'QB']
}

columns = {
            "utility": "string",
            "climate_zone": "string",
            "year": "int",
            "hour_of_year": "int",
        }
        
# Add all value_stream columns as float
for value_stream in value_stream_ranges_dict.keys():
    columns[value_stream] = "float"
        
# file_path = os.path.join(DATA_DIR, "2024 ACC Electric Model v1b.xlsb")

# app = xw.App(visible=False)
# app.display_alerts = False
# app.screen_updating = False
# wb = app.books.open(file_path)
# output_sheet = wb.sheets['Detailed Output']

# # First range: P5:AU5
# years = [int(year) for year in output_sheet.range('P6:AU6').value]
# print(years)

# wb.close()
# app.quit()

years = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053, 2054]

        
#         # Read metric names from row 5 for both ranges
#         # First range: P5:AU5
#         headers_range1 = output_sheet.range('P5:AU5')

# def extract_header_name(header_value):
#     """
#     Extract the header name from a cell value.
#     Returns the part before ' (' and processes it (lowercase, replace spaces with _).
#     """
#     if pd.isna(header_value) or header_value is None:
#         return None
    
#     header_str = str(header_value)
    
#     # Extract part before ' ('
#     if ' (' in header_str:
#         header_str = header_str.split(' (')[0]
    
#     # Make lowercase and replace spaces with underscores
#     header_str = header_str.strip().lower().replace(' ', '_')
    
#     return header_str


# def get_metric_columns_from_excel():
#     """
#     Read metric column names from row 5 of Detailed Output sheet.
#     This is called at module import time to build the SQLMesh schema.
#     """
#     file_path = os.path.join(DATA_DIR, "2024 ACC Electric Model v1b.xlsb")
    
#     if not os.path.exists(file_path):
#         # If file doesn't exist, return base columns only
#         # This allows the module to be imported even if the file isn't present
#         return {
#             "utility": "string",
#             "climate_zone": "string",
#             "year": "int",
#             "hour_of_year": "int",
#         }
    
#     try:
#         app = xw.App(visible=False)
#         app.display_alerts = False
#         app.screen_updating = False
        
#         wb = app.books.open(file_path)
#         output_sheet = wb.sheets['Detailed Output']
        
#         # Read metric names from row 5 for both ranges
#         # First range: P5:AU5
#         headers_range1 = output_sheet.range('P5:AU5')
#         headers1 = headers_range1.value
        
#         # Second range: AW5:NM5
#         headers_range2 = output_sheet.range('AW5:NM5')
#         headers2 = headers_range2.value
        
#         # Process headers
#         if headers1 is None:
#             processed_headers1 = []
#         elif isinstance(headers1, list):
#             processed_headers1 = [extract_header_name(h) for h in headers1]
#         else:
#             processed_headers1 = [extract_header_name(headers1)]
        
#         if headers2 is None:
#             processed_headers2 = []
#         elif isinstance(headers2, list):
#             processed_headers2 = [extract_header_name(h) for h in headers2]
#         else:
#             processed_headers2 = [extract_header_name(headers2)]
        
#         # Remove None values and get unique metrics
#         all_metrics = [h for h in processed_headers1 if h is not None]
#         all_metrics.extend([h for h in processed_headers2 if h is not None])
#         unique_metrics = sorted(set(all_metrics))
        
#         wb.close()
#         app.quit()
        
        # Build columns dictionary
        # columns = {
        #     "utility": "string",
        #     "climate_zone": "string",
        #     "year": "int",
        #     "hour_of_year": "int",
        # }
        
        # # Add all metric columns as float
        # for metric in unique_metrics:
        #     columns[metric] = "float"
        
        # return columns
        
    # except Exception as e:
    #     # If there's an error reading the file, return base columns
    #     # This allows the module to be imported even if Excel isn't available
    #     print(f"Warning: Could not read Excel file to determine schema: {e}")
    #     return {
    #         "utility": "string",
    #         "climate_zone": "string",
    #         "year": "int",
    #         "hour_of_year": "int",
    #     }


# Get column schema from Excel file at module import time
# MODEL_COLUMNS = get_metric_columns_from_excel()


# @model(
#     name="acc_electric_model.ts",
#     kind="FULL",
#     grain=ID_COLUMNS,
#     columns=columns
# )

# def execute(context: ExecutionContext, **kwargs: Any) -> pd.DataFrame:
#     """
#     Execute the model to scrape ACC Electric Model data.
    
#     This function will:
#     1. Read filter structure from Dashboard Viewer sheet
#     2. Identify Utility and Climate Zone filters
#     3. Get all unique combinations (from environment variables or defaults)
#     4. Scrape data for each combination
#     5. Return combined DataFrame
#     """
#     return load_acc_data_from_excel(
#         input_file="2024 ACC Electric Model v1b.xlsb",
#         utilities=os.environ.get('ACC_UTILITIES', '').split(',') if os.environ.get('ACC_UTILITIES') else None,
#         climate_zones=os.environ.get('ACC_CLIMATE_ZONES', '').split(',') if os.environ.get('ACC_CLIMATE_ZONES') else None,
#         utility_filter=os.environ.get('ACC_UTILITY_FILTER'),
#         climate_zone_filter=os.environ.get('ACC_CLIMATE_ZONE_FILTER'),
#         macro_wait=float(os.environ.get('ACC_MACRO_WAIT', '2.0')),
#     )


def get_filter_structure(wb):
    """
    Read the filter structure from Dashboard Viewer sheet.
    Returns a dictionary mapping filter names to their cell locations.
    
    Args:
        wb: xlwings workbook object (already open)
    """
    sheet = wb.sheets['Dashboard Viewer']
    
    filters = {}
    for row in range(3, 13):  # Rows 3-12
        filter_name = sheet.range(f'F{row}').value
        filter_cell = f'G{row}'
        if filter_name:
            filters[filter_name] = filter_cell
    
    return filters


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


def scrape_single_combination(wb, filter_values, utility, climate_zone, macro_wait=2.0):
    """
    Set filters on Dashboard Viewer sheet and scrape data from Detailed Output for a single combination.
    
    Args:
        wb: xlwings workbook object (already open)
        filter_values: Dictionary mapping filter names to their values
        utility: Utility name for this combination
        climate_zone: Climate Zone name for this combination
        metric_names1: List of metric names for first range (from row 5)
        years1: List of years for first range (from row 6)
        metric_names2: List of metric names for second range (from row 5)
        years2: List of years for second range (from row 6)
        macro_wait: Seconds to wait after setting filters for macros to execute
    
    Returns:
        DataFrame with the scraped data in pivoted format
    """
    dashboard_sheet = wb.sheets['Dashboard Viewer']
    output_sheet = wb.sheets['Detailed Output']
    app = wb.app
    
    # Enable events and ensure calculation is automatic
    app.api.Calculation = -4105  # xlCalculationAutomatic
    app.api.EnableEvents = True
    app.api.ScreenUpdating = True  # Temporarily enable for event triggering
    
    # Check initial state in Detailed Output sheet
    initial_utility = output_sheet.range('H2').value
    initial_climate_zone = output_sheet.range('H3').value
    print(f"Initial state - H2 (utility): {initial_utility}, H3 (climate_zone): {initial_climate_zone}")
    
    # Activate the Dashboard Viewer sheet to ensure it's active
    dashboard_sheet.activate()
    time.sleep(0.2)  # Give Excel time to activate the sheet
    
    # Set discount rate to 0 (cell G11)
    discount_rate_cell = dashboard_sheet.range('G11')
    old_discount_rate = discount_rate_cell.value
    
    # Set discount rate using API which should trigger events
    if old_discount_rate != 0:
        discount_rate_cell.select()
        discount_rate_cell.api.Value = 0
        # Small delay to let event fire
        time.sleep(0.3)
    
    # Debug: Print all filter names found in the sheet
    print("Available filter names in Dashboard Viewer:")
    for row in range(3, 13):
        name_cell = dashboard_sheet.range(f'F{row}')
        value_cell = dashboard_sheet.range(f'G{row}')
        print(f"  Row {row}: F{row}='{name_cell.value}', G{row}='{value_cell.value}'")
    
    # Set each filter - iterate to set all filters
    filter_cells_set = []
    for filter_name, filter_value in filter_values.items():
        print(f"\nLooking for filter: '{filter_name}' with value: '{filter_value}'")
        
        # Find the cell for this filter (G3:G12)
        found = False
        for row in range(3, 13):
            name_cell = dashboard_sheet.range(f'F{row}')
            name_cell_value = name_cell.value
            
            # Try exact match first, then case-insensitive match
            if name_cell_value == filter_name or (name_cell_value and filter_name and str(name_cell_value).strip().lower() == str(filter_name).strip().lower()):
                value_cell = dashboard_sheet.range(f'G{row}')
                old_value = value_cell.value
                
                print(f"Found filter at row {row}. Setting {filter_name}: '{old_value}' -> '{filter_value}'")
                
                # Try multiple methods to set the value (for dropdown/validation cells)
                # Method 1: Use .value property (sometimes works better for dropdowns)
                try:
                    value_cell.value = filter_value
                    time.sleep(0.2)
                    actual_value = value_cell.value
                    print(f"  After .value: '{actual_value}'")
                    
                    # If that didn't work, try API
                    if str(actual_value) != str(filter_value):
                        value_cell.select()
                        time.sleep(0.1)
                        value_cell.api.Value = filter_value
                        time.sleep(0.2)
                        actual_value = value_cell.value
                        print(f"  After .api.Value: '{actual_value}'")
                    
                    # If still not set, try clearing first
                    if str(actual_value) != str(filter_value):
                        value_cell.select()
                        value_cell.clear()
                        time.sleep(0.1)
                        value_cell.value = filter_value
                        time.sleep(0.2)
                        actual_value = value_cell.value
                        print(f"  After clear + .value: '{actual_value}'")
                    
                    filter_cells_set.append((value_cell, filter_value))
                    
                    # After setting, try to force event triggering by:
                    # 1. Deselecting and reselecting the cell
                    dashboard_sheet.range('A1').select()
                    time.sleep(0.1)
                    value_cell.select()
                    time.sleep(0.2)
                    
                    # 2. Calculate the specific cell to trigger any dependent formulas/macros
                    try:
                        value_cell.api.Calculate()
                    except:
                        pass
                    
                    # Small delay between setting cells to allow events to process
                    time.sleep(0.5)
                    found = True
                    
                except Exception as e:
                    print(f"  Error setting value: {e}")
                    import traceback
                    traceback.print_exc()
                
                break
        
        if not found:
            print(f"WARNING: Could not find filter '{filter_name}' in Dashboard Viewer sheet!")
    
    # After setting all filters, try to force macro execution by:
    # 1. Activate the Dashboard Viewer sheet to ensure it's the active sheet
    dashboard_sheet.activate()
    time.sleep(0.2)
    
    # 2. Try to trigger worksheet change events by selecting each changed cell and pressing Enter
    # (Note: On macOS, we can't use SendKeys, but we can try selecting cells to trigger events)
    for cell, value in filter_cells_set:
        cell.select()
        time.sleep(0.2)
        # Try to trigger by accessing the cell's formula (even if it doesn't have one)
        try:
            _ = cell.api.Formula
        except:
            pass
        time.sleep(0.2)
    
    # 3. Wait a moment for macros to run
    time.sleep(2.0)  # Increased wait time
    
    # Check updated state in Detailed Output sheet
    updated_utility = output_sheet.range('H2').value
    updated_climate_zone = output_sheet.range('H3').value
    print(f"After setting filters - H2 (utility): {updated_utility}, H3 (climate_zone): {updated_climate_zone}")
    
    # Verify the macros ran by checking if H2/H3 match expected values
    # The filter_values dict might have different key names, so check all possibilities
    expected_utility = (filter_values.get('Utility') or 
                       filter_values.get('utility') or 
                       utility)
    expected_climate_zone = (filter_values.get('Climate Zone') or 
                            filter_values.get('climate_zone') or 
                            filter_values.get('ClimateZone') or
                            climate_zone)
    
    # Check if macros ran successfully
    macro_success = True
    if expected_utility and str(updated_utility).strip() != str(expected_utility).strip():
        print(f"WARNING: Macro may not have run. Expected utility '{expected_utility}' but H2 shows '{updated_utility}'")
        macro_success = False
    if expected_climate_zone and str(updated_climate_zone).strip() != str(expected_climate_zone).strip():
        print(f"WARNING: Macro may not have run. Expected climate_zone '{expected_climate_zone}' but H3 shows '{updated_climate_zone}'")
        macro_success = False
    
    # If macros didn't run, try alternative approaches
    if not macro_success:
        print("Macros did not update H2/H3. Trying alternative triggering methods...")
        
        # Method 1: Try triggering by activating/deactivating sheets
        for attempt in range(3):
            dashboard_sheet.activate()
            time.sleep(0.3)
            
            # Try to trigger by recalculating the filter cells
            for cell, value in filter_cells_set:
                cell.select()
                time.sleep(0.1)
                try:
                    # Try setting the value again (might trigger change event)
                    cell.value = value
                    time.sleep(0.1)
                except:
                    pass
            
            output_sheet.activate()
            time.sleep(0.5)
            
            # Re-check H2/H3
            updated_utility = output_sheet.range('H2').value
            updated_climate_zone = output_sheet.range('H3').value
            print(f"After attempt {attempt + 1} - H2: {updated_utility}, H3: {updated_climate_zone}")
            
            if (str(updated_utility).strip() == str(expected_utility).strip() and 
                str(updated_climate_zone).strip() == str(expected_climate_zone).strip()):
                print("Macros updated successfully after sheet activation!")
                macro_success = True
                break
        
        # Method 2: Try calling macro directly if possible (requires macro name)
        # This would require knowing the macro name, which we don't have yet
        # But we could try common names like "Worksheet_Change" or similar
    
    # After setting all filters, try multiple approaches to ensure macros execute:
    # 1. Activate a different sheet and back to trigger sheet events
    if filter_cells_set:
        output_sheet = wb.sheets['Detailed Output']
        output_sheet.activate()
        time.sleep(0.2)
        dashboard_sheet.activate()
        time.sleep(0.2)
    
    # 2. Force workbook calculation (macOS-compatible)
    # CalculateFullRebuild is Windows-only, so use Calculate instead
    try:
        wb.api.Calculate()
    except:
        # If Calculate fails, try calculating each sheet
        try:
            for sheet in wb.sheets:
                sheet.api.Calculate()
        except:
            pass  # Ignore if calculation fails
    
    # 3. Also calculate the Detailed Output sheet specifically
    output_sheet = wb.sheets['Detailed Output']
    try:
        output_sheet.api.Calculate()
    except:
        pass  # Ignore if calculation fails
    
    # 4. Try to refresh all data connections if any
    try:
        wb.api.RefreshAll()
    except:
        pass  # Ignore if refresh fails
    
    # Wait a moment for macros to execute
    time.sleep(macro_wait)
    
    # Disable screen updating again for efficiency
    app.api.ScreenUpdating = False
    
    # Read data from Detailed Output sheet
    output_sheet = wb.sheets['Detailed Output']
    
    # Read data from both ranges in chunks to avoid buffer overflow
    # First range: P9:AU8768


    for i, value_stream in enumerate(list(value_stream_ranges_dict.keys())[:2]):
        
        avoided_costs = read_large_range_in_chunks(output_sheet, value_stream_ranges_dict[value_stream][0], value_stream_ranges_dict[value_stream][1], 9, 8768, chunk_size=1000)
        df = pd.DataFrame(avoided_costs, columns = years).reset_index(names = 'hour_of_year')
        df['utility'] = utility
        df['climate_zone'] = climate_zone
        #print(value_stream, df.shape)
        print(df.head(3))
        
        if i == 0:
            long_df = df.melt(
            id_vars=['utility', 'climate_zone', 'hour_of_year'],
            value_vars=years,
            var_name="year",
            value_name=value_stream
            )
        else:
            long_df = pd.merge(
                long_df, 
                df[['hour_of_year']+years].melt(
                    id_vars=['hour_of_year'],
                    value_vars=years,
                    var_name="year",
                    value_name=value_stream
                    ), 
                on = ['year', 'hour_of_year']
            )
        # print(long_df.shape)
        # print(long_df.head(3))

    return long_df
    
    
    # Second range: AW9:NM8768
    #data_values2 = read_large_range_in_chunks(output_sheet, 'AW', 'NM', 9, 8768, chunk_size=1000)
    
    # Convert to DataFrames
    # if not data_values1 or len(data_values1) == 0:
    #     df1 = pd.DataFrame()
    # else:
    #     df1 = pd.DataFrame(data_values1)
    
    # if not data_values2 or len(data_values2) == 0:
    #     df2 = pd.DataFrame()
    # else:
    #     df2 = pd.DataFrame(data_values2)
    
    # Now we need to structure the data properly
    # Each column in Excel has: metric name (row 5), year (row 6), data (rows 9-8768)
    # We want: rows indexed by (hour_of_year, year) with metric columns
    
    # Combine both dataframes and their metadata
    # all_data = []
    # all_metrics = []
    # all_years = []
    
    # # Process first range
    # if not df1.empty and len(years1) > 0 and len(metric_names1) > 0:
    #     # Ensure we have matching lengths
    #     min_len = min(len(metric_names1), len(years1), len(df1.columns))
    #     for col_idx in range(min_len):
    #         metric_name = metric_names1[col_idx]
    #         year = years1[col_idx]
    #         if metric_name and year is not None:
    #             all_metrics.append(metric_name)
    #             all_years.append(int(year))
    #             all_data.append(df1.iloc[:, col_idx].values)
    
    # # Process second range
    # if not df2.empty and len(years2) > 0 and len(metric_names2) > 0:
    #     min_len = min(len(metric_names2), len(years2), len(df2.columns))
    #     for col_idx in range(min_len):
    #         metric_name = metric_names2[col_idx]
    #         year = years2[col_idx]
    #         if metric_name and year is not None:
    #             all_metrics.append(metric_name)
    #             all_years.append(int(year))
    #             all_data.append(df2.iloc[:, col_idx].values)
    
    # if not all_data:
    #     return pd.DataFrame()
    
    # # Determine number of rows (should be 8760)
    # num_rows = len(all_data[0]) if all_data else 0
    
    # # Get all unique metrics (across all years)
    # unique_metrics = sorted(set(all_metrics))
    # unique_years = sorted(set(all_years))
    
    # # Create a lookup: (metric, year) -> column index in all_data
    # metric_year_to_col = {}
    # for idx, (metric, year) in enumerate(zip(all_metrics, all_years)):
    #     key = (metric, year)
    #     if key not in metric_year_to_col:
    #         metric_year_to_col[key] = []
    #     metric_year_to_col[key].append(idx)
    
    # # Create rows: one per (hour_of_year, year) combination
    # rows = []
    # for hour_idx in range(num_rows):
    #     for year in unique_years:
    #         row = {
    #             'hour_of_year': hour_idx,
    #             'year': year
    #         }
            
    #         # For each unique metric, get the value for this year (if it exists)
    #         for metric in unique_metrics:
    #             key = (metric, year)
    #             if key in metric_year_to_col:
    #                 # Get values from all columns with this metric+year combination
    #                 col_indices = metric_year_to_col[key]
    #                 values = [all_data[col_idx][hour_idx] for col_idx in col_indices if hour_idx < len(all_data[col_idx])]
    #                 # Sum if multiple, or take first if single
    #                 if values:
    #                     non_null_values = [v for v in values if pd.notna(v) and v is not None]
    #                     if non_null_values:
    #                         value = sum(non_null_values) if len(non_null_values) > 1 else non_null_values[0]
    #                     else:
    #                         value = None
    #                 else:
    #                     value = None
    #             else:
    #                 value = None
                
    #             row[metric] = value
            
    #         rows.append(row)
    
    # if not rows:
    #     print("Warning: No rows created")
    #     return pd.DataFrame()
    
    # # Convert to DataFrame
    # df_final = pd.DataFrame(rows)
    
    # # Add utility and climate_zone columns
    # df_final['utility'] = utility
    # df_final['climate_zone'] = climate_zone
    
    # # Reorder columns: utility, climate_zone, year, hour_of_year, then all metric columns
    # metric_cols_final = [c for c in df_final.columns if c not in ['utility', 'climate_zone', 'year', 'hour_of_year']]
    # df_final = df_final[['utility', 'climate_zone', 'year', 'hour_of_year'] + metric_cols_final]
    
    # return df_final


def load_acc_data_from_excel(
    input_file: str,
    utilities: list = None,
    climate_zones: list = None,
    utility_filter: str = None,
    climate_zone_filter: str = None,
    macro_wait: float = 2.0,
) -> DataFrame:
    """
    Load ACC Electric Model data from Excel file.
    
    Args:
        input_file: Name of the Excel file in raw_acc_files directory
        utilities: List of utility names to process (None to auto-detect)
        climate_zones: List of climate zone names to process (None to auto-detect)
        utility_filter: Name of the Utility filter (None to auto-detect)
        climate_zone_filter: Name of the Climate Zone filter (None to auto-detect)
        macro_wait: Seconds to wait after setting filters for macros to execute
    
    Returns:
        DataFrame with all combinations of utility and climate zone
    """
    file_path = os.path.join(DATA_DIR, input_file)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")
    
    # If utilities or climate_zones not provided, we need to discover them
    # For now, raise an error if they're not provided
    # if not utilities or len(utilities) == 0 or (len(utilities) == 1 and not utilities[0]):
    #     raise ValueError(
    #         "Utilities must be provided via ACC_UTILITIES environment variable "
    #         "(comma-separated list, e.g., 'PG&E,SCE,SDG&E')"
    #     )
    
    # if not climate_zones or len(climate_zones) == 0 or (len(climate_zones) == 1 and not climate_zones[0]):
    #     raise ValueError(
    #         "Climate zones must be provided via ACC_CLIMATE_ZONES environment variable "
    #         "(comma-separated list, e.g., 'CZ1,CZ2,CZ3')"
    #     )
    
    # Clean up empty strings from splitting
    utilities = [u.strip() for u in utilities if u.strip()]
    climate_zones = [cz.strip() for cz in climate_zones if cz.strip()]
    print("utilities = ", utilities)
    print("climate zones = ", climate_zones)
    
    # Open workbook once and keep it open for all combinations
    app = xw.App(visible=False)
    # Disable alerts to prevent macro enable prompts from blocking
    app.display_alerts = False
    # IMPORTANT: Enable screen updating and events to allow macros to run
    # Setting screen_updating=False can prevent macros from executing on macOS
    app.screen_updating = True
    app.api.EnableEvents = True
    
    wb = None
    try:
        wb = app.books.open(file_path)
        
        # Get filter structure from the open workbook
        filters = get_filter_structure(wb)
        
        #Identify Utility and Climate Zone filters
        if not utility_filter:
            for filter_name in filters.keys():
                filter_lower = filter_name.lower()
                if 'utility' in filter_lower:
                    utility_filter = filter_name
                    break
        
        if not climate_zone_filter:
            for filter_name in filters.keys():
                filter_lower = filter_name.lower()
                if 'climate' in filter_lower and 'zone' in filter_lower:
                    climate_zone_filter = filter_name
                    break
        
        if not utility_filter or not climate_zone_filter:
            raise ValueError(
                f"Could not identify filters. Utility filter: {utility_filter}, "
                f"Climate Zone filter: {climate_zone_filter}. "
                f"Available filters: {list(filters.keys())}"
            )
        
        # Read headers once (they should be the same for all combinations)
        output_sheet = wb.sheets['Detailed Output']
        
        # Read metric names from row 5 for both ranges
        # First range: P5:AU5
        # headers_range1 = output_sheet.range('P5:AU5')
        # headers1 = headers_range1.value
        
        # # Second range: AW5:NM5
        # headers_range2 = output_sheet.range('AW5:NM5')
        # headers2 = headers_range2.value
        
        # # Read years from row 6 for both ranges
        # # First range: P6:AU6
        # years_range1 = output_sheet.range('P6:AU6')
        # years1 = years_range1.value
        
        # # Second range: AW6:NM6
        # years_range2 = output_sheet.range('AW6:NM6')
        # years2 = years_range2.value
        
        # # Process metric names: extract part before ' (', lowercase, replace spaces with _
        # if headers1 is None:
        #     processed_headers1 = []
        # elif isinstance(headers1, list):
        #     processed_headers1 = [extract_header_name(h) for h in headers1]
        # else:
        #     processed_headers1 = [extract_header_name(headers1)]
        
        # if headers2 is None:
        #     processed_headers2 = []
        # elif isinstance(headers2, list):
        #     processed_headers2 = [extract_header_name(h) for h in headers2]
        # else:
        #     processed_headers2 = [extract_header_name(headers2)]
        
        # # Remove None values from metric names
        # processed_headers1 = [h for h in processed_headers1 if h is not None]
        # processed_headers2 = [h for h in processed_headers2 if h is not None]
        
        # # Process years: convert to integers
        # if years1 is None:
        #     processed_years1 = []
        # elif isinstance(years1, list):
        #     processed_years1 = [int(y) if y and pd.notna(y) else None for y in years1]
        # else:
        #     processed_years1 = [int(years1)] if years1 and pd.notna(years1) else []
        
        # if years2 is None:
        #     processed_years2 = []
        # elif isinstance(years2, list):
        #     processed_years2 = [int(y) if y and pd.notna(y) else None for y in years2]
        # else:
        #     processed_years2 = [int(years2)] if years2 and pd.notna(years2) else []
        
        # Collect all dataframes
        all_dfs = []
        
        # Iterate through all combinations
        for utility in utilities:
            for climate_zone in climate_zones:
                filter_values = {
                    utility_filter: utility,
                    climate_zone_filter: climate_zone
                }
                print(utility, climate_zone, filter_values)
                
                try:
                    df = scrape_single_combination(
                        wb, filter_values, utility, climate_zone, macro_wait
                    )
                    if not df.empty:
                        all_dfs.append(df)
                except Exception as e:
                    # Log error but continue with other combinations
                    print(f"Error scraping Utility={utility}, Climate Zone={climate_zone}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        if not all_dfs:
            return pd.DataFrame()
        
        # Combine all dataframes
        combined_df = pd.concat(all_dfs, ignore_index=True)
        print("COMBINED DF")
        print(combined_df.head(4))
        
        # Ensure all metric columns are properly typed as float
        # Get all columns except the ID columns
        metric_cols = [c for c in combined_df.columns if c not in ID_COLUMNS]
        for col in metric_cols:
            if col in combined_df.columns:
                # Convert to float, handling any non-numeric values
                combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
        
        # Remove debug print statements for production
        # (Keep them commented for debugging if needed)
        
        return combined_df
        
    finally:
        # Close workbook and quit app only at the end
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


"""
Script to scrape data from the 2024 ACC Electric Model Excel file.

This script:
1. Reads the Dashboard Viewer sheet to identify filter options
2. Iterates through all unique combinations of Utility and Climate Zone
3. For each combination:
   - Sets discount rate (G11) to 0
   - Sets the filters (which triggers macros)
   - Scrapes data from Detailed Output sheet (P9:AU8768 and AW9:NM8768)
   - Extracts column headers from row 5 (text before ' (')
   - Adds hour_of_year column (0-8759)
   - Adds utility and climate_zone columns
   - Saves as pivoted vertical format with schema: utility, climate_zone, hour_of_year, [metrics...]
4. Saves the data to CSV files in ca_acc/models folder

Requirements:
- xlwings: pip install xlwings
- Excel must be installed on macOS
- The Excel file must be closed before running this script
"""

import os
import pandas as pd
from pathlib import Path
import sys
import time
import argparse

try:
    import xlwings as xw
    HAS_XLWINGS = True
except ImportError:
    HAS_XLWINGS = False
    print("ERROR: xlwings is required. Install with: pip install xlwings")
    print("Note: xlwings requires Excel to be installed on macOS")
    sys.exit(1)


def get_filter_structure(file_path):
    """
    Read the filter structure from Dashboard Viewer sheet.
    Returns a dictionary mapping filter names to their cell locations.
    """
    app = xw.App(visible=False)
    wb = app.books.open(file_path)
    sheet = wb.sheets['Dashboard Viewer']
    
    filters = {}
    for row in range(3, 13):  # Rows 3-12
        filter_name = sheet.range(f'F{row}').value
        filter_cell = f'G{row}'
        if filter_name:
            filters[filter_name] = filter_cell
    
    wb.close()
    app.quit()
    
    return filters


def try_discover_filter_options(file_path, filter_name):
    """
    Try to discover all available options for a filter.
    This attempts to read from common data sheets or query the filter.
    Returns None if unable to discover automatically.
    """
    app = xw.App(visible=False)
    wb = app.books.open(file_path)
    
    options = None
    
    # Try to find a sheet with filter options
    # Common names: 'Data', 'Input', 'Lookup', 'Lists', 'Reference', etc.
    sheet_names = [s.name for s in wb.sheets]
    
    # Look for sheets that might contain filter options
    for sheet_name in sheet_names:
        sheet_lower = sheet_name.lower()
        if any(keyword in sheet_lower for keyword in ['data', 'input', 'lookup', 'list', 'reference', 'option']):
            try:
                sheet = wb.sheets[sheet_name]
                # Try to find the filter name in the sheet
                used_range = sheet.used_range
                if used_range:
                    # Search for the filter name
                    for cell in used_range:
                        if cell.value and str(cell.value).lower() == filter_name.lower():
                            # Found the filter name, try to get options from adjacent cells
                            # This is a heuristic approach
                            pass
            except:
                continue
    
    wb.close()
    app.quit()
    
    return options


def extract_header_name(header_value):
    """
    Extract the header name from a cell value.
    Returns the part before ' (' and processes it (lowercase, replace spaces with _).
    """
    if pd.isna(header_value) or header_value is None:
        return None
    
    header_str = str(header_value)
    
    # Extract part before ' ('
    if ' (' in header_str:
        header_str = header_str.split(' (')[0]
    
    # Make lowercase and replace spaces with underscores
    header_str = header_str.strip().lower().replace(' ', '_')
    
    return header_str


def set_filter_and_scrape(file_path, filter_values, utility, climate_zone, output_file, macro_wait=2.0):
    """
    Set filters on Dashboard Viewer sheet and scrape data from Detailed Output.
    
    Args:
        file_path: Path to Excel file
        filter_values: Dictionary mapping filter names to their values
        utility: Utility name for this combination
        climate_zone: Climate Zone name for this combination
        output_file: Path to save the CSV file
        macro_wait: Seconds to wait after setting filters for macros to execute
    """
    app = xw.App(visible=False)
    wb = app.books.open(file_path)
    
    try:
        dashboard_sheet = wb.sheets['Dashboard Viewer']
        
        # Set discount rate to 0 (cell G11)
        discount_rate_cell = dashboard_sheet.range('G11')
        discount_rate_cell.value = 0
        print(f"  Set discount rate (G11) = 0")
        
        # Set each filter
        for filter_name, filter_value in filter_values.items():
            # Find the cell for this filter (G3:G12)
            for row in range(3, 13):
                name_cell = dashboard_sheet.range(f'F{row}')
                if name_cell.value == filter_name:
                    value_cell = dashboard_sheet.range(f'G{row}')
                    value_cell.value = filter_value
                    print(f"  Set {filter_name} = {filter_value}")
                    break
        
        # Wait a moment for macros to execute
        time.sleep(macro_wait)
        
        # Read data from Detailed Output sheet
        output_sheet = wb.sheets['Detailed Output']
        
        # Read headers from row 5 for both ranges
        # First range: P5:AU5
        headers_range1 = output_sheet.range('P5:AU5')
        headers1 = headers_range1.value
        
        # Second range: AW5:NM5
        headers_range2 = output_sheet.range('AW5:NM5')
        headers2 = headers_range2.value
        
        # Process headers: extract part before ' (', lowercase, replace spaces with _
        # Handle both single value and list cases
        if headers1 is None:
            processed_headers1 = []
        elif isinstance(headers1, list):
            processed_headers1 = [extract_header_name(h) for h in headers1]
        else:
            processed_headers1 = [extract_header_name(headers1)]
        
        if headers2 is None:
            processed_headers2 = []
        elif isinstance(headers2, list):
            processed_headers2 = [extract_header_name(h) for h in headers2]
        else:
            processed_headers2 = [extract_header_name(headers2)]
        
        # Remove None values
        processed_headers1 = [h for h in processed_headers1 if h is not None]
        processed_headers2 = [h for h in processed_headers2 if h is not None]
        
        # Read data from both ranges
        # First range: P9:AU8768
        data_range1 = output_sheet.range('P9:AU8768')
        data_values1 = data_range1.value
        
        # Second range: AW9:NM8768
        data_range2 = output_sheet.range('AW9:NM8768')
        data_values2 = data_range2.value
        
        # Convert to DataFrames
        # Handle empty or None cases
        if data_values1 is None or (isinstance(data_values1, list) and len(data_values1) == 0):
            df1 = pd.DataFrame()
        elif isinstance(data_values1, list) and len(data_values1) > 0:
            if isinstance(data_values1[0], list):
                # Multiple rows
                df1 = pd.DataFrame(data_values1)
            else:
                # Single row
                df1 = pd.DataFrame([data_values1])
        else:
            df1 = pd.DataFrame([data_values1])
        
        if data_values2 is None or (isinstance(data_values2, list) and len(data_values2) == 0):
            df2 = pd.DataFrame()
        elif isinstance(data_values2, list) and len(data_values2) > 0:
            if isinstance(data_values2[0], list):
                # Multiple rows
                df2 = pd.DataFrame(data_values2)
            else:
                # Single row
                df2 = pd.DataFrame([data_values2])
        else:
            df2 = pd.DataFrame([data_values2])
        
        # Set column names
        if len(processed_headers1) > 0:
            if len(df1.columns) > len(processed_headers1):
                df1 = df1.iloc[:, :len(processed_headers1)]
            elif len(df1.columns) < len(processed_headers1):
                processed_headers1 = processed_headers1[:len(df1.columns)]
            df1.columns = processed_headers1
        
        if len(processed_headers2) > 0:
            if len(df2.columns) > len(processed_headers2):
                df2 = df2.iloc[:, :len(processed_headers2)]
            elif len(df2.columns) < len(processed_headers2):
                processed_headers2 = processed_headers2[:len(df2.columns)]
            df2.columns = processed_headers2
        
        # Combine both dataframes horizontally
        df_combined = pd.concat([df1, df2], axis=1)
        
        # Add hour_of_year column (0 to 8759)
        df_combined['hour_of_year'] = range(len(df_combined))
        
        # Add utility and climate_zone columns
        df_combined['utility'] = utility
        df_combined['climate_zone'] = climate_zone
        
        # Reorder columns: utility, climate_zone, hour_of_year, then all other columns
        other_cols = [c for c in df_combined.columns if c not in ['utility', 'climate_zone', 'hour_of_year']]
        df_final = df_combined[['utility', 'climate_zone', 'hour_of_year'] + other_cols]
        
        # Save to CSV
        df_final.to_csv(output_file, index=False)
        print(f"  Saved {len(df_final)} rows with {len(other_cols)} metrics to {output_file}")
        
        return df_final
        
    finally:
        wb.close()
        app.quit()


def main():
    """Main function to orchestrate the scraping process."""
    parser = argparse.ArgumentParser(
        description='Scrape data from 2024 ACC Electric Model Excel file'
    )
    parser.add_argument(
        '--utilities',
        type=str,
        help='Comma-separated list of Utility values (e.g., "PG&E,SCE,SDG&E")'
    )
    parser.add_argument(
        '--climate-zones',
        type=str,
        help='Comma-separated list of Climate Zone values (e.g., "CZ1,CZ2,CZ3")'
    )
    parser.add_argument(
        '--utility-filter',
        type=str,
        help='Name of the Utility filter (auto-detected if not provided)'
    )
    parser.add_argument(
        '--climate-zone-filter',
        type=str,
        help='Name of the Climate Zone filter (auto-detected if not provided)'
    )
    parser.add_argument(
        '--macro-wait',
        type=float,
        default=2.0,
        help='Seconds to wait after setting filters for macros to execute (default: 2.0)'
    )
    
    args = parser.parse_args()
    
    # File paths
    script_dir = Path(__file__).parent
    file_path = script_dir / 'raw_acc_files' / '2024 ACC Electric Model v1b.xlsb'
    output_dir = script_dir / 'models'
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return
    
    print(f"Reading file: {file_path}")
    print("Note: Make sure Excel is installed and the file is closed.\n")
    
    # Step 1: Read filter structure
    print("=== Step 1: Reading filter structure ===")
    try:
        filters = get_filter_structure(str(file_path))
        print(f"Found {len(filters)} filters:")
        for name, cell in filters.items():
            print(f"  {name} -> {cell}")
    except Exception as e:
        print(f"Error reading filter structure: {e}")
        return
    
    # Step 2: Identify Utility and Climate Zone filters
    print("\n=== Step 2: Identifying Utility and Climate Zone filters ===")
    utility_filter = args.utility_filter
    climate_zone_filter = args.climate_zone_filter
    
    # Auto-detect if not provided
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
    
    # Prompt if still not found and not provided via args
    if not utility_filter:
        print("Warning: Could not identify Utility filter. Please check filter names.")
        print("Available filters:", list(filters.keys()))
        if not args.utility_filter:
            utility_filter = input("Enter the name of the Utility filter (or press Enter to skip): ").strip()
            if not utility_filter:
                utility_filter = None
    
    if not climate_zone_filter:
        print("Warning: Could not identify Climate Zone filter. Please check filter names.")
        print("Available filters:", list(filters.keys()))
        if not args.climate_zone_filter:
            climate_zone_filter = input("Enter the name of the Climate Zone filter (or press Enter to skip): ").strip()
            if not climate_zone_filter:
                climate_zone_filter = None
    
    if not utility_filter or not climate_zone_filter:
        print("\nError: Could not identify both Utility and Climate Zone filters.")
        print("Please provide the filter names manually or check the Dashboard Viewer sheet.")
        return
    
    print(f"Utility filter: {utility_filter}")
    print(f"Climate Zone filter: {climate_zone_filter}")
    
    # Step 3: Get unique combinations
    print("\n=== Step 3: Getting unique combinations ===")
    
    # Get from command line args or prompt user
    if args.utilities:
        utilities = [u.strip() for u in args.utilities.split(',')]
    else:
        print(f"Please provide the unique values for {utility_filter}.")
        print("You can find these by examining the filter dropdowns in Excel.")
        utilities_input = input("Enter Utility values (comma-separated): ").strip()
        if utilities_input:
            utilities = [u.strip() for u in utilities_input.split(',')]
        else:
            utilities = None
    
    if args.climate_zones:
        climate_zones = [cz.strip() for cz in args.climate_zones.split(',')]
    else:
        print(f"Please provide the unique values for {climate_zone_filter}.")
        print("You can find these by examining the filter dropdowns in Excel.")
        climate_zones_input = input("Enter Climate Zone values (comma-separated): ").strip()
        if climate_zones_input:
            climate_zones = [cz.strip() for cz in climate_zones_input.split(',')]
        else:
            climate_zones = None
    
    if not utilities or not climate_zones:
        print("Error: Both Utility and Climate Zone values are required.")
        return
    
    print(f"\nFound {len(utilities)} utilities and {len(climate_zones)} climate zones")
    print(f"Total combinations: {len(utilities) * len(climate_zones)}")
    
    # Step 4: Iterate through combinations and scrape
    print("\n=== Step 4: Scraping data for each combination ===")
    total_combinations = len(utilities) * len(climate_zones)
    current = 0
    
    for utility in utilities:
        for climate_zone in climate_zones:
            current += 1
            print(f"\n[{current}/{total_combinations}] Processing: Utility={utility}, Climate Zone={climate_zone}")
            
            # Create safe filename
            safe_utility = str(utility).replace('/', '_').replace('\\', '_').replace(' ', '_')
            safe_climate_zone = str(climate_zone).replace('/', '_').replace('\\', '_').replace(' ', '_')
            output_file = output_dir / f'acc_data_{safe_utility}_{safe_climate_zone}.csv'
            
            # Set filters and scrape
            filter_values = {
                utility_filter: utility,
                climate_zone_filter: climate_zone
            }
            
            try:
                set_filter_and_scrape(str(file_path), filter_values, utility, climate_zone, str(output_file), args.macro_wait)
            except Exception as e:
                print(f"  Error: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    print(f"\n=== Complete! Scraped {current} combinations ===")
    print(f"Output directory: {output_dir}")


if __name__ == '__main__':
    main()

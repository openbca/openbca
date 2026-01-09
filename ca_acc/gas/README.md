# ACC Data Scraping

This directory contains a SQLMesh model for scraping data from the 2024 ACC Electric Model Excel file (`2024 ACC Electric Model v1b.xlsb`).

## SQLMesh Model

The SQLMesh model (`models/acc_electric_model_ts.py`) is used to load ACC data into DuckDB.

### Requirements

1. **xlwings**: Install with `pip install xlwings` (or via `uv sync`)
2. **Excel**: Must be installed on macOS (xlwings requires Excel to be installed)
3. **File must be closed**: Make sure the Excel file is closed before running
4. **SQLMesh**: Should be installed as part of the project dependencies

### Prerequesits

1. Upload the CA electric ACC workbook into the ca_acc/raw_acc_files folder.
2. Save this file with 0% entered as the discount rate.
3. Review the ACC workbook, in particiular the Dashboard Viewer and Detailed Outputs pages. Make any necessary changes within the SETUP section of the ca_acc/models/acc_electric_model_ts.py file.

### Usage

Run the model using the Makefile command:

```bash
make run-ca-electric-acc
```

This command will:
1. Create the `ca_acc/output` directory if it doesn't exist
2. Run SQLMesh with the `ca_acc` project to scrape all combinations
3. Output data to `ca_acc/output/ca_acc.db`
4. Export the final table to `ca_acc/output/full_ca_avoided_costs_2024acc.csv`

The model processes all combinations defined in the `UTILITY_CLIMATE_ZONES` dictionary:
- **PG&E**: CZ1, CZ2, CZ3A, CZ3B, CZ4, CZ5, CZ11, CZ12, CZ13, CZ16
- **SCE**: CZ6, CZ8, CZ9, CZ10, CZ13, CZ14, CZ15, CZ16
- **SDG&E**: CZ7, CZ10, CZ14, CZ15

**Total: 26 combinations**

### Interactive Process

The model uses an **interactive approach** where you manually update Excel filters for each combination:

1. Excel opens automatically in visible mode
2. For each combination, the script will prompt you to:
   - **Set the discount rate to 0** in the Dashboard Viewer sheet (cell G11)
   - Set the Utility filter to the specified utility
   - Set the Climate Zone filter to the specified climate zone
   - Run the macro in Excel (if needed)
   - Save the Excel file
   - Press ENTER in the terminal to continue

3. The script verifies the macro ran by checking cells H2 and H3 in the Detailed Output sheet
4. If verification fails, you'll be prompted to correct the values
5. Data is scraped after confirmation

This manual process is necessary because Excel macros on macOS don't reliably trigger from programmatic cell changes via xlwings.

### Model Schema

The output table (`acc_electric_model.full_ca_avoided_costs_2024acc`) has the following structure:

#### ID Columns (Grain)
- `utility`: string - The utility name (with '&' removed, e.g., "PGE", "SCE", "SDGE")
- `region`: string - The climate zone name (e.g., "CZ1", "CZ2", etc.)
- `year`: int - The year
- `hour_of_year`: int - Hour of year (0-8759)
- `month`: int - Month (1-12), derived from hour_of_year
- `quarter`: int - Quarter (1-4), derived from month

#### Value Stream Columns (All float)
- `total`: Total annual values
- `cap_and_trade`: Cap and trade hourly marginal emissions
- `ghg_adder`: GHG adder
- `ghg_rebalancing`: GHG rebalancing
- `energy`: Energy value stream
- `capacity`: Capacity value stream
- `transmission`: Transmission value stream
- `distribution`: Distribution value stream
- `ancillary_services`: Ancillary services value stream
- `losses`: Losses value stream
- `methane_leakage`: Methane leakage value stream
- `air_quality_adder`: Air quality adder value stream
- `marginal_ghg`: Marginal GHG (multiplied by 1000)

#### Computed Columns
- `ghg_adder_rebalancing`: float - Sum of `ghg_adder` + `ghg_rebalancing`
- `hour_of_day`: int - Hour of day (0-23), derived from `hour_of_year % 24`

### Data Sources

The metrics are extracted from multiple column ranges in the Detailed Output sheet:

| Value Stream | Column Range | Data Range |
|-------------|--------------|------------|
| total | P:AU | P9:AU8768 |
| cap_and_trade | AW:CB | AW9:CB8768 |
| ghg_adder | CD:DI | CD9:DI8768 |
| ghg_rebalancing | DK:EP | DK9:EP8768 |
| energy | ER:FW | ER9:FW8768 |
| capacity | FY:HD | FY9:HD8768 |
| transmission | HF:IK | HF9:IK8768 |
| distribution | IM:JR | IM9:JR8768 |
| ancillary_services | JT:KY | JT9:KY8768 |
| losses | LA:MF | LA9:MF8768 |
| methane_leakage | MH:NM | MH9:NM8768 |
| air_quality_adder | NO:OT | NO9:OT8768 |
| marginal_ghg | OW:QB | OW9:QB8768 |

**Years are read from**: P6:AU6

**Verification cells**:
- Utility: H2
- Climate Zone: H3

### Data Transformations

1. **Utility name normalization**: The '&' character is removed from utility names (e.g., "PG&E" → "PGE")

2. **Month mapping**: Hours of year (0-8759) are mapped to months (1-12) using a 2023 calendar year (8760 hours = 365 days × 24 hours)

3. **Quarter mapping**: Months are mapped to quarters:
   - Q1: January-March (months 1-3)
   - Q2: April-June (months 4-6)
   - Q3: July-September (months 7-9)
   - Q4: October-December (months 10-12)

4. **Hour of day**: Calculated as `hour_of_year % 24`

5. **marginal_ghg scaling**: The `marginal_ghg` value stream is multiplied by 1000

6. **ghg_adder_rebalancing**: Computed as the sum of `ghg_adder` + `ghg_rebalancing`

### Output Files

After running `make run-ca-acc`, the following files are created:

- **Database**: `ca_acc/output/ca_acc.db` - DuckDB database containing the table `ca_acc.acc_electric_model.full_ca_avoided_costs_2024acc`
- **CSV Export**: `ca_acc/output/full_ca_avoided_costs_2024acc.csv` - CSV export of the complete table

### How It Works

1. Opens the Excel file using xlwings in **visible mode** so you can interact with it
2. Reads years from row 6 (P6:AU6) in the Detailed Output sheet
3. Iterates through all utility/climate zone combinations from `UTILITY_CLIMATE_ZONES`
4. For each combination:
   - Prompts you to manually set filters and discount rate in Excel
   - Waits for your confirmation (ENTER key)
   - Verifies the macro ran by checking H2 and H3
   - Reads data from all 13 value stream ranges (8760 rows each)
   - Combines all value streams into a single DataFrame
   - Pivots data from wide format to long format (one row per hour/year/utility/region combination)
5. After all combinations are processed:
   - Combines all DataFrames
   - Adds computed columns (`ghg_adder_rebalancing`, `hour_of_day`, `month`, `quarter`)
   - Applies transformations (marginal_ghg scaling, utility name normalization)
   - Returns the final DataFrame to SQLMesh
6. SQLMesh writes the data to DuckDB and exports to CSV

### Notes

- **Manual intervention required**: You must manually set filter values and run macros in Excel for each combination. This is a limitation of Excel macros on macOS when triggered programmatically.
- **Discount rate**: Must be manually set to 0 in the Dashboard Viewer sheet (cell G11) before scraping each combination.
- **File must be closed**: Ensure the Excel file is closed before running the command, or Excel may refuse to open it programmatically.
- **Process time**: With 26 combinations and manual steps, the full process can take 30-60 minutes depending on how quickly you complete each step.
- **Chunk size**: Data is read in chunks of 8760 rows (one full year of hourly data) to avoid buffer overflow errors.

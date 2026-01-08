# ACC Data Scraping

This directory contains both a standalone scraping script and a SQLMesh model for scraping data from the 2024 ACC Electric Model Excel file (`2024 ACC Electric Model v1b.xlsb`).

## SQLMesh Model (Recommended)

The SQLMesh model (`models/acc_electric_model_ts.py`) is the recommended way to load ACC data into DuckDB.

### Requirements

1. **xlwings**: Install with `pip install xlwings`
2. **Excel**: Must be installed on macOS (xlwings requires Excel to be installed)
3. **File must be closed**: Make sure the Excel file is closed before running
4. **SQLMesh**: Should be installed as part of the project dependencies

### Usage

1. Set environment variables for utilities and climate zones:
```bash
export ACC_UTILITIES="PG&E,SCE,SDG&E"
export ACC_CLIMATE_ZONES="CZ1,CZ2,CZ3,CZ4,CZ5,CZ6,CZ7,CZ8,CZ9,CZ10,CZ11,CZ12,CZ13,CZ14,CZ15,CZ16"
export ACC_UTILITY_FILTER="Utility"  # Optional, auto-detected if not provided
export ACC_CLIMATE_ZONE_FILTER="Climate Zone"  # Optional, auto-detected if not provided
export ACC_MACRO_WAIT="2.0"  # Optional, default is 2.0 seconds
export DB="output/openbca.db"  # DuckDB database path
```

2. Run SQLMesh to execute the model:
```bash
cd ca_acc
sqlmesh run
```

The model will:
- Scrape data for all combinations of utilities and climate zones
- Output the data to the DuckDB database specified by the `DB` environment variable
- Create a table named `acc_electric_model.ts` (or as configured in your SQLMesh project)

### Model Schema

The output table has the following structure:
- `utility`: string - The utility name
- `climate_zone`: string - The climate zone name  
- `hour_of_year`: int - Hour of year (0-8759)
- `[metric_name]`: float - Various metrics (dynamically determined from the Excel file)

The metrics are extracted from:
- **First range**: P9:AU8768 (headers from P5:AU5)
- **Second range**: AW9:NM8768 (headers from AW5:NM5)

Column headers are extracted from row 5 by taking the text before ' (' (if present), converting to lowercase, and replacing spaces with underscores. For example, "Losses (something)" becomes "losses".

## Standalone Script

The standalone script (`scrape_acc_data.py`) can be used for testing or one-off data extraction.

## Requirements

1. **xlwings**: Install with `pip install xlwings`
2. **Excel**: Must be installed on macOS (xlwings requires Excel to be installed)
3. **File must be closed**: Make sure the Excel file is closed before running the script

## Usage

### Interactive Mode

Run the script without arguments to use interactive mode:

```bash
python ca_acc/scrape_acc_data.py
```

The script will:
1. Read the filter structure from the Dashboard Viewer sheet
2. Auto-detect Utility and Climate Zone filters (or prompt you)
3. Ask you to provide the unique values for Utility and Climate Zone
4. For each combination:
   - Set discount rate (G11) to 0
   - Set filter values and wait for macros to execute
   - Scrape data from Detailed Output sheet (P9:AU8768 and AW9:NM8768)
   - Extract column headers from row 5 (text before ' (')
   - Add hour_of_year, utility, and climate_zone columns
   - Save as pivoted vertical format

### Command-Line Mode

You can provide all parameters via command-line arguments:

```bash
python ca_acc/scrape_acc_data.py \
  --utilities "PG&E,SCE,SDG&E" \
  --climate-zones "CZ1,CZ2,CZ3,CZ4,CZ5,CZ6,CZ7,CZ8,CZ9,CZ10,CZ11,CZ12,CZ13,CZ14,CZ15,CZ16" \
  --utility-filter "Utility" \
  --climate-zone-filter "Climate Zone" \
  --macro-wait 3.0
```

### Arguments

- `--utilities`: Comma-separated list of Utility values
- `--climate-zones`: Comma-separated list of Climate Zone values
- `--utility-filter`: Name of the Utility filter (auto-detected if not provided)
- `--climate-zone-filter`: Name of the Climate Zone filter (auto-detected if not provided)
- `--macro-wait`: Seconds to wait after setting filters for macros to execute (default: 2.0)

## Output

The script saves CSV files in `ca_acc/models/` with the naming pattern:
```
acc_data_{utility}_{climate_zone}.csv
```

Each CSV file contains data in a pivoted vertical format with the following schema:

- `utility`: string - The utility name
- `climate_zone`: string - The climate zone name
- `hour_of_year`: int - Hour of year (0-8759)
- `[metric_name]`: float - Various metrics extracted from the data

The metrics are extracted from:
- **First range**: P9:AU8768 (headers from P5:AU5)
- **Second range**: AW9:NM8768 (headers from AW5:NM5)

Column headers are extracted from row 5 by taking the text before ' (' (if present), converting to lowercase, and replacing spaces with underscores. For example, "Losses (something)" becomes "losses".

## How It Works

1. Opens the Excel file using xlwings (invisible Excel instance)
2. Reads the Dashboard Viewer sheet to identify filters (cells F3:F12 and G3:G12)
3. For each combination of Utility and Climate Zone:
   - Sets discount rate (G11) to 0
   - Sets the filter values in cells G3:G12
   - Waits for Excel macros to execute (which filter the data)
   - Reads column headers from row 5 (P5:AU5 and AW5:NM5)
   - Extracts header names (text before ' ('), converts to lowercase, replaces spaces with underscores
   - Reads the filtered data from the Detailed Output sheet:
     - First range: P9:AU8768
     - Second range: AW9:NM8768
   - Combines both ranges horizontally
   - Adds `hour_of_year` column (0-8759)
   - Adds `utility` and `climate_zone` columns
   - Reorders columns: utility, climate_zone, hour_of_year, then all metrics
   - Saves the data to a CSV file

## Notes

- The script automatically identifies filters containing "Utility" and "Climate Zone" in their names
- If auto-detection fails, you'll be prompted to provide the filter names
- The macro wait time can be adjusted if macros take longer to execute
- Make sure Excel is not running or the file is closed before starting


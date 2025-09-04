import pandas as pd
import duckdb
import re
import os

# Paths
excel_path = r"nspm\Input\OpenBCA Code CONFIG File-2.xlsm"
program_path = r"nspm/Input/OpenBCA Code PROGRAM INPUT.xlsx"
db_path = "testdb2.db"
sql_out_dir = "models"

# Connect to DuckDB
con = duckdb.connect(db_path)

# Sheets to skip
skip_sheets = {"Front Page", "Common Data", "Test Set Up", "Copy Data", "Validations", "Peak Definition",
               "Copy Sheet TO BE USED", "Validations_2", "Test Set Up_2", "Configuration Data", "Config Dat"}

# Ensure models folder exists
os.makedirs(sql_out_dir, exist_ok=True)

# -------- Part 1: Load SYSTEM INPUT Macro.xlsm sheets --------
xls = pd.ExcelFile(excel_path)

for i, sheet in enumerate(xls.sheet_names, start=1):
    if sheet in skip_sheets:
        print(f"⏭️ Skipping sheet '{sheet}'")
        continue

    # Read raw data
    df = pd.read_excel(excel_path, sheet_name=sheet, header=None,skiprows=2)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    if df.empty:
        print(f"Skipping {sheet} (no data).")
        continue

    # First row as header
    df.columns = df.iloc[0].astype(str)
    df = df[1:]
    df.columns = [str(c).strip().replace(" ", "_").replace("-", "_") for c in df.columns]
    df = df.astype(str)

    # Table name cleaning
    table_name = re.sub(r'[^0-9a-zA-Z_]', '_', sheet.strip()).lower()
    safe_table_name = f'"{table_name}"'

    # Register DataFrame in DuckDB and save table
    con.register("df_view", df)
    con.execute(f"DROP TABLE IF EXISTS {safe_table_name}")
    con.execute(f"CREATE TABLE {safe_table_name} AS SELECT * FROM df_view")

    # --- Generate model-style SQL ---
    sql_script = f"""-- test run {i}
MODEL (
  name input.{table_name},
  kind FULL
);

SELECT *
FROM {table_name};
"""

    # Save separate SQL file for each table
    sql_file = os.path.join(sql_out_dir, f"{table_name}.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql_script)

    print(f"✅ Saved sheet '{sheet}' as DuckDB table '{table_name}' and SQL model '{sql_file}'")

# -------- Part 2: Load CONFIG file (Inputs and Assumptions) --------
df_cfg = pd.read_excel(excel_path, sheet_name="Common Data", header=None)
df_cfg = df_cfg.dropna(how="all").dropna(axis=1, how="all")

# Find "INPUTS AND ASSUMPTIONS" block across all columns
mask = df_cfg.apply(lambda row: row.astype(str).str.contains("INPUTS AND ASSUMPTIONS", case=False, na=False)).any(axis=1)
if not mask.any():
    raise ValueError("❌ Could not find 'INPUTS AND ASSUMPTIONS' in config file")

start_row = mask[mask].index[0]

# Extract block from next row until first blank row
inputs_block = df_cfg.loc[start_row+1:, [0, 1, 2]].dropna(how="all")
inputs_block.columns = ["parameter", "units", "value"]

# Save into DuckDB
con.execute("DROP TABLE IF EXISTS inputs_and_assumptions")
con.register("df_view_cfg", inputs_block)
con.execute("CREATE TABLE inputs_and_assumptions AS SELECT * FROM df_view_cfg")

# --- Generate model-style SQL for config ---
sql_script = """-- test run config
MODEL (
  name input.inputs_and_assumptions,
  kind FULL
);

SELECT *
FROM inputs_and_assumptions;
"""

# Save separate SQL file
sql_file = os.path.join(sql_out_dir, "inputs_and_assumptions.sql")
with open(sql_file, "w", encoding="utf-8") as f:
    f.write(sql_script)

print("✅ Saved Inputs and Assumptions as DuckDB table 'inputs_and_assumptions' and SQL model 'inputs_and_assumptions.sql'")

# -------- Part 3: Load PROGRAM INPUT file (Program Inputs & Measure Inputs) --------
xls_prog = pd.ExcelFile(program_path)

for sheet in ["Program Inputs", "Measure Inputs"]:
    if sheet not in xls_prog.sheet_names:
        print(f"⚠️ Sheet '{sheet}' not found in {program_path}, skipping.")
        continue

    # Read raw data 
    df = pd.read_excel(program_path, sheet_name=sheet, header=None)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    if df.empty:
        print(f"Skipping {sheet} (no data).")
        continue

    # First row as header
    df.columns = df.iloc[0].astype(str)
    df = df[1:]
    df.columns = [str(c).strip().replace(" ", "_").replace("-", "_") for c in df.columns]
    df = df.astype(str)

    # Table name cleaning
    table_name = re.sub(r'[^0-9a-zA-Z_]', '_', sheet.strip()).lower()
    safe_table_name = f'"{table_name}"'

    # Register DataFrame in DuckDB and save table
    con = duckdb.connect(db_path)  # reopen connection
    con.register("df_view", df)
    con.execute(f"DROP TABLE IF EXISTS {safe_table_name}")
    con.execute(f"CREATE TABLE {safe_table_name} AS SELECT * FROM df_view")
    con.close()

    # --- Generate model-style SQL ---
    sql_script = f"""-- auto-generated from {sheet}
MODEL (
  name input.{table_name},
  kind FULL
);

SELECT *
FROM {table_name};
"""

    # Save SQL model file
    sql_file = os.path.join(sql_out_dir, f"{table_name}.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write(sql_script)

    print(f"✅ Saved sheet '{sheet}' as DuckDB table '{table_name}' and SQL model '{sql_file}'")

# -------- Close connection --------
con.close()
print(f"🎉 All sheets written to {db_path}")
print(f"📝 Individual model SQL scripts saved to {sql_out_dir}")

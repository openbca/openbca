import duckdb

# Connect to DuckDB
con = duckdb.connect("testdb2.db")

# Show all tables in the DB
tables = con.execute("SHOW TABLES").fetchdf()
print("📋 Available tables:")
print(tables)

# Loop through all tables and preview first 5 rows
for _, row in tables.iterrows():
    table_name = row[0]  # table name
    print(f"\n🔹 Preview of table: {table_name}")
    try:
        df_preview = con.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()
        print(df_preview)
    except Exception as e:
        print(f"⚠️ Could not fetch from {table_name}: {e}")

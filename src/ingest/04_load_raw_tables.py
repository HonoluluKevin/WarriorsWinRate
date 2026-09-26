from pathlib import Path
import sqlite3
import pandas as pd

# Define paths and the sources to create three tables
PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "db" / "warriors.db"
SCHEMA_OUT_PATH = PROJECT_ROOT / "src" / "sql" / "01_create_raw_tables.sql"

SOURCES = {
    "gsw_2015-16_gamelog.csv": "raw_game_log",
    "gsw_2015-16_linescores.csv": "raw_line_scores",
    "pbpstats_2015.csv": "raw_possession_events",
}


# create function to create tables as needed following logic of the three sources
def build_create_table_sql(table_name: str, columns: list[str]) -> str:
    col_defs = ",\n    ".join(f'"{c}" TEXT' for c in columns)
    return (
        f"DROP TABLE IF EXISTS {table_name};\n"
        f"CREATE TABLE {table_name} (\n"
        f"    row_id INTEGER PRIMARY KEY,\n"
        f"    {col_defs}\n"
        f");"
    )


conn = sqlite3.connect(DB_PATH)
schema_statements = []

for csv_name, table_name in SOURCES.items():
    csv_path = RAW_DIR / csv_name
    columns = list(pd.read_csv(csv_path, nrows=0).columns)

    create_sql = build_create_table_sql(table_name, columns)
    schema_statements.append(create_sql)
    conn.executescript(create_sql)

    print(f"Loading {csv_name} -> {table_name} ({len(columns)} columns)...")
    for chunk in pd.read_csv(csv_path, dtype=str, chunksize=50_000):
        chunk.to_sql(table_name, conn, if_exists="append", index=False)

    n_rows = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"  -> {n_rows:,} rows loaded")

conn.commit()
conn.close()

SCHEMA_OUT_PATH.write_text("\n\n".join(schema_statements) + "\n")
print(f"\nSchema written to {SCHEMA_OUT_PATH}")
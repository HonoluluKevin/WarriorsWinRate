import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "db" / "warriors.db"


def run_sql_file(sql_filename: str):
    sql_path = PROJECT_ROOT / "src" / "sql" / sql_filename
    sql_text = sql_path.read_text()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(sql_text)
    conn.commit()
    conn.close()
    print(f"Ran {sql_path.relative_to(PROJECT_ROOT)} against {DB_PATH.name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/run_sql.py <filename.sql>")
        sys.exit(1)
    run_sql_file(sys.argv[1])
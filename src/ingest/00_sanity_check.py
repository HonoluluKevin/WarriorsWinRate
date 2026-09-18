import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent.parent / "db" / "warriors.db"
conn = sqlite3.connect(db_path)

conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
conn.commit()

print(f"Connected OK. Tables: {conn.execute('SELECT name FROM sqlite_master').fetchall()}")
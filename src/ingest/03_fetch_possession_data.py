import csv
import tarfile
import urllib.request
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

SEASON = 2015  # season-start year; 2015 = the 2015-16 season
TAR_PATH = RAW_DIR / f"pbpstats_{SEASON}.tar.xz"
CSV_PATH = RAW_DIR / f"pbpstats_{SEASON}.csv"
URL = f"https://github.com/shufinskiy/nba_data/raw/main/datasets/pbpstats_{SEASON}.tar.xz"

if not TAR_PATH.exists():
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, TAR_PATH)
else:
    print(f"{TAR_PATH.name} already downloaded, skipping.")

if not CSV_PATH.exists():
    print("Extracting...")
    with tarfile.open(TAR_PATH) as tf:
        tf.extractall(RAW_DIR, filter="data")
else:
    print(f"{CSV_PATH.name} already extracted, skipping.")

# sanity peek only — no filtering, no deduping, that happens in Phase 2
preview = pd.read_csv(CSV_PATH, nrows=5)
print(f"\nColumns: {list(preview.columns)}")

with open(CSV_PATH, newline="") as f:
    row_count = sum(1 for _ in csv.reader(f)) - 1  # -1 for the header row
print(f"Total rows (whole league, every event, all 30 teams): {row_count:,}")
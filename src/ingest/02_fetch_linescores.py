import time
from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import boxscoresummaryv2

PROJECT_ROOT = Path(__file__).parent.parent.parent
GAME_LOG_PATH = PROJECT_ROOT / "data" / "raw" / "gsw_2015-16_gamelog.csv"
OUT_PATH = PROJECT_ROOT / "data" / "raw" / "gsw_2015-16_linescores.csv"

# reuse the game IDs from the file we already built in step 1a
game_log = pd.read_csv(GAME_LOG_PATH)
game_ids = game_log["Game_ID"].astype(str).str.zfill(10).tolist()
print(f"Fetching line scores for {len(game_ids)} games...")

all_line_scores = []
failed = []

for i, game_id in enumerate(game_ids, start=1):
    try:
        box = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id, timeout=60)
        dfs = box.get_data_frames()
        line_score = next(d for d in dfs if "PTS_QTR1" in d.columns)
        all_line_scores.append(line_score)
        print(f"  [{i}/{len(game_ids)}] {game_id} OK")
    except Exception as e:
        print(f"  [{i}/{len(game_ids)}] {game_id} FAILED: {e}")
        failed.append(game_id)
    time.sleep(0.6)  # be polite to the API — don't hammer it with rapid requests

combined = pd.concat(all_line_scores, ignore_index=True)
combined.to_csv(OUT_PATH, index=False)
print(f"\nSaved {len(combined)} line-score rows ({combined['GAME_ID'].nunique()} games) to {OUT_PATH}")
if failed:
    print(f"Failed to fetch {len(failed)} games: {failed}")
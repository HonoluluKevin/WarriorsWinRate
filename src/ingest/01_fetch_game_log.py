from pathlib import Path

import pandas as pd
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams

SEASON = "2015-16"
TEAM_ABBREV = "GSW"

# --- look up the team's internal numeric ID ---
team = [t for t in teams.get_teams() if t["abbreviation"] == TEAM_ABBREV][0]
team_id = team["id"]
print(f"Found {team['full_name']}, team_id={team_id}")

# --- fetch the game log ---
log = teamgamelog.TeamGameLog(
    team_id=team_id,
    season=SEASON,
    season_type_all_star="Regular Season",
)
df = log.get_data_frames()[0]

# --- land it, untouched, in data/raw ---
out_path = Path(__file__).parent.parent.parent / "data" / "raw" / "gsw_2015-16_gamelog.csv"
df.to_csv(out_path, index=False)
print(f"Saved {len(df)} games to {out_path}")
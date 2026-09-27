-- Phase 3 validation checks for gsw_possessions

-- 1. Which games went to overtime?
SELECT DISTINCT game_id
FROM gsw_possessions
WHERE period > 4
ORDER BY game_id;

-- 2. Spot-check the period 4 -> 5 handoff on one OT game
SELECT period, start_time_remaining, elapsed_seconds, possession_seq, offense_team, gsw_margin_before
FROM gsw_possessions
WHERE game_id = (SELECT game_id FROM gsw_possessions WHERE period > 4 ORDER BY game_id LIMIT 1)
  AND period IN (4, 5)
ORDER BY possession_seq;

-- 3. Overall possession-count range across all 82 games
WITH counts AS (
    SELECT game_id, COUNT(*) AS n FROM gsw_possessions GROUP BY game_id
)
SELECT MIN(n) AS min_poss, MAX(n) AS max_poss, AVG(n) AS avg_poss FROM counts;

-- 4. Flag any game with an implausible possession count (should return nothing)
WITH counts AS (
    SELECT game_id, COUNT(*) AS n FROM gsw_possessions GROUP BY game_id
)
SELECT * FROM counts WHERE n < 150 OR n > 300;

-- 5. Confirm strict alternation holds WITHIN each period (period-boundary
--    carryovers are expected and excluded). Should return very few rows —
--    at most the rare adjacent-tie-group edge case noted in 02_create_gsw_possessions.sql.
WITH checked AS (
    SELECT game_id, period, possession_seq, offense_team,
           LAG(offense_team) OVER (PARTITION BY game_id ORDER BY possession_seq) AS prev_team,
           LAG(period) OVER (PARTITION BY game_id ORDER BY possession_seq) AS prev_period
    FROM gsw_possessions
)
SELECT * FROM checked
WHERE offense_team = prev_team AND period = prev_period;
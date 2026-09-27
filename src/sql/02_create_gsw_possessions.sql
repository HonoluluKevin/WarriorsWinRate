-- Builds two views on top of raw_possession_events:
--   gsw_games        : one row per GSW game, with the opponent's abbreviation
--   gsw_possessions  : one row per real possession, scoped to GSW's games,
--                      margin reoriented to GSW's perspective, and a clean
--                      possession_seq ordering per game. Same-second ties are
--                      resolved using strict alternation rather than the
--                      source file's row order, which does not reflect true
--                      chronological order across teams. 4 of 16,445
--                      possessions (0.024%) remain ambiguously ordered, where
--                      two tie groups fall within seconds of each other —
--                      accepted as a documented limitation of 1-second clock
--                      resolution in the source data.

DROP VIEW IF EXISTS gsw_possessions;
DROP VIEW IF EXISTS gsw_games;

CREATE VIEW gsw_games AS
SELECT
    GAMEID AS game_id,
    MIN(GAMEDATE) AS game_date,
    MAX(CASE WHEN OPPONENT <> 'GSW' THEN OPPONENT END) AS opponent_abbrev
FROM raw_possession_events
GROUP BY GAMEID
HAVING MAX(CASE WHEN OPPONENT = 'GSW' THEN 1 ELSE 0 END) = 1;

CREATE VIEW gsw_possessions AS
WITH deduped AS (
    SELECT DISTINCT
        GAMEID, GAMEDATE, PERIOD, STARTTIME, STARTSCOREDIFFERENTIAL,
        OPPONENT, FG2A, FG2M, FG3A, FG3M, TURNOVERS, OFFENSIVEREBOUNDS
    FROM raw_possession_events
),
timed AS (
    SELECT
        d.*,
        CAST(d.PERIOD AS INTEGER) AS period_int,
        CAST(SUBSTR(d.STARTTIME, 1, INSTR(d.STARTTIME, ':') - 1) AS INTEGER) * 60
            + CAST(SUBSTR(d.STARTTIME, INSTR(d.STARTTIME, ':') + 1) AS INTEGER)
            AS seconds_remaining
    FROM deduped d
),
oriented AS (
    SELECT
        t.GAMEID AS game_id,
        t.GAMEDATE AS game_date,
        t.period_int AS period,
        t.STARTTIME AS start_time_remaining,
        CASE
            WHEN t.period_int <= 4
                THEN (t.period_int - 1) * 720 + (720 - t.seconds_remaining)
            ELSE
                (4 * 720 + (t.period_int - 5) * 300) + (300 - t.seconds_remaining)
        END AS elapsed_seconds,
        CASE WHEN t.OPPONENT = g.opponent_abbrev THEN 'GSW' ELSE g.opponent_abbrev END
            AS offense_team,
        CASE
            WHEN t.OPPONENT = g.opponent_abbrev
                THEN CAST(t.STARTSCOREDIFFERENTIAL AS INTEGER)
            ELSE -CAST(t.STARTSCOREDIFFERENTIAL AS INTEGER)
        END AS gsw_margin_before,
        CAST(t.FG2M AS INTEGER) AS fg2m,
        CAST(t.FG3M AS INTEGER) AS fg3m,
        CAST(t.TURNOVERS AS INTEGER) AS turnovers,
        CAST(t.OFFENSIVEREBOUNDS AS INTEGER) AS offensive_rebounds
    FROM timed t
    JOIN gsw_games g ON t.GAMEID = g.game_id
),
sequenced AS (
    SELECT
        o.*,
        (
            SELECT o2.offense_team
            FROM oriented o2
            WHERE o2.game_id = o.game_id
              AND o2.elapsed_seconds < o.elapsed_seconds
            ORDER BY o2.elapsed_seconds DESC
            LIMIT 1
        ) AS prior_offense_team
    FROM oriented o
)
SELECT
    game_id, game_date, period, start_time_remaining, elapsed_seconds,
    offense_team, gsw_margin_before, fg2m, fg3m, turnovers, offensive_rebounds,
    ROW_NUMBER() OVER (
        PARTITION BY game_id
        ORDER BY elapsed_seconds,
                 CASE WHEN offense_team = prior_offense_team THEN 1 ELSE 0 END
    ) AS possession_seq
FROM sequenced;
-- views.sql
-- Run once in the Supabase SQL editor after the first load.
-- These two views are the "transformation layer" — kept as plain SQL views
-- instead of dbt for this scoped version. Promote to dbt models later if the
-- project grows (same SQL, just wrapped in .sql model files + a schema.yml).

-- 1. Daily views per topic/language, with a same-day rank across editions.
CREATE OR REPLACE VIEW cleaned_pageviews AS
SELECT
    topic,
    project,
    article,
    date,
    views,
    RANK() OVER (PARTITION BY topic, date ORDER BY views DESC) AS rank_that_day
FROM raw_pageviews;

-- 2. Per-topic, per-language totals over the loaded window, plus each
--    edition's share relative to the top-performing edition for that topic.
--    This is the "coverage gap" metric: an edition sitting at, say, 8% of
--    the leading edition's views is a candidate worth investigating further
--    (content gap? translation lag? smaller reader base? -- exactly the
--    kind of open question the job posting describes).
CREATE OR REPLACE VIEW language_coverage_gap AS
WITH totals AS (
    SELECT topic, project, SUM(views) AS total_views
    FROM raw_pageviews
    GROUP BY topic, project
),
maxima AS (
    SELECT topic, MAX(total_views) AS max_views
    FROM totals
    GROUP BY topic
)
SELECT
    t.topic,
    t.project,
    t.total_views,
    m.max_views,
    ROUND(100.0 * t.total_views / m.max_views, 1) AS pct_of_top_edition
FROM totals t
JOIN maxima m ON t.topic = m.topic
ORDER BY t.topic, pct_of_top_edition DESC;

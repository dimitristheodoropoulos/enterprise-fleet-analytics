select
    topic,
    project,
    article,
    date,
    views,
    rank() over (partition by topic, date order by views desc) as rank_that_day
from {{ ref('stg_pageviews') }}

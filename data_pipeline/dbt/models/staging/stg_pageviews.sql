select
    topic,
    project,
    article,
    date,
    views
from {{ source('raw', 'raw_pageviews') }}
where views >= 0

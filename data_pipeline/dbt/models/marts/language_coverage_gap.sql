with totals as (
    select topic, project, sum(views) as total_views
    from {{ ref('stg_pageviews') }}
    group by topic, project
),

maxima as (
    select topic, max(total_views) as max_views
    from totals
    group by topic
)

select
    t.topic,
    t.project,
    t.total_views,
    m.max_views,
    round(100.0 * t.total_views / m.max_views, 1) as pct_of_top_edition
from totals t
join maxima m on t.topic = m.topic
order by t.topic, pct_of_top_edition desc

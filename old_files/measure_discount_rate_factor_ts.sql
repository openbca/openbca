MODEL(
    name  measure.measure_discount_rate_factor_ts,
    kind full,
    grain (measure_id, year, quarter),
);

WITH discount_rates as (
SELECT
    measure_id
    , start_year  
    , start_quarter 
    , estimated_useful_life
    , coalesce(m.discount_rate, gp.discount_rate) as discount_rate, 
FROM
    openbca_core.measures m, openbca_core.global_parameters gp
)

SELECT
    measure_id,
    --avoided_cost_subset,
    ((quarter_index - quarter_index % 4) / 4)::int AS year,
    (quarter_index % 4 + 1) AS quarter,
    1.0 / POW(
        1.0 + (discount_rate / 4.0),
        ((year - start_year) * 4) + quarter - start_quarter
    ) AS discount_factor
FROM discount_rates--measure.measure_costs
CROSS JOIN generate_series(start_year * 4 + (start_quarter - 1), (start_year + estimated_useful_life) * 4 + (start_quarter - 1 - 1)) AS gs(quarter_index)
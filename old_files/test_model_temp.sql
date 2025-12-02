MODEL(
    name  measure.test_model_temp,
    kind full,
    grain (measure_id, year, quarter),
);


WITH discount_rates AS (
SELECT
    measure_id
    , start_year  
    , start_quarter 
    , estimated_useful_life
    , coalesce(m.discount_rate, gp.discount_rate) as discount_rate, 
FROM
    openbca_core.measures m, openbca_core.global_parameters gp
)

, measure_discount_rate_factor_ts AS (
SELECT
    measure_id,
    ((quarter_index - quarter_index % 4) / 4)::int AS year,
    (quarter_index % 4 + 1) AS quarter,
    1.0 / POW(
        1.0 + (discount_rate / 4.0),
        ((year - start_year) * 4) + quarter - start_quarter
    ) AS discount_factor
FROM 
discount_rates
CROSS JOIN generate_series(start_year * 4 + (start_quarter - 1), (start_year + estimated_useful_life) * 4 + (start_quarter - 1 - 1)) AS gs(quarter_index)
)

SELECT  
    m.measure_id
    , year 
    , quarter
    , discount_factor
    , ntg  
    , unit_quantity
    , discount_factor * ntg * unit_quantity AS factor
    , k.commodity AS commodity
    , energy_savings_by_commodity[k.commodity] AS energy_savings
    , discount_factor * ntg * unit_quantity * energy_savings_by_commodity[k.commodity] AS energy_savings_factor_applied
    , load_shape_mapping_by_commodity[k.commodity] AS load_shape
    , avoided_cost_subset
FROM 
--measure.measure_discount_rate_factor_ts d 
measure_discount_rate_factor_ts d
JOIN openbca_core.measures m ON 
m.measure_id = d.measure_id
CROSS JOIN UNNEST(map_keys(m.energy_savings_by_commodity)) AS k(commodity)
, openbca_core.global_parameters gp
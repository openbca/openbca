MODEL(
    name core_layer2_precompute.cost_factors,
    kind VIEW,
);


WITH discount_rates AS (
    SELECT
        id
        , start_year  
        --, start_quarter 
        , estimated_useful_life
        , COALESCE(m.discount_rate, gp.discount_rate) AS discount_rate, 
--        , discount_cadence
    FROM
        core_layer0_base.measures m, core_layer0_base.global_parameters gp
    )

    , measure_discount_rate_factor_ts AS (
    SELECT
        id,
        start_year,
        --start_quarter,
        year_index AS year,
--        quarter_index AS quarter,
        1.0 / POW(
            1.0 + discount_rate,
            (year - start_year) 
        ) AS discount_factor
--        , discount_cadence
    FROM 
        discount_rates
    CROSS JOIN GENERATE_SERIES(start_year, (start_year + estimated_useful_life)) AS gs(year_index)
--    CROSS JOIN GENERATE_SERIES(1, 4) AS gs(quarter_index)
    WHERE
        year BETWEEN start_year AND start_year + estimated_useful_life - 1
        --(year = start_year
        --AND quarter >= start_quarter)
        --OR (year BETWEEN start_year + 1 AND (start_year + estimated_useful_life - 1))
        --OR (year = start_year + estimated_useful_life AND quarter <= start_quarter - 1)
)

SELECT 
    cg.id
    , cg.cost
    --, d.start_year
    , d.year
    , cg.cost_value * unit_quantity * discount_factor AS cost_factors_applied
    , cg.calc_type
    , cg.value_stream_group
FROM 
    core_layer1_mappings.cost_groupings cg 
JOIN measure_discount_rate_factor_ts d ON 
    cg.id = d.id
WHERE
    (cg.calc_type = 'Single Value - First Year' AND d.year = d.start_year)
    OR cg.calc_type = 'Time Series - Annual'
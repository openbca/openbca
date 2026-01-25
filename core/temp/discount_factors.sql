MODEL(
    name core_layer2_precompute.discount_factors,
    kind VIEW,
);


WITH discount_rates AS (
    SELECT
        id::VARCHAR AS id
        , start_year::INTEGER AS start_year  
        , start_quarter::INTEGER AS start_quarter 
        , estimated_useful_life::INTEGER AS estimated_useful_life
        , COALESCE(m.discount_rate, gp.discount_rate)::FLOAT AS discount_rate
        , gp.discount_cadence::INTEGER AS discount_cadence
    FROM
        core_layer0_base.measures m, core_layer0_base.global_parameters gp
)

, measure_discount_rate_factor_quarterly_ts AS (
    SELECT
        id::VARCHAR AS id,
        ((quarter_index - quarter_index % 4) / 4)::INTEGER AS year,
        (quarter_index % 4 + 1)::INTEGER AS quarter,
        1.0 / POW(
            1.0 + (discount_rate / 4),
            ((year - start_year) * 4) + quarter - start_quarter
        )::FLOAT AS discount_factor
        , discount_cadence::INTEGER AS discount_cadence
    FROM 
        discount_rates
    CROSS JOIN GENERATE_SERIES(start_year * 4 + (start_quarter - 1), (start_year + estimated_useful_life) * 4 + (start_quarter - 2)) AS gs(quarter_index)
)

, measure_discount_rate_factor_annual_ts AS (
    SELECT
        id::VARCHAR AS id,
        start_quarter::INTEGER AS start_quarter,
        year_index::INTEGER AS year,
        quarter_index::INTEGER AS quarter,
        1.0 / POW(
            1.0 + discount_rate,
            (year - start_year) 
        )::FLOAT AS discount_factor
        , discount_cadence::INTEGER AS discount_cadence
    FROM 
        discount_rates
    CROSS JOIN GENERATE_SERIES(start_year, (start_year + estimated_useful_life)) AS gs(year_index)
    CROSS JOIN GENERATE_SERIES(1, 4) AS gs(quarter_index)
    WHERE
        (year = start_year AND quarter >= start_quarter)
        OR (year BETWEEN start_year + 1 AND (start_year + estimated_useful_life - 1))
        OR (year = start_year + estimated_useful_life AND quarter <= start_quarter - 1)
)

    SELECT 
        * EXCEPT(discount_cadence)
    FROM 
        measure_discount_rate_factor_quarterly_ts
    WHERE 
        discount_cadence = 4

    UNION ALL 

    SELECT 
        * EXCEPT(start_quarter, discount_factor, discount_cadence)
        , COALESCE(
            LAG(discount_factor, start_quarter - 1) OVER (
                PARTITION BY id
                ORDER BY year, quarter
               ), 
            1.0)::FLOAT AS discount_factor
    FROM 
        measure_discount_rate_factor_annual_ts
    WHERE
        discount_cadence = 1
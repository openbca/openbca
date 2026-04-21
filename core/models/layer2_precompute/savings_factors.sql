MODEL(
    name core_layer2_precompute.savings_factors,
    kind VIEW,
);


WITH discount_rates AS (
    SELECT
        id
        , start_year  
        , start_quarter 
        , estimated_useful_life
        , m.discount_rate 
        , gp.inflation_rate
        , discount_cadence
    FROM
        core_layer0_base.measures m, core_layer0_base.global_parameters gp
)

, measure_discount_rate_factor_quarterly_ts AS (
    SELECT
        id,
        ((quarter_index - quarter_index % 4) / 4) AS year,
        (quarter_index % 4 + 1) AS quarter,
        1.0 / POW(
            1.0 + ((discount_rate - inflation_rate) / 4),
            ((year - start_year) * 4) + quarter - start_quarter
        ) AS discount_factor
        , discount_cadence
    FROM 
        discount_rates
    CROSS JOIN GENERATE_SERIES(start_year * 4 + (start_quarter - 1), (start_year + estimated_useful_life) * 4 + (start_quarter - 2)) AS gs(quarter_index)
)

, measure_discount_rate_factor_annual_ts AS (
    SELECT
        id,
        start_quarter,
        year_index AS year,
        quarter_index AS quarter,
        1.0 / POW(
            1.0 + (discount_rate - inflation_rate),
            (year - start_year) 
        ) AS discount_factor
        , discount_cadence
    FROM 
        discount_rates
    CROSS JOIN GENERATE_SERIES(start_year, (start_year + estimated_useful_life)) AS gs(year_index)
    CROSS JOIN GENERATE_SERIES(1, 4) AS gs(quarter_index)
    WHERE
        (year = start_year AND quarter >= start_quarter)
        OR (year BETWEEN start_year + 1 AND (start_year + estimated_useful_life - 1))
        OR (year = start_year + estimated_useful_life AND quarter <= start_quarter - 1)
)

, measure_discount_rate_factor_ts AS (
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
            1.0) AS discount_factor
    FROM 
        measure_discount_rate_factor_annual_ts
    WHERE
        discount_cadence = 1
)

SELECT  
    m.id
    , k.commodity AS commodity
    , year 
    , quarter
    , discount_factor
    , 1.0 / POW(
        1.0 + gp.inflation_rate,
        (year - gp.dollar_year) 
    ) AS inflation_factor
    , net_to_gross_ratio  
    , unit_quantity
    , energy_savings_by_commodity[k.commodity] * unit_quantity * net_to_gross_ratio AS annual_net_energy_savings
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN 1/(1-electric_line_loss)  
    WHEN UPPER(k.commodity) = 'NATURAL GAS' THEN 1/(1-natural_gas_line_loss)
    ELSE 1.0 
    END AS line_loss_factor
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN 1/(1-peak_capacity_line_loss)  
    END AS peak_capacity_line_loss_factor
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN energy_savings_by_commodity[k.commodity] * unit_quantity * net_to_gross_ratio * discount_factor  / ((1-electric_line_loss) * POW(1.0 + gp.inflation_rate, (year - gp.dollar_year)))  
    WHEN UPPER(k.commodity) = 'NATURAL GAS' THEN energy_savings_by_commodity[k.commodity] * unit_quantity * net_to_gross_ratio * discount_factor / ((1-natural_gas_line_loss) * POW(1.0 + gp.inflation_rate, (year - gp.dollar_year)))
    ELSE energy_savings_by_commodity[k.commodity] * unit_quantity * net_to_gross_ratio * discount_factor / (POW(1.0 + gp.inflation_rate, (year - gp.dollar_year)))
    END AS energy_savings_factors_applied
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN coincident_peak_savings_kw * unit_quantity * net_to_gross_ratio * discount_factor / ((1-peak_capacity_line_loss) * POW(1.0 + gp.inflation_rate, (year - gp.dollar_year))) 
    ELSE NULL 
    END AS coincident_peak_savings_factors_applied
FROM 
    measure_discount_rate_factor_ts d
JOIN core_layer0_base.measures m ON 
    m.id = d.id
CROSS JOIN UNNEST(map_keys(m.energy_savings_by_commodity)) AS k(commodity)
, core_layer0_base.global_parameters gp
WHERE 
    annual_net_energy_savings IS NOT NULL 

UNION ALL

SELECT 
    m.id
    , k.commodity
    , year 
    , quarter
    , discount_factor
    , 1.0 / POW(
        1.0 + gp.inflation_rate,
        (year - gp.dollar_year) 
    ) AS inflation_factor
    , net_to_gross_ratio  
    , unit_quantity
    , NULL AS annual_net_energy_savings
    , NULL AS line_loss_factor
    , NULL AS peak_capacity_line_loss_factor
    , NULL AS energy_savings_factors_applied
    , NULL AS coincident_peak_savings_factors_applied
FROM 
    measure_discount_rate_factor_ts d
JOIN core_layer0_base.measures m ON 
    m.id = d.id
CROSS JOIN UNNEST(cost_commodities) AS k(commodity)
, core_layer0_base.global_parameters gp
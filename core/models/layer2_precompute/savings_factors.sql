MODEL(
    name core_layer2_precompute.savings_factors,
    kind VIEW,
);


WITH discount_rates AS (
SELECT
    measure_id
    , start_year  
    , start_quarter 
    , estimated_useful_life
    , COALESCE(m.discount_rate, gp.discount_rate) AS discount_rate, 
FROM
    core_layer0_base.measures m, core_layer0_base.global_parameters gp
)

, measure_discount_rate_factor_ts AS (
SELECT
    measure_id,
    ((quarter_index - quarter_index % 4) / 4) AS year,
    (quarter_index % 4 + 1) AS quarter,
    1.0 / POW(
        1.0 + (discount_rate / 4.0),
        ((year - start_year) * 4) + quarter - start_quarter
    ) AS discount_factor
FROM 
discount_rates
CROSS JOIN GENERATE_SERIES(start_year * 4 + (start_quarter - 1), (start_year + estimated_useful_life) * 4 + (start_quarter - 1 - 1)) AS gs(quarter_index)
)

SELECT  
    m.measure_id
    , k.commodity AS commodity
    , year 
    , quarter
    , energy_savings_by_commodity[k.commodity] AS energy_savings
    , discount_factor
    , ntg  
    , unit_quantity
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN 1/(1-electric_line_loss)  
    WHEN UPPER(k.commodity) = 'NATURAL GAS' THEN 1/(1-natural_gas_line_loss)
    ELSE 1.0 
    END AS line_loss_factor
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN energy_savings_by_commodity[k.commodity] * unit_quantity * ntg * discount_factor / (1-electric_line_loss)  
    WHEN UPPER(k.commodity) = 'NATURAL GAS' THEN energy_savings_by_commodity[k.commodity] * unit_quantity * ntg * discount_factor / (1-natural_gas_line_loss)
    ELSE energy_savings_by_commodity[k.commodity] * unit_quantity * ntg * discount_factor 
    END AS energy_savings_factors_applied
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN coincident_peak_kw_savings * unit_quantity * ntg * discount_factor / (1-electric_line_loss) 
    ELSE NULL 
    END AS coincident_peak_savings_factors_applied
FROM 
    measure_discount_rate_factor_ts d
JOIN core_layer0_base.measures m ON 
    m.measure_id = d.measure_id
CROSS JOIN UNNEST(map_keys(m.energy_savings_by_commodity)) AS k(commodity)
, core_layer0_base.global_parameters gp
WHERE 
    energy_savings IS NOT NULL 
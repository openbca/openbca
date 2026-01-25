MODEL(
    name core_layer2_precompute.savings_factors,
    kind VIEW,
);

SELECT  
    d.id::VARCHAR AS id
    , k.commodity::VARCHAR AS commodity
    , d.year::INTEGER AS year 
    , d.quarter::INTEGER AS quarter
    , m.energy_savings_by_commodity[k.commodity]::DOUBLE AS energy_savings
    , d.discount_factor::DOUBLE AS discount_factor
    , i.inflation_factor::DOUBLE AS inflation_factor
    , m.ntg::DOUBLE AS ntg  
    , m.unit_quantity::DOUBLE AS unit_quantity
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN 1/(1-gp.electric_line_loss)  
    WHEN UPPER(k.commodity) = 'NATURAL GAS' THEN 1/(1-gp.natural_gas_line_loss)
    ELSE 1.0 
    END::DOUBLE AS line_loss_factor
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN energy_savings_by_commodity[k.commodity] * unit_quantity * ntg * discount_factor * inflation_factor / (1-gp.electric_line_loss)  
    WHEN UPPER(k.commodity) = 'NATURAL GAS' THEN energy_savings_by_commodity[k.commodity] * unit_quantity * ntg * discount_factor * inflation_factor / (1-gp.natural_gas_line_loss)
    ELSE energy_savings_by_commodity[k.commodity] * unit_quantity * ntg * discount_factor * inflation_factor
    END::DOUBLE AS energy_savings_factors_applied
    , CASE 
    WHEN UPPER(k.commodity) = 'ELECTRIC' THEN coincident_peak_savings_kw * unit_quantity * ntg * discount_factor * inflation_factor / (1-gp.electric_line_loss) 
    ELSE NULL 
    END::DOUBLE AS coincident_peak_savings_factors_applied

FROM 
    core_layer2_precompute.discount_factors d
JOIN core_layer2_precompute.inflation_factors i ON 
    d.year = i.year
JOIN core_layer0_base.measures m ON
    m.id = d.id
CROSS JOIN UNNEST(map_keys(m.energy_savings_by_commodity)) AS k(commodity)
, core_layer0_base.global_parameters gp
WHERE 
    energy_savings IS NOT NULL 

-- UNION ALL

-- SELECT 
--     m.id::VARCHAR AS id
--     , k.commodity::VARCHAR AS commodity
--     , d.year::INTEGER AS year 
--     , d.quarter::INTEGER AS quarter
--     , NULL::FLOAT AS energy_savings
--     , d.discount_factor::FLOAT AS discount_factor
--     , i.inflation_factor::FLOAT AS inflation_factor
--     , m.ntg::FLOAT AS ntg  
--     , m.unit_quantity::FLOAT AS unit_quantity
--     , NULL::FLOAT AS line_loss_factor
--     , NULL::FLOAT AS energy_savings_factors_applied
--     , NULL::FLOAT AS coincident_peak_savings_factors_applied
-- FROM 
--     measure_discount_rate_factor_ts d
-- JOIN inflation_factor_annual_ts i ON 
--     d.id = i.id
--     AND d.year = i.year
-- JOIN core_layer0_base.measures m ON 
--     m.id = d.id
-- CROSS JOIN UNNEST(cost_commodities) AS k(commodity)
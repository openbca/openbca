MODEL(
    name core_layer1_mappings.commodity_load_shape_by_id,
    kind VIEW,
    grain (id, commodity),
);

    SELECT
        id
        , k.commodity
        , energy_savings_by_commodity[k.commodity] * unit_quantity * ntg AS total_net_annual_energy_savings
        , CASE 
        WHEN commodity = 'ELECTRIC' THEN electric_load_shape
        WHEN commodity = 'NATURAL GAS' THEN natural_gas_load_shape 
        ELSE 'ANNUAL'
        END AS load_shape
    FROM 
        core_layer0_base.measures 
    CROSS JOIN UNNEST(map_keys(energy_savings_by_commodity)) AS k(commodity)
    WHERE 
        energy_savings_by_commodity[k.commodity] IS NOT NULL

UNION ALL

    SELECT
        id
        , k.commodity
        , NULL AS total_net_annual_energy_savings
        , 'ANNUAL' AS load_shape
    FROM 
        core_layer0_base.measures 
    CROSS JOIN UNNEST(cost_commodities) AS k(commodity)
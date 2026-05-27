MODEL(
    name core_layer1_mappings.impact_category_load_shape_by_id,
    kind VIEW,
    grain (id, impact_category),
);

    SELECT
        id
        , k.impact_category
        , energy_savings_by_impact_category[k.impact_category] * unit_quantity * net_to_gross_ratio AS total_net_annual_energy_savings
        , CASE 
        WHEN impact_category = 'ELECTRIC' THEN electric_savings_load_shape
        WHEN impact_category = 'NATURAL GAS' THEN natural_gas_savings_load_shape 
        ELSE 'ANNUAL'
        END AS load_shape
    FROM 
        core_layer0_base.measures 
    CROSS JOIN UNNEST(map_keys(energy_savings_by_impact_category)) AS k(impact_category)
    WHERE 
        energy_savings_by_impact_category[k.impact_category] IS NOT NULL

UNION ALL

    SELECT
        id
        , k.impact_category
        , NULL AS total_net_annual_energy_savings
        , 'ANNUAL' AS load_shape
    FROM 
        core_layer0_base.measures 
    CROSS JOIN UNNEST(cost_commodities) AS k(impact_category)
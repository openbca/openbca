MODEL(
    name core_layer1_mappings.commodity_load_shape_by_id,
    kind VIEW,
    grain (id, commodity),
);

    SELECT
        id
        , commodity
        , CASE 
        WHEN commodity = 'ELECTRIC' THEN electric_load_shape
        WHEN commodity = 'NATURAL GAS' THEN natural_gas_load_shape 
        ELSE 'ANNUAL'
        END AS load_shape
    FROM 
        core_layer0_base.measures 
    CROSS JOIN UNNEST(map_keys(energy_savings_by_commodity)) AS k(commodity)
    WHERE 
        commodity NOT LIKE 'STANDARD%'
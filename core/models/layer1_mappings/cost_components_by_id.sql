MODEL(
    name core_layer1_mappings.cost_components_by_id,
    kind VIEW,
    grain (id, commodity),
);

WITH costs_by_id_commodity AS (
    SELECT 
        m.id  
        , m.start_year
        , m.ntg
        , vsg.commodity
        , k.avoided_cost
        , unit_quantity * costs_by_type[k.avoided_cost] AS cost_value
        , vsg.calc_type
    FROM 
        openbca.core_layer0_base.measures m 
    CROSS JOIN UNNEST(map_keys(costs_by_type)) AS k(avoided_cost)
    JOIN openbca.core_layer0_base.value_stream_groups vsg ON
        k.avoided_cost = vsg.avoided_cost
    WHERE 
        vsg.include_in_test 
        AND cost_value IS NOT NULL -- Include?
)

SELECT
    c.*
    , cost_treatment
    , CASE 
    WHEN factor = '0' THEN 0
    WHEN factor = '1' THEN 1
    WHEN factor = '-1' THEN -1
    WHEN factor = 'ntg' THEN ntg 
    WHEN factor = '1-ntg' THEN 1 - ntg 
    END AS cost_treatment_factor 
FROM 
    costs_by_id_commodity c 
JOIN core_layer0_base.cost_treatment_factors t ON 
    c.commodity = t.commodity
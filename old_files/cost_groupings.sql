MODEL(
    name core_layer1_mappings.cost_groupings,
    kind VIEW,
);

WITH cost_categories AS (
    SELECT 
        avoided_cost AS cost
        , calc_type
        , value_stream_group 
    FROM 
        openbca.core_layer0_base.value_stream_groups vsg 
    WHERE 
        upper(commodity) IN ('ADMIN', 'INCENTIVE', 'MEASURE', 'TAX INCENTIVE') 
)

, costs_by_id AS (
    SELECT 
        id  
        , unit_quantity
        , cost
        , costs_by_type[k.cost] as cost_value
    FROM 
        openbca.core_layer0_base.measures 
    CROSS JOIN UNNEST(map_keys(costs_by_type)) AS k(cost)
)

SELECT
    cid.id
    , cid.unit_quantity
    , cid.cost  
    , cid.cost_value  
    , cc.calc_type
    , cc.value_stream_group
FROM 
    cost_categories cc
JOIN costs_by_id cid ON 
    cc.cost = cid.cost
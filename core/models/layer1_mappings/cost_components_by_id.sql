MODEL(
    name core_layer1_mappings.cost_components_by_id,
    kind VIEW,
    grain (id, impact_category),
);

WITH costs_by_id_impact_category AS (
    SELECT 
        m.id  
        , m.start_year
        , m.net_to_gross_ratio
        , vsg.impact_category
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

UNION ALL 

SELECT 
	p.program_name AS id 
	, p.program_year AS start_year  
	, 1.0 AS net_to_gross_ratio
    , vsg.impact_category
    , p.avoided_cost AS avoided_cost
    , p.avoided_cost_value AS cost_value
    , vsg.calc_type
FROM 
	core_layer0_base.program_value_streams p
	JOIN core_layer0_base.value_stream_groups vsg ON 
	p.avoided_cost = vsg.avoided_cost
)

SELECT
    c.*
    , cost_treatment
    , CASE 
    WHEN factor = '0' THEN 0
    WHEN factor = '1' THEN 1
    WHEN factor = '-1' THEN -1
    WHEN factor = 'net_to_gross_ratio' THEN net_to_gross_ratio 
    WHEN factor = '1-net_to_gross_ratio' THEN 1 - net_to_gross_ratio 
    END AS cost_treatment_factor 
FROM 
    costs_by_id_impact_category c 
JOIN core_layer0_base.cost_treatment_factors t ON 
    c.impact_category = t.impact_category
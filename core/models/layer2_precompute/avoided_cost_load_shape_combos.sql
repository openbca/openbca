MODEL(
    name core_layer2_precompute.avoided_cost_load_shape_combos,
    kind VIEW,
);

WITH year_range_by_ac AS (
SELECT 
    avoided_cost 
    , avoided_cost_subset 
    , MIN(start_year) AS min_start_year
    , MAX(start_year + estimated_useful_life) AS max_last_year
FROM 
    core_layer1_mappings.avoided_cost_subsets_by_id
GROUP BY 
    avoided_cost 
    , avoided_cost_subset 
)

(
SELECT  
    false::BOOLEAN AS coincident_peak_capacity_calc
    , ac.avoided_cost
    , ac.avoided_cost_subset 
    , ac.year  
    , ac.quarter  
    , ac.month  
    , ac.day_of_year   
    , ac.hour_of_day  
    , ac.hour_of_year  
    , ac.avoided_cost_value  
    , ls.load_shape 
    , ls.load_shape_value 
    , ac.avoided_cost_value * ls.load_shape_value AS avoided_cost_x_load_shape
FROM 
    core_layer0_base.avoided_costs_ts ac
JOIN core_layer0_base.load_shapes_ts ls ON 
    ac.hour_of_year = ls.hour_of_year
JOIN core_layer0_base.value_stream_groups vsg ON
    ac.avoided_cost = vsg.avoided_cost
    AND ls.commodity = vsg.commodity
JOIN year_range_by_ac y ON  
    ac.avoided_cost = y.avoided_cost  
    AND ac.avoided_cost_subset = y.avoided_cost_subset
WHERE 
    load_shape IN (SELECT DISTINCT load_shape FROM core_layer1_mappings.commodity_load_shape_by_id)
    AND vsg.include_in_test
    AND value_stream_group IN ('electric', 'natural_gas')
    AND ac.hour_of_year IS NOT NULL
    AND ac.year BETWEEN min_start_year AND max_last_year
    --AND ac.hour_of_year in (0, 1, 2, 8757, 8758, 8759, 8760) --Testing only
)

UNION ALL 

(
    SELECT 
    false::BOOLEAN AS coincident_peak_capacity_calc
    , ac.avoided_cost
    , ac.avoided_cost_subset 
    , ac.year  
    , ac.quarter  
    , ac.month  
    , ac.day_of_year   
    , NULL AS hour_of_day  
    , NULL AS hour_of_year  
    , ac.avoided_cost_value  
    , ls.load_shape 
    , SUM(ls.load_shape_value) AS load_shape_value 
    , ac.avoided_cost_value * SUM(ls.load_shape_value) AS avoided_cost_x_load_shape
    FROM 
    core_layer0_base.avoided_costs_ts ac
    JOIN core_layer0_base.load_shapes_ts ls ON 
    ac.day_of_year = ls.day_of_year
    JOIN core_layer0_base.value_stream_groups vsg ON
    ac.avoided_cost = vsg.avoided_cost
    AND ls.commodity = vsg.commodity
    JOIN year_range_by_ac y ON  
    ac.avoided_cost = y.avoided_cost  
    AND ac.avoided_cost_subset = y.avoided_cost_subset
    WHERE 
    load_shape IN (SELECT DISTINCT load_shape FROM core_layer1_mappings.commodity_load_shape_by_id)
    AND vsg.include_in_test
    AND value_stream_group IN ('electric', 'natural_gas')
    AND ac.hour_of_year IS NULL
    AND ac.day_of_year IS NOT NULL 
    AND ac.year BETWEEN min_start_year AND max_last_year
    --AND ac.day_of_year in (0, 1, 2, 3, 363, 364, 365, 366) --Testing only
    GROUP BY 
    ac.avoided_cost
    , ac.avoided_cost_subset 
    , ac.year  
    , ac.quarter  
    , ac.month  
    , ac.day_of_year   
    , ac.avoided_cost_value  
    , ls.load_shape 
)

UNION ALL 

(
    SELECT  
    false::BOOLEAN AS coincident_peak_capacity_calc
    , ac.avoided_cost
    , ac.avoided_cost_subset 
    , ac.year  
    , ac.quarter  
    , ac.month  
    , NULL AS day_of_year   
    , NULL AS hour_of_day  
    , NULL AS hour_of_year  
    , ac.avoided_cost_value  
    , ls.load_shape 
    , SUM(ls.load_shape_value) AS load_shape_value 
    , ac.avoided_cost_value * SUM(ls.load_shape_value) AS avoided_cost_x_load_shape
    FROM 
    core_layer0_base.avoided_costs_ts ac
    JOIN core_layer0_base.load_shapes_ts ls ON 
    ac.month = ls.month
    JOIN core_layer0_base.value_stream_groups vsg ON
    ac.avoided_cost = vsg.avoided_cost
    AND ls.commodity = vsg.commodity
    JOIN year_range_by_ac y ON  
    ac.avoided_cost = y.avoided_cost  
    AND ac.avoided_cost_subset = y.avoided_cost_subset
    WHERE 
    load_shape IN (SELECT DISTINCT load_shape FROM core_layer1_mappings.commodity_load_shape_by_id)
    AND vsg.include_in_test
    AND vsg.value_stream_group IN ('electric', 'natural_gas')
    AND ac.hour_of_year IS NULL
    AND ac.day_of_year IS NULL
    AND ac.month IS NOT NULL
    AND ac.year BETWEEN min_start_year AND max_last_year
    GROUP BY 
    ac.avoided_cost
    , ac.avoided_cost_subset 
    , ac.year  
    , ac.quarter  
    , ac.month    
    , ac.avoided_cost_value  
    , ls.load_shape
)

UNION ALL 

(
    select  
    false::BOOLEAN AS coincident_peak_capacity_calc
    , ac.avoided_cost
    , ac.avoided_cost_subset 
    , ac.year  
    , NULL AS quarter
    , NULL AS month   
    , NULL AS day_of_year   
    , NULL AS hour_of_day  
    , NULL AS hour_of_year  
    , ac.avoided_cost_value  
    , ls.load_shape 
    , SUM(ls.load_shape_value) AS load_shape_value 
    , ac.avoided_cost_value * SUM(ls.load_shape_value) AS avoided_cost_x_load_shape
    FROM 
    core_layer0_base.avoided_costs_ts ac
    JOIN core_layer0_base.value_stream_groups vsg ON
    ac.avoided_cost = vsg.avoided_cost
    JOIN core_layer0_base.load_shapes_ts ls ON
    ls.commodity = vsg.commodity
    JOIN year_range_by_ac y ON  
    ac.avoided_cost = y.avoided_cost  
    AND ac.avoided_cost_subset = y.avoided_cost_subset
    WHERE 
    load_shape IN (SELECT DISTINCT load_shape FROM core_layer1_mappings.commodity_load_shape_by_id)
    AND vsg.include_in_test
    AND vsg.value_stream_group IN ('electric', 'natural_gas')
    AND ac.hour_of_year IS NULL
    AND ac.day_of_year IS NULL
    AND ac.month IS NULL
    AND ac.year BETWEEN min_start_year AND max_last_year
    GROUP BY 
    ac.avoided_cost
    , ac.avoided_cost_subset 
    , ac.year     
    , ac.avoided_cost_value  
    , ls.load_shape
)

UNION ALL

(
    SELECT  
    false::BOOLEAN AS coincident_peak_capacity_calc
    , ac.avoided_cost
    , ac.avoided_cost_subset 
    , ac.year  
    , NULL AS quarter  
    , ac.month  
    , ac.day_of_year   
    , ac.hour_of_day  
    , ac.hour_of_year  
    , ac.avoided_cost_value  
    , 'ANNUAL' AS load_shape 
    , 1.0 AS load_shape_value 
    , ac.avoided_cost_value AS avoided_cost_x_load_shape 
    FROM 
    core_layer0_base.avoided_costs_ts ac
    JOIN core_layer0_base.value_stream_groups vsg ON
    ac.avoided_cost = vsg.avoided_cost
    JOIN year_range_by_ac y ON  
    ac.avoided_cost = y.avoided_cost  
    AND ac.avoided_cost_subset = y.avoided_cost_subset
    WHERE 
    vsg.include_in_test
    AND vsg.value_stream_group IN ('annual', 'first_year')
    AND ac.hour_of_year IS NULL
    AND ac.day_of_year IS NULL
    AND ac.month IS NULL
    AND ac.year IS NOT NULL
    AND ac.year BETWEEN min_start_year AND max_last_year
)

UNION ALL 

(
    SELECT  
    distinct
    true::BOOLEAN AS coincident_peak_capacity_calc
    , ac.avoided_cost
    , ac.avoided_cost_subset 
    , ac.year  
    , NULL AS quarter  
    , ac.month  
    , ac.day_of_year   
    , ac.hour_of_day  
    , ac.hour_of_year  
    , ac.avoided_cost_value  
    , ls.load_shape  
    , 1.0 AS load_shape_value 
    , ac.avoided_cost_value AS avoided_cost_x_load_shape 
    FROM 
    core_layer0_base.avoided_costs_ts ac
    JOIN core_layer0_base.value_stream_groups vsg ON
    ac.avoided_cost = vsg.avoided_cost
    JOIN core_layer0_base.load_shapes_ts ls ON
    ls.commodity = vsg.commodity
    JOIN year_range_by_ac y ON  
    ac.avoided_cost = y.avoided_cost  
    AND ac.avoided_cost_subset = y.avoided_cost_subset
    WHERE 
    load_shape IN (SELECT DISTINCT load_shape FROM core_layer1_mappings.commodity_load_shape_by_id)
    AND vsg.include_in_test
    AND vsg.value_stream_group = 'capacity'
    AND ac.hour_of_year IS NULL
    AND ac.day_of_year IS NULL
    AND ac.month IS NULL
    AND ac.year IS NOT NULL
    AND ac.year BETWEEN min_start_year AND max_last_year
)
MODEL(
    name core_layer3_finalization.final_value_calculations,
    kind FULL,
);

SELECT 
    factors.measure_id
    , factors.commodity 
    --, cls.load_shape
    , acs.avoided_cost
    --, acs.avoided_cost_subset
    , ac_ls.year
    , coalesce(ac_ls.quarter, acs.start_quarter) AS quarter
    , ac_ls.month
    , ac_ls.day_of_year 
    , ac_ls.hour_of_year
    , factors.energy_savings_factors_applied * ac_ls.avoided_cost_x_load_shape as final_dollar_value
FROM 
    core_layer2_computation.savings_factors factors
JOIN core_layer1_mappings.commodity_load_shape_by_id cls ON 
    factors.measure_id = cls.measure_id 
    AND factors.commodity = cls.commodity
JOIN core_layer1_mappings.avoided_cost_subsets_by_id acs ON 
    factors.measure_id = acs.measure_id
    AND factors.commodity = acs.commodity
JOIN core_layer2_computation.avoided_cost_load_shape_combos ac_ls ON  
    factors.year = ac_ls.year 
    AND factors.quarter = coalesce(ac_ls.quarter, acs.start_quarter)   
    AND cls.load_shape = ac_ls.load_shape
    AND acs.avoided_cost = ac_ls.avoided_cost 
    AND acs.avoided_cost_subset = ac_ls.avoided_cost_subset 
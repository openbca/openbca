MODEL(
    name core_layer3_finalization.final_value_calculations_ts,
    kind FULL,
);

WITH standard_value_streams AS (
SELECT 
    factors.id
    , factors.commodity 
    , acs.avoided_cost AS value_stream 
    , ac_ls.year
    , COALESCE(ac_ls.quarter, acs.start_quarter) AS quarter
    , ac_ls.month
    , ac_ls.day_of_year 
    , ac_ls.hour_of_year
	, ac_ls.hour_of_day
    , factors.energy_savings_factors_applied * ac_ls.avoided_cost_x_load_shape AS final_dollar_value
	, factors.discount_factor
FROM 
    core_layer2_precompute.savings_factors factors
JOIN core_layer1_mappings.commodity_load_shape_by_id cls ON 
    factors.id = cls.id 
    AND factors.commodity = cls.commodity
JOIN core_layer1_mappings.avoided_cost_subsets_by_id acs ON 
    factors.id = acs.id
    AND factors.commodity = acs.commodity
JOIN core_layer2_precompute.avoided_cost_load_shape_combos ac_ls ON  
    factors.year = ac_ls.year 
    AND factors.quarter = COALESCE(ac_ls.quarter, acs.start_quarter)   
    AND cls.load_shape = ac_ls.load_shape
    AND acs.avoided_cost = ac_ls.avoided_cost 
    AND acs.avoided_cost_subset = ac_ls.avoided_cost_subset 
)

SELECT 
    * EXCEPT(discount_factor)
FROM 
    standard_value_streams 
WHERE
	commodity NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')

UNION ALL  

SELECT 
	svs.id  
	, svs.commodity
	, c.avoided_cost as value_stream
	, svs.year
	, svs.quarter
	, svs.month
    , svs.day_of_year 
    , svs.hour_of_year
	, svs.hour_of_day
	, -c.cost_value * discount_factor * cost_treatment_factor AS final_dollar_value
FROM 
	standard_value_streams svs 
JOIN core_layer1_mappings.cost_components_by_id c ON  
	svs.id = c.id 
	AND svs.value_stream = c.avoided_cost
	, core_layer0_base.global_parameters gp
WHERE 
	c.cost_treatment = gp.cost_treatment
	AND (
    (c.calc_type = 'Single Value - First Year' AND svs.year = c.start_year)
    OR c.calc_type = 'Time Series - Annual'
	)

UNION ALL

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year 
	, svs.hour_of_day
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.value_stream = 'Energy Generation (E)'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'ELECTRIC'
	AND include_in_test 

UNION ALL

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year 
	, svs.hour_of_day
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.value_stream = 'Fuel Supply and O&M (NG)'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'NATURAL GAS'
	AND include_in_test 

UNION ALL

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year
	, svs.hour_of_day 
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.value_stream = 'Propane Supply'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'PROPANE'
	AND include_in_test 

UNION ALL 

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year
	, svs.hour_of_day 
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.value_stream = 'Oil Supply'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'OIL'
	AND include_in_test 

UNION ALL 

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year 
	, svs.hour_of_day
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.value_stream = 'Diesel Supply'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'DIESEL'
	AND include_in_test 

UNION ALL 

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, NULL AS quarter
	, NULL AS month  
	, NULL AS day_of_year 
	, NULL AS hour_of_year 
	, NULL AS hour_of_day
	, SUM(svs.final_dollar_value) * vsg.pct_adder AS final_dollar_value -- Check if null values in sum
FROM 
	standard_value_streams svs
	, openbca.core_layer0_base.value_stream_groups vsg  
WHERE 
	svs.value_stream IN ('Energy Generation (E)', 'Fuel Supply and O&M (NG)', 'Propane Supply', 'Oil Supply', 'Diesel Supply')
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) NOT IN ('ELECTRIC', 'NATURAL GAS', 'PROPANE', 'OIL', 'DIESEL')
	AND include_in_test 
GROUP BY 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost 
	, svs.year 
	, vsg.pct_adder 
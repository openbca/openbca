MODEL(
    name core_layer3_finalization.final_value_calculations,
    kind FULL,
);

WITH standard_value_streams AS (
SELECT 
    factors.id
    , factors.commodity 
    , acs.avoided_cost
    , ac_ls.year
    , COALESCE(ac_ls.quarter, acs.start_quarter) AS quarter
    , ac_ls.month
    , ac_ls.day_of_year 
    , ac_ls.hour_of_year
    , factors.energy_savings_factors_applied * ac_ls.avoided_cost_x_load_shape as final_dollar_value
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
    *
FROM 
    standard_value_streams 

UNION ALL

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year 
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.avoided_cost = 'Energy Generation (Electric)'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'ELECTRIC'
	AND include_in_test 

UNION ALL

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year 
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.avoided_cost = 'Fuel Supply and O&M (NG)'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'NATURAL GAS'
	AND include_in_test 

UNION ALL

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year 
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.avoided_cost = 'Propane Supply'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'PROPANE'
	AND include_in_test 

UNION ALL 

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year 
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.avoided_cost = 'Oil Supply'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'OIL'
	AND include_in_test 

UNION ALL 

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost 
	, svs.year 
	, svs.quarter
	, svs.month  
	, svs.day_of_year 
	, svs.hour_of_year 
	, svs.final_dollar_value * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
JOIN openbca.core_layer0_base.value_stream_groups vsg ON 
	svs.commodity = vsg.commodity 
WHERE 
	svs.avoided_cost = 'Diesel Supply'
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) = 'DIESEL'
	AND include_in_test 

UNION ALL 

SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost 
	, svs.year 
	, NULL AS quarter
	, NULL AS month  
	, NULL AS day_of_year 
	, NULL AS hour_of_year 
	, SUM(svs.final_dollar_value) * vsg.pct_adder AS final_dollar_value
FROM 
	standard_value_streams svs
	, openbca.core_layer0_base.value_stream_groups vsg  
WHERE 
	svs.avoided_cost IN ('Energy Generation (Electric)', 'Fuel Supply and O&M (NG)', 'Propane Supply', 'Oil Supply', 'Diesel Supply')
	AND UPPER(vsg.calc_type) = 'ADDER (%)' 
	AND UPPER(vsg.commodity) NOT IN ('ELECTRIC', 'NATURAL GAS', 'PROPANE', 'OIL', 'DIESEL')
	AND include_in_test 
GROUP BY 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost 
	, svs.year 
	, vsg.pct_adder 
MODEL(
    name core_layer3_finalization.final_value_calculations_ts,
    kind FULL,
);

WITH standard_value_stream_hourly AS (
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
	, factors.annual_net_energy_savings * ac_ls.load_shape_value AS net_energy_savings
    , factors.energy_savings_factors_applied * ac_ls.avoided_cost_x_load_shape AS final_dollar_value
	--, factors.discount_factor
    --, factors.inflation_factor
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

, standard_value_streams AS (  
	SELECT 
		id
		, commodity
		, value_stream
		, year
		, quarter
		, month
		, hour_of_day
		, SUM(net_energy_savings) AS net_energy_savings
		, SUM(final_dollar_value) AS final_dollar_value
	FROM 
		standard_value_stream_hourly
	GROUP BY 
		id
		, commodity
		, value_stream
		, year
		, quarter
		, month
		, hour_of_day
)

-- "Standard" value streams (not program-level, cost components, or adders)
SELECT 
    * 
FROM 
    standard_value_streams 
WHERE
	commodity NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')

UNION ALL  

-- Measure-level cost components
SELECT 
	svs.id  
	, svs.commodity
	, c.avoided_cost as value_stream
	, svs.year
	, svs.quarter
	, svs.month
    --, svs.day_of_year 
    --, svs.hour_of_year
	, svs.hour_of_day
	, NULL AS net_energy_savings
	, -c.cost_value * cost_treatment_factor / (POW(1.0 + gp.inflation_rate, (year - gp.dollar_year))) AS final_dollar_value --leaving out discount factor as costs are accrued on an ongoing basis.
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

-- Electric adders
SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	--, svs.day_of_year 
	--, svs.hour_of_year 
	, svs.hour_of_day
	, svs.net_energy_savings
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

-- Natural Gas adders
SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	--, svs.day_of_year 
	--, svs.hour_of_year 
	, svs.hour_of_day
	, svs.net_energy_savings
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

-- Propane adders
SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	--, svs.day_of_year 
	--, svs.hour_of_year
	, svs.hour_of_day 
	, svs.net_energy_savings
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

-- Oil adders
SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	--, svs.day_of_year 
	--, svs.hour_of_year
	, svs.hour_of_day 
	, svs.net_energy_savings
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

-- Diesel adders
SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, svs.quarter
	, svs.month  
	--, svs.day_of_year 
	--, svs.hour_of_year 
	, svs.hour_of_day
	, svs.net_energy_savings
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

-- All fuels adders 
SELECT 
	svs.id 
	, vsg.commodity 
	, vsg.avoided_cost AS value_stream 
	, svs.year 
	, NULL AS quarter
	, NULL AS month  
	--, NULL AS day_of_year 
	--, NULL AS hour_of_year 
	, NULL AS hour_of_day
	, NULL AS net_energy_savings -- Convert kWh to MMBtu and create sum of all fuels metric?
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

UNION ALL 

-- Program-level benefits 
SELECT 
	p.program_name AS id 
	, vsg.commodity 
	, p.avoided_cost AS value_stream 
	, p.program_year AS year  
	, NULL AS quarter
	, NULL AS month  
	-- , NULL AS day_of_year 
	-- , NULL AS hour_of_year 
	, NULL AS hour_of_day
	, NULL AS net_energy_savings
	, avoided_cost_value / (POW(1.0 + gp.inflation_rate, (p.program_year - gp.dollar_year))) AS final_dollar_value 
FROM core_layer0_base.program_value_streams p
JOIN core_layer0_base.value_stream_groups vsg ON 
 	p.avoided_cost = vsg.avoided_cost
	, openbca.core_layer0_base.global_parameters gp
WHERE 
	vsg.commodity NOT IN ['ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE']

UNION ALL

-- Program-level costs 
SELECT 
	c.id 
	, c.commodity 
	, c.avoided_cost AS value_stream 
	, c.start_year AS year  
	, NULL AS quarter
	, NULL AS month  
	-- , NULL AS day_of_year 
	-- , NULL AS hour_of_year 
	, NULL AS hour_of_day
	, NULL AS net_energy_savings
	, -c.cost_value * cost_treatment_factor / (POW(1.0 + gp.inflation_rate, (c.start_year - gp.dollar_year))) AS final_dollar_value 
FROM 
	core_layer1_mappings.cost_components_by_id c  
JOIN core_layer0_base.program_value_streams p ON 
	c.id = p.program_name
	AND c.avoided_cost = p.avoided_cost 
	AND c.start_year = p.program_year 
	, openbca.core_layer0_base.global_parameters gp
WHERE 
	c.cost_treatment = gp.cost_treatment

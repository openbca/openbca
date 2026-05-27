MODEL(
    name core_layer3_finalization.svs,
    kind FULL,
);

WITH standard_value_stream_hourly AS (
SELECT 
    factors.id
    , factors.impact_category 
    , acs.avoided_cost AS value_stream 
    , ac_ls.year
    , COALESCE(ac_ls.quarter, acs.start_quarter) AS quarter
    , ac_ls.month
    , ac_ls.day_of_year 
    , ac_ls.hour_of_year
	, ac_ls.hour_of_day
	, ac_ls.marginal_ghg
	, CASE
		WHEN ac_ls.coincident_peak_capacity_calc THEN 0	
		ELSE factors.annual_net_energy_savings * ac_ls.load_shape_value 
		END AS net_energy_savings
	, CASE 
		WHEN ac_ls.coincident_peak_capacity_calc THEN factors.coincident_peak_savings_factors_applied * ac_ls.avoided_cost_x_load_shape
		ELSE factors.energy_savings_factors_applied * ac_ls.avoided_cost_x_load_shape
		END AS final_dollar_value
FROM 
    core_layer2_precompute.savings_factors factors
JOIN core_layer1_mappings.impact_category_load_shape_by_id cls ON 
    factors.id = cls.id 
    AND factors.impact_category = cls.impact_category
JOIN core_layer1_mappings.avoided_cost_subsets_by_id acs ON 
    factors.id = acs.id
    AND factors.impact_category = acs.impact_category
JOIN core_layer2_precompute.avoided_cost_load_shape_combos ac_ls ON  
    factors.year = ac_ls.year 
    AND factors.quarter = COALESCE(ac_ls.quarter, acs.start_quarter)   
    AND cls.load_shape = ac_ls.load_shape
    AND acs.avoided_cost = ac_ls.avoided_cost 
    AND acs.avoided_cost_subset = ac_ls.avoided_cost_subset 
)

	SELECT 
		id
		, impact_category
		, value_stream
		, year
		, quarter
		, month
		, hour_of_day
        --, marginal_ghg
		, SUM(net_energy_savings) AS net_energy_savings
		, SUM(CASE WHEN NOT marginal_ghg THEN final_dollar_value ELSE NULL END) AS final_dollar_value
		, SUM(CASE WHEN marginal_ghg THEN final_dollar_value ELSE NULL END) AS marginal_ghg
	FROM 
		standard_value_stream_hourly 
	GROUP BY 
		id
		, impact_category
		, value_stream
		, year
		, quarter
		, month
		, hour_of_day

MODEL(
    name core_layer3_finalization.final_savings_calculations_ts,
    kind FULL,
);

SELECT 
	cls.id 
	, cls.commodity 
	, ls.month 
	, ls.day_of_year
	, ls.hour_of_year
	, ls.hour_of_day
	, ls.load_shape_value * total_net_annual_energy_savings AS total_net_annual_energy_savings
FROM 
	openbca.core_layer1_mappings.commodity_load_shape_by_id cls
JOIN core_layer0_base.load_shapes_ts ls ON 
	cls.commodity = ls.commodity 
	AND cls.load_shape  = ls.load_shape 
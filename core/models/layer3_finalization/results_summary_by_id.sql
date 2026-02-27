MODEL(
    name core_layer3_finalization.results_summary_by_id,
    kind FULL,
);

WITH lifecycle_savings_calc AS (
	SELECT 
		m.id::VARCHAR AS id
		, m.measure_id::VARCHAR AS measure_id
		, m.measure_name::VARCHAR AS measure_name
		, m.project_id::VARCHAR AS project_id
		, m.program_name::VARCHAR AS program_name
		, m.avoided_cost_subset::VARCHAR AS avoided_cost_subset
		, m.start_year::INTEGER AS start_year
		, m.ntg::FLOAT AS ntg
		, m.estimated_useful_life::INTEGER AS estimated_useful_life
		, m.unit_quantity::INTEGER AS unit_quantity
		, cls.commodity::VARCHAR AS commodity
		, m.label_1::VARCHAR AS label_1
		, m.label_2::VARCHAR AS label_2
		, m.label_3::VARCHAR AS label_3
		, m.label_4::VARCHAR AS label_4
		, m.label_5::VARCHAR AS label_5
		, cls.total_net_annual_energy_savings * m.estimated_useful_life AS total_net_lifecycle_energy_savings
	FROM
		core_layer1_mappings.commodity_load_shape_by_id cls 
	JOIN core_layer0_base.measures m ON 
		cls.id = m.id
	WHERE 
		cls.commodity NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
)

, lifecycle_savings AS (
	PIVOT (
		SELECT 
			id
			, measure_id
			, measure_name
			, project_id
			, program_name
			, avoided_cost_subset
			, start_year
			, ntg 
			, estimated_useful_life
			, unit_quantity 
			, CASE 
			WHEN commodity = 'ELECTRIC' THEN commodity || ' Lifecycle kWh Savings'
			WHEN commodity IN ('NATURAL GAS', 'PROPANE', 'OIL', 'DIESEL') THEN commodity || ' Lifecycle MMBtu Savings'
			ELSE commodity || ' Lifecycle Savings'
			END AS commodity
			, label_1
			, label_2
			, label_3
			, label_4
			, label_5
			, total_net_lifecycle_energy_savings
		FROM 
			lifecycle_savings_calc
	)
	ON 
		commodity
	USING 
		SUM(total_net_lifecycle_energy_savings)
)

, value_streams_value_calc AS (
	SELECT 
		id
		, value_stream
		, final_dollar_value
	FROM  
		core_layer3_finalization.final_value_calculations_ts
)

, value_stream_values AS (
	PIVOT (
		SELECT 
			id
			, value_stream || ' ($)' AS value_stream
			, final_dollar_value
		FROM 
			value_streams_value_calc
	)
	ON
		value_stream
	USING 
		SUM(final_dollar_value)
)

, commodity_value_calc AS (
	SELECT 
		id
		, commodity
		, final_dollar_value
	FROM  
		core_layer3_finalization.final_value_calculations_ts
)

, commodity_values AS (
	PIVOT (
		SELECT 
			id
			, commodity || ' Total ($)' AS commodity
			, final_dollar_value
		FROM 
			commodity_value_calc
	)
	ON
		commodity
	USING 
		SUM(final_dollar_value)
)

, total_values AS (
	SELECT 
		id
		, MIN(year) AS start_year
		, SUM(CASE WHEN commodity IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE') THEN final_dollar_value END) AS total_costs
		, SUM(CASE WHEN commodity NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE') THEN final_dollar_value END) AS total_benefits
		, SUM(final_dollar_value) AS total_net_benefits
	FROM  
		core_layer3_finalization.final_value_calculations_ts
	GROUP BY
		id
)

SELECT 
	CASE 
	WHEN tv.id = m.id THEN 'Measure' ELSE 'Program' END AS type
	, tv.id
	, COALESCE(lc.program_name, tv.id) AS program_name
	, COALESCE(lc.start_year, tv.start_year) AS start_year
	, lc.* EXCEPT(id, program_name, start_year)
	, tv.* EXCEPT(id, start_year)
	, cv.* EXCEPT(id)
	, vs.* EXCEPT(id)
FROM
	total_values tv 
FULL OUTER JOIN commodity_values cv ON
	tv.id = cv.id
FULL OUTER JOIN value_stream_values vs ON  
	tv.id = vs.id
FULL OUTER JOIN lifecycle_savings lc ON
	tv.id = lc.id
FULL OUTER JOIN core_layer0_base.measures m ON
	tv.id = m.id
ORDER BY  
	type
	, id
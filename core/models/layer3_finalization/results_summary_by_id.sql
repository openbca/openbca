MODEL(
    name core_layer3_finalization.results_summary_by_id,
    kind FULL,
);

WITH lifecycle_savings_calc AS (
	SELECT 
		m.id
		, m.measure_id
		, m.project_id
		, m.program_name
		, m.ntg 
		, m.estimated_useful_life
		, m.unit_quantity 
		, cls.commodity
		, label_1
		, label_2
		, label_3
		, label_4
		, label_5
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
			, project_id
			, program_name
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
		, SUM(final_dollar_value) AS total_dollar_value
	FROM  
		core_layer3_finalization.final_value_calculations_ts
	GROUP BY
		id
)

SELECT 
	lc.*
	, tv.* EXCEPT(id)
	, cv.* EXCEPT(id)
	, vs.* EXCEPT(id)
FROM
	lifecycle_savings lc 
JOIN total_values tv ON
	lc.id = tv.id
JOIN commodity_values cv ON
	lc.id = cv.id
JOIN value_stream_values vs ON  
	lc.id = vs.id
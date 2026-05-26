MODEL(
    name core_layer3_finalization.jst_ratio,
    kind FULL,
);


WITH measure_costs_benefits AS (
	SELECT 
		SUM(
			CASE 
			WHEN impact_category IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
			THEN final_dollar_value END
		) AS dollar_costs
		, SUM(
			CASE 
			WHEN impact_category NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
			THEN final_dollar_value END
		) AS dollar_benefits
	FROM
		core_layer3_finalization.final_value_calculations_ts  
)

SELECT 
	 m.dollar_costs AS total_costs
	, m.dollar_benefits AS total_benefits
	, m.dollar_benefits + m.dollar_costs AS net_benefits
	, (m.dollar_benefits) / -(m.dollar_costs) AS jst_ratio
FROM   
measure_costs_benefits m 
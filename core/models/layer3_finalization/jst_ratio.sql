MODEL(
    name core_layer3_finalization.jst_ratio,
    kind FULL,
);

SELECT 
	SUM(
		CASE 
		WHEN commodity NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
		THEN final_dollar_value END
	) AS dollar_benefits
	, SUM(
		CASE 
		WHEN commodity IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
		THEN final_dollar_value END
	) AS dollar_costs
	, SUM(final_dollar_value) AS net_benefits
	, SUM(
		CASE 
		WHEN commodity NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
		THEN final_dollar_value END
	) / -SUM(
		CASE 
		WHEN commodity IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
		THEN final_dollar_value END
	) AS jst_ratio
FROM
	core_layer3_finalization.final_value_calculations_ts  
	
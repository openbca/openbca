MODEL(
    name core_layer3_finalization.jst_ratio,
    kind FULL,
);

WITH program_costs_benefits AS (
	SELECT 
		-(SUM(program_admin_costs_dollar_per_year) + SUM(program_incentive_utility_dollar_per_year)) AS dollar_costs
		, SUM(program_performance_incentive_utility_dollar_per_year) + SUM(program_federal_incentive_dollar_per_year) AS dollar_benefits
	FROM 
		openbca.core_layer0_base.program_value_streams 
)


, measure_costs_benefits AS (
	SELECT 
		SUM(
			CASE 
			WHEN commodity IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
			THEN final_dollar_value END
		) AS dollar_costs
		, SUM(
			CASE 
			WHEN commodity NOT IN ('ADMIN', 'UTILITY INCENTIVE', 'MEASURE COST', 'TAX INCENTIVE')
			THEN final_dollar_value END
		) AS dollar_benefits
	FROM
		core_layer3_finalization.final_value_calculations_ts  
)

SELECT 
p.dollar_costs + m.dollar_costs AS total_costs
, p.dollar_benefits + m.dollar_benefits AS total_benefits
, p.dollar_benefits + m.dollar_benefits + p.dollar_costs + m.dollar_costs AS net_benefits
, (p.dollar_benefits + m.dollar_benefits) / -(p.dollar_costs + m.dollar_costs) AS jst_ratio
FROM   
program_costs_benefits p 
, measure_costs_benefits m 
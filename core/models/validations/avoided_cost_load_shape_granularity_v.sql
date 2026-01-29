MODEL(
  name core_validations.avoided_cost_load_shape_granularity_v,
  kind FULL,
);

WITH load_shapes_in_use AS (
	SELECT 
		DISTINCT
		'ELECTRIC' AS commodity
		, electric_load_shape AS load_shape
	FROM 
		openbca_input.measures
		
	UNION ALL 
	
	SELECT 
		DISTINCT
		'NATURAL GAS' AS commodity
		, natural_gas_load_shape AS load_shape
	FROM 
		openbca_input.measures
)


, load_shape_counts AS (
SELECT
	'ELECTRIC' AS commodity
    , load_shape
    , COUNT(DISTINCT hour_of_year) AS count_hour_of_year
    , COUNT(DISTINCT day_of_year) AS count_day_of_year
    , COUNT(DISTINCT month) AS count_month
FROM 
    openbca_input.load_shapes_ts
GROUP BY
	load_shape
WHERE 
	load_shape IN (SELECT load_shape FROM load_shapes_in_use WHERE commodity = 'ELECTRIC')
	
UNION ALL 

SELECT
	'NATURAL GAS' AS commodity
    , load_shape
    , COUNT(DISTINCT hour_of_year) AS count_hour_of_year
    , COUNT(DISTINCT day_of_year) AS count_day_of_year
    , COUNT(DISTINCT month) AS count_month
FROM 
    openbca_input.load_shapes_ts
GROUP BY
	load_shape
WHERE 
	load_shape IN (SELECT load_shape FROM load_shapes_in_use WHERE commodity = 'NATURAL GAS')
)


, avoided_cost_counts AS (
SELECT 
	UPPER(vsg.commodity) AS commodity
	, ac.avoided_cost 
	, COUNT(DISTINCT hour_of_year) AS count_hour_of_year
	, COUNT(DISTINCT day_of_year) AS count_day_of_year
	, COUNT(DISTINCT month) AS count_month
FROM 
    openbca_input.avoided_costs_ts ac
JOIN openbca_input.value_stream_groups vsg ON 
	ac.avoided_cost = vsg.avoided_cost 
WHERE  
	UPPER(vsg.commodity) IN ('ELECTRIC', 'NATURAL GAS')
	AND vsg.include_in_test 
GROUP BY
	ac.avoided_cost 
	, vsg.commodity
)


SELECT 
	ac.commodity
	, ac.avoided_cost
	, ls.load_shape
	, GREATEST(ls.count_hour_of_year, ls.count_day_of_year, ls.count_month) AS load_shape_granularity
	, GREATEST(ac.count_hour_of_year, ac.count_day_of_year, ac.count_month) AS avoided_cost_granularity
	, CASE
	WHEN 
	GREATEST(ac.count_hour_of_year, ac.count_day_of_year, ac.count_month) > GREATEST(ls.count_hour_of_year, ls.count_day_of_year, ls.count_month) THEN 'FAIL'
	ELSE 'PASS'
	END AS validation_result	
	
FROM 
	load_shape_counts ls  
JOIN avoided_cost_counts ac ON 
	ls.commodity = ac.commodity
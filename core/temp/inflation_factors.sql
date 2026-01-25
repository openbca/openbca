MODEL(
    name core_layer2_precompute.inflation_factors,
    kind VIEW,
);


WITH measure_year_range as (
	SELECT 
	    MIN(start_year)::INTEGER AS min_start_year
	    , MAX(start_year + estimated_useful_life)::INTEGER AS max_last_year
	FROM
		core_layer0_base.measures
)

-- , program_year_range as (
-- 	SELECT 
-- 	    MIN(program_year)::INTEGER AS min_program_year
-- 	    , MAX(program_year)::INTEGER AS max_program_year
-- 	FROM
-- 		core_layer0_base.program_value_streams
-- )

SELECT
--    id::VARCHAR AS id,
    year_index::INTEGER AS year
    , (CASE  
    WHEN gp.real_or_nominal_inputs = 'real' THEN 1.0  
    ELSE (1.0 / POW(
        1.0 + gp.inflation_rate,
        (year_index::INTEGER - gp.dollar_year) 
    ))
    END)::DOUBLE AS inflation_factor
FROM 
    measure_year_range, core_layer0_base.global_parameters gp --measure_program_ids, program_year_range, 
CROSS JOIN GENERATE_SERIES(min_start_year, max_last_year) AS gs(year_index)

--CROSS JOIN GENERATE_SERIES(LEAST(min_start_year, min_program_year), GREATEST(max_last_year, max_program_year)) AS gs(year_index)
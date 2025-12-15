MODEL(
    name core_layer1_mappings.avoided_cost_subsets_by_id,
    kind VIEW,
    grain (measure_id, avoided_cost, avoided_cost_subset),
);

    WITH ac_subset_by_measure AS (
    SELECT    
        measure_id  
        , avoided_cost_subset 
        , start_year 
        , start_quarter
        , estimated_useful_life
    FROM 
        core_layer0_base.measures
)

    , ac_subsets AS (
    SELECT 
        DISTINCT 
        avoided_cost 
        , avoided_cost_subset AS available_avoided_cost_subset 
    FROM 
        core_layer0_base.avoided_costs_ts
    )

    , ac_subset_measure_combos AS (
    SELECT  
        * 
    FROM  
        ac_subset_by_measure 
    CROSS JOIN ac_subsets
    )


    , first_assignments as (
    SELECT 
        measure_id 
        , avoided_cost
        , avoided_cost_subset
        , start_year
        , start_quarter
        , estimated_useful_life
        , CONCAT(measure_id, avoided_cost) as measure_id_ac
    FROM 
        ac_subset_measure_combos
    WHERE 
        avoided_cost_subset = available_avoided_cost_subset
    )

    SELECT 
        measure_id 
        , smc.avoided_cost
        , avoided_cost_subset
        , vsg.commodity
        , start_year
        , start_quarter
        , estimated_useful_life
    FROM
        first_assignments smc
    JOIN core_layer0_base.value_stream_groups vsg ON  
        smc.avoided_cost = vsg.avoided_cost  

    UNION ALL 
    
    SELECT 
        measure_id 
        , smc.avoided_cost
        , available_avoided_cost_subset AS avoided_cost_subset
        , vsg.commodity
        , start_year
        , start_quarter
        , estimated_useful_life
    FROM 
        ac_subset_measure_combos smc
    JOIN core_layer0_base.value_stream_groups vsg ON  
        smc.avoided_cost = vsg.avoided_cost
    WHERE 
        avoided_cost_subset != available_avoided_cost_subset
        AND available_avoided_cost_subset = 'System-wide'
        AND CONCAT(measure_id, smc.avoided_cost) NOT IN (SELECT measure_id_ac FROM first_assignments)
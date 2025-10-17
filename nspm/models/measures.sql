MODEL (
    name openbca_input.measures,
    kind FULL,
);

SELECT
    CAST(unique_row_id AS INT) AS unique_row_id,
    CAST(measure_id AS STRING) AS measure_id,
    CAST(project_id AS STRING) AS project_id,
    CAST(program_name AS STRING) AS program_name,
    CAST(measure_include AS STRING) AS measure_include,
    CAST(version AS STRING) AS version,
    CAST(subset AS STRING) AS avoided_cost_subset,
    CAST(start_year AS INT) AS start_year,
    CAST(start_quarter AS STRING) AS start_quarter,
    CAST(measure_name AS STRING) AS measure_name,
    CAST(measure_unit AS STRING) AS measure_unit,
    CAST(unit_quantity AS FLOAT) AS unit_quantity,
    CAST(peak_kw_impact AS FLOAT) AS peak_kw_impact,
    CAST(annual_other_fuels_impact_mmbtu AS FLOAT) AS annual_other_fuels_impact_mmbtu,
    CAST(estimated_useful_life_years AS INT) AS estimated_useful_life_years,
    CAST(measure_incremental_costs_per_unit_dollar AS FLOAT) AS measure_incremental_costs_per_unit_dollar,
    CAST(measure_annual_o_m_cost_per_unit_dollar_per_year AS FLOAT) AS measure_annual_o_m_cost_per_unit_dollar_per_year,
    CAST(measure_one_time_incentive_utility_per_unit_dollar_per_year AS FLOAT) AS measure_one_time_incentive_utility_per_unit_dollar_per_year,
    CAST(measure_annual_incentive_utility_per_unit_dollar_per_year AS FLOAT) AS measure_annual_incentive_utility_per_unit_dollar_per_year,
    CAST(measure_transaction_costs_per_unit_dollar_per_year AS FLOAT) AS measure_transaction_costs_per_unit_dollar_per_year,
    CAST(measure_interconnection_costs_per_unit_dollar_per_year AS FLOAT) AS measure_interconnection_costs_per_unit_dollar_per_year,
    CAST(measure_tax_incentives_per_unit_dollar_per_year AS FLOAT) AS measure_tax_incentives_per_unit_dollar_per_year,
    CAST(measure_non_energy_impacts_per_unit_dollar_per_year AS FLOAT) AS measure_non_energy_impacts_per_unit_dollar_per_year,      
    CAST(measure_non_energy_impacts_low_income_per_unit_dollar_per_year AS FLOAT) AS measure_non_energy_impacts_low_income_per_unit_dollar_per_year,
    CAST(change_in_host_customer_reliability_customer_minute_outages_cmo AS FLOAT)
        AS change_in_host_customer_reliability_customer_minute_outages_cmo,
    CAST(custom_1_subsector AS STRING) AS custom_1_subsector,
    CAST(custom_2_zip_code AS STRING) AS custom_2_zip_code, 
    CAST(custom_3 AS STRING) AS custom_3,
    CAST(custom_4 AS STRING) AS custom_4,
    CAST(custom_5 AS STRING) AS custom_5,
    0.1 AS discount_rate_ratio,
    10 AS estimated_useful_life,
    CAST(ntg AS FLOAT) AS net_to_gross_ratio,

    CAST(administration_costs_dollar_per_year AS FLOAT) AS administration_costs_dollar_per_year,
    0 AS admin_cost_dollars, -- FIXME
    0 AS incentive_cost_dollars, -- FIXME
    0 AS measure_cost_dollars, -- FIXME
    MAP {
        'ELECTRICITY': - annual_kwh_impact / 1000.0,
        'GAS': - annual_ng_impact_mmbtu * 10.0
    } AS energy_savings_by_commodity,
    MAP {
        'ELECTRICITY': CAST(loadshape_mapping AS STRING),
        'GAS': NULL -- FIXME
    } AS load_shape_mapping_by_commodity,
    NULL AS avoided_costs, -- FIXME
FROM nspm.openbca_input_measures

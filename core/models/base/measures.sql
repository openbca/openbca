MODEL(
  name openbca_core.measures,
  kind VIEW,
  grain (measure_id),
  audits (
    not_null(columns := (measure_id, start_year, start_quarter, estimated_useful_life)),
    unique_combination_of_columns(columns := (measure_id)),
    accepted_range(column := start_year, min_v := 2010, max_v := 2100),
    accepted_values(column := start_quarter, is_in := (1, 2, 3, 4)),
    accepted_range(column := discount_rate_ratio, min_v := 0, max_v := 1),
    accepted_range(column := net_to_gross_ratio, min_v := 0, max_v := 10),
    accepted_range(column := estimated_useful_life, min_v := 0, max_v := 100),
    accepted_range(column := unit_quantity, min_v := 0),
    accepted_range(column := admin_cost_dollars, min_v := 0),
    accepted_range(column := incentive_cost_dollars, min_v := 0),
    accepted_range(column := measure_cost_dollars, min_v := 0),
    unique_id_validation_audit,
    time_slice_validation_audit,
    avoided_cost_mapping_validation_audit
  )
);

SELECT
    measure_id::VARCHAR AS measure_id,
    avoided_cost_subset::VARCHAR AS avoided_cost_subset,
    --avoided_cost_version::VARCHAR AS avoided_cost_version,
    start_year::INT AS start_year,
    start_quarter::INT AS start_quarter,
    discount_rate_ratio::FLOAT AS discount_rate_ratio,
    estimated_useful_life::INT AS estimated_useful_life,
    unit_quantity::FLOAT AS unit_quantity,
    net_to_gross_ratio::FLOAT AS net_to_gross_ratio,
    admin_cost_dollars::FLOAT AS admin_cost_dollars,
    incentive_cost_dollars::FLOAT AS incentive_cost_dollars,
    measure_cost_dollars::FLOAT AS measure_cost_dollars,
    elec_savings_mwh::FLOAT AS elec_savings_mwh,
    gas_saving_therms::FLOAT AS gas_saving_therms,
    elec_load_shape_mapping::VARCHAR AS elec_load_shape_mapping,
    gas_load_shape_mapping::VARCHAR AS gas_load_shape_mapping,
    avoided_costs::ARRAY<VARCHAR> AS avoided_costs
FROM openbca_input.measures

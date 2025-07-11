MODEL(
  name openbca_core.measures,
  kind VIEW,
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

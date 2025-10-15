MODEL(
    name measure.measure_commodity,
    kind VIEW,
);
SELECT
    measure_id,
    'ELECTRICITY' as commodity,
    avoided_cost_subset,
    upper(elec_load_shape_mapping) as load_shape_mapping,
    elec_savings_mwh as energy_savings,
    unit_quantity * net_to_gross_ratio * elec_savings_mwh as net_energy_savings,
FROM openbca_core.measures
UNION ALL
SELECT
    measure_id,
    'GAS' as commodity,
    avoided_cost_subset,
    upper(gas_load_shape_mapping) as load_shape_mapping,
    gas_saving_therms as energy_savings,
    unit_quantity * net_to_gross_ratio * gas_saving_therms as net_energy_savings,
FROM openbca_core.measures

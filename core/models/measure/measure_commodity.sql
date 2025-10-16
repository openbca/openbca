MODEL(
    name measure.measure_commodity,
    kind VIEW,
);
SELECT
    m.measure_id,
    k.commodity AS commodity,
    m.avoided_cost_subset,
    load_shape_mapping_by_commodity[k.commodity] as load_shape_mapping,
    energy_savings_by_commodity[k.commodity] as energy_savings,
    m.unit_quantity * m.net_to_gross_ratio * energy_savings as net_energy_savings,
FROM openbca_core.measures m
CROSS JOIN UNNEST(map_keys(m.energy_savings_by_commodity)) AS k(commodity)

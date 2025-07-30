MODEL(
    name measure.measure_commodity,
    kind VIEW,
    grain (measure_id, commodity),
);

WITH
latest_avoided_cost_version AS (
    SELECT
        commodity, avoided_cost_subset,
        MAX(avoided_cost_version) AS latest_avoided_cost_version
    FROM openbca_core.all_avoided_costs_ts
    GROUP BY commodity, avoided_cost_subset
),
pivoted_measure_commodity AS (
    SELECT
        measure_id,
        'ELECTRICITY' as commodity,
        avoided_cost_version,
        avoided_cost_subset,
        upper(elec_load_shape_mapping) as load_shape_mapping,
        elec_savings_mwh as energy_savings,
        unit_quantity * net_to_gross_ratio * elec_savings_mwh as net_energy_savings,
    FROM openbca_core.measures m
    UNION ALL
    SELECT
        measure_id,
        'GAS' as commodity,
        avoided_cost_version,
        avoided_cost_subset,
        upper(gas_load_shape_mapping) as load_shape_mapping,
        gas_saving_therms as energy_savings,
        unit_quantity * net_to_gross_ratio * gas_saving_therms as net_energy_savings,
    FROM openbca_core.measures
)
SELECT
    measure_id,
    pmc.commodity,
    COALESCE(pmc.avoided_cost_version, v.latest_avoided_cost_version) AS avoided_cost_version,
    pmc.avoided_cost_subset,
    load_shape_mapping,
    energy_savings,
    net_energy_savings
FROM pivoted_measure_commodity pmc
JOIN latest_avoided_cost_version v ON pmc.avoided_cost_subset = v.avoided_cost_subset AND pmc.commodity = v.commodity

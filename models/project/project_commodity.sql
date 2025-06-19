MODEL(
    name openbca_project.project_commodity,
    kind VIEW,
    grain (project_id, commodity),
);

WITH
latest_avoided_cost_version AS (
    SELECT * FROM (
	    SELECT DISTINCT commodity, avoided_cost_version,
	    FROM openbca_reference.avoided_costs_ts
    )
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY commodity ORDER BY avoided_cost_version DESC
    ) = 1
),
project_elec AS (
    SELECT
        project_id,
        'ELECTRICITY' as commodity,
        avoided_cost_subset,
        upper(load_shape) as load_shape,
        mwh_savings as energy_savings,
        units * ntg * mwh_savings as net_energy_savings,
    FROM openbca_input.projects
),
project_gas AS (
    SELECT
        project_id,
        'GAS' as commodity,
        avoided_cost_subset,
        upper(therms_profile) as load_shape,
        therms_savings as energy_savings,
        units * ntg * therms_savings as net_energy_savings,
    FROM openbca_input.projects
)
SELECT
    pc.project_id, pc.commodity, pc.avoided_cost_subset,
    acv.avoided_cost_version,
    pc.load_shape, pc.energy_savings, pc.net_energy_savings
FROM (
    SELECT * FROM project_elec
    UNION ALL
    SELECT * FROM project_gas
) pc
LEFT JOIN latest_avoided_cost_version acv
    ON pc.commodity = acv.commodity

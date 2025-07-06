MODEL(
    name project.project_commodity,
    kind VIEW,
    grain (project_id, commodity),
);
SELECT
    project_id,
    'ELECTRICITY' as commodity,
    avoided_cost_subset,
    upper(load_shape) as load_shape,
    mwh_savings as energy_savings,
    units * ntg * mwh_savings as net_energy_savings,
FROM openbca_core.projects
UNION ALL
SELECT
    project_id,
    'GAS' as commodity,
    avoided_cost_subset,
    upper(therms_profile) as load_shape,
    therms_savings as energy_savings,
    units * ntg * therms_savings as net_energy_savings,
FROM openbca_core.projects

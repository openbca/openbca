MODEL(
    name project.project_commodity,
    kind VIEW,
    grain (project_id, commodity),
);
SELECT
    project_id,
    'ELECTRICITY' as commodity,
    utility, region,
    load_shape,
    mwh_savings as energy_savings,
    units * ntg * mwh_savings as net_energy_savings,
FROM openbca_input.projects
UNION ALL
SELECT
    project_id,
    'GAS' as commodity,
    utility, region,
    therms_profile as load_shape,
    therms_savings as energy_savings,
    units * ntg * therms_savings as net_energy_savings,
FROM openbca_input.projects

MODEL(
    name project.project_commodity,
    kind FULL,
    grain (project_id),
);
SELECT
    project_id,
    utility, region,
    'ELECTRICITY' as commodity,
    load_shape,
FROM project.projects
UNION ALL
SELECT
    project_id,
    utility, region,
    'GAS' as commodity,
    therms_profile as load_shape,
FROM project.projects

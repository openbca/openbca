MODEL(
    name  project.project_commodity_avoided_costs,
    kind VIEW,
    grain (project_id, commodity, avoided_cost),
);

SELECT
    p.project_id,
    pc.commodity,
    p.avoided_cost_subset,
    unnest(COALESCE(p.avoided_costs, [NULL])) AS avoided_cost
FROM openbca_core.projects p
JOIN project.project_commodity pc ON p.project_id = pc.project_id

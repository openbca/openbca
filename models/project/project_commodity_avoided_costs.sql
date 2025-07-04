MODEL(
    name  project.project_commodity_avoided_costs,
    kind VIEW,
    grain (project_id, commodity, avoided_cost),
);

SELECT
    project_id,
    commodity,
    avoided_cost_subset,
    avoided_cost
FROM openbca_input.projects
CROSS JOIN avoided_costs AS ac(avoided_cost)

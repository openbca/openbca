MODEL(
    name project.project_costs,
    kind VIEW,
    grain (project_id),
);
SELECT
    project_id,
    avoided_cost_subset,
    start_year, start_quarter,
    discount_rate, eul,
    units, ntg,
    admin_cost + (((1 - ntg) * incentive_cost) + (ntg * measure_cost)) / (1 + (discount_rate / 4.0)) as trc_costs,
    admin_cost + (incentive_cost / (1 + (discount_rate / 4.0))) as pac_costs,
FROM
    openbca_input.projects

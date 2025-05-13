MODEL(
    name flexvalue.project_benefits,
    kind FULL,
    grain (project_id),
);
SELECT
    pc.project_id,
    peb.* EXCLUDE (project_id, marginal_cost),
    pgb.* EXCLUDE (project_id, marginal_cost),
    peb.marginal_cost as elec_marginal_cost,
    pgb.marginal_cost as gas_marginal_cost,
    (COALESCE(lifecycle_elec_ghg_savings, 0) + COALESCE(lifecycle_gas_ghg_savings, 0)) as lifecycle_total_ghg_savings,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) as total_benefits,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) / trc_costs as trc_ratio,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) / pac_costs as pac_ratio,
FROM flexvalue.project_costs pc
LEFT JOIN flexvalue.project_elec_benefits peb
    ON pc.project_id = peb.project_id
LEFT JOIN flexvalue.project_gas_benefits pgb
    ON pc.project_id = pgb.project_id

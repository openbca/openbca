MODEL(
    name openbca.project_impacts,
    kind VIEW,
    grain (project_id),
);
WITH pivoted_vsb(
    SELECT
        project_id,
        -- FIXME we need to exclude total
        -- FIXME we need to 2 types of costs: $ and marginal_ghg
        SUM(IF(cost_type = 'total' AND commodity = 'ELECTRICITY', impact_value)) AS electric_benefits,
        SUM(IF(cost_type = 'total' AND commodity = 'GAS', impact_value)) AS gas_benefits,
        SUM(IF(cost_type = 'marginal_ghg' AND commodity = 'ELECTRICITY', impact_value)) AS lifecycle_elec_ghg_savings,
        SUM(IF(cost_type = 'marginal_ghg' AND commodity = 'GAS', impact_value)) AS lifecycle_gas_ghg_savings,
    FROM openbca.project_commodity_impacts
    GROUP BY ALL
)
SELECT
    pc.project_id,
    vsb.* EXCLUDE (project_id),
    (COALESCE(lifecycle_elec_ghg_savings, 0) + COALESCE(lifecycle_gas_ghg_savings, 0)) as lifecycle_total_ghg_savings,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) as total_benefits,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) / trc_costs as trc_ratio,
    (COALESCE(electric_benefits, 0) + COALESCE(gas_benefits, 0)) / pac_costs as pac_ratio,
FROM project.project_costs pc
LEFT JOIN pivoted_vsb vsb
    ON pc.project_id = vsb.project_id

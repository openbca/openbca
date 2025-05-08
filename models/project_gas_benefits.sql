MODEL(
    name flexvalue.project_gas_benefits,
    kind FULL,
    grain (project_id),
);
SELECT
    bgbh.*,
    lifecycle_net_therms_savings / pc.eul as annual_net_therms_savings
FROM (
    SELECT
        project_id,
        SUM(gas_benefits) as gas_benefits,
        SUM(net_therms_savings) as lifecycle_net_therms_savings,
        SUM(marginal_ghg) as lifecycle_gas_ghg_savings,
        SUM(t_d) as t_d,
        SUM(environment) as environment,
        SUM(upstream_methane) as upstream_methane,
        SUM(btm_methane) as btm_methane,
        SUM(market) as market,
    FROM
        flexvalue.project_gas_benefits_monthly
    GROUP BY
        project_id
) bgbh
LEFT JOIN flexvalue.project_costs pc
    ON pc.project_id = bgbh.project_id

MODEL(
    name openbca.project_commodity_impacts,
    kind VIEW,
    grain (project_id, commodity),
);
SELECT
    vsb_ts.*,
    net_energy_savings / pc.eul as annual_net_mwh_savings
FROM (
    SELECT
        project_id, commodity, avoided_cost,
        SUM(av_cost_value) as av_cost_value,
        SUM(impact_value) as impact_value,
        SUM(net_energy_savings_ts) as net_energy_savings
    FROM
        openbca.project_commodity_impact_ts
    GROUP BY
        project_id, commodity, avoided_cost
) vsb_ts
LEFT JOIN project.project_costs pc
    ON pc.project_id = vsb_ts.project_id

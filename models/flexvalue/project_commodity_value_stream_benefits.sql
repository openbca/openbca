MODEL(
    name flexvalue.project_commodity_value_stream_benefits,
    kind FULL,
    grain (project_id, commodity),
);
SELECT
    vsb_ts.*,
    net_energy_savings / pc.eul as annual_net_mwh_savings
FROM (
    SELECT
        project_id, commodity, value_stream,
        SUM(value_stream_value) as value_stream_value,
        SUM(benefit_value) as benefit_value,
        SUM(net_energy_savings_ts) as net_energy_savings
    FROM
        flexvalue.project_commodity_value_stream_benefits_ts
    GROUP BY
        project_id, commodity, value_stream
) vsb_ts
LEFT JOIN project.project_costs pc
    ON pc.project_id = vsb_ts.project_id

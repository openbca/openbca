MODEL(
    name openbca_core.measure_commodity_economic_impacts,
    kind VIEW,
    grain (measure_id, commodity),
);
SELECT
    vsb_ts.*,
    net_energy_savings / pc.estimated_useful_life as annual_net_energy_savings
FROM (
    SELECT
        measure_id, commodity, avoided_cost,
        SUM(av_cost_dollar_per_energy_unit) as av_cost_dollar_per_energy_unit,
        SUM(impact_dollars) as impact_dollars,
        SUM(net_energy_savings_ts) as net_energy_savings
    FROM
        openbca_core.measure_commodity_economic_impact_ts
    GROUP BY
        measure_id, commodity, avoided_cost
) vsb_ts
LEFT JOIN measure.measure_costs pc
    ON pc.measure_id = vsb_ts.measure_id

MODEL(
    name flexvalue.project_elec_benefits,
    kind FULL,
    grain (project_id),
);
SELECT
    bebh.*,
    lifecycle_net_mwh_savings / pc.eul as annual_net_mwh_savings
FROM (
    SELECT
        project_id,
        SUM(electric_benefits) as electric_benefits,
        SUM(losses) as losses,
        SUM(marginal_ghg) as lifecycle_elec_ghg_savings,
        SUM(ghg_rebalancing) as ghg_rebalancing,
        SUM(distribution) as distribution,
        SUM(methane_leakage) as methane_leakage,
        SUM(ancillary_services) as ancillary_services,
        SUM(energy) as energy,
        SUM(capacity) as capacity,
        SUM(cap_and_trade) as cap_and_trade,
        SUM(transmission) as transmission,
        SUM(ghg_adder_rebalancing) as ghg_adder_rebalancing,
        SUM(ghg_adder) as ghg_adder,
        SUM(net_mwh_savings) as lifecycle_net_mwh_savings,
    FROM
        flexvalue.project_elec_benefits_hourly
    GROUP BY
        project_id
) bebh
LEFT JOIN flexvalue.project_costs pc
    ON pc.project_id = bebh.project_id


MODEL(
    name openbca_impact.project_commodity_environmental_impact_ts,
    kind VIEW,
    grain (project_id, commodity, avoided_cost, year, month, hour_of_year),
);

SELECT
    *,
    net_energy_savings_ts * av_cost_value AS impact_tons_co2e
 FROM openbca_impact.project_commodity_impact_ts
 WHERE avoided_cost = 'marginal_ghg'

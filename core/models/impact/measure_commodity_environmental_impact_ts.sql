MODEL(
    name openbca_core.measure_commodity_environmental_impact_ts,
    kind VIEW,
    grain (measure_id, commodity, avoided_cost, year, month, hour_of_year),
);

SELECT
    *,
    net_energy_savings_ts * av_cost_dollar_per_energy_unit AS impact_tons_co2e
 FROM openbca_core.measure_commodity_impact_ts
 WHERE avoided_cost = 'marginal_ghg'

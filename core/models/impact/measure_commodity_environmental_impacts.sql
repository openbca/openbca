MODEL(
    name openbca_core.measure_commodity_environmental_impacts,
    kind VIEW,
    grain (measure_id, commodity),
);
SELECT
    measure_id, commodity,
    SUM(impact_tons_co2e) as impact_tons_co2e
FROM
    openbca_core.measure_commodity_environmental_impact_ts
GROUP BY
    measure_id, commodity

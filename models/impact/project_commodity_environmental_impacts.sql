MODEL(
    name openbca_impact.project_commodity_environmental_impacts,
    kind VIEW,
    grain (project_id, commodity),
);
SELECT
    project_id, commodity,
    SUM(av_cost_value) as av_cost_value,
    SUM(impact_tons_co2e) as impact_tons_co2e
FROM
    openbca_impact.project_commodity_environmental_impact_ts
GROUP BY
    project_id, commodity

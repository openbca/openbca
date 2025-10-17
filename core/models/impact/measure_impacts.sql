MODEL(
    name openbca_core.measure_impacts,
    kind VIEW,
    grain (measure_id),
);
WITH
economic_impacts AS (
    SELECT
        measure_id,
        SUM(impact_dollars) AS total_benefits
    FROM openbca_core.measure_commodity_economic_impacts
    GROUP BY measure_id
),
environmental_impacts AS (
    SELECT
        measure_id,
        SUM(impact_tons_co2e) AS total_ghg_benefits
    FROM openbca_core.measure_commodity_environmental_impacts
    GROUP BY measure_id
)
SELECT
    pc.measure_id,
    env.total_ghg_benefits,
    eco.total_benefits,
    SAFE_DIVIDE(eco.total_benefits, trc_cost_dollars)  as trc_ratio,
    SAFE_DIVIDE(eco.total_benefits, pac_cost_dollars) as pac_ratio
FROM measure.measure_costs pc
LEFT JOIN economic_impacts eco
    ON pc.measure_id = eco.measure_id
LEFT JOIN environmental_impacts env
    ON pc.measure_id = env.measure_id

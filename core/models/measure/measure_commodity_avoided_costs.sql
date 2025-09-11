MODEL(
    name  measure.measure_commodity_avoided_costs,
    kind VIEW,
    grain (measure_id, commodity, avoided_cost),
);

SELECT
    p.measure_id,
    pc.commodity,
    p.avoided_cost_subset,
    p.avoided_cost_version,
    unnest(COALESCE(p.avoided_costs, [NULL])) AS avoided_cost
FROM openbca_input.measures p
JOIN measure.measure_commodity pc ON p.measure_id = pc.measure_id

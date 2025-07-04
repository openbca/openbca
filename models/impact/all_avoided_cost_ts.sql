MODEL(
    name openbca_impact.all_avoided_costs_ts,
    kind VIEW,
    grain (utility, region, commodity, avoided_cost, year, hour_of_year),
);

SELECT * FROM openbca_reference.avoided_costs_ts
WHERE (commodity, avoided_cost) NOT IN (SELECT commodity, avoided_cost FROM openbca_input.input_avoided_costs_ts)
UNION ALL
SELECT * FROM openbca_input.input_avoided_costs_ts;

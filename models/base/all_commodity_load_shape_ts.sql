MODEL(
    name openbca_impact.all_commodity_load_shape_ts,
    kind VIEW,
    grain (commodity, load_shape, hour_of_year),
);

SELECT * FROM openbca_reference.commodity_load_shape_ts
WHERE (commodity, load_shape) NOT IN (SELECT commodity, load_shape FROM openbca_input.input_commodity_load_shape_ts)
UNION ALL
SELECT * FROM openbca_input.input_commodity_load_shape_ts

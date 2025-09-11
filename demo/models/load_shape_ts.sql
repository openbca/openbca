MODEL(
    name openbca_input.load_shape_ts,
    kind FULL,
    grain (commodity, load_shape, hour_of_year),
);
SELECT commodity, quarter, month, hour_of_day, hour_of_year, load_shape, load_shape_normalized_fraction
FROM openbca_reference.commodity_load_shape_ts
WHERE
    (load_shape) IN (
        SELECT elec_load_shape_mapping FROM openbca_input.measures
        UNION ALL
        SELECT gas_load_shape_mapping FROM openbca_input.measures
    )
    AND -- allow custom load shapes to override reference ones
    (commodity, load_shape) NOT IN (SELECT commodity, load_shape FROM demo.custom_load_shapes)
UNION ALL
SELECT commodity, quarter, month, hour_of_day, hour_of_year, load_shape, value AS load_shape_normalized_fraction
FROM demo.custom_load_shapes
WHERE
    (load_shape) IN (
        SELECT elec_load_shape_mapping FROM openbca_input.measures
        UNION ALL
        SELECT gas_load_shape_mapping FROM openbca_input.measures
    )


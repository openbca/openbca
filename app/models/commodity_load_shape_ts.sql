MODEL(
  name openbca_input.load_shape_ts,
  kind VIEW,
);
SELECT
    commodity, quarter,
    month, hour_of_day, hour_of_year,
    load_shape, load_shape_normalized_fraction
FROM openbca_reference.commodity_load_shape_ts

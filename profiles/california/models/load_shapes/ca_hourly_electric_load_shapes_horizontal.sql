MODEL (
  name california.ca_hourly_electric_load_shapes_horizontal,
  kind FULL,
  grain (utility, hour_of_year),
);
SELECT *
FROM read_csv_auto('profiles/california/test_data/test_real_data_calculations_aggregated/ca_hourly_electric_load_shapes_horizontal_copy.csv')

MODEL (
  name michigan.ca_hourly_electric_load_shapes_horizontal,
  kind FULL,
  grain (utility, hour_of_year),
);
SELECT *
FROM read_csv_auto('states/california/test_data/test_real_data_calculations_aggregated/ca_hourly_electric_load_shapes_horizontal_copy.csv')

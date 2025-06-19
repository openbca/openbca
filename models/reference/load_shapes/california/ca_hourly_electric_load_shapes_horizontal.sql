MODEL (
  name california.ca_hourly_electric_load_shapes_horizontal,
  kind VIEW,
  grain (utility, hour_of_year),
);
SELECT *
FROM read_csv_auto('models/reference/load_shapes/california/data/ca_hourly_electric_load_shapes_horizontal_copy.csv')

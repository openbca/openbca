MODEL (
  name california.therms_profile,
  kind FULL,
  grain (utility, quarter, month),
);
SELECT *
FROM read_csv_auto('reference/models/load_shapes/california/ca_monthly_therms_load_profiles_copy.csv')

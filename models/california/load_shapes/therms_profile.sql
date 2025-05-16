MODEL (
  name california.therms_profile,
  kind FULL,
  grain (state, utility, quarter, month),
);
SELECT *
FROM read_csv_auto('test_data/test_real_data_calculations_aggregated/ca_monthly_therms_load_profiles_copy.csv')

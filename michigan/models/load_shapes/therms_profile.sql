MODEL (
  name michigan.therms_profile,
  kind FULL,
  grain (utility, quarter, month),
);
SELECT *
FROM read_csv_auto('california/test_data/test_real_data_calculations_aggregated/ca_monthly_therms_load_profiles_copy.csv')

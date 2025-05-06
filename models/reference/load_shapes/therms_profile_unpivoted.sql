MODEL (
  name flexvalue_reference.therms_profile_unpivoted,
  kind FULL,
  grain (state, utility, quarter, month, therms_profile),
);
WITH therms_profile AS (
    SELECT * FROM read_csv_auto('test_data/test_real_data_calculations_aggregated/ca_monthly_therms_load_profiles_copy.csv')
)
-- Unpivoting therms profile data
SELECT state, utility, quarter, month, 'summer' AS therms_profile, summer AS value FROM therms_profile
UNION ALL
SELECT state, utility, quarter, month, 'annual' AS therms_profile, annual AS value FROM therms_profile
UNION ALL
SELECT state, utility, quarter, month, 'winter' AS therms_profile, winter AS value FROM therms_profile

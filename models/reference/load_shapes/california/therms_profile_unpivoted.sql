MODEL (
  name california.therms_profile_unpivoted,
  kind VIEW,
  grain (utility, quarter, month, therms_profile),
);
WITH therms_profile AS (
    SELECT * FROM california.therms_profile
)
-- Unpivoting therms profile data
SELECT utility, quarter, month, 'summer' AS therms_profile, summer AS saved_therm FROM therms_profile
UNION ALL
SELECT utility, quarter, month, 'annual' AS therms_profile, annual AS saved_therm FROM therms_profile
UNION ALL
SELECT utility, quarter, month, 'winter' AS therms_profile, winter AS saved_therm FROM therms_profile

MODEL (
  name michigan.therms_profile_unpivoted,
  kind FULL,
  grain (utility, quarter, month, therms_profile),
);
WITH therms_profile AS (
    SELECT * FROM michigan.therms_profile
)
-- Unpivoting therms profile data
SELECT utility, quarter, month, 'summer' AS therms_profile, summer AS value FROM therms_profile
UNION ALL
SELECT utility, quarter, month, 'annual' AS therms_profile, annual AS value FROM therms_profile
UNION ALL
SELECT utility, quarter, month, 'winter' AS therms_profile, winter AS value FROM therms_profile

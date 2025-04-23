MODEL (
  name flexvalue.therms_profile_pivoted,
  kind FULL,
  grain (state, utility, quarter, month, therms_profile),
);

SELECT state, utility, quarter, month, 'summer' AS therms_profile, summer AS value FROM flexvalue.therms_profile
UNION ALL
SELECT state, utility, quarter, month, 'annual' AS therms_profile, annual AS value FROM flexvalue.therms_profile
UNION ALL
SELECT state, utility, quarter, month, 'winter' AS therms_profile, winter AS value FROM flexvalue.therms_profile

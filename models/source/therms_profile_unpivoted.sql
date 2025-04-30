MODEL (
  name flexvalue.therms_profile_unpivoted,
  kind FULL,
  grain (state, utility, quarter, month, therms_profile),
);
-- Unpivoting therms profile data
SELECT state, utility, quarter, month, 'summer' AS therms_profile, summer AS value FROM flexvalue_input.therms_profile
UNION ALL
SELECT state, utility, quarter, month, 'annual' AS therms_profile, annual AS value FROM flexvalue_input.therms_profile
UNION ALL
SELECT state, utility, quarter, month, 'winter' AS therms_profile, winter AS value FROM flexvalue_input.therms_profile

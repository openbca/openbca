AUDIT (
  name commodity_time_granularity_audit,
);

WITH
hourly_load_shape_commodity AS (
	SELECT distinct commodity
	FROM openbca_core.all_commodity_load_shape_ts
	WHERE hour_of_year IS NOT NULL OR hour_of_day IS NOT NULL
),
hourly_avoided_cost_commodity AS (
    SELECT distinct commodity
    FROM openbca_core.all_avoided_costs_ts
    WHERE hour_of_year IS NOT NULL OR hour_of_day IS NOT NULL
)
-- if we don't have hourly load shapes we can't have hourly avoided costs
SELECT *
FROM hourly_load_shape_commodity
FULL OUTER JOIN hourly_avoided_cost_commodity USING (commodity)
WHERE hourly_load_shape_commodity.commodity IS NULL AND hourly_avoided_cost_commodity.commodity IS NOT NULL

MODEL(
  name openbca_input.avoided_costs_ts,
  kind VIEW,
);

CREATE SCHEMA IF NOT EXISTS openbca_app;

DROP TABLE IF EXISTS openbca_app.avoided_costs_ts;
CREATE TABLE openbca_app.avoided_costs_ts (
    avoided_cost_subset STRING,
    commodity STRING,
    year INT,
    quarter INT,
    month INT,
    hour_of_year INT,
    hour_of_day INT,
    avoided_cost STRING,
    av_cost_dollar_per_energy_unit FLOAT
);

SELECT
    'app_avoided_cost_version' AS avoided_cost_version,
    *
FROM openbca_app.avoided_costs_ts

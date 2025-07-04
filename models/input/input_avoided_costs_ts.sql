MODEL(
  name openbca_input.input_avoided_costs_ts,
  kind VIEW,
);

CREATE SCHEMA IF NOT EXISTS openbca_user_input;

DROP TABLE IF EXISTS openbca_user_input.user_avoided_costs_ts;
CREATE TABLE openbca_user_input.user_avoided_costs_ts (
    avoided_cost_subset STRING,
    commodity STRING,
    year INT,
    quarter INT,
    month INT,
    hour_of_year INT,
    hour_of_day INT,
    avoided_cost STRING,
    value FLOAT
);

SELECT * FROM openbca_user_input.user_avoided_costs_ts

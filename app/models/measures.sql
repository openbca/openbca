MODEL(
  name openbca_input.measures,
  kind VIEW,
);

CREATE SCHEMA IF NOT EXISTS openbca_app;

DROP TABLE IF EXISTS openbca_app.measures;
CREATE TABLE openbca_app.measures (
    measure_id STRING PRIMARY KEY,
    elec_load_shape_mapping STRING,
    start_year INT,
    start_quarter INT,
    avoided_cost_subset STRING,
    unit_quantity FLOAT,
    estimated_useful_life INT,
    net_to_gross_ratio FLOAT,
    discount_rate_ratio FLOAT,
    admin_cost_dollars_dollars FLOAT,
    measure_cost_dollars FLOAT,
    incentive_cost_dollars FLOAT,
    gas_load_shape_mapping STRING,
    gas_saving_therms FLOAT,
    elec_savings_mwh FLOAT,
    avoided_costs STRING
);

SELECT
    * EXCEPT avoided_costs,
    SPLIT(avoided_costs, ',') AS avoided_costs
FROM openbca_app.measures

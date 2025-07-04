MODEL(
  name openbca_input.projects,
  kind VIEW,
);

CREATE SCHEMA IF NOT EXISTS openbca_user_input;

CREATE TABLE IF NOT EXISTS openbca_user_input.user_projects (
    project_id STRING PRIMARY KEY,
    load_shape STRING,
    start_year INT,
    start_quarter INT,
    avoided_cost_subset STRING,
    units FLOAT,
    eul INT,
    ntg FLOAT,
    discount_rate FLOAT,
    admin_cost FLOAT,
    measure_cost FLOAT,
    incentive_cost FLOAT,
    therms_profile STRING,
    therms_savings FLOAT,
    mwh_savings FLOAT,
    avoided_costs STRING
);

SELECT
    * EXCEPT avoided_costs,
    SPLIT(avoided_costs) AS avoided_costs
FROM openbca_user_input.user_projects;

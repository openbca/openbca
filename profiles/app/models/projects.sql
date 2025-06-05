MODEL(
  name openbca_input.projects,
  kind VIEW,
);

CREATE SCHEMA IF NOT EXISTS app_tmp;

-- empty table to be re-created as temp table and populated by the OpenBCA app at runtime

CREATE TABLE IF NOT EXISTS app_tmp.empty_projects (
    project_id STRING PRIMARY KEY,
    utility STRING,
    region STRING,
    start_year INT,
    start_quarter INT,
    discount_rate FLOAT,
    eul INT,
    units FLOAT,
    ntg FLOAT,
    admin_cost FLOAT,
    incentive_cost FLOAT,
    measure_cost FLOAT,
    mwh_savings FLOAT,
    therms_savings FLOAT,
    load_shape STRING,
    therms_profile STRING
);

CREATE VIEW IF NOT EXISTS app_tmp.view_projects AS SELECT * FROM app_tmp.empty_projects;

SELECT * FROM app_tmp.view_projects

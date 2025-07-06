MODEL(
  name openbca_input.load_shape_ts,
  kind VIEW,
);

CREATE SCHEMA IF NOT EXISTS openbca_app;

DROP TABLE IF EXISTS openbca_app.load_shape_ts;
CREATE TABLE openbca_app.load_shape_ts (
    commodity STRING,
    quarter INT,
    month INT,
    hour_of_year INT,
    hour_of_day INT,
    load_shape STRING,
    value FLOAT
);

SELECT * FROM openbca_app.load_shape_ts

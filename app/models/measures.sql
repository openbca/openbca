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
    admin_cost_dollars FLOAT,
    measure_cost_dollars FLOAT,
    incentive_cost_dollars FLOAT,
    gas_load_shape_mapping STRING,
    gas_saving_therms FLOAT,
    elec_savings_mwh FLOAT,
    avoided_costs STRING
);

-- Expose app input in the shape expected by core: include per-commodity maps and avoided_costs as array
SELECT
    measure_id,
    avoided_cost_subset,
    start_year,
    start_quarter,
    discount_rate_ratio,
    estimated_useful_life,
    unit_quantity,
    net_to_gross_ratio,
    admin_cost_dollars,
    incentive_cost_dollars,
    measure_cost_dollars,
    -- Build maps keyed by commodity so core can look up the right commodity
    map(['ELECTRICITY', 'GAS'], [elec_savings_mwh, gas_saving_therms]) AS energy_savings_by_commodity,
    map(['ELECTRICITY', 'GAS'], [elec_load_shape_mapping, gas_load_shape_mapping]) AS load_shape_mapping_by_commodity,
    SPLIT(avoided_costs, ',') AS avoided_costs
FROM openbca_app.measures

MODEL(
  name openbca_input.measures,
  kind SEED (
    path '$root/data/measures.csv'
  ),
  columns (
    measure_id VARCHAR,
    avoided_cost_subset VARCHAR,
    start_year INT,
    start_quarter INT,
    discount_rate_ratio FLOAT,
    estimated_useful_life INT,
    unit_quantity FLOAT,
    net_to_gross_ratio FLOAT,
    admin_cost_dollars FLOAT,
    incentive_cost_dollars FLOAT,
    measure_cost_dollars FLOAT,
    elec_savings_mwh FLOAT,
    gas_saving_therms FLOAT,
    elec_load_shape_mapping VARCHAR,
    gas_load_shape_mapping VARCHAR,
    avoided_costs ARRAY<VARCHAR>,
    avoided_cost_version VARCHAR
  )
)

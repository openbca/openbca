MODEL(
  name openbca_input.projects,
  kind SEED (
    path '$root/data/projects.csv'
  ),
  columns (
    project_id VARCHAR,
    avoided_cost_subset VARCHAR,
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
    load_shape VARCHAR,
    therms_profile VARCHAR,
    avoided_costs ARRAY<VARCHAR>
  )
)

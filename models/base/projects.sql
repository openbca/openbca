MODEL(
  name openbca_impact.projects,
  kind VIEW,
);

SELECT
    project_id::VARCHAR AS project_id,
    avoided_cost_subset::VARCHAR AS avoided_cost_subset,
    start_year::INT AS start_year,
    start_quarter::INT AS start_quarter,
    discount_rate::FLOAT AS discount_rate,
    eul::INT AS eul,
    units::FLOAT AS units,
    ntg::FLOAT AS ntg,
    admin_cost::FLOAT AS admin_cost,
    incentive_cost::FLOAT AS incentive_cost,
    measure_cost::FLOAT AS measure_cost,
    mwh_savings::FLOAT AS mwh_savings,
    therms_savings::FLOAT AS therms_savings,
    load_shape::VARCHAR AS load_shape,
    therms_profile::VARCHAR AS therms_profile,
    avoided_costs::ARRAY<VARCHAR> AS avoided_costs
FROM openbca_input.projects

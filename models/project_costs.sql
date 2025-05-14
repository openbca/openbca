MODEL(
    name flexvalue.project_costs,
    kind FULL,
    grain (project_id),
);
SELECT
    project_id,
    utility, region,
    start_year, start_quarter,
    discount_rate, eul,
    load_shape, therms_profile,
    units, ntg, mwh_savings,
    admin_cost + (((1 - ntg) * incentive_cost) + (ntg * measure_cost)) / (1 + (discount_rate / 4.0)) as trc_costs,
    admin_cost + (incentive_cost / (1 + (discount_rate / 4.0))) as pac_costs,
    units * ntg * mwh_savings as gross_adjusted_savings,
FROM
    flexvalue_input.projects project_info

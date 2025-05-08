MODEL(
    name flexvalue.project_costs,
    kind FULL,
    grain (project_id),
);
SELECT *,
    project_start_quarter + eul * INTERVAL '1 year' AS project_end_quarter
FROM (
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
        make_timestamp(start_year, (start_quarter - 1) * 3 + 1, 1, 0, 0, 0) as project_start_quarter,
    FROM
        flexvalue_input.projects project_info
)

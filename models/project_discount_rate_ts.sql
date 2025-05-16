MODEL(
    name  flexvalue.project_discount_rate_ts,
    kind FULL,
    grain (project_id, year, quarter),
);

SELECT
    project_id,
    state, utility, region,
    ((quarter_index - quarter_index%4) / 4)::int AS year,
    (quarter_index%4 + 1) AS quarter,
    gross_adjusted_savings,
    1.0 / POW(
        1.0 + (discount_rate / 4.0),
        ((year - start_year) * 4) + quarter - start_quarter
    ) AS discount
FROM flexvalue.project_costs
CROSS JOIN generate_series(start_year * 4 + (start_quarter - 1), (start_year + eul) * 4 + (start_quarter - 1 - 1)) AS gs(quarter_index)

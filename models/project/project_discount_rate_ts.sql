MODEL(
    name  project.project_discount_rate_ts,
    kind VIEW,
    grain (project_id, year, quarter),
);

SELECT
    project_id,
    avoided_cost_subset,
    ((quarter_index - quarter_index%4) / 4)::int AS year,
    (quarter_index % 4 + 1) AS quarter,
    1.0 / POW(
        1.0 + (discount_rate / 4.0),
        ((year - start_year) * 4) + quarter - start_quarter
    ) AS discount
FROM project.project_costs
CROSS JOIN generate_series(start_year * 4 + (start_quarter - 1), (start_year + eul) * 4 + (start_quarter - 1 - 1)) AS gs(quarter_index)

MODEL(
    name flexvalue.project_value_stream_benefits_ts,
    kind FULL,
    grain (project_id, year, month, hour_of_year)
);

WITH
project_commodity AS (
    SELECT
        project_id, utility, region,state,
        start_year, start_quarter,
        eul, discount_rate,
        unnest([
            {'commodity': 'ELECTRICITY', 'load_shape': load_shape},
            {'commodity': 'GAS', 'load_shape': therms_profile}
        ], recursive := true)
    FROM flexvalue.project_costs
),
project_vs_ts AS (
    SELECT
        pc.project_id, pc.load_shape, vsts.*,
        1.0 / POW(
            1.0 + (pc.discount_rate / 4.0),
            ((vsts.year - pc.start_year) * 4) + vsts.quarter - pc.start_quarter
        ) AS discount
    FROM flexvalue.value_stream_ts vsts
    JOIN project_commodity pc
        ON vsts.utility = pc.utility AND vsts.region = pc.region AND vsts.commodity = pc.commodity
        AND (
            (vsts.year > pc.start_year OR (vsts.year = pc.start_year AND vsts.quarter >= pc.start_quarter))
            AND
            (vsts.year < pc.start_year + pc.eul OR (vsts.year = pc.start_year + pc.eul AND vsts.quarter < pc.start_quarter))
        )
),
project_vs_cst AS (
    SELECT
        project_vs_ts.project_id, project_vs_ts.load_shape,
    FROM
        project_vs_ts
    JOIN flexvalue.value_stream_cst vs_cst
    ON project_vs_ts.utility = vs_cst.utility
        AND project_vs_ts.region = vs_cst.region
        AND project_vs_ts.commodity = vs_cst.commodity

),
all_vs_ts AS (
    SELECT
),
vs_ts_with_load_shape AS (
    SELECT
        vsts.*,
        COALESCE(els_hourly.value, els_monthly.value) AS load_shape_value,
    FROM project_vs_ts vsts
    LEFT JOIN flexvalue.commodity_load_shape_hourly els_hourly
        ON vsts.state = els_hourly.state AND vsts.commodity = els_hourly.commodity
            AND vsts.load_shape = els_hourly.load_shape AND vsts.utility = els_hourly.utility
            AND vsts.hour_of_year = els_hourly.hour_of_year
    LEFT JOIN flexvalue.commodity_load_shape_monthly els_monthly
        ON vsts.state = els_monthly.state AND vsts.commodity = els_monthly.commodity
            AND vsts.load_shape = els_monthly.load_shape AND vsts.utility = els_monthly.utility
            AND vsts.month = els_monthly.month
)
SELECT
    vsts.project_id, vsts.commodity, vsts.value_stream,
    vsts.year, vsts.hour_of_year,
    vsts.discount,
    CASE WHEN vsts.value_stream = 'marginal_ghg' THEN
        pc.gross_adjusted_savings * vsts.load_shape_value * value
    ELSE
        pc.gross_adjusted_savings * vsts.load_shape_value * vsts.discount * value
    END AS value,
    pc.gross_adjusted_savings * vsts.load_shape_value AS net_energy_savings,
FROM vs_ts_with_load_shape vsts
LEFT JOIN flexvalue.project_costs pc
    ON vsts.project_id = pc.project_id

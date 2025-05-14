MODEL(
    name flexvalue.project_value_stream_benefits_ts,
    kind FULL,
    grain (project_id, year, month, hour_of_year)
);
WITH
project_commodity AS (
    SELECT
        project_id,
        utility, region,state,
        start_year, start_quarter,
        eul, discount_rate,
        unnest([
            {'commodity': 'ELECTRICITY', 'load_shape': load_shape},
            {'commodity': 'GAS', 'load_shape': therms_profile}
        ], recursive := true)
    FROM flexvalue.project_costs
),
project_elec_hourly AS (
    SELECT
        pc.project_id,
        vsts.*,
        1.0 / POW(
            1.0 + (pc.discount_rate / 4.0),
            ((vsts.year - pc.start_year) * 4) + vsts.quarter - pc.start_quarter
        ) AS discount,
        COALESCE(els_hourly.value, els_monthly.value) AS load_shape_value,
    FROM project_commodity pc
    JOIN flexvalue.value_stream_ts vsts
        ON vsts.utility = pc.utility
            AND vsts.region = pc.region
            AND vsts.commodity = pc.commodity
            AND (
                (vsts.year > pc.start_year OR (vsts.year = pc.start_year AND vsts.quarter >= pc.start_quarter))
                AND
                (vsts.year < pc.start_year + pc.eul OR (vsts.year = pc.start_year + pc.eul AND vsts.quarter < pc.start_quarter))
            )
    LEFT JOIN flexvalue.commodity_load_shape_hourly els_hourly
        ON pc.state = els_hourly.state
            AND pc.commodity = els_hourly.commodity
            AND pc.load_shape = els_hourly.load_shape
            AND pc.utility = els_hourly.utility
            AND vsts.hour_of_year = els_hourly.hour_of_year
    LEFT JOIN flexvalue.commodity_load_shape_monthly els_monthly
        ON pc.state = els_monthly.state
            AND pc.commodity = els_monthly.commodity
            AND pc.load_shape = els_monthly.load_shape
            AND pc.utility = els_monthly.utility
            AND vsts.month = els_monthly.month
)
SELECT
    peh.project_id, peh.commodity, peh.value_stream,
    peh.year, peh.hour_of_year,
    peh.discount,
    CASE WHEN value_stream = 'marginal_ghg' THEN
        pc.gross_adjusted_savings * peh.load_shape_value * value
    ELSE
        pc.gross_adjusted_savings * peh.load_shape_value * peh.discount * value
    END AS value,
    pc.gross_adjusted_savings * peh.load_shape_value AS net_energy_savings,
FROM project_elec_hourly peh
LEFT JOIN flexvalue.project_costs pc
    ON peh.project_id = pc.project_id

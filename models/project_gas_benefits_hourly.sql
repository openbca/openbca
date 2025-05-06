MODEL (
    name flexvalue.project_gas_benefits_hourly,
    kind FULL,
    grain (project_id, year,  hour_of_year),
);
-- , project_costs_with_discounted_gas_av AS (
--     SELECT
--         project_costs.*
--         , gas_av_costs.year
--         , gas_av_costs.month
--         , gas_av_costs.quarter
--         , gas_av_costs.total, gas_av_costs.market, gas_av_costs.t_d
--         , gas_av_costs.environment, gas_av_costs.btm_methane, gas_av_costs.upstream_methane, gas_av_costs.marginal_ghg
--         , 1.0 / POW(1.0 + (project_costs.discount_rate / 4.0), ((gas_av_costs.year - project_costs.start_year) * 4) + gas_av_costs.quarter - project_costs.start_quarter) AS discount
--         , gas_av_costs.datetime
--     FROM project_costs
--     JOIN
--       flexvalue_reference.gas_av_costs_lol gas_av_costs
--         ON gas_av_costs.utility = project_costs.utility
--             AND gas_av_costs.datetime >= project_start_quarter
--             AND gas_av_costs.datetime < project_end_quarter
--             ),
-- gas_calculations AS (
--     SELECT pcwdga.project_id
--     , tpp.therms_profile
--     , MAX(pcwdga.trc_costs) as trc_costs
--     , MAX(pcwdga.pac_costs) as pac_costs
--     , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.total) as gas_benefits
--     , SUM((pcwdga.units * pcwdga.therms_savings * pcwdga.ntg * tpp.value) / CAST(pcwdga.eul AS FLOAT) ) as annual_net_therms_savings
--     , SUM(pcwdga.units * pcwdga.therms_savings * pcwdga.ntg * tpp.value) as lifecycle_net_therms_savings
--     , SUM(pcwdga.units * pcwdga.therms_savings * pcwdga.ntg * tpp.value * pcwdga.marginal_ghg) as lifecycle_gas_ghg_savings
--     , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.t_d) as t_d
--     , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.environment) as environment
--     , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.upstream_methane) as upstream_methane
--     , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.btm_methane) as btm_methane
--     , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.market) as market
--     , pcwdga.datetime
--     FROM project_costs_with_discounted_gas_av pcwdga
--     JOIN flexvalue_reference.therms_profile_unpivoted tpp
--         ON UPPER(pcwdga.therms_profile) = UPPER(tpp.therms_profile)
--             AND tpp.utility = pcwdga.utility
--             AND tpp.month = pcwdga.month
--     GROUP BY pcwdga.project_id, pcwdga.eul, pcwdga.datetime, tpp.therms_profile
--     )
WITH
project_gas_hourly AS (      
    SELECT
        pc.project_id,
        gac.*,
        1.0 / POW(
            1.0 + (pc.discount_rate / 4.0),
            ((gac.year - pc.start_year) * 4) + gac.quarter - pc.start_quarter
        ) AS discount,
        tpp.value as therms_profile_value
    FROM
        flexvalue.project_costs pc
    JOIN
      flexvalue_reference.gas_av_costs gac
        ON gac.utility = pc.utility
            AND gac.datetime >= pc.project_start_quarter
            AND gac.datetime < pc.project_end_quarter
    JOIN flexvalue_reference.therms_profile_unpivoted tpp
        ON pc.therms_profile = tpp.therms_profile
            AND pc.utility = tpp.utility
            AND gac.month = tpp.month
)
SELECT
    pgh.project_id,
    pgh.year, pgh.hour_of_year,
    pgh.discount,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.total AS gas_benefits,
    pc.gross_adjusted_savings * pgh.therms_profile_value AS net_therms_savings,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.t_d AS t_d,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.environment AS environment,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.upstream_methane AS upstream_methane,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.btm_methane AS btm_methane,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.market AS market,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.marginal_ghg as marginal_ghg
FROM project_gas_hourly pgh
LEFT JOIN flexvalue.project_costs pc
    ON pgh.project_id = pc.project_id

MODEL (
    name flexvalue.project_gas_benefits_monthly,
    kind FULL,
    grain (project_id, year,  month),
);
WITH
project_gas_monthly AS (
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
    pgh.year, pgh.month,
    pgh.discount,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.total AS gas_benefits,
    pc.gross_adjusted_savings * pgh.therms_profile_value AS net_therms_savings,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.t_d AS t_d,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.environment AS environment,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.upstream_methane AS upstream_methane,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.btm_methane AS btm_methane,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * pgh.market AS market,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.discount * emc.marginal_cost as marginal_cost,
    pc.gross_adjusted_savings * pgh.therms_profile_value * pgh.marginal_ghg as marginal_ghg
FROM project_gas_monthly pgh
LEFT JOIN flexvalue.project_costs pc
    ON pgh.project_id = pc.project_id
LEFT JOIN flexvalue.elec_marginal_cost emc
    ON pgh.utility = emc.utility AND pgh.region = emc.region

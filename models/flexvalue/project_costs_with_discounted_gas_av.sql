MODEL (
    name flexvalue.project_costs_with_discounted_gas_av,
    kind FULL,
    grains (project_id, utility, region, datetime),
);
      
SELECT
    project_id,
    project_costs.utility, project_costs.region,
    discount_rate, eul, units, ntg,
    therms_savings, therms_profile,
    project_costs.trc_costs, project_costs.pac_costs
    , gas_av_costs.year
    , gas_av_costs.month
    , gas_av_costs.quarter
    , gas_av_costs.total
    , gas_av_costs.marginal_ghg
    , 1.0 / POW(1.0 + (project_costs.discount_rate / 4.0), ((gas_av_costs.year - project_costs.start_year) * 4) + gas_av_costs.quarter - project_costs.start_quarter) AS discount
    , gas_av_costs.datetime
FROM flexvalue.gas_av_costs
JOIN flexvalue.project_costs
    ON gas_av_costs.utility = project_costs.utility
        AND gas_av_costs.datetime >= project_start_quater
        AND gas_av_costs.datetime < project_start_quater + INTERVAL (project_costs.eul) YEAR

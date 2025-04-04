MODEL (
    name flexvalue.project_costs_with_discounted_elec_av,
    kind FULL,
    grains (project_id, utility, region, datetime),
);

SELECT
    project_id,
    project_costs.utility, project_costs.region,
    discount_rate, eul, units, ntg,
    mwh_savings, load_shape,
    project_costs.trc_costs, project_costs.pac_costs,
    elec_av_costs.hour_of_year,
    elec_av_costs.datetime,
    elec_av_costs.total,
    elec_av_costs.marginal_ghg,
    1.0 / POW(1.0 + (project_costs.discount_rate / 4.0), ((elec_av_costs.year - project_costs.start_year) * 4) + elec_av_costs.quarter - project_costs.start_quarter) AS discount
FROM flexvalue.elec_av_costs
JOIN flexvalue.project_costs
    ON elec_av_costs.utility = project_costs.utility AND elec_av_costs.region = project_costs.region
        AND elec_av_costs.datetime >= project_start_quater AND elec_av_costs.datetime < project_start_quater + INTERVAL (project_costs.eul) YEAR

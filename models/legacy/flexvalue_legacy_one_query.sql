MODEL (
  name flexvalue.flexvalue_legacy_one_query,
  kind FULL,
  grain id,
);

WITH project_costs AS (
    SELECT
        project_info.*,
        project_info.admin_cost + (((1 - project_info.ntg) * project_info.incentive_cost) + (project_info.ntg * project_info.measure_cost)) / (1 + (project_info.discount_rate / 4.0)) as trc_costs,
        project_info.admin_cost + (project_info.incentive_cost / (1 + (project_info.discount_rate / 4.0))) as pac_costs
    FROM
    flexvalue.project_info project_info
),
project_costs_with_discounted_elec_av AS (
    SELECT
        project_costs.*,
        elec_av_costs.hour_of_year,
        elec_av_costs.year,
        elec_av_costs.month,
        elec_av_costs.hour_of_day,
        elec_av_costs.datetime,
        elec_av_costs.quarter,
        elec_av_costs.energy, elec_av_costs.losses, elec_av_costs.ancillary_services,
        elec_av_costs.capacity, elec_av_costs.transmission, elec_av_costs.distribution,
        elec_av_costs.cap_and_trade, elec_av_costs.ghg_adder, elec_av_costs.ghg_rebalancing,
        elec_av_costs.methane_leakage, elec_av_costs.total, elec_av_costs.marginal_ghg,
        elec_av_costs.ghg_adder_rebalancing,
        1.0 / POW(1.0 + (project_costs.discount_rate / 4.0), ((elec_av_costs.year - project_costs.start_year) * 4) + elec_av_costs.quarter - project_costs.start_quarter) AS discount
    FROM project_costs
    JOIN
        flexvalue.elec_av_costs elec_av_costs
        ON elec_av_costs.utility = project_costs.utility
            AND elec_av_costs.region = project_costs.region
            AND elec_av_costs.datetime >= project_start_quarter
            AND elec_av_costs.datetime < project_end_quarter
            ),
elec_calculations AS (
    SELECT
    pcwdea.project_id
    , elec_load_shape.load_shape_name
    , pcwdea.datetime
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.total) AS electric_benefits
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.losses) AS losses
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.marginal_ghg) AS marginal_ghg
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.ghg_rebalancing) AS ghg_rebalancing
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.distribution) AS distribution
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.methane_leakage) AS methane_leakage
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.ancillary_services) AS ancillary_services
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.energy) AS energy
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.capacity) AS capacity
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.cap_and_trade) AS cap_and_trade
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.transmission) AS transmission
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.ghg_adder_rebalancing) AS ghg_adder_rebalancing
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.discount * pcwdea.ghg_adder) AS ghg_adder
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value) / CAST(pcwdea.eul AS FLOAT) as annual_net_mwh_savings
    , MAX(pcwdea.trc_costs) AS trc_costs
    , MAX(pcwdea.pac_costs) AS pac_costs
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value) as lifecycle_net_mwh_savings
    , SUM(pcwdea.units * pcwdea.ntg * pcwdea.mwh_savings * elec_load_shape.value * pcwdea.marginal_ghg) as lifecycle_elec_ghg_savings
    , pcwdea.measure_cost
    , pcwdea.admin_cost
    , pcwdea.incentive_cost
    FROM project_costs_with_discounted_elec_av pcwdea
    JOIN flexvalue.elec_load_shape_unpivoted elec_load_shape
        ON UPPER(elec_load_shape.load_shape_name) = UPPER(pcwdea.load_shape_name)
            AND elec_load_shape.utility = pcwdea.utility
            AND elec_load_shape.hour_of_year = pcwdea.hour_of_year
    GROUP BY pcwdea.project_id, pcwdea.eul, pcwdea.datetime, elec_load_shape.load_shape_name
    , pcwdea.measure_cost
    , pcwdea.admin_cost
    , pcwdea.incentive_cost
    )
, project_costs_with_discounted_gas_av AS (
    SELECT
        project_costs.*
        , gas_av_costs.year
        , gas_av_costs.month
        , gas_av_costs.quarter
        , gas_av_costs.total, gas_av_costs.market, gas_av_costs.t_d
        , gas_av_costs.environment, gas_av_costs.btm_methane, gas_av_costs.upstream_methane, gas_av_costs.marginal_ghg
        , 1.0 / POW(1.0 + (project_costs.discount_rate / 4.0), ((gas_av_costs.year - project_costs.start_year) * 4) + gas_av_costs.quarter - project_costs.start_quarter) AS discount
        , gas_av_costs.datetime
    FROM project_costs
    JOIN
      flexvalue.gas_av_costs_lol gas_av_costs
        ON gas_av_costs.utility = project_costs.utility
            AND gas_av_costs.datetime >= project_start_quarter
            AND gas_av_costs.datetime < project_end_quarter
            ),
gas_calculations AS (
    SELECT pcwdga.project_id
    , tpp.therms_profile
    , MAX(pcwdga.trc_costs) as trc_costs
    , MAX(pcwdga.pac_costs) as pac_costs
    , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.total) as gas_benefits
    , SUM((pcwdga.units * pcwdga.therms_savings * pcwdga.ntg * tpp.value) / CAST(pcwdga.eul AS FLOAT) ) as annual_net_therms_savings
    , SUM(pcwdga.units * pcwdga.therms_savings * pcwdga.ntg * tpp.value) as lifecycle_net_therms_savings
    , SUM(pcwdga.units * pcwdga.therms_savings * pcwdga.ntg * tpp.value * pcwdga.marginal_ghg) as lifecycle_gas_ghg_savings
    , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.t_d) as t_d
    , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.environment) as environment
    , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.upstream_methane) as upstream_methane
    , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.btm_methane) as btm_methane
    , SUM(pcwdga.units * pcwdga.ntg * pcwdga.therms_savings * tpp.value * pcwdga.discount * pcwdga.market) as market
    , pcwdga.datetime
    FROM project_costs_with_discounted_gas_av pcwdga
    JOIN flexvalue.therms_profile_unpivoted tpp
        ON UPPER(pcwdga.therms_profile) = UPPER(tpp.therms_profile)
            AND tpp.utility = pcwdga.utility
            AND tpp.month = pcwdga.month
    GROUP BY pcwdga.project_id, pcwdga.eul, pcwdga.datetime, tpp.therms_profile
    )

SELECT
if(
    elec_calculations.load_shape_name is NULL,
    gas_calculations.project_id,
    elec_calculations.project_id
) as project_id
, IF(
    MAX(COALESCE(elec_calculations.trc_costs, gas_calculations.trc_costs)) = 0,
    IF(
        SUM(COALESCE(elec_calculations.electric_benefits, gas_calculations.gas_benefits)) > 0,
        cast('inf' as FLOAT),
        cast('-inf' as FLOAT)
    ),
    SUM(COALESCE(elec_calculations.electric_benefits, gas_calculations.gas_benefits)) / MAX(COALESCE(elec_calculations.trc_costs, gas_calculations.trc_costs))
  ) as trc_ratio
, IF(
    MAX(COALESCE(elec_calculations.pac_costs, gas_calculations.pac_costs)) = 0,
    IF(
        SUM(COALESCE(elec_calculations.electric_benefits, gas_calculations.gas_benefits)) > 0,
        cast('inf' as FLOAT),
        cast('-inf' as FLOAT)),
    SUM(COALESCE(elec_calculations.electric_benefits, gas_calculations.gas_benefits)) / MAX(COALESCE(elec_calculations.pac_costs, gas_calculations.pac_costs))
  ) as pac_ratio
, COALESCE(SUM(elec_calculations.electric_benefits), 0) as electric_benefits
, COALESCE(SUM(gas_calculations.gas_benefits), 0) as gas_benefits
, SUM(COALESCE(elec_calculations.electric_benefits, 0)) + SUM(COALESCE(gas_calculations.gas_benefits, 0)) as total_benefits
, MAX(COALESCE(elec_calculations.trc_costs, gas_calculations.trc_costs)) as trc_costs
, MAX(COALESCE(elec_calculations.pac_costs, gas_calculations.pac_costs)) as pac_costs
, COALESCE(SUM(elec_calculations.annual_net_mwh_savings), 0) as annual_net_mwh_savings
, COALESCE(SUM(elec_calculations.lifecycle_net_mwh_savings), 0) as lifecycle_net_mwh_savings
, COALESCE(SUM(gas_calculations.annual_net_therms_savings), 0) as annual_net_therms_savings
, COALESCE(SUM(gas_calculations.lifecycle_net_therms_savings), 0) as lifecycle_net_therms_savings
, COALESCE(SUM(elec_calculations.lifecycle_elec_ghg_savings), 0) as lifecycle_elec_ghg_savings
, COALESCE(SUM(gas_calculations.lifecycle_gas_ghg_savings), 0) as lifecycle_gas_ghg_savings
, SUM(COALESCE(elec_calculations.lifecycle_elec_ghg_savings, 0)) + SUM(COALESCE(gas_calculations.lifecycle_gas_ghg_savings, 0)) as lifecycle_total_ghg_savings
, elec_calculations.measure_cost
, elec_calculations.admin_cost
, elec_calculations.incentive_cost
, COALESCE(SUM(elec_calculations.losses), 0) as losses
, COALESCE(SUM(elec_calculations.marginal_ghg), 0) as marginal_ghg
, COALESCE(SUM(elec_calculations.ghg_rebalancing), 0) as ghg_rebalancing
, COALESCE(SUM(elec_calculations.distribution), 0) as distribution
, COALESCE(SUM(elec_calculations.methane_leakage), 0) as methane_leakage
, COALESCE(SUM(elec_calculations.ancillary_services), 0) as ancillary_services
, COALESCE(SUM(elec_calculations.energy), 0) as energy
, COALESCE(SUM(elec_calculations.capacity), 0) as capacity
, COALESCE(SUM(elec_calculations.cap_and_trade), 0) as cap_and_trade
, COALESCE(SUM(elec_calculations.transmission), 0) as transmission
, COALESCE(SUM(elec_calculations.ghg_adder_rebalancing), 0) as ghg_adder_rebalancing
, COALESCE(SUM(elec_calculations.ghg_adder), 0) as ghg_adder
, COALESCE(SUM(gas_calculations.t_d), 0) as t_d
, COALESCE(SUM(gas_calculations.environment), 0) as environment
, COALESCE(SUM(gas_calculations.upstream_methane), 0) as upstream_methane
, COALESCE(SUM(gas_calculations.btm_methane), 0) as btm_methane
, COALESCE(SUM(gas_calculations.market), 0) as market
FROM
    elec_calculations
FULL JOIN
    gas_calculations
    ON elec_calculations.project_id = gas_calculations.project_id
    AND elec_calculations.datetime = gas_calculations.datetime
GROUP BY

1
, elec_calculations.measure_cost
, elec_calculations.admin_cost
, elec_calculations.incentive_cost

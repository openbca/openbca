-- create table from path '../../tests/test_real_data_calculations_aggregated/formatted_for_metered_deer_run_p2021_light.csv',
-- id,load_shape,start_year,start_quarter,utility,units,eul,ntg,discount_rate,admin_cost,measure_cost,incentive_cost,therms_profile,therms_savings,mwh_savings,region

DROP SCHEMA IF EXISTS flexvalue;

CREATE SCHEMA flexvalue;

CREATE TABLE duckdb.flexvalue.source_project AS
    SELECT
        CAST(id AS VARCHAR) AS id,
        CAST(load_shape AS VARCHAR) AS value_curve_name,
        CAST(load_shape AS VARCHAR) AS load_shape,
        CAST(start_year AS INT) AS start_year,
        CAST(start_quarter AS INT) AS start_quarter,
        CAST(utility AS VARCHAR) AS utility,
        CAST(units AS INT) AS units,
        CAST(eul AS INT) AS eul,
        CAST(ntg AS FLOAT) AS ntg,
        CAST(discount_rate AS FLOAT) AS discount_rate,
        CAST(admin_cost AS FLOAT) AS admin_cost,
        CAST(measure_cost AS FLOAT) AS measure_cost,
        CAST(incentive_cost AS FLOAT) AS incentive_cost,
        CAST(therms_profile AS VARCHAR) AS therms_profile,
        CAST(therms_savings AS FLOAT) AS therms_savings,
        CAST(mwh_savings AS FLOAT) AS mwh_savings,
        CAST(region AS VARCHAR) AS region
    FROM
        read_csv_auto('tests/test_real_data_calculations_aggregated/formatted_for_metered_deer_run_p2021.csv');

    CREATE TABLE duckdb.flexvalue.elec_av_costs AS
    SELECT
        utility, region,
        datetime::TIMESTAMP AS datetime,
        energy, losses, ancillary_services, capacity,
        transmission, distribution, cap_and_trade, ghg_adder, ghg_rebalancing,
        methane_leakage, ghg_adder_rebalancing,
        total, marginal_ghg,
        EXTRACT(year from datetime::TIMESTAMP) AS year,
        EXTRACT(quarter from datetime::TIMESTAMP) AS quarter,
        EXTRACT(month from datetime::TIMESTAMP) AS month,
        EXTRACT(hour from datetime::TIMESTAMP) AS hour_of_day,
--         (EXTRACT(DOY FROM datetime::TIMESTAMP) - 1) * 24 + EXTRACT(HOUR FROM datetime::TIMESTAMP) AS hour_of_year somehow this gives very different result than the existing hour_of_year field
        hour_of_year
    FROM
        read_csv_auto('tests/test_real_data_calculations_aggregated/full_ca_avoided_costs_2020acc.csv.gz');

CREATE TABLE duckdb.flexvalue.gas_av_costs AS
    SELECT
        utility, region,
        datetime::TIMESTAMP AS datetime,
        total, marginal_ghg,
        market, t_d, environment, btm_methane, upstream_methane,
        EXTRACT(year from datetime::TIMESTAMP) AS year,
        EXTRACT(quarter from datetime::TIMESTAMP) AS quarter,
        EXTRACT(month from datetime::TIMESTAMP) AS month,
        (EXTRACT(DOY FROM datetime::TIMESTAMP) - 1) * 24 + EXTRACT(HOUR FROM datetime::TIMESTAMP) AS hour_of_year
    FROM
        read_csv_auto('tests/test_real_data_calculations_aggregated/full_ca_avoided_costs_2020acc_gas.csv');

CREATE TABLE duckdb.flexvalue.elec_load_shape AS
    SELECT
        state,utility,quarter,month,hour_of_day,hour_of_year,Res_Indoor_CFL_Ltg,Res_RefgFrzr_HighEff,Res_RefgFrzr_Recyc_Conditioned,Res_RefgFrzr_Recyc_UnConditioned,Res_HVAC_Eff_AC,Res_HVAC_Eff_HP,Res_HVAC_Duct_Sealing,Res_HVAC_Refrig_Charge,Res_Refg_Chrg_Duct_Seal,Res_RefgFrzr_Recycling,NonRes_Indoor_CFL_Ltg,NonRes_Indoor_Non_CFL_Ltg,NonRes_HVAC_Chillers,Non_Res_HVAC_Refrig_Charge,NonRes_HVAC_Split_Package_AC,NonRes_HVAC_Duct_Sealing,NonRes_HVAC_Split_Package_HP,Res_ClothesDishWasher,Res_BldgShell_Ins,region
    FROM
        read_csv_auto('tests/test_real_data_calculations_aggregated/ca_hourly_electric_load_shapes_horizontal_copy.csv');

CREATE TABLE duckdb.flexvalue.therms_profile AS
    SELECT
        state,utility,region,quarter,month,summer,annual,winter
    FROM
        read_csv_auto('tests/test_real_data_calculations_aggregated/ca_monthly_therms_load_profiles_copy.csv');


CREATE TABLE duckdb.flexvalue.rdc_output_table AS
    SELECT
        project_id,trc_ratio,pac_ratio,electric_benefits,gas_benefits,total_benefits,trc_costs,pac_costs,annual_net_mwh_savings,lifecycle_net_mwh_savings,annual_net_therms_savings,lifecycle_net_therms_savings,lifecycle_elec_ghg_savings,lifecycle_gas_ghg_savings,lifecycle_total_ghg_savings,measure_cost,admin_cost,incentive_cost,losses,marginal_ghg,ghg_rebalancing,distribution,methane_leakage,ancillary_services,energy,capacity,cap_and_trade,transmission,ghg_adder_rebalancing,ghg_adder,t_d,environment,upstream_methane,btm_methane,market
    FROM
        read_csv_auto('tests/test_real_data_calculations_aggregated/rdc_output_table.csv');


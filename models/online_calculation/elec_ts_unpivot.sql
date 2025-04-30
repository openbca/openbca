MODEL (
  name flexvalue.elec_ts_unpivot,
  kind FULL,
  grain id,
);

SELECT utility, region, datetime, year, hour_of_year, quarter, 'energy' as value_stream, energy as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'ancillary_services' as value_stream, ancillary_services as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'capacity' as value_stream, capacity as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'transmission' as value_stream, transmission as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'distribution' as value_stream, distribution as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'cap_and_trade' as value_stream, cap_and_trade as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'ghg_adder' as value_stream, ghg_adder as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'ghg_rebalancing' as value_stream, ghg_rebalancing as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'methane_leakage' as value_stream, methane_leakage as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'total' as value_stream, total as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'marginal_ghg' as value_stream, marginal_ghg as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts
UNION ALL
SELECT utility, region, datetime, year, hour_of_year, quarter, 'ghg_adder_rebalancing' as value_stream, ghg_adder_rebalancing as value, NonRes_Indoor_CFL_Ltg, NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_ts

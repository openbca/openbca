MODEL (
  name flexvalue.elec_load_shape_pivoted,
  kind FULL,
  grain (state, utility, quarter, month, hour_of_year, load_shape_name),
);

SELECT state, utility, quarter, month, hour_of_year, 'Res_Indoor_CFL_Ltg' AS load_shape_name, Res_Indoor_CFL_Ltg AS value FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_RefgFrzr_HighEff', Res_RefgFrzr_HighEff FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_RefgFrzr_Recyc_Conditioned', Res_RefgFrzr_Recyc_Conditioned FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_RefgFrzr_Recyc_UnConditioned', Res_RefgFrzr_Recyc_UnConditioned FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_HVAC_Eff_AC', Res_HVAC_Eff_AC FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_HVAC_Eff_HP', Res_HVAC_Eff_HP FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_HVAC_Duct_Sealing', Res_HVAC_Duct_Sealing FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_HVAC_Refrig_Charge', Res_HVAC_Refrig_Charge FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_Refg_Chrg_Duct_Seal', Res_Refg_Chrg_Duct_Seal FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_RefgFrzr_Recycling', Res_RefgFrzr_Recycling FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'NonRes_Indoor_CFL_Ltg', NonRes_Indoor_CFL_Ltg FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'NonRes_Indoor_Non_CFL_Ltg', NonRes_Indoor_Non_CFL_Ltg FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'NonRes_HVAC_Chillers', NonRes_HVAC_Chillers FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Non_Res_HVAC_Refrig_Charge', Non_Res_HVAC_Refrig_Charge FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'NonRes_HVAC_Split_Package_AC', NonRes_HVAC_Split_Package_AC FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'NonRes_HVAC_Duct_Sealing', NonRes_HVAC_Duct_Sealing FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'NonRes_HVAC_Split_Package_HP', NonRes_HVAC_Split_Package_HP FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_ClothesDishWasher', Res_ClothesDishWasher FROM flexvalue.elec_load_shape
UNION ALL
SELECT state, utility, quarter, month, hour_of_year, 'Res_BldgShell_Ins', Res_BldgShell_Ins FROM flexvalue.elec_load_shape

CREATE SCHEMA flexvalue;

CREATE VIEW flexvalue.source_project AS SELECT * FROM oeem-avdcosts-platform.flexvalue_refactor_tables.formatted_for_metered_deer_run_p2021;
CREATE VIEW flexvalue.elec_load_shape AS SELECT * FROM oeem-avdcosts-platform.flexvalue_refactor_tables.ca_hourly_electric_load_shapes_horizontal_copy;
CREATE VIEW flexvalue.therms_profile AS SELECT * FROM oeem-avdcosts-platform.flexvalue_refactor_tables.ca_monthly_therms_load_profiles_copy;
CREATE VIEW flexvalue.elec_av_costs AS SELECT * FROM oeem-avdcosts-platform.avoided_costs_platform_use.full_ca_avoided_costs_2020acc;
CREATE VIEW flexvalue.gas_av_costs AS SELECT * FROM oeem-avdcosts-platform.avoided_costs_platform_use.full_ca_avoided_costs_2020acc_gas;

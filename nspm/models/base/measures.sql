MODEL(
  name openbca_input.measures,
  kind VIEW,
);

select
	m.measure_id,
	NULL as avoided_cost_subset, -- FIXME set it to m.subset once the subset is defined in the load shapes
	m.version as avoided_cost_version,
	m.measure_year as start_year,
	1 AS start_quarter, -- TODO missing from input file
    c.jurisdiction_test_pct AS discount_rate_ratio, -- TODO handle secondary_test_pct
	m.efficient_measure_life_years AS estimated_useful_life,
	1 AS unit_quantity, -- TODO missing from input file
    1 AS net_to_gross_ratio, -- TODO missing from input file
    m.administration_costs_dollar_year AS admin_cost_dollars,
	m.measure_one_time_incentive_utility_dollar_participant_year AS incentive_cost_dollars,
	m.measure_incremental_costs_customer_dollar_year AS measure_cost_dollars, --FIXME plenty of measures* cost but no measure_cost_dollars
	1000 AS elec_savings_mwh, -- FIXME missing from input file
	NULL AS gas_saving_therms, -- TODO missing from input file
	m.loadshape_mapping as elec_load_shape_mapping,
	NULL AS gas_load_shape_mapping, -- TODO missing from input file
	NULL AS avoided_costs -- TODO get all the activated avoided cost from input file
from nspm_raw.measure_inputs m
join nspm_raw.program_inputs p on m.measure_id = p.program_id -- FIXME we don't have a program_id on measures
cross join nspm_raw.config_inputs c

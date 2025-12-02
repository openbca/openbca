MODEL(
    name core_layer0_base.value_stream_groups,
    kind VIEW,
    grain (avoided_cost),
);

SELECT
    avoided_cost::VARCHAR AS avoided_cost,
    UPPER(commodity)::VARCHAR AS commodity,
    include_in_test::BOOLEAN AS include_in_test,
    calc_type::VARCHAR AS calc_type,
    pct_adder::FLOAT AS pct_adder,
    value_stream_group::VARCHAR AS value_stream_group,
FROM 
    openbca_input.value_stream_groups

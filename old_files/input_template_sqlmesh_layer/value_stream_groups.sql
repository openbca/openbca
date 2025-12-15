MODEL (
    name openbca_input.value_stream_groups,
    kind FULL,
    audits(include_in_test_not_bool),
    grain ('avoided_cost')
);

SELECT
    avoided_cost::VARCHAR AS avoided_cost,
    UPPER(commodity)::VARCHAR AS commodity,
    include_in_test::BOOLEAN AS include_in_test,
    calc_type::VARCHAR AS calc_type,
    pct_adder::FLOAT AS pct_adder,
    value_stream_group::VARCHAR AS value_stream_group

FROM nspm.openbca_input_value_stream_groups;

AUDIT (name include_in_test_not_bool);
SELECT * FROM @this_model
WHERE include_in_test not in (True, False);
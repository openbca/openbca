-- MODEL (
--     name openbca_input.adder_value_streams,
--     kind FULL,
--     audits(adder_is_not_null),
--     grain (avaoided_cost, adder)
-- );

-- SELECT
--     avoided_cost::VARCHAR AS avoided_cost,
--     adder::FLOAT AS adder
-- FROM nspm.openbca_input_adder_value_streams;

-- AUDIT (name adder_is_not_null);
-- SELECT * FROM @this_model
-- WHERE adder IS NULL;
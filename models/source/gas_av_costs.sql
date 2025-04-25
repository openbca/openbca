MODEL(
    name flexvalue.gas_av_costs_lol,
    kind FULL,
    grain (utility, year, month),
);

SELECT
    utility
    ,year
    ,month
    ,quarter
    ,total,market,t_d
    ,environment,btm_methane,upstream_methane,marginal_ghg
    ,datetime
FROM flexvalue_input.gas_av_costs

MODEL(
    name nspm.elec_marginal_cost,
    kind SEED (
        path '$root/test_data/elec_marginal_cost.csv'
    ),
    columns (
        region VARCHAR,
        utility VARCHAR,
        marginal_cost FLOAT
    )
);

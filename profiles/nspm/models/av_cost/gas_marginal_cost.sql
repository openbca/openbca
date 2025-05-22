MODEL(
    name nspm.gas_marginal_cost,
    kind SEED (
        path '$root/test_data/gas_marginal_cost.csv'
    ),
    columns (
        region VARCHAR,
        utility VARCHAR,
        marginal_cost FLOAT
    )
);

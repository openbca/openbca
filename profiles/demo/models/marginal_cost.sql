MODEL(
    name demo.marginal_cost,
    kind SEED (
        path '$root/data/marginal_cost.csv'
    ),
    columns (
        commodity VARCHAR,
        region VARCHAR,
        utility VARCHAR,
        marginal_cost FLOAT
    )
);

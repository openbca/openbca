MODEL(
    name flexvalue_reference.regions,
    kind SEED (
        path '$root/input/regions.csv'
    ),
    columns (
        region VARCHAR,
    )
);

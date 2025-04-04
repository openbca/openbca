MODEL (
    name flexvalue.elec_load_shape,
    kind FULL,
    grains (utility, load_shape, hour_of_year),
);
select
    utility, UPPER(load_shape_name) as load_shape, hour_of_year, value
from
    read_parquet('parquet/elec_load_shape/*.parquet')

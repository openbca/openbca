MODEL (
    name flexvalue.therms_profile,
    kind FULL,
    grains (utility, therms_profile_name, month),
);

select utility, profile_name, UPPER(profile_name) as therms_profile_name, month, value
from
    read_parquet('parquet/therms_profile/*.parquet')

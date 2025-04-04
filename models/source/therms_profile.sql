MODEL (
    name flexvalue.therms_profile,
    kind FULL,
    grains (utility, therms_profile, month),
);

select utility, UPPER(profile_name) as therms_profile, month, value
from
    read_parquet('parquet/therms_profile/*.parquet')

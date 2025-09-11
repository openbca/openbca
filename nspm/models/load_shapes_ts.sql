MODEL (
    name openbca_input.load_shapes_ts,
    kind FULL,
    grain (
        year,
        month,
        day,
        hour_of_year,
        res_cooling,
        res_heating,
        res_lighting,
        res_cooking,
        test1,
        tes3,
        test4,
        tes5,
        tedst6,
        test9,
        test10,
        test11
        source_sheet
    )
);

SELECT
    CAST(year AS INT) AS year,
    CAST(month AS INT) AS month,
    CAST(day AS INT) AS day,
    CAST(hour_of_year AS INT) AS hour_of_year,
    CAST(res_cooling AS FLOAT) AS res_cooling,
    CAST(res_heating AS FLOAT) AS res_heating,
    CAST(res_lighting AS FLOAT) AS res_lighting,
    CAST(res_cooking AS FLOAT) AS res_cooking,
    CAST(test1 AS FLOAT) AS test1,
    CAST(tes3 AS FLOAT) AS test3,
    CAST(test4 AS FLOAT) AS test4,
    CAST(tes5 AS FLOAT) AS test5,
    CAST(tedst6 AS FLOAT) AS test6,
    CAST(test9 AS FLOAT) AS test9,
    CAST(test10 AS FLOAT) AS test10,
    CAST(test11 AS FLOAT) AS test11,
    source_sheet
FROM nspm.openbca_input_load_shapes_ts


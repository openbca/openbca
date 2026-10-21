MODEL(
    name ca_acc_layer1_smoothing_shifting.electric_acc_smoothed_shifted_to_wednesday,
    kind FULL,
    dialect bigquery,
);

WITH
 shift_jan_1_to_wednesday AS (
   SELECT
     * except(month, quarter, hour_of_year),
     CASE
       WHEN hour_of_year < 48 THEN 12
       WHEN hour_of_year > 8711 THEN 1
       ELSE month
       END AS month,
     CASE
       WHEN hour_of_year < 48 THEN 4
       WHEN hour_of_year > 8711 THEN 1
       ELSE quarter
       END AS quarter,
     CASE
       WHEN hour_of_year < 48 THEN hour_of_year + 8712
       WHEN hour_of_year > 8711 THEN hour_of_year - 8712
       ELSE hour_of_year
       END AS hour_of_year,
   FROM
     ca_acc_layer1_smoothing_shifting.electric_acc_smoothed
 )
SELECT
 *,
 DATETIME_ADD(
   CAST(CONCAT(CAST(year AS STRING), '01') AS DATETIME FORMAT 'YYYYMM'),
   INTERVAL hour_of_year HOUR) AS datetime
FROM
 shift_jan_1_to_wednesday

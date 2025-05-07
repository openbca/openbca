install:
	pip install -r requirements.txt

run:
	sqlmesh plan --auto-apply
	echo "Writing output to output/flexvalue_legacy_one_query.csv"
	@duckdb output/duckdb.db -c "COPY (SELECT * FROM flexvalue.flexvalue_legacy_one_query) TO 'output/flexvalue_legacy_one_query.csv' WITH (FORMAT CSV, HEADER TRUE);"

duckdb:
	duckdb output/duckdb.db

test:
	PYTHONPATH=. pytest tests/
	sqlmesh test

clean:
	rm -f duckdb.db && rm -rf logs && rm -rf .cache && rm -rf output/*

DUCKDB_ARCH?=aarch64
docker-build:
	docker build --build-arg DUCKDB_ARCH=${DUCKDB_ARCH} -t open-bca -f Dockerfile .

DOCKER_RUN_ARGS=-v $(shell pwd)/input:/app/input -v $(shell pwd)/output:/app/output -v $(shell pwd)/models:/app/models -v $(shell pwd)/test_data:/app/test_data -v $(shell pwd)/logs:/app/logs -v $(shell pwd)/tests:/app/tests open-bca

docker-run: docker-build
	docker run --rm ${DOCKER_RUN_ARGS}

docker-shell: docker-build
	docker run -it --rm ${DOCKER_RUN_ARGS} bash

docker-test: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test"

check-output:
	#duckdb output/duckdb.db -c "DROP TABLE flexvalue.rdc_output_table;"
	duckdb output/duckdb.db -c "CREATE OR REPLACE TABLE flexvalue.rdc_output_table AS SELECT CAST(project_id AS VARCHAR) AS project_id, CAST(trc_ratio AS FLOAT) AS trc_ratio, CAST(pac_ratio AS FLOAT) AS pac_ratio, CAST(electric_benefits AS INT) AS electric_benefits, CAST(gas_benefits AS INT) AS gas_benefits, CAST(total_benefits AS BIGINT) AS total_benefits, CAST(trc_costs AS DOUBLE) AS trc_costs, CAST(pac_costs AS DOUBLE) AS pac_costs, CAST(annual_net_mwh_savings AS DOUBLE) AS annual_net_mwh_savings, CAST(lifecycle_net_mwh_savings AS DOUBLE) AS lifecycle_net_mwh_savings, CAST(annual_net_therms_savings AS INT) AS annual_net_therms_savings, CAST(lifecycle_net_therms_savings AS INT) AS lifecycle_net_therms_savings, CAST(lifecycle_elec_ghg_savings AS INT) AS lifecycle_elec_ghg_savings, CAST(lifecycle_gas_ghg_savings AS INT) AS lifecycle_gas_ghg_savings, CAST(lifecycle_total_ghg_savings AS BIGINT) AS lifecycle_total_ghg_savings, CAST(measure_cost AS DOUBLE) AS measure_cost, CAST(admin_cost AS DOUBLE) AS admin_cost, CAST(incentive_cost AS DOUBLE) AS incentive_cost, CAST(losses AS INT) AS losses, CAST(marginal_ghg AS INT) AS marginal_ghg, CAST(ghg_rebalancing AS INT) AS ghg_rebalancing, CAST(distribution AS INT) AS distribution, CAST(methane_leakage AS INT) AS methane_leakage, CAST(ancillary_services AS INT) AS ancillary_services, CAST(energy AS INT) AS energy, CAST(capacity AS INT) AS capacity, CAST(cap_and_trade AS INT) AS cap_and_trade, CAST(transmission AS INT) AS transmission, CAST(ghg_adder_rebalancing AS INT) AS ghg_adder_rebalancing, CAST(ghg_adder AS INT) AS ghg_adder, CAST(t_d AS INT) AS t_d, CAST(environment AS INT) AS environment, CAST(upstream_methane AS INT) AS upstream_methane, CAST(btm_methane AS INT) AS btm_methane, CAST(market AS INT) AS market, CAST(test AS VARCHAR) AS test FROM read_csv_auto('test_data/test_real_data_calculations_aggregated/rdc_output_table.csv');"
	sqlmesh table_diff flexvalue.flexvalue_legacy_one_query:flexvalue.rdc_output_table -o project_id --show-sample

reload-ref-output:
	duckdb output/duckdb.db "COPY flexvalue.flexvalue_legacy_one_query TO 'test_data/test_real_data_calculations_aggregated/rdc_output_table.csv' (HEADER, DELIMITER ',');"

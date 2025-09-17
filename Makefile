DB?=output/openbca.db
export DB

DUCKDB_ARCH?=aarch64
docker-build:
	docker build --build-arg DUCKDB_ARCH=${DUCKDB_ARCH} -t openbca -f Dockerfile .

DOCKER_RUN_ARGS=-e DB=${DB} -v $(shell pwd)/reference:/app/reference -v $(shell pwd)/core:/app/core -v $(shell pwd)/demo:/app/demo -v $(shell pwd)/nspm:/app/nspm -v $(shell pwd)/output:/app/output -v $(shell pwd)/app:/app/app -v $(shell pwd)/logs:/app/logs openbca

install:
	pip install -r requirements.txt

test-core:
	sqlmesh -p core test

run-reference:
	sqlmesh -p reference plan --auto-apply

test-reference:
	PYTHONPATH=. pytest reference/tests
	sqlmesh -p reference test

run-demo:
	sqlmesh -p reference -p demo -p core plan --auto-apply
	@echo "Evaluating and writing output in output/measure_impacts.csv..."
	@time duckdb ${DB} -c "COPY (SELECT * FROM openbca_core.measure_impacts) TO 'output/measure_impacts.csv' WITH (FORMAT CSV, HEADER TRUE);"

docker-run-demo: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make run-demo"

test-demo:
	#@duckdb ${DB} -c "CREATE OR REPLACE TABLE openbca_core.rdc_output_table AS SELECT CAST(measure_id AS VARCHAR) AS measure_id, CAST(trc_ratio AS DOUBLE) AS trc_ratio, CAST(pac_ratio AS DOUBLE) AS pac_ratio, CAST(electric_benefits AS DOUBLE) AS electric_benefits, CAST(gas_benefits AS DOUBLE) AS gas_benefits, CAST(total_benefits AS DOUBLE) AS total_benefits, CAST(annual_net_elec_savings_mwh AS DOUBLE) AS annual_net_elec_savings_mwh, CAST(lifecycle_net_elec_savings_mwh AS DOUBLE) AS lifecycle_net_elec_savings_mwh, CAST(annual_net_gas_saving_therms AS DOUBLE) AS annual_net_gas_saving_therms, CAST(lifecycle_net_gas_saving_therms AS DOUBLE) AS lifecycle_net_gas_saving_therms, CAST(lifecycle_elec_ghg_savings AS DOUBLE) AS lifecycle_elec_ghg_savings, CAST(lifecycle_gas_ghg_savings AS DOUBLE) AS lifecycle_gas_ghg_savings, CAST(lifecycle_total_ghg_savings AS DOUBLE) AS lifecycle_total_ghg_savings, CAST(losses AS DOUBLE) AS losses, CAST(ghg_rebalancing AS DOUBLE) AS ghg_rebalancing, CAST(distribution AS DOUBLE) AS distribution, CAST(methane_leakage AS DOUBLE) AS methane_leakage, CAST(ancillary_services AS DOUBLE) AS ancillary_services, CAST(energy AS DOUBLE) AS energy, CAST(capacity AS DOUBLE) AS capacity, CAST(cap_and_trade AS DOUBLE) AS cap_and_trade, CAST(transmission AS DOUBLE) AS transmission, CAST(ghg_adder_rebalancing AS DOUBLE) AS ghg_adder_rebalancing, CAST(ghg_adder AS DOUBLE) AS ghg_adder, CAST(t_d AS INT) AS t_d, CAST(environment AS DOUBLE) AS environment, CAST(upstream_methane AS DOUBLE) AS upstream_methane, CAST(btm_methane AS DOUBLE) AS btm_methane, CAST(market AS DOUBLE) AS market FROM read_csv_auto('california/data/test_real_data_calculations_aggregated/rdc_output_table.csv');"
	#sqlmesh table_diff openbca_core.measure_impacts:openbca_core.rdc_output_table -o measure_id --show-sample
	#duckdb ${DB} "COPY openbca_core.measure_impacts TO 'california/data/test_real_data_calculations_aggregated/rdc_output_table.csv' (HEADER, DELIMITER ',');"
	echo "TODO: Implement test for demo"

prepare-app:
	sqlmesh -p reference -p app -p core plan --auto-apply

run-app: prepare-app
	streamlit run app/src/main.py

test-app: prepare-app
	PYTHONPATH=app/src python3 app/tests/test_app.py

docker-run-app: docker-build
	docker run -it -p 8501:8501 ${DOCKER_RUN_ARGS} bash -c "make run-app"

run-nspm:
	sqlmesh -p reference -p nspm -p core plan --auto-apply
	@echo "Evaluating and writing output in output/nspm_measure_impacts.csv..."
	@time duckdb ${DB} -c "COPY (SELECT * FROM openbca_core.measure_impacts) TO 'output/nspm_measure_impacts.csv' WITH (FORMAT CSV, HEADER TRUE);"

test-nspm:
	PYTHONPATH=. pytest nspm/tests

test: test-reference test-core test-demo test-app

docker-test: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test"

clean:
	@rm -rf logs && rm -rf output/*
	@find . -type d -name ".cache" -exec rm -rf {} +

docker-shell: docker-build
	docker run -it --rm ${DOCKER_RUN_ARGS} bash

generate-flow-diagram:
	sqlmesh -p . dag output/dag.html

sqlmesh-ui-core:
	sqlmesh -p core ui

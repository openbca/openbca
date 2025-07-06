

install:
	pip install -r requirements.txt

run-demo:
	DB=output/demo.db sqlmesh -p projects/reference -p projects/demo -p projects/core plan --auto-apply
	@echo "Evaluating and writing output in output/project_impacts.csv..."
	@time duckdb output/demo.db -c "COPY (SELECT * FROM openbca_core.project_impacts) TO 'output/project_impacts.csv' WITH (FORMAT CSV, HEADER TRUE);"

duckdb:
	duckdb ${DB}

test:
	PYTHONPATH=. pytest tests/
	sqlmesh -p . test

clean:
	rm -f duckdb.db && rm -rf logs && rm -rf .cache && rm -rf output/*
	find . -type d -name ".cache" -exec rm -rf {} +

DUCKDB_ARCH?=aarch64
docker-build:
	docker build --build-arg DUCKDB_ARCH=${DUCKDB_ARCH} -t openbca -f Dockerfile .

DOCKER_RUN_ARGS=-e DB=${DB} -v $(shell pwd)/input:/app/input -v $(shell pwd)/output:/app/output -v $(shell pwd)/models:/app/models -v $(shell pwd)/logs:/app/logs -v $(shell pwd)/app:/app/app openbca

docker-run: docker-build
	docker run --rm ${DOCKER_RUN_ARGS}

docker-shell: docker-build
	docker run -it --rm ${DOCKER_RUN_ARGS} bash

docker-test: docker-build
	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test"

check-output:
	@duckdb ${DB} -c "CREATE OR REPLACE TABLE openbca_core.rdc_output_table AS SELECT CAST(project_id AS VARCHAR) AS project_id, CAST(trc_ratio AS DOUBLE) AS trc_ratio, CAST(pac_ratio AS DOUBLE) AS pac_ratio, CAST(electric_benefits AS DOUBLE) AS electric_benefits, CAST(gas_benefits AS DOUBLE) AS gas_benefits, CAST(total_benefits AS DOUBLE) AS total_benefits, CAST(annual_net_mwh_savings AS DOUBLE) AS annual_net_mwh_savings, CAST(lifecycle_net_mwh_savings AS DOUBLE) AS lifecycle_net_mwh_savings, CAST(annual_net_therms_savings AS DOUBLE) AS annual_net_therms_savings, CAST(lifecycle_net_therms_savings AS DOUBLE) AS lifecycle_net_therms_savings, CAST(lifecycle_elec_ghg_savings AS DOUBLE) AS lifecycle_elec_ghg_savings, CAST(lifecycle_gas_ghg_savings AS DOUBLE) AS lifecycle_gas_ghg_savings, CAST(lifecycle_total_ghg_savings AS DOUBLE) AS lifecycle_total_ghg_savings, CAST(losses AS DOUBLE) AS losses, CAST(ghg_rebalancing AS DOUBLE) AS ghg_rebalancing, CAST(distribution AS DOUBLE) AS distribution, CAST(methane_leakage AS DOUBLE) AS methane_leakage, CAST(ancillary_services AS DOUBLE) AS ancillary_services, CAST(energy AS DOUBLE) AS energy, CAST(capacity AS DOUBLE) AS capacity, CAST(cap_and_trade AS DOUBLE) AS cap_and_trade, CAST(transmission AS DOUBLE) AS transmission, CAST(ghg_adder_rebalancing AS DOUBLE) AS ghg_adder_rebalancing, CAST(ghg_adder AS DOUBLE) AS ghg_adder, CAST(t_d AS INT) AS t_d, CAST(environment AS DOUBLE) AS environment, CAST(upstream_methane AS DOUBLE) AS upstream_methane, CAST(btm_methane AS DOUBLE) AS btm_methane, CAST(market AS DOUBLE) AS market FROM read_csv_auto('california/data/test_real_data_calculations_aggregated/rdc_output_table.csv');"
	sqlmesh table_diff openbca_core.project_impacts:openbca_core.rdc_output_table -o project_id --show-sample

refresh-ref-output:
	duckdb ${DB} "COPY openbca_core.project_impacts TO 'california/data/test_real_data_calculations_aggregated/rdc_output_table.csv' (HEADER, DELIMITER ',');"

generate-flow-diagram:
	sqlmesh -p . dag output/dag.html

sqlmesh-ui:
	sqlmesh ui

prepare-app:
	DB=output/app.db sqlmesh -p projects/reference -p projects/app -p projects/core plan --auto-apply

run-app: prepare-app
	DB=output/app.db streamlit run app/main.py

docker-run-app: docker-run
	docker run -it -p 8501:8501 ${DOCKER_RUN_ARGS} bash -c "make run-app"

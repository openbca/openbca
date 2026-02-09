DB?=output/openbca.db
DBV?=output/openbca_input_validation.db
export DB
export DBV

# docker-build:
# 	docker build -t openbca -f Dockerfile .

# DOCKER_RUN_ARGS=-e DB=${DB} -v $(shell pwd)/reference:/app/reference -v $(shell pwd)/core:/app/core -v $(shell pwd)/demo:/app/demo -v $(shell pwd)/nspm:/app/nspm -v $(shell pwd)/output:/app/output -v $(shell pwd)/app:/app/app -v $(shell pwd)/logs:/app/logs openbca

install:
	uv sync

test-streamlit:
	uv run streamlit run streamlit_test/Upload_Data_and_Run_Model.py

# test-core:
# 	uv run sqlmesh -p core test

# run-reference:
# 	uv run sqlmesh -p reference plan --auto-apply

# test-reference:
# 	PYTHONPATH=. pytest reference/tests
# 	uv run sqlmesh -p reference test

# prepare-app:
# 	uv run sqlmesh -p reference -p app -p core plan --auto-apply

# run-app: prepare-app
# 	uv run streamlit run app/src/main.py

# test-app: prepare-app
# 	PYTHONPATH=app/src python3 app/tests/test_app.py

# docker-test-app: docker-build
# 	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test-app"

# docker-run-app: docker-build
# 	docker run -it -p 8501:8501 ${DOCKER_RUN_ARGS} bash -c "make run-app"

run-ca-electric-acc:
	@echo "Starting ACC Electric Model data scraping..."
	@echo ""
	@mkdir -p ca_acc/output
	@DB=ca_acc/output/ca_electric_acc.db uv run sqlmesh -p ca_acc/electric plan --auto-apply
	@echo "Exporting electric ACC table to CSV..."
	@time DB=ca_acc/output/ca_electric_acc.db uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DB']); con.execute(\"COPY (SELECT * FROM ca_electric_acc.ca_acc_layer1_smoothing.electric_acc_smoothed) TO 'ca_acc/output/full_ca_avoided_costs_acc_smoothed.csv' (HEADER, DELIMITER ',');\"); con.close()"
	@echo "CSV file saved to: ca_acc/output/full_ca_avoided_costs_acc_smoothed.csv"

run-ca-gas-acc:
	@echo "Starting ACC Gas Model data scraping..."
	@echo ""
	@mkdir -p ca_acc/output
	@DB=ca_acc/output/ca_gas_acc.db uv run sqlmesh -p ca_acc/gas plan --auto-apply
	@echo "Exporting gas ACC table to CSV..."
	@time DB=ca_acc/output/ca_gas_acc.db uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DB']); con.execute(\"COPY (SELECT * FROM ca_gas_acc.gas.acc_gas_model_ts) TO 'ca_acc/output/full_ca_avoided_costs_acc_gas.csv' (HEADER, DELIMITER ',');\"); con.close()"
	@echo "CSV file saved to: ca_acc/output/full_ca_avoided_costs_acc_gas.csv"

run-input-transform-validations:
	@echo "Running parsing scripts and validating input data..."
# Note: we use a separate DuckDB instance and gateway for validation of initial parsing and ingestion steps
	@uv run sqlmesh --gateway validations_duckdb -p nspm -p core plan --select-model openbca_input.* --select-model core_layer0_base.* --select-model core_validations.* --auto-apply
	@uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DBV']); con.close();"

# test-environment-var-windows:
# 	@echo DB is %DB%
# 	@echo DBV is %DBV%
# 	DB=$(DB)
# 	DBV=$(DBV)

run-nspm:
	uv run sqlmesh -p nspm -p core plan --auto-apply
	@echo "Evaluating and writing output in output/results_summary_by_id.csv..."
	@time uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DB']); con.execute(\"COPY (SELECT * FROM openbca.core_layer3_finalization.results_summary_by_id) TO 'output/results_summary_by_id.csv' (HEADER, DELIMITER ',');\"); con.close()"

# run-nspm-group-outputs:
# 	@time uv run sqlmesh -p nspm -p core plan --auto-apply
# 	@echo "Evaluating and writing output in output/results_summary_by_id.csv..."
# 	@time uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DB']); con.execute(\"COPY (SELECT * FROM openbca.core_layer3_finalization.results_summary_by_id) TO 'output/results_summary_by_id.csv' (HEADER, DELIMITER ',');\"); con.close()"
# 	@echo "Evaluating and writing output in output/custom_aggregation_results_summary.csv..."
# 	@time uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DB']); con.execute(\"COPY (SELECT $(GB), sum(final_dollar_value) AS final_dollar_value FROM openbca.core_layer3_finalization.final_value_calculations_ts GROUP BY $(GB)) TO 'output/custom_aggregation_results_summary.csv' (HEADER, DELIMITER ',');\"); con.close()"

test-parsing:
	@echo "\nTesting parsing of Excel input templates."
	cd nspm && PYTHONPATH=.. uv run python test_parsing.py

# docker-run-nspm: docker-build
# 	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make run-nspm"

# test-nspm:
# 	PYTHONPATH=. pytest nspm/tests

# test: test-reference test-core test-demo test-app

# docker-test: docker-build
# 	docker run --rm ${DOCKER_RUN_ARGS} bash -c "make test"

clean:
	@rm -rf logs && rm -rf output/*
	@find . -type d -name ".cache" -exec rm -rf {} +

# docker-shell: docker-build
# 	docker run -it --rm ${DOCKER_RUN_ARGS} bash

generate-flow-diagram:
	uv run sqlmesh -p . dag output/dag.html

sqlmesh-ui-core:
	uv run sqlmesh -p core ui
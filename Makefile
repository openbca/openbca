# DB?=output/openbca.db
# DBV?=output/openbca_input_validation.db
# export DB
# export DBV

install:
	uv sync

run-openbca:
	uv run streamlit run user_interface/Entrypoint.py

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
	@uv run sqlmesh --gateway validations_duckdb -p excel_input_parsing -p core plan --select-model openbca_input.* --select-model core_layer0_base.* --select-model core_validations.* --auto-apply
	@uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DBV']); con.close();"

run-openbca-model:
	uv run sqlmesh -p excel_input_parsing -p core plan --auto-apply --run --ignore-cron
	@echo "Evaluating and writing output in output/results_summary_by_id.csv..."
	@time uv run python -c "import os,duckdb; con=duckdb.connect(os.environ['DB']); con.execute(\"COPY (SELECT * FROM openbca.core_layer3_finalization.results_summary_by_id) TO 'output/results_summary_by_id.csv' (HEADER, DELIMITER ',');\"); con.close()"

test-parsing:
	@echo "\nTesting parsing of Excel input templates."
	cd excel_input_parsing && PYTHONPATH=.. uv run python test_parsing.py

build-pyinstaller-package:
	@echo "Building PyInstaller openbca-app..."
	uv run pyinstaller openbca-app.spec --clean --noconfirm

# Note: this assumes the package has already been built with the above command, and will fail if it has not been built yet
run-pyinstaller-package:
	@echo "Running PyInstaller openbca-app..."
	@cd ./dist/openbca-app && ./openbca-app

clean:
	@rm -rf logs && rm -rf output/*
	@find . -type d -name ".cache" -exec rm -rf {} +

generate-flow-diagram:
	uv run sqlmesh -p . dag output/dag.html

sqlmesh-ui-core:
	uv run sqlmesh -p core ui
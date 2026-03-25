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
# 	@uv run sqlmesh --gateway validations_duckdb -p excel_input_parsing -p core plan --select-model openbca_input.* --select-model core_layer0_base.* --select-model core_validations.* --auto-apply
	@uv run python model_runners.py input_transform_validations
	@uv run python -c "import os,duckdb; from config.env import setup_env_vars; setup_env_vars(); con=duckdb.connect(os.environ['DBV']); con.close();"

run-openbca-model:
# 	uv run sqlmesh -p excel_input_parsing -p core plan --auto-apply --run --ignore-cron
	@uv run python model_runners.py openbca_excel_model
	@echo "Evaluating and writing output in output/results_summary_by_id.csv..."
	@uv run python -c "import os,duckdb; from config.env import setup_env_vars; setup_env_vars(); con=duckdb.connect(os.environ['DB']); con.execute(\"COPY (SELECT * FROM openbca.core_layer3_finalization.results_summary_by_id) TO 'output/results_summary_by_id.csv' (HEADER, DELIMITER ',');\"); con.close()"

test-parsing:
	@echo "\nTesting parsing of Excel input templates."
	cd excel_input_parsing && PYTHONPATH=.. uv run python test_parsing.py

build-pyinstaller-package:
	@echo "Building openbca-app with streamlit-desktop-app..."
	uv run streamlit-desktop-app build user_interface/Entrypoint.py \
		--name desktop-openbca \
		--pyinstaller-options \
			--onedir \
			--noconfirm \
			--add-data excel_input_parsing:excel_input_parsing \
			--add-data core/models:core/models \
			--add-data core/config.yaml:core \
			--add-data user_interface:user_interface \
			--add-data model_runners.py:. \
			--add-data output/.keepme:output \
			--add-data .env:. \
			--hidden-import model_runners \
			--hidden-import config.env \
			--hidden-import config.paths \
			--hidden-import validation_functions \
			--hidden-import helper_functions \
			--hidden-import figures \
			--hidden-import sql_queries \
			--collect-all sqlmesh \
			--collect-all sqlglot \
			--collect-submodules sqlglot.dialects \
			--collect-all duckdb \
			--collect-all openpyxl
# also create symlinks from dist/desktop-openbca/_internal/[input/output] to dist/desktop-openbca/[input/output] for easier access to these folders in the packaged app
# may need to be relative symlinks

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

# Generate styled HTML from README.md (open in browser and Print to PDF if needed).
# Requires pandoc (e.g. brew install pandoc).
readme-html:
	@echo "Generating README.html..."
	pandoc README.md -o README.html -s --css=readme-pdf.css
	@echo "Done: README.html (open in a browser; use Print to save as PDF)"

# Generate a styled PDF from README.md. Mermaid diagrams are rendered as images (via mermaid-cli or mermaid.ink).
# Requires: pandoc (e.g. brew install pandoc) and WeasyPrint system libs (macOS: brew install pango cairo glib).
# Optional: Node/npx for local Mermaid rendering; otherwise diagrams are fetched from mermaid.ink (network needed).
# On macOS with Homebrew, DYLD_LIBRARY_PATH is set so WeasyPrint finds pango/cairo/glib.
readme-pdf:
	@echo "Generating README.pdf..."
	uv sync --extra pdf
	uv run python scripts/render_mermaid_for_pdf.py
	pandoc README.pdf.md -o README.html -s --css=readme-pdf.css
	DYLD_LIBRARY_PATH="/opt/homebrew/lib:$$DYLD_LIBRARY_PATH" uv run python -c "from weasyprint import HTML; HTML('README.html').write_pdf('README.pdf')"
	@rm -f README.html README.pdf.md
	@rm -rf readme_pdf_temp
	@echo "Done: README.pdf"
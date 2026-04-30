import argparse
from shutil import rmtree
import warnings

from sqlmesh.core.console import set_console, get_console, TerminalConsole, CaptureTerminalConsole
from sqlmesh.core.context import Context

from config.paths import get_excel_input_parsing_project_dir, get_core_project_dir, get_output_dir, get_logs_dir
from config.env import setup_env_vars

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")  # Suppress openpyxl warnings about data validation and conditional formatting

def run_openbca_excel_model() -> None:
    setup_env_vars()

    ctx = Context(
            paths=[get_excel_input_parsing_project_dir(), get_core_project_dir()],
    )
    try:
        ctx.plan(run=True, ignore_cron=True, auto_apply=True)
    finally:
        ctx.close()


def run_input_transform_validations() -> None:
    print("\nRunning input transformation validations...")
# Note: we use a separate DuckDB instance and gateway for validation of initial parsing and ingestion steps
	# @uv run sqlmesh --gateway validations_duckdb -p excel_input_parsing -p core plan --select-model openbca_input.* --select-model core_layer0_base.* --select-model core_validations.* --auto-apply
    setup_env_vars()

    ctx = Context(
            paths=[get_excel_input_parsing_project_dir(), get_core_project_dir()],
            gateway="validations_duckdb",
    )
    
    try:
        ctx.plan(
            select_models=["openbca_input.*", "core_layer0_base.*", "core_validations.*"], 
            auto_apply=True,
        )
    finally:
        ctx.close()


def clean_output_directory():
    """Clean the output directory before running tests."""
    output_dir = get_output_dir()
    for item in output_dir.iterdir():
        if item.name == ".keepme":
            continue
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            rmtree(item)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run model runners for OpenBCA.")
    parser.add_argument(
        "runner",
        choices=["openbca_excel_model", "input_transform_validations", "clean_output"],
        help="Specify which runner to execute.",
    )
    args = parser.parse_args()
    
    # for cli runs, set terminal output
    term_console = TerminalConsole()
    set_console(term_console)

    if args.runner == "openbca_excel_model":
        run_openbca_excel_model()
    elif args.runner == "input_transform_validations":
        run_input_transform_validations()
    elif args.runner == "clean_output":
        clean_output_directory()
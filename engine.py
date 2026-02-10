from shutil import rmtree

from sqlmesh.core.context import Context

from config.paths import get_nspm_project_dir, get_core_project_dir, get_output_dir, get_logs_dir
from config.env import setup_env_vars

def run_all() -> None:
    setup_env_vars()

    ctx = Context(
            paths=[get_nspm_project_dir(), get_core_project_dir()],
    )
    try:
        plan = ctx.plan()
        ctx.apply(plan)
    finally:
        ctx.close()


def run_input_transform_validations() -> None:
    print("\nRunning input transformation validations...")
# Note: we use a separate DuckDB instance and gateway for validation of initial parsing and ingestion steps
	# @uv run sqlmesh --gateway validations_duckdb -p nspm -p core plan --select-model openbca_input.* --select-model core_layer0_base.* --select-model core_validations.* --auto-apply
    setup_env_vars()

    ctx = Context(
            paths=[get_nspm_project_dir(), get_core_project_dir()],
            gateway="validations_duckdb",
    )
    
    try:
        plan = ctx.plan(
            select_models=["openbca_input.*", "core_layer0_base.*", "core_validations.*"], 
        )
        ctx.apply(plan)
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
    clean_output_directory()
    # run_all()
    run_input_transform_validations()
    
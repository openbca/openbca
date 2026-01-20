#!/usr/bin/env python3
"""
Test script to validate parsing of Excel input templates.
This tests that all Excel files can be successfully read and parsed.
"""

import sys
import os

# Add parent directory to path so we can import from models
sys.path.insert(0, os.path.dirname(__file__))

from models.openbca_input_measures import load_measure_inputs_from_excel
from models.openbca_input_load_shapes_ts import load_load_shapes_from_excel
from models.openbca_input_avoided_costs_ts import load_avoided_costs_from_excel
from models.openbca_input_value_stream_groups import load_value_stream_groups_from_excel
from models.openbca_input_global_parameters import compile_global_parameters_from_excel
from models.openbca_input_program_value_streams import load_program_value_streams_from_excel


def test_measures_parsing():
    """Test parsing of measure inputs."""
    print("\nTesting measures parsing...")
    try:
        df = load_measure_inputs_from_excel(
            input_file="OpenBCA Program Input.xlsx",
            sheet_name="Measure Inputs",
            skiprows=2
        )
        print(f"  ✓ Successfully parsed measures: {len(df)} rows")
        return True
    except Exception as e:
        print(f"  ✗ Failed to parse measures: {e}")
        return False


def test_load_shapes_parsing():
    """Test parsing of load shapes."""
    print("\nTesting load shapes parsing...")
    try:
        df = load_load_shapes_from_excel(
            input_file="OpenBCA Program Input.xlsx",
            skip_sheets={"Front Page", "Program Inputs", "Measure Inputs", "Define Load Shape Names", "Updates & Improvements", "Custom Period - LS Support"},
            skiprows=1,
        )
        print(f"  ✓ Successfully parsed load shapes: {len(df)} rows")
        return True
    except Exception as e:
        print(f"  ✗ Failed to parse load shapes: {e}")
        return False


def test_avoided_costs_parsing():
    """Test parsing of avoided costs."""
    print("\nTesting avoided costs parsing...")
    try:
        df = load_avoided_costs_from_excel(
            input_file="OpenBCA Configuration.xlsm",
            skip_sheets={"Front Page", "Updates & Improvements", "Common Data", "Validations", "Configuration Data", "Dictionary"},
            skiprows=3
        )
        print(f"  ✓ Successfully parsed avoided costs: {len(df)} rows")
        return True
    except Exception as e:
        print(f"  ✗ Failed to parse avoided costs: {e}")
        return False


def test_value_stream_groups_parsing():
    """Test parsing of value stream groups."""
    print("\nTesting value stream groups parsing...")
    try:
        df = load_value_stream_groups_from_excel(
            input_file='OpenBCA Configuration.xlsm'
        )
        print(f"  ✓ Successfully parsed value stream groups: {len(df)} rows")
        return True
    except Exception as e:
        print(f"  ✗ Failed to parse value stream groups: {e}")
        return False


def test_global_parameters_parsing():
    """Test parsing of global parameters."""
    print("\nTesting global parameters parsing...")
    try:
        df = compile_global_parameters_from_excel(
            input_file='OpenBCA Configuration.xlsm'
        )
        print(f"  ✓ Successfully parsed global parameters: {len(df)} rows")
        return True
    except Exception as e:
        print(f"  ✗ Failed to parse global parameters: {e}")
        return False


def test_program_value_streams_parsing():
    """Test parsing of program value streams."""
    print("\nTesting program value streams parsing...")
    try:
        df = load_program_value_streams_from_excel(
            input_file='OpenBCA Program Input.xlsx'
        )
        print(f"  ✓ Successfully parsed program value streams: {len(df)} rows")
        return True
    except Exception as e:
        print(f"  ✗ Failed to parse program value streams: {e}")
        return False


def main():
    """Run all parsing tests."""
    #print("\nTesting parsing of Excel input templates.")
    print("=" * 60)
    
    results = []
    # results.append(test_measures_parsing())
    # results.append(test_load_shapes_parsing())
    # results.append(test_avoided_costs_parsing())
    results.append(test_value_stream_groups_parsing())
    # results.append(test_global_parameters_parsing())
    # results.append(test_program_value_streams_parsing())
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All {total} parsing tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} out of {total} parsing tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
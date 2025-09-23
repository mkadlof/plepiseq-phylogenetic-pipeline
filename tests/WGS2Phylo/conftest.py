# conftest.py
import pytest
from pathlib import Path

def pytest_addoption(parser):
    # THis is a special function that according to pytest documentation:
    # Register argparse-style options and ini-style config values, called once at the beginning of a test run.
    # Options defined here can later be accessed through the config object, respectively:
    parser.addoption(
        "--data-dir",
        action="store",
        default=None,
        help="Path to directory containing JSON files for testing"
    )

def pytest_generate_tests(metafunc):
    # once a "hook" pytest_adoption is parsed its output is stored in a pytest config
    # that is accessable her via metafunc.config
    # This function name is also special it is a hook that is applied to all tested functions withoud a need to define a decorator
    data_dir = metafunc.config.getoption("data_dir")
    if "json_file" in metafunc.fixturenames:
        if not data_dir:
            pytest.skip("No data-dir provided for JSON files.")
        files = sorted(Path(data_dir).glob("*.json"))
        if not files:
            pytest.skip(f"No JSON files found in directory: {data_dir}")
        metafunc.parametrize(
            "json_file",
            files,
            ids=[f.name for f in files]
        )
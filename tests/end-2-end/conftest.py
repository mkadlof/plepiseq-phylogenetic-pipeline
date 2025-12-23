# conftest.py

from pathlib import Path
import pytest

def pytest_addoption(parser):
    parser.addoption("--data-dir", action="store", default="data",
                     help="Path with JSON/NWK/microreact test artefacts")
    parser.addoption("--schema", action="store", default="https://raw.githubusercontent.com/michallaz/plepiseq_json/refs/heads/main/main_output_schema_phylogenetics.json",
                     help="URL or local path to main schema (optional)")


def pytest_generate_tests(metafunc):
    data_dir = Path(metafunc.config.getoption("data_dir"))
    if not data_dir.exists():
        pytest.skip(f"--data-dir {data_dir} does not exist")

    if "json_file" in metafunc.fixturenames:
        files = sorted((data_dir).glob("*.json"))

        if not files:
            pytest.skip(f"No JSON files found under {data_dir}")

        metafunc.parametrize("json_file", files, ids=[f.name for f in files])
    elif "tree_file" in metafunc.fixturenames:
        files = sorted((data_dir).glob("*.nwk"))
        if not files:
            pytest.skip(f"No NWK files found under {data_dir}")
        metafunc.parametrize("tree_file", files, ids=[f.name for f in files])
    elif "microreact_file" in metafunc.fixturenames:
        files = sorted((data_dir).glob("*.microreact"))
        if not files:
            pytest.skip(f"No microreact files found under {data_dir}")
        metafunc.parametrize("microreact_file", files, ids=[f.name for f in files])



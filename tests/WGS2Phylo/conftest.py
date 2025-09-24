# conftest.py
import pytest
from pathlib import Path

def pytest_addoption(parser):
    parser.addoption(
        "--data-dir",
        action="store",
        default="data",
        help="Base path to directory containing JSON files for testing"
    )

def pytest_generate_tests(metafunc):
    data_dir = Path(metafunc.config.getoption("data_dir"))
    if not data_dir:
        pytest.skip("No data-dir provided for JSON files.")

    # all JSONs from bacteria + viruses
    if "json_file" in metafunc.fixturenames:
        b = sorted((data_dir / "bacteria").glob("*.json"))
        v = sorted((data_dir / "viruses").glob("*.json"))
        files = b + v
        if not files:
            pytest.skip(f"No JSON files found under {data_dir}")
        metafunc.parametrize("json_file", files, ids=[f.name for f in files])

    # bacteria-only
    if "bacterial_json" in metafunc.fixturenames:
        files = sorted((data_dir / "bacteria").glob("*.json"))
        if not files:
            pytest.skip(f"No bacterial JSON files found in {data_dir/'bacteria'}")
        metafunc.parametrize("bacterial_json", files, ids=[f.name for f in files])

    # viruses-only
    if "viral_json" in metafunc.fixturenames:
        files = sorted((data_dir / "viruses").glob("*.json"))
        if not files:
            pytest.skip(f"No viral JSON files found in {data_dir/'viruses'}")
        metafunc.parametrize("viral_json", files, ids=[f.name for f in files])

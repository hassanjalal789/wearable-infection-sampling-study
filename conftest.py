"""Publication-stage pytest configuration.

This file is new code, written for this repository in September 2026. It is not
part of the research-stage test suite and does not change any test.

tests/test_reproduction.py reads the two supplementary workbooks of the source
studies from metadata/. They are third-party files and are not redistributed in
this repository, and the module cannot be imported without them. When either
workbook is absent, the module is not collected and the test header says why.
Save both workbooks under metadata/ to run it; see
docs/REPRODUCTION_GATES_AND_POWER.md.
"""
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_WORKBOOKS = (
    _ROOT / "metadata" / "phase1_supplementary_data.xlsx",
    _ROOT / "metadata" / "phase2_covid_metadata.xlsx",
)
_MISSING = [p.name for p in _WORKBOOKS if not p.is_file()]


def pytest_ignore_collect(collection_path, config):
    if _MISSING and collection_path.name == "test_reproduction.py":
        return True
    return None


def pytest_report_header(config):
    if _MISSING:
        return (
            "tests/test_reproduction.py not collected: source workbook(s) absent "
            "from metadata/: " + ", ".join(_MISSING)
        )
    return None

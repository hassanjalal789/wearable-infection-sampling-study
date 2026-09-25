#!/usr/bin/env python3
import hashlib
import runpy
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import style as mstyle

for old, new in {
    "seaborn-dark-palette": "seaborn-v0_8-dark-palette",
    "seaborn-darkgrid": "seaborn-v0_8-darkgrid",
    "seaborn-whitegrid": "seaborn-v0_8-whitegrid",
    "seaborn": "seaborn-v0_8",
}.items():
    if old not in mstyle.library and new in mstyle.library:
        mstyle.library[old] = mstyle.library[new]

from pandas.core.window.rolling import Rolling

_original_rolling_mean = Rolling.mean

def legacy_rolling_mean(self, *args, **kwargs):
    kwargs.setdefault("numeric_only", True)
    return _original_rolling_mean(self, *args, **kwargs)

Rolling.mean = legacy_rolling_mean

import statsmodels.tsa.seasonal as seasonal

_original_seasonal_decompose = seasonal.seasonal_decompose

def legacy_seasonal_decompose(*args, **kwargs):
    if "freq" in kwargs and "period" not in kwargs:
        kwargs["period"] = kwargs.pop("freq")
    return _original_seasonal_decompose(*args, **kwargs)

seasonal.seasonal_decompose = legacy_seasonal_decompose

target = Path(sys.argv[1])
before = hashlib.sha256(target.read_bytes()).hexdigest()

print(
    f"[gate_a_compat] upstream {target.name} sha256={before}",
    file=sys.stderr
)

sys.argv = sys.argv[1:]

try:
    runpy.run_path(str(target), run_name="__main__")
finally:
    after = hashlib.sha256(target.read_bytes()).hexdigest()
    state = "UNCHANGED" if after == before else "MODIFIED — INVALID"
    print(
        f"[gate_a_compat] upstream {target.name} sha256={after} ({state})",
        file=sys.stderr
    )

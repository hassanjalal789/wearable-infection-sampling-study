#!/usr/bin/env python3
"""
Gate A compatibility shim.  Runs UPSTREAM CODE BYTE-IDENTICAL.

NightSignal calls plt.style.use('seaborn-dark-palette'), a style name matplotlib
removed in 3.6 (renamed 'seaborn-v0_8-dark-palette').  This is an environment
incompatibility, not an algorithmic difference, so it is repaired in the
ENVIRONMENT rather than in the file: the old name is aliased into matplotlib's
style library, then the unmodified script is executed with runpy.

The upstream file's sha256 is printed before and after execution so the record
shows it was never touched.  No statistical or algorithmic behaviour is altered.

Usage:  python3 gate_a_shim.py <script.py> [args...]
"""
import hashlib, runpy, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import style as mstyle

ALIASES = {
    "seaborn-dark-palette": "seaborn-v0_8-dark-palette",
    "seaborn-darkgrid": "seaborn-v0_8-darkgrid",
    "seaborn-whitegrid": "seaborn-v0_8-whitegrid",
    "seaborn": "seaborn-v0_8",
}
for old, new in ALIASES.items():
    if old not in mstyle.library and new in mstyle.library:
        mstyle.library[old] = mstyle.library[new]

target = Path(sys.argv[1])
digest = hashlib.sha256(target.read_bytes()).hexdigest()
print(f"[gate_a_shim] upstream {target.name} sha256={digest}", file=sys.stderr)
sys.argv = sys.argv[1:]
try:
    runpy.run_path(str(target), run_name="__main__")
finally:
    after = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"[gate_a_shim] upstream {target.name} sha256={after} "
          f"({'UNCHANGED' if after == digest else 'MODIFIED — INVALID'})", file=sys.stderr)

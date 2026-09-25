#!/usr/bin/env python3
"""Check the published package using only files in this repository.

New code, written for this repository; it is not part of the research pipeline.
It runs four groups of checks:

links       every relative link in a Markdown file points to a file that
            exists, and every #anchor matches a heading in its target;
arithmetic  in the published confirmatory summary, win, loss and tie counts
            sum to N; theta = (W + 0.5 x T) / N; the exact two-sided sign-test
            p-value is recomputed from W and L; each point estimate lies inside
            its interval; the gate decisions follow from the H1 row; the same
            count and theta checks are applied to every sensitivity row, and no
            sensitivity row carries a p-value; the README results table and the
            main summary documents quote the published H1 values;
intervals   the 95% BCa bootstrap intervals, recomputed with the bootstrap
            functions of the two published scripts that produced them, from the
            published win, loss and tie counts and each script's recorded seed
            schedule, equal the published limits for the four confirmatory
            comparisons and all 33 sensitivity rows. Both scripts bootstrap a
            vector built from the counts alone, so no participant-level file is
            needed;
energy      the energy feasibility audit, recomputed from the published model
            and configuration, is byte-for-byte identical to the archived file;
tables      the unchanged src/make_final_tables_figures.py, run in a temporary
            folder that holds only the two published summary files, regenerates
            the result tables and digest byte-for-byte. It also redraws the
            figures, which are not compared: the archived figures were drawn with
            a different Matplotlib version and are compared by eye only;
power       (optional, about three minutes) the unchanged src/power_sim.py
            recomputes the 12 effect-ray cells of the frozen power calculation
            at N = 38, and every recorded field matches the archived
            results/power_sim_frozen_n38.json. The 432-cell surface is not re-run.

It does not re-run the analysis on source data or check anything that needs
withheld participant-level files.
Exit status 0 means every selected check passed.

Usage: python src/check_public_package.py [links] [arithmetic] [intervals] [energy] [tables] [power]
With no arguments, every group except power runs; power runs only when named.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results" / "primary_e3_run_83cc8d1"
SUMMARY = RUN / "confirmatory_analysis" / "confirmatory_comparison_summary.csv"
GATES = RUN / "confirmatory_analysis" / "gatekeeping_decisions.json"
SENS = RUN / "sensitivity_analysis" / "sensitivity_summary.csv"
TABLES = RUN / "final_tables_figures"
SKIP_DIRS = {".git", ".venv", "venv", "metadata", "__pycache__", ".pytest_cache", "node_modules"}
SUMMARY_DOCS = ["README.md", "docs/RESEARCH_SUMMARY.md", "docs/RESULTS_AND_LIMITATIONS.md", "docs/OVERVIEW.md"]
TOL = 1e-9


def markdown_files() -> list[Path]:
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        out += [Path(dirpath) / f for f in sorted(filenames) if f.endswith(".md")]
    return out


def heading_anchors(path: Path) -> set[str]:
    """Anchors GitHub generates for the headings of a Markdown file."""
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    fence = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            if fence is None:
                fence = marker.group(1)[0]
            elif stripped.startswith(fence * 3):
                fence = None
            continue
        if fence is not None:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", m.group(2))
        slug = re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        anchors.add(slug if n == 0 else f"{slug}-{n}")
    return anchors


def check_links() -> tuple[bool, str, list[str]]:
    problems, n_links, cache = [], 0, {}
    files = markdown_files()
    for md in files:
        text = md.read_text(encoding="utf-8")
        for m in re.finditer(r"\]\(([^)\s]+)\)", text):
            url = m.group(1)
            if url.startswith(("http://", "https://", "mailto:")):
                continue
            n_links += 1
            path, _, frag = url.partition("#")
            target = (md.parent / urllib.parse.unquote(path)).resolve() if path else md
            rel = md.relative_to(ROOT)
            try:
                target.relative_to(ROOT)
            except ValueError:
                problems.append(f"{rel}: {url} points outside the repository")
                continue
            if not target.exists():
                problems.append(f"{rel}: {url} target does not exist")
                continue
            if frag and target.suffix == ".md":
                if target not in cache:
                    cache[target] = heading_anchors(target)
                if frag.lower() not in cache[target]:
                    problems.append(f"{rel}: {url} anchor not found")
    return not problems, f"{n_links} relative links in {len(files)} Markdown files", problems


def _rows(path: Path) -> list[dict]:
    import csv
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def check_arithmetic() -> tuple[bool, str, list[str]]:
    from scipy.stats import binomtest

    problems = []
    rows = {r["comparison"]: r for r in _rows(SUMMARY)}
    for name, r in rows.items():
        n, w, l, t = (int(r[k]) for k in ("N_pair", "W", "L", "T"))
        theta, lo, hi = (float(r[k]) for k in ("theta", "theta_bca95_lo", "theta_bca95_hi"))
        p = float(r["p_exact_two_sided"])
        if w + l + t != n:
            problems.append(f"{name}: W + L + T = {w + l + t}, N = {n}")
        if abs(theta - (w + 0.5 * t) / n) > TOL:
            problems.append(f"{name}: theta {theta} does not equal (W + 0.5 T) / N")
        if not lo <= theta <= hi:
            problems.append(f"{name}: theta {theta} outside its interval {lo}-{hi}")
        if int(r["discordant_W_plus_L"]) != w + l:
            problems.append(f"{name}: discordant count is not W + L")
        p_new = binomtest(w, w + l, 0.5).pvalue if w + l else 1.0
        if abs(p - p_new) > TOL:
            problems.append(f"{name}: exact p {p} differs from recomputed {p_new}")
        for arm in ("A", "B"):
            ev, det, rate = int(r[f"{arm}_eval_n"]), int(r[f"{arm}_detected_n"]), float(r[f"{arm}_detection_rate"])
            if abs(rate - det / ev) > TOL:
                problems.append(f"{name}: {arm} detection rate is not detected / evaluable")

    gates = json.loads(GATES.read_text(encoding="utf-8"))
    h1 = rows["H1"]
    h1_rejected = float(h1["p_exact_two_sided"]) < gates["alpha"]
    h1_up = float(h1["theta"]) > 0.5
    if gates["H1_rejected_two_sided"] != h1_rejected:
        problems.append("gate decisions: H1 rejection does not follow from its p-value")
    if gates["H1_theta_gt_0_5"] != h1_up:
        problems.append("gate decisions: H1 direction does not follow from its theta")
    if gates["stage2_gate_open"] != (h1_rejected and h1_up):
        problems.append("gate decisions: stage 2 gate does not follow from H1")
    if not gates["stage2_gate_open"] and (gates["M1_tested_confirmatorily"] or gates["stage3_gate_open"] or gates["H2_H3_Holm_applied"]):
        problems.append("gate decisions: a later stage is open although stage 2 is closed")

    sens = _rows(SENS)
    for r in sens:
        tag = f"sensitivity {r['scenario']} {r['comparison']}"
        n, w, l, t = (int(r[k]) for k in ("N", "W", "L", "T"))
        theta, lo, hi = (float(r[k]) for k in ("theta", "theta_bca95_lo", "theta_bca95_hi"))
        if w + l + t != n:
            problems.append(f"{tag}: W + L + T does not equal N")
        if abs(theta - (w + 0.5 * t) / n) > TOL:
            problems.append(f"{tag}: theta does not equal (W + 0.5 T) / N")
        if not lo <= theta <= hi:
            problems.append(f"{tag}: theta outside its interval")
        if r.get("sensitivity_p_value", "").strip():
            problems.append(f"{tag}: carries a p-value")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name, r in rows.items():
        m = re.search(rf"^\| {name} \|[^|]*\| (\d+) \| ([\d/]+) \| ([\d.]+) \| ([\d.]+)–([\d.]+) \| ([\d.]+)\*? \|", readme, re.M)
        if not m:
            problems.append(f"README.md: no results-table row for {name}")
            continue
        expected = (r["N_pair"], f"{r['W']}/{r['L']}/{r['T']}", f"{float(r['theta']):.3f}",
                    f"{float(r['theta_bca95_lo']):.3f}", f"{float(r['theta_bca95_hi']):.3f}",
                    f"{float(r['p_exact_two_sided']):.4f}")
        if m.groups() != expected:
            problems.append(f"README.md: {name} row {m.groups()} differs from the summary {expected}")
    h1_values = [f"{float(h1['theta']):.3f}", f"{float(h1['theta_bca95_lo']):.3f}",
                 f"{float(h1['theta_bca95_hi']):.3f}", f"{float(h1['p_exact_two_sided']):.4f}"]
    checked_docs = 0
    for rel in SUMMARY_DOCS:
        path = ROOT / rel
        if not path.exists():
            continue
        checked_docs += 1
        text = path.read_text(encoding="utf-8")
        missing = [v for v in h1_values if v not in text]
        if missing:
            problems.append(f"{rel}: H1 value(s) {missing} not quoted")
    detail = (f"{len(rows)} confirmatory rows, gate decisions, {len(sens)} sensitivity rows, "
              f"README results table, H1 values in {checked_docs} summary documents")
    return not problems, detail, problems


# Seed offsets passed to summarize_pairs() in src/sensitivity_analysis.py: fixed
# offsets for the first four scenarios, 500 + 20 x (scenarios already summarised)
# for the four refitted scenarios, and 900 for the realised-minute M1 match.
SENSITIVITY_SEED_OFFSETS = {
    "phase2_only": 100,
    "common_cohort_all_primary_arms_Cfloor16": 200,
    "coarse_calibration_resolution_le_1pm": 300,
    "exclude_multiple_episode_rows": 400,
    "alert_budget_B1": 580,
    "alert_budget_B4": 600,
    "todz_without_time_of_day_normalisation": 620,
    "rolling_tau_recalibration": 640,
    "m1_realised_minute_matched": 900,
}
COMPARISON_ORDER = ["H1", "M1", "H2", "H3"]


def _published_bootstrap(path: Path):
    """Load bca_ci and the bootstrap constants from a published script without running it."""
    import numpy as np
    from statistics import NormalDist

    tree = ast.parse(path.read_text(encoding="utf-8"))
    ns = {"np": np, "NormalDist": NormalDist}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in {"BOOT_N", "BOOT_SEED"}):
            ns[node.targets[0].id] = ast.literal_eval(node.value)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "bca_ci")
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(path), "exec"), ns)
    return ns["bca_ci"], ns["BOOT_SEED"]


def check_intervals() -> tuple[bool, str, list[str]]:
    import numpy as np

    def vector(w, l, t):
        return np.r_[np.ones(w), np.zeros(l), np.full(t, 0.5)]

    problems = []
    bca, seed = _published_bootstrap(ROOT / "evidence" / "scripts" / "reveal_primary_e3_confirmatory_results_fixed.py")
    rows = {r["comparison"]: r for r in _rows(SUMMARY)}
    for j, name in enumerate(COMPARISON_ORDER):
        r = rows[name]
        lo, hi = bca(vector(int(r["W"]), int(r["L"]), int(r["T"])), seed=seed + j)
        if abs(lo - float(r["theta_bca95_lo"])) > 1e-12 or abs(hi - float(r["theta_bca95_hi"])) > 1e-12:
            problems.append(f"{name}: recomputed {lo}-{hi}, published {r['theta_bca95_lo']}-{r['theta_bca95_hi']}")
    bca_s, seed_s = _published_bootstrap(ROOT / "src" / "sensitivity_analysis.py")
    sens = _rows(SENS)
    for r in sens:
        tag = f"{r['scenario']} {r['comparison']}"
        if r["scenario"] not in SENSITIVITY_SEED_OFFSETS:
            problems.append(f"{tag}: no known seed offset")
            continue
        s = seed_s + SENSITIVITY_SEED_OFFSETS[r["scenario"]] + COMPARISON_ORDER.index(r["comparison"])
        lo, hi = bca_s(vector(int(r["W"]), int(r["L"]), int(r["T"])), s)
        if abs(lo - float(r["theta_bca95_lo"])) > 1e-12 or abs(hi - float(r["theta_bca95_hi"])) > 1e-12:
            problems.append(f"sensitivity {tag}: recomputed {lo}-{hi}, published {r['theta_bca95_lo']}-{r['theta_bca95_hi']}")
    return not problems, f"{len(rows)} confirmatory and {len(sens)} sensitivity intervals", problems


def check_energy() -> tuple[bool, str, list[str]]:
    sys.path.insert(0, str(ROOT / "src"))
    import modelled_energy_match

    archived = ROOT / "results" / "modelled_energy_match_audit.json"
    fresh = json.dumps(modelled_energy_match.audit(), indent=2) + "\n"
    same = fresh.encode("utf-8") == archived.read_bytes()
    problems = [] if same else [f"recomputed audit differs from {archived.relative_to(ROOT)}"]
    return same, f"recomputed audit compared with {archived.relative_to(ROOT)}", problems


def check_tables() -> tuple[bool, str, list[str]]:
    if importlib.util.find_spec("tabulate") is not None:
        return False, "not run", [
            "the optional 'tabulate' package is installed; the archived Markdown tables were "
            "written without it, so uninstall it (or use environment/publication-requirements.txt)"]
    problems = []
    with tempfile.TemporaryDirectory() as home:
        run = Path(home) / "rq1" / "results" / "primary_e3_run_83cc8d1"
        for src in (SUMMARY, SENS):
            dst = run / src.parent.name / src.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        env = dict(os.environ, HOME=home, MPLBACKEND="Agg")
        proc = subprocess.run([sys.executable, str(ROOT / "src" / "make_final_tables_figures.py")],
                              env=env, cwd=home, capture_output=True, text=True)
        if proc.returncode != 0:
            return False, "script failed", [proc.stderr.strip()[-2000:]]
        out = run / "final_tables_figures"
        compared = sorted(p.name for p in TABLES.iterdir() if p.suffix in {".csv", ".md", ".txt"})
        for name in compared:
            new = out / name
            if not new.exists():
                problems.append(f"{name} was not regenerated")
            elif new.read_bytes() != (TABLES / name).read_bytes():
                problems.append(f"{name} differs from the archived copy")
        figures = sorted(p.name for p in TABLES.iterdir() if p.suffix in {".png", ".pdf"})
        redrawn = [f for f in figures if (out / f).exists() and (out / f).stat().st_size > 0]
        if len(redrawn) != len(figures):
            problems.append("not every figure was redrawn")
    detail = f"{len(compared)} table and digest files compared byte for byte; {len(redrawn)} figure files redrawn, not compared"
    return not problems, detail, problems


def check_power() -> tuple[bool, str, list[str]]:
    archived = json.loads((ROOT / "results" / "power_sim_frozen_n38.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "power_rays.json"
        proc = subprocess.run([sys.executable, str(ROOT / "src" / "power_sim.py"), "--audited", "--reps", "4000",
                               "--sweep-p-b", "0.40,0.50,0.60", "--out", str(out)],
                              cwd=tmp, capture_output=True, text=True)
        if proc.returncode != 0:
            return False, "script failed", [proc.stderr.strip()[-2000:]]
        fresh = json.loads(out.read_text(encoding="utf-8"))["ray_cells"]
    old = archived["ray_cells"]
    problems = []
    if len(fresh) != len(old):
        problems.append(f"{len(fresh)} cells recomputed, {len(old)} archived")
    fields = 0
    for i, (a, b) in enumerate(zip(fresh, old)):
        flat_a = {**{k: v for k, v in a.items() if k != "mde"}, **{f"mde.{k}": v for k, v in (a.get("mde") or {}).items()}}
        flat_b = {**{k: v for k, v in b.items() if k != "mde"}, **{f"mde.{k}": v for k, v in (b.get("mde") or {}).items()}}
        fields += len(flat_b)
        if flat_a != flat_b:
            diff = sorted(k for k in set(flat_a) | set(flat_b) if flat_a.get(k) != flat_b.get(k))
            problems.append(f"cell {i} ({b['dependence']}, p_B {b['p_B']}): differs in {diff}")
    return not problems, f"{len(fresh)} effect-ray cells, {fields} recorded fields compared", problems


CHECKS = {"links": check_links, "arithmetic": check_arithmetic, "intervals": check_intervals,
          "energy": check_energy, "tables": check_tables, "power": check_power}
DEFAULT = ["links", "arithmetic", "intervals", "energy", "tables"]


def main(argv: list[str]) -> int:
    selected = argv or DEFAULT
    unknown = [s for s in selected if s not in CHECKS]
    if unknown:
        print(f"unknown check(s): {', '.join(unknown)}; choose from {', '.join(CHECKS)}")
        return 2
    failed = 0
    for name in selected:
        ok, detail, problems = CHECKS[name]()
        print(f"{name}: {'PASS' if ok else 'FAIL'} ({detail})")
        for p in problems:
            print(f"  - {p}")
        failed += not ok
    print("ALL CHECKS PASSED" if not failed else f"{failed} CHECK GROUP(S) FAILED")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

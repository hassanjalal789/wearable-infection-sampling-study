#!/usr/bin/env bash
# Phase 1 acquisition, inventory and cohort pipeline.  Run from the repo root.
# Steps 1-2 need network access to storage.googleapis.com.
#   ./run_phase1.sh --preflight   verify every input and command, compute nothing
#   ./run_phase1.sh               run the pipeline
set -euo pipefail
PREFLIGHT=0
[ "${1:-}" = "--preflight" ] && PREFLIGHT=1

P1_URL="https://storage.googleapis.com/gbsc-gcp-project-ipop_public/COVID-19/COVID-19-Wearables.zip"
P2_URL="https://storage.googleapis.com/gbsc-gcp-project-ipop_public/COVID-19-Phase2/COVID-19-Phase2-Wearables.zip"
INV="results/inventory_phase1.parquet results/inventory_phase2.parquet"

die() { echo "FATAL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1 || die "missing command: $1"; }

preflight() {
  echo "== preflight =="
  for c in curl unzip sha256sum python3 git; do have "$c"; done
  python3 - <<'PY' || die "python dependencies missing"
import numpy, pandas, scipy, pytest  # noqa
print("  python deps ok:", numpy.__version__, pandas.__version__)
PY
  for f in src/phase1_inventory.py src/build_device_map.py src/build_cohort.py \
           src/coverage_diagnostic.py src/check_overlap.py src/calibration_resolution.py \
           src/check_device_coverage.py; do
    [ -f "$f" ] || die "missing script: $f"
  done
  mkdir -p data_raw results docs
  echo "  scripts present"
  for F in COVID-19-Wearables.zip COVID-19-Phase2-Wearables.zip; do
    if [ -s "data_raw/$F" ]; then
      echo "  $F already present ($(wc -c < "data_raw/$F") bytes) — will be used as supplied"
    else
      echo "  $F absent — will be downloaded (needs network egress)"
    fi
  done
  [ -f results/onset_labels.csv ] \
    && echo "  onset_labels.csv present" \
    || echo "  WARNING: results/onset_labels.csv absent — required first; the device
      gate is scoped to the candidates it names"
  [ -f results/device_map_external.csv ] \
    && echo "  curated external device provenance present" \
    || echo "  NOTE: no results/device_map_external.csv — Phase 1 rows will be UNKNOWN"
  echo "  preflight OK"
}

preflight
[ "$PREFLIGHT" = "1" ] && { echo "preflight only; nothing computed."; exit 0; }

echo "== 1-2. acquire (or accept manually supplied archives) =="
cd data_raw
ACQ=""
for spec in "COVID-19-Wearables.zip|$P1_URL" "COVID-19-Phase2-Wearables.zip|$P2_URL"; do
  F="${spec%%|*}"; U="${spec##*|}"
  if [ -s "$F" ]; then
    echo "  $F present ($(wc -c < "$F") bytes) — NOT downloading, NOT overwriting"
    ACQ="manually_supplied_existing_archive"
  elif [ -e "$F" ]; then
    die "$F exists but is EMPTY. Remove it or replace it with the real archive;
  this script will never overwrite a file that is already there."
  else
    echo "  $F absent — downloading"
    curl -fL --retry 3 -o "$F" "$U"
    [ -n "$ACQ" ] || ACQ="downloaded"
  fi
done

echo "  verifying ZIP integrity"
for F in COVID-19-Wearables.zip COVID-19-Phase2-Wearables.zip; do
  [ -s "$F" ] || die "$F is missing or empty after acquisition"
  unzip -t "$F" > "../docs/${F%.zip}_integrity.txt" 2>&1 \
    || die "unzip -t failed for $F — the archive is truncated or corrupt.
  See docs/${F%.zip}_integrity.txt. Re-transfer the file; do not proceed."
  echo "    $F integrity OK"
done

{ date -u +"verified_utc=%Y-%m-%dT%H:%M:%SZ"
  echo "acquisition_method=${ACQ:-downloaded}"
  echo "url_phase1=$P1_URL"; echo "url_phase2=$P2_URL"
  sha256sum ./*.zip; ls -l ./*.zip; } | tee ../docs/dataset_checksums.txt

unzip -l COVID-19-Wearables.zip        > ../docs/phase1_ziplist.txt
unzip -l COVID-19-Phase2-Wearables.zip > ../docs/phase2_ziplist.txt
mkdir -p phase1 phase2
unzip -q -o COVID-19-Wearables.zip        -d phase1
unzip -q -o COVID-19-Phase2-Wearables.zip -d phase2
chmod -R a-w phase1 phase2
cd ..

echo "== 3. inventory =="
python3 src/phase1_inventory.py --root data_raw/phase1 --phase phase1
python3 src/phase1_inventory.py --root data_raw/phase2 --phase phase2

echo "== 4. onset / infection metadata (required BEFORE the device gate) =="
[ -f results/onset_labels.csv ] || die "results/onset_labels.csv is required and must
  come first: the device gate is scoped to the infection-positive candidates it names.
  See src/find_onset_labels.md. Onset dates are NEVER inferred from physiology."
CANDS=$(python3 - <<'PY'
import pandas as pd
print(len(pd.read_csv("results/onset_labels.csv")))
PY
)
echo "  $CANDS candidate infection cases listed"

echo "== 5. device map, then a gate scoped to those candidates only =="
EXT=""
[ -f results/device_map_external.csv ] && EXT="--external results/device_map_external.csv"
python3 src/build_device_map.py --inventory $INV $EXT
[ -f results/device_map.csv ] || die "device_map.csv was not produced"
python3 src/check_device_coverage.py --device-map results/device_map.csv \
        --onsets results/onset_labels.csv \
  || die "device gate failed for candidate infection-positive participants (see above).
  Unrelated archive participants may remain UNKNOWN; only candidates block."

echo "== 6-11. cohort, C_p, C_min, final N =="
python3 src/build_cohort.py --inventory $INV --onsets results/onset_labels.csv \
        --device-map results/device_map.csv

echo "== 11. coverage diagnostic (three populations) =="
python3 src/coverage_diagnostic.py --inventory $INV \
        --device-map results/device_map.csv --cohort results/cohort.json

echo "== 12. overlap =="
HR=""
[ -f results/nightly_rhr.parquet ] && HR="--hr-series results/nightly_rhr.parquet"
[ -z "$HR" ] && echo "  NOTE: no results/nightly_rhr.parquet — verdict will be
  UNDETERMINABLE; coverage similarity is supplementary only, never an HR identity test."
python3 src/check_overlap.py $INV $HR

echo "== 13. property tests (synthetic only) =="
python3 -m pytest tests/ -q

echo "== done. Outputs in results/ and docs/. Prereg is NOT frozen. =="

# Verification report

*Publication-stage report, begun on 25 September 2026, for research I designed and conducted. It records the verification I carried out for this repository: what was checked, how, in which environment, what it showed, and what could not be checked. It is new writing. Each section is dated and describes the files as they stood when it was added; the [verification log](../evidence/VERIFICATION_LOG.md) keeps the individual entries, and the [reproducibility guide](REPRODUCIBILITY.md) gives the commands.*

## What verification means here

Four kinds of check are kept apart throughout:

| Kind | Meaning | Done? |
|---|---|---|
| Inspecting archived results | Reading and hashing the result files preserved from the research | Yes |
| Recomputing from published files | Recomputing a published number, table or interval from other published files and published code | Yes, for every aggregate where the inputs are published |
| Re-running tests | Running the published test suite on synthetic inputs, published aggregates and, for Gate B, third-party tables | Yes |
| Executing the raw-data analysis | Running the primary pipeline on the source archives | No; not possible from this repository |

No new scientific analysis was carried out for this publication. Nothing here changes a result reported by the research.

## 1. Fresh verification, 25 September 2026

**Environment.** A fresh clone, and a new virtual environment built from [`environment/publication-requirements.txt`](../environment/publication-requirements.txt): Python 3.13.13 on Linux x86-64, NumPy 2.4.4, pandas 3.0.2, SciPy 1.17.1, Matplotlib 3.10.9, PyArrow 25.0.1, openpyxl 3.1.5, pytest 9.1.1, without the optional `tabulate` package. The commands were run from the repository root on the files of the revision that added this section.

| Check | Command | Outcome |
|---|---|---|
| File integrity | `sha256sum -c evidence/SHA256SUMS.txt` | Every listed file OK |
| Links | `python src/check_public_package.py links` | Every relative link and anchor resolves |
| Published arithmetic | `python src/check_public_package.py arithmetic` | Counts, θ, exact p-values, detection rates and gate decisions consistent for H1, M1, H2 and H3; counts and θ consistent for all 33 sensitivity rows, none with a p-value; the README table and summary documents quote the published values |
| Bootstrap intervals | `python src/check_public_package.py intervals` | All 4 confirmatory and 33 sensitivity BCa intervals recomputed exactly from the published counts and recorded seeds |
| Energy audit | `python src/check_public_package.py energy` | Recomputed audit byte-for-byte identical to the archived file |
| Result tables and figures | `python src/check_public_package.py tables` | Three CSV tables, three Markdown tables and the digest byte-for-byte identical; six figure files redrawn and, compared side by side, visually identical |
| Test suite | `python -m pytest tests/ -q` | 174 passed, 0 failed |
| Chronology | `python src/validate_chronology.py` | No unresolved finding |
| Gate B | Both workbooks supplied, checked first against the SHA-256 values in the [data availability guide](DATA_AVAILABILITY.md); `python -m pytest tests/ -q`, then `python src/gate_b_compute.py` | 181 passed; the regenerated result file has the SHA-256 recorded for the preserved research version, and equals the published copy apart from the removed identifier list |
| Power | `python src/check_public_package.py power` | All 12 effect-ray cells identical to the archived frozen calculation in all 204 recorded fields |
| Runner guard | `python src/primary_e3_experiment.py --preflight` | Stopped as designed: `Energy freeze commit 4023717 is not an ancestor of HEAD.` |
| Acquisition preflight | `./run_phase1.sh --preflight` | Dependencies and scripts present; archives, onset labels and external device map absent; nothing computed |

**A correction found by this verification.** Earlier publication notes said the BCa intervals could not be recomputed because they need withheld participant-level results. That was wrong. The confirmatory script and the sensitivity script both bootstrap a vector built only from each comparison's win, loss and tie counts, so the published counts and the scripts' recorded seeds determine every interval. All 37 were recomputed exactly. The affected statements have been corrected, and the [publication notes](PUBLICATION_NOTES.md#material-corrections) record the correction.

**Not verified.** The raw-data analysis, Gate A and the 432-cell power surface were not re-run; the [reproducibility guide](REPRODUCIBILITY.md) sets out why. The figures were compared by eye, not byte for byte, because the archived figures were drawn with a newer Matplotlib version. Passing tests and recomputed aggregates show consistency between published files and published code; they do not show that the withheld per-participant results are correct.

**Continuous checks.** [`.github/workflows/public-checks.yml`](../.github/workflows/public-checks.yml) runs file integrity, the chronology validator, `python src/check_public_package.py` and the test suite on GitHub for every change to the main branch. Its runs are recorded in a later section of this report once they exist.

## 2. Method and reader review, 25 September 2026

**Methods against code and amendments.** Each executed rule was traced to the amendment that set it, the function or constant that implements it, the tests that exercise it and, where recorded, the run manifest. The [method traceability review](METHOD_TRACEABILITY.md) gives the matrix and 18 findings. The main ones: daylight-saving transition days were not excluded as v1.1 §6.12 requires; the paired warning-time difference, the same-day and at-or-before tabulations, and part of the v1.1 reporting set were not produced; and the runner's calibration exclusion windows use onset dates only. None changes a published number. Two could in principle affect individual thresholds or alerts, and their effect cannot be measured from the published files.

**Public numerical claims.** Every quoted value of the primary and estimation-only comparisons, the sensitivity table, the cohort flow, the power table, the Gate A and Gate B tables, the energy errors, and the coverage, schema and device counts was compared with the published result files. No value differed. The README results table and the H1 values in the overview, summary and results documents are also checked automatically by `python src/check_public_package.py arithmetic`.

**Corrections made.** The [methods guide](METHODS_GUIDE.md) described two A1 reporting items as carried out; it now says they were not produced. The research timeline said the baseline protocol is undated; its header states a revision date of 31 August 2026. Status statements written before later material was published were brought up to date, among them the contribution statement's note on third-party notices, changed with my specific approval. The [publication notes](PUBLICATION_NOTES.md#material-corrections) list the material corrections.

**Readability, figures and links.** The three published figures have alt text that states their values; each was compared with its image. Every relative link and anchor resolves. A one-page [overview](OVERVIEW.md) and citation metadata, [`CITATION.cff`](../CITATION.cff), validated against the Citation File Format 1.2.0 schema, were added. No PDF was produced: the Markdown overview is the one-page summary, and an unchecked binary would add nothing.

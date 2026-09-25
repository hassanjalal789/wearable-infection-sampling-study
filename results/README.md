# Results

*Publication-stage note, written on 24 September 2026 and extended on 25 September 2026. Every other file under `results/` is an archived output of the research. All but two are byte-identical to the versions I preserved during the research process; I have not retrospectively edited them for publication. The two exceptions are sanitized copies, described [below](#reproduction-and-power-records). This note is new writing. No output generated during publication checks is stored here.*

## The authoritative run

The primary analysis was executed twice. **`primary_e3_run_83cc8d1/` is the corrected run and the only one used for any result in this repository.** The earlier run, `primary_e3_run_d1d5265`, was superseded by the Phase-2 step-data correction in [amendment A6](../docs/prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md) before any outcome was inspected. Only its run manifest is published, at [`primary_e3_run_d1d5265/run_manifest.json`](primary_e3_run_d1d5265/run_manifest.json), so that its configuration can be compared with the corrected run's; the [execution excerpts](../evidence/EXECUTION_EXCERPTS.md) set out the comparison. Its outputs are participant-level and are not published.

## What is here

| Path | Contents |
|---|---|
| `primary_e3_run_83cc8d1/run_manifest.json` | The corrected run's configuration: commit, energy-freeze commit, scenario, budget, burst structure, alert budget, calibration floor and stop, endpoint window, Phase-2 step semantics, cohort size and input archive sizes |
| `primary_e3_run_83cc8d1/confirmatory_analysis/` | The confirmatory summary for H1, M1, H2 and H3, and the fixed-sequence gate decisions |
| `primary_e3_run_83cc8d1/sensitivity_analysis/` | The post-primary sensitivity summary and its manifest; estimation-only, with no p-values |
| `primary_e3_run_83cc8d1/final_tables_figures/` | Result tables, the results digest, and three figures in PNG and PDF |
| `modelled_energy_match_audit.json` | The pre-outcome energy feasibility audit |
| `primary_e3_run_d1d5265/run_manifest.json` | Configuration of the superseded first run; no outputs |
| `gate_a/`, `gate_a_summary.json` | Gate A: upstream code against its own outputs |
| `gate_b_results.json` | Gate B: published cohort numbers rebuilt from the source studies' tables (sanitized copy) |
| `power_sim_frozen_n38.json` | The frozen power calculation at N = 38 |
| `power_sim_output.json`, `power_surface_PLANNING_demo.json`, `power_planning.log`, `power_sim_run.log` | Earlier, non-binding planning runs |
| The other JSON files at this level | Aggregate outputs of the data and cohort stage; see the [data and cohort guide](../docs/DATA_AND_COHORT.md) |

The three `.md` table files are plain-text tables, not Markdown tables. The script writes plain text when an optional table library is not installed, and the archived copies match that plain-text output exactly. The `.csv` files hold the same values.

The PDF figures carry only the plotting library's creator and producer fields and their creation time; the PNG figures carry only the plotting library's software field.

## Reproduction and power records

The [gates and power guide](../docs/REPRODUCTION_GATES_AND_POWER.md) explains these files.

- **`gate_a/`** holds the authoritative Gate A record `gate_a_results.json`, the earlier record it supersedes, `gate_a_results_PRELIMINARY_DO_NOT_USE.json` (published under its own name, which says not to use it), two NightSignal summaries, and the run logs. `gate_a/hrosad_offline.log` is a **sanitized copy**: a private project path is replaced by `<PROJECT_ROOT>` and a participant identifier in an error message by `<participant>`. The other logs are byte-identical; the paths they show are generic system or temporary paths. Empty logs are not published, nor are the logs kept in folders named after an upstream sample participant; the one failure recorded there is shown in the [execution log](../evidence/historical_execution_log.md#74-hros-ad-attempts-in-the-current-environment).
- **`gate_b_results.json`** is a **sanitized copy**: the preserved version also lists the 32 participant identifiers of the source study's analysed cases, and that list is removed. Every other line is unchanged.
- **Withheld from Gate A and Gate B:** detection rows, anomaly rows, per-night signals and plots generated from the upstream repositories' sample participants, and the Gate B audit files and table extracts that print rows of the source studies' supplementary tables. Row counts for the Gate A outputs, and SHA-256 values for the two reproduced WearableDetection outputs, are in `gate_a_results.json`.

## What is withheld

Every file in the corrected run that has a row per participant is withheld, because each names participants: the per-arm outcomes, the pair-by-pair results, the daily schedule checks, the daily M1 feasibility record, the participant input summary, the per-participant sensitivity outcomes and pair results, and the M1 minute-matching record. The primary input diagnostic is withheld for the same reason. The [manifest](../evidence/PUBLICATION_MANIFEST.csv) lists each group.

## What was checked for this publication

On 24 September 2026:

- every published file was hashed against the version I preserved;
- θ and the exact two-sided p-value were recomputed from the published win, loss and tie counts for all four comparisons, and θ for all 33 sensitivity rows, with no discrepancy; every point estimate lies inside its interval;
- the result tables and digest were regenerated from the two published summary files with the published script, and matched the archived copies byte for byte;
- the figures were regenerated the same way and matched the archived ones visually. They are not byte-identical, because the plotting library version differs and image rendering is not bit-stable across versions;
- the BCa intervals were **not** recomputed: they need the withheld participant-level results.

On 25 September 2026:

- the 12 effect-ray cells of `power_sim_frozen_n38.json` were re-run with the published script, seed and replicate count and matched in every field; the surface was not re-run;
- `gate_b_results.json` was regenerated from the two source workbooks, checked against the checksums in my preserved research record, and matched the preserved version byte for byte before the identifier list was removed from the published copy;
- every other archived file added on this date was hashed against the version I preserved.

The [verification log](../evidence/VERIFICATION_LOG.md) gives the environment and commands.

# Results

*Publication-stage note, written on 24 September 2026. Every other file under `results/` is an archived output of the research, byte-identical to the version I preserved during the research process; I have not retrospectively edited any of them for publication. This note is new writing. No output generated during publication checks is stored here.*

## The authoritative run

The primary analysis was executed twice. **`primary_e3_run_83cc8d1/` is the corrected run and the only one used for any result in this repository.** The earlier run, `primary_e3_run_d1d5265`, was superseded by the Phase-2 step-data correction in [amendment A6](../docs/prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md) before any outcome was inspected. Its outputs are participant-level and are not published; how its configuration compares with the corrected run is set out in the [execution excerpts](../evidence/EXECUTION_EXCERPTS.md).

## What is here

| Path | Contents |
|---|---|
| `primary_e3_run_83cc8d1/run_manifest.json` | The corrected run's configuration: commit, energy-freeze commit, scenario, budget, burst structure, alert budget, calibration floor and stop, endpoint window, Phase-2 step semantics, cohort size and input archive sizes |
| `primary_e3_run_83cc8d1/confirmatory_analysis/` | The confirmatory summary for H1, M1, H2 and H3, and the fixed-sequence gate decisions |
| `primary_e3_run_83cc8d1/sensitivity_analysis/` | The post-primary sensitivity summary and its manifest; estimation-only, with no p-values |
| `primary_e3_run_83cc8d1/final_tables_figures/` | Result tables, the results digest, and three figures in PNG and PDF |
| `modelled_energy_match_audit.json` | The pre-outcome energy feasibility audit |
| The other JSON files at this level | Aggregate outputs of the data and cohort stage; see the [data and cohort guide](../docs/DATA_AND_COHORT.md) |

The three `.md` table files are plain-text tables, not Markdown tables. The script writes plain text when an optional table library is not installed, and the archived copies match that plain-text output exactly. The `.csv` files hold the same values.

The PDF figures carry only the plotting library's creator and producer fields and their creation time; the PNG figures carry only the plotting library's software field.

## What is withheld

Every file in the corrected run that has a row per participant is withheld, because each names participants: the per-arm outcomes, the pair-by-pair results, the daily schedule checks, the daily M1 feasibility record, the participant input summary, the per-participant sensitivity outcomes and pair results, and the M1 minute-matching record. The primary input diagnostic is withheld for the same reason. The [manifest](../evidence/PUBLICATION_MANIFEST.csv) lists each group.

## What was checked for this publication

On 24 September 2026:

- every published file was hashed against the version I preserved;
- θ and the exact two-sided p-value were recomputed from the published win, loss and tie counts for all four comparisons, and θ for all 33 sensitivity rows, with no discrepancy; every point estimate lies inside its interval;
- the result tables and digest were regenerated from the two published summary files with the published script, and matched the archived copies byte for byte;
- the figures were regenerated the same way and matched the archived ones visually. They are not byte-identical, because the plotting library version differs and image rendering is not bit-stable across versions;
- the BCa intervals were **not** recomputed: they need the withheld participant-level results.

The [verification log](../evidence/VERIFICATION_LOG.md) gives the environment and commands.

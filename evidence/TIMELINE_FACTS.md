# Timeline fact file

*Publication-stage record, written on 20 September 2026. Every row states one dated or countable fact about the research chronology and names the preserved project record it comes from. It exists so that the [research timeline](../docs/RESEARCH_TIMELINE.md) can be checked line by line rather than taken on trust. Facts I could not establish from a preserved record are listed at the end as unestablished, not estimated.*

## How dates were established

Three kinds of source were used, and they are not equally strong:

| Source kind | What it establishes | What it does not |
|---|---|---|
| A date written in a document's own header | The date I recorded when writing it | Not an independent timestamp; no external registry holds these documents |
| An ordering in the preserved audit trail | The sequence in which work was committed | Not a wall-clock date on its own |
| A value inside a preserved result or rule record | What the executed analysis actually produced | Nothing about when it was read |

No date in this file is derived from file modification times, and none is inferred from a date elsewhere in the chain.

## Document dates, as recorded in each document

| Document | Recorded date | Status marker carried in the document |
|---|---|---|
| [`prereg-v1.1.md`](../docs/prereg-v1.1.md) | None stated | `DRAFT — NOT FROZEN`; the `prereg-v1` tag required by its own §0.2 was never created |
| [A1](../docs/prereg-v1.2-amendment.md) | Issued 31 August 2026 | `DRAFT — NOT FROZEN` |
| [A2](../docs/prereg-v1.2-amendment-A2.md) | Issued 31 August 2026 | `DRAFT — NOT FROZEN` |
| [A3](../docs/prereg-v1.2-amendment-A3.md) | Issued 31 August 2026, with a correction dated 1 September 2026 | `DRAFT — NOT FROZEN` |
| [Pre-outcome checkpoint](../docs/PRE_OUTCOME_CHECKPOINT.md) | 1 September 2026 | Records that no schedule-performance outcomes had been inspected |
| [A4](../docs/prereg-v1.2-amendment-A4-no-hardware.md) | 2 September 2026 | `PROSPECTIVE — to be frozen before any schedule-performance outcome analysis` |
| [A5](../docs/prereg-v1.2-amendment-A5-runner-operationalization.md) | 2 September 2026 | `PROSPECTIVE — must be committed before any real S1–S6 schedule-performance outcome is generated` |
| [A6](../docs/prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md) | 2 September 2026 | `POST-GENERATION / PRE-SCIENTIFIC-OUTCOME-INSPECTION CORRECTION` |
| [A7](../docs/prereg-v1.2-amendment-A7-sensitivity-operationalization.md) | 4 September 2026 | `POST-PRIMARY-OUTCOME OPERATIONALIZATION; sensitivity-only, never confirmatory` |

The status markers are the load-bearing part of this table. A4 and A5 declare themselves prospective; A6 declares that outputs existed but no scientific outcome had been inspected; A7 declares that the primary result was already known.

## Execution sequence, from the preserved audit trail

The preserved audit trail records eight commits. In chronological order:

| Order | Recorded subject |
|---|---|
| 1 | pre-outcome data and reproduction checkpoint |
| 2 | freeze hardware energy measurement protocol |
| 3 | amend preregistration to modelled energy design |
| 4 | freeze pre-outcome modelled energy parameters and budgets |
| 5 | freeze primary E3 experiment runner before outcomes |
| 6 | correct Phase2 sparse step semantics before outcome inspection |
| 7 | freeze post-primary sensitivity analysis plan |
| 8 | add final results tables and figures |

This ordering is what establishes that the energy parameters were frozen before the runner, that the runner was frozen before any outcome, that the step-semantics correction came before outcome inspection, and that the sensitivity plan was frozen after. It carries no wall-clock times, so it constrains order, not duration.

## Values fixed before any outcome was inspected

From the pre-outcome checkpoint dated 1 September 2026:

| Quantity | Value |
|---|---|
| Full regression suite | 140 tests passed |
| Final primary base cohort | N = 38 |
| `C_min` | 28, selected by the prespecified availability-only fallback |
| Retention at `C_min` | 0.7755102041 — the 0.80 floor was **not** met |
| Gate A | Complete, with mixed reproduction |
| Gate B | Six published quantities independently reconstructed |
| Schedule-performance outcomes inspected | None |

From the preserved calibration rule record, which the checkpoint summarises:

| Quantity | Value |
|---|---|
| Participants entering the calibration-days distribution | 49 |
| Candidate minima considered | 28, 42, 61, 91 |
| Retention at each candidate | 0.7755, 0.6327, 0.3469, 0.3061 |
| Retention floor | 0.80, met by no candidate |
| Fallback invoked | Yes, to `C_min` = 28 |
| Calibration-days median (IQR) | 46.0 (34.0–112.0), range 0–407 |

The rule record states in its own words that this is an availability-only rule frozen before any outcome inspection. It reads the distribution of available calibration days and cannot see an alert, a schedule output or a comparison.

From the preserved participant-flow record:

| Phase | Infection-positive | Fitbit with provenance | Unknown or conflicting device | Symptomatic with onset date | Sufficient baseline |
|---|---|---|---|---|---|
| Phase 1 | 32 | 32 | 0 | 30 | 18 |
| Phase 2 | 84 | 49 | 0 | 37 | 31 |

Pre-calibration eligible across both phases: 49. No participant was excluded for an unknown or conflicting device, because none had one.

## The two executions

| | Superseded run | Corrected run |
|---|---|---|
| Recorded status | Real primary E3 outcomes generated | Real primary E3 outcomes generated |
| Energy-freeze commit recorded as ancestor | Same frozen energy commit in both | Same frozen energy commit in both |
| Scenario / budget | CENTRAL / E3 | CENTRAL / E3 |
| Burst count and length | N = 7, 10 minutes | N = 7, 10 minutes |
| Alert budget | 2.0 alert-days per person-month | 2.0 alert-days per person-month |
| `C_floor` | 16 | 16 |
| Calibration stop | Through onset − 28 inclusive | Through onset − 28 inclusive |
| Presymptomatic window | onset − 21 through onset − 1 inclusive | onset − 21 through onset − 1 inclusive |
| Frozen cohort | 38 | 38 |
| Phase-2 step semantics recorded | Not recorded | Recorded explicitly, per A6 |
| Eligible for confirmatory inference | **No** | **Yes** |

The only recorded difference between the two manifests is the Phase-2 step-semantics rule. Everything the two runs hold in common — cohort, scenario, budget, burst structure, alert budget, calibration floor, calibration stop and endpoint window — is identical, which is what makes the correction a data-encoding fix rather than a change of design. Both manifests record that no detection or warning summary was printed during generation.

## Unestablished from the preserved records

These are named rather than estimated:

- **A wall-clock time for either execution.** The audit trail records order and the manifests record configuration; neither carries an execution timestamp.
- **A date for the baseline protocol.** `prereg-v1.1.md` states no date in its header.
- **A date on which each outcome was first read.** The manifests record that no scientific summary was printed during generation, but nothing records when the outputs were subsequently inspected.
- **Overlap between participants in the two source releases.** Recorded as undetermined in the research materials; it is not resolved here.

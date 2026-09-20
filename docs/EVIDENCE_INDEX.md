# Evidence index

*Publication-stage guide, written on 19 September 2026 for research I designed and conducted. It maps the claims this repository makes to the files that support them, and says where the support stops. It is extended as further material is published.*

## How to read this index

A claim is **supported** when a published file in this repository contains the evidence for it. It is **supported privately** when the evidence exists in the preserved project records but the file is not yet published or is not eligible for publication. It is **outstanding** when the check has not been performed for this publication. Nothing below is an independent verification of the research by a third party.

## Study design and executed rules

| Claim | Supporting file | Limit |
|---|---|---|
| The baseline design, its endpoint, hypotheses, gatekeeping and cohort rules | [`prereg-v1.1.md`](prereg-v1.1.md) | A preserved project record, still marked "DRAFT, NOT FROZEN", with unfilled placeholders. Not an independently timestamped registration, and the Git tag its own §0.2 requires was never created. |
| The executed endpoint [onset − 21, onset − 1], the calibration rule, schedule placement, energy accounting and the power treatment | [`prereg-v1.2-amendment.md`](prereg-v1.2-amendment.md) (A1) | Replaces the corresponding v1.1 sections in full; also marked draft. |
| The calibration floor of 16 z-defined days, cohort construction and device provenance | [`prereg-v1.2-amendment-A2.md`](prereg-v1.2-amendment-A2.md) | Supplements A1 and takes precedence where both touch a section. |
| The corrected single-pass baseline, the 90-day lookback, exact M1 matching | [`prereg-v1.2-amendment-A3.md`](prereg-v1.2-amendment-A3.md) | Includes a correction dated 1 September 2026. Measured effects quoted there are on synthetic records, not participant data. |
| Which document set each final rule | [`METHODS_GUIDE.md`](METHODS_GUIDE.md), [`PROTOCOL_INDEX.md`](PROTOCOL_INDEX.md) | Publication-stage writing, checked against the amendments; not itself historical evidence. |
| The runner specification, including evaluability and the executed window | [`prereg-v1.2-amendment-A5-runner-operationalization.md`](prereg-v1.2-amendment-A5-runner-operationalization.md) | Prospective by its own header: written before any schedule-performance outcome was generated. Still marked a project record, not a registration. |
| The Phase-2 step-data correction and why the first run is superseded | [`prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md`](prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md) | The diagnostic counts it reports are input-encoding diagnostics, not results. The superseded run's outputs are not published and appear in no table here. |
| The post-primary sensitivity operationalisation, and which planned analyses were not run | [`prereg-v1.2-amendment-A7-sensitivity-operationalization.md`](prereg-v1.2-amendment-A7-sensitivity-operationalization.md) | **Written after the primary result was known**, and labelled so in its own header. Sensitivity-only; it cannot reopen the closed gate. The sensitivity outputs themselves are not yet published. |
| The state of the work before any outcome was inspected | [`PRE_OUTCOME_CHECKPOINT.md`](PRE_OUTCOME_CHECKPOINT.md) | A contemporaneous record. It asserts that no schedule-performance outcome had been inspected; nothing external corroborates that. |
| The order of design, energy freeze, execution, correction and sensitivity work | [`RESEARCH_TIMELINE.md`](RESEARCH_TIMELINE.md), [`../evidence/TIMELINE_FACTS.md`](../evidence/TIMELINE_FACTS.md) | Dates come from document headers and the preserved audit trail. The audit trail fixes order, not wall-clock time; facts that could not be established are listed as unestablished. |
| Run configuration, the frozen calibration rule, and participant-flow counts | [`../evidence/EXECUTION_EXCERPTS.md`](../evidence/EXECUTION_EXCERPTS.md) | Configuration, decision rules and counts only. No per-participant record, and no output of the superseded run. |

## Energy

| Claim | Supporting file | Limit |
|---|---|---|
| The study reports modelled schedule-attributable rail-level energy, not measured energy | [`prereg-v1.2-amendment-A4-no-hardware.md`](prereg-v1.2-amendment-A4-no-hardware.md) | The amendment is the decision record; it is not a measurement. |
| The parameter values, their sources, and the LOW/CENTRAL/HIGH scenarios | [`modelled_energy_parameter_provenance.md`](modelled_energy_parameter_provenance.md) | Datasheet values and declared engineering assumptions. The duration assumptions are explicitly unmeasured. |
| Those eleven parameters match the configuration the analysis actually read | Publication check, 19 September 2026: 33 comparisons across the three scenarios, all equal | The configuration file itself is **not yet published**, so the check cannot yet be repeated from this repository. |
| The bench protocol was planned and never executed | [`../hardware/measurement_protocol.md`](../hardware/measurement_protocol.md) with its [note](../hardware/README.md) | Supported by A4.1, the protocol's own empty replication record, and the absence of any measurement output in the preserved hardware folder. |
| E3 resolves to seven ten-minute bursts in all three scenarios, so one central outcome analysis was run | [`ENERGY_SCOPE.md`](ENERGY_SCOPE.md) | The feasibility audit it quotes is **not yet published**. Separate LOW and HIGH outcome analyses were never performed. |

## Results

| Claim | Supporting file | Limit |
|---|---|---|
| H1: 8 wins, 12 losses, 10 ties among 30 pairs; θ ≈ 0.433; 95% BCa 0.300–0.583; exact two-sided p ≈ 0.5034 | [`RESULTS_AND_LIMITATIONS.md`](RESULTS_AND_LIMITATIONS.md), transcribed from the archived corrected run | The archived tables and digest are **not yet published**, so the figures cannot yet be checked against source files inside this repository. |
| M1, H2 and H3 values are descriptive because the testing sequence closed after H1 | [`RESULTS_AND_LIMITATIONS.md`](RESULTS_AND_LIMITATIONS.md), [`METHODS_GUIDE.md`](METHODS_GUIDE.md) | Unadjusted values, shown for description only. |
| Detection counts and warning-time medians | [`RESULTS_AND_LIMITATIONS.md`](RESULTS_AND_LIMITATIONS.md) | Warning-time statistics are computed among detected participants only, a different denominator from the paired comparison. |
| The authoritative outputs are the corrected run; an earlier run is superseded | [`METHODS_GUIDE.md`](METHODS_GUIDE.md) §8, [`prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md`](prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md), [`../evidence/EXECUTION_EXCERPTS.md`](../evidence/EXECUTION_EXCERPTS.md) | The two run manifests differ only in the Phase-2 step-semantics field. The superseded run's outputs are not mixed into any table here, and neither run's result files are published yet. |

## Contributions and provenance

| Claim | Supporting file | Limit |
|---|---|---|
| Roles, advice received, and AI assistance | [`CONTRIBUTIONS.md`](CONTRIBUTIONS.md) | The roles listed are as I confirmed them. The preserved records document what was run; they cannot establish who performed each step. |
| What is published, what is excluded, and how privacy is handled | [`PUBLICATION_NOTES.md`](PUBLICATION_NOTES.md), [`../evidence/PUBLICATION_MANIFEST.csv`](../evidence/PUBLICATION_MANIFEST.csv) | Detailed redaction mappings are kept privately with the research evidence. |
| Every archived document here is byte-identical to the version I preserved during the research | Publication check, 19 September 2026: seven documents compared byte for byte | The check establishes content identity with the version I preserved; it does not by itself date when I wrote that version. |

## Outstanding for this publication

- The test suite has not been rerun; the archived report of 159 passing tests is historical until it is.
- No figure has been regenerated, and no aggregate table has been recomputed from raw data.
- The full raw-data analysis has not been rerun; the analysis runner requires an ancestry this repository does not have, which will be documented with the code.
- Reproduction of upstream algorithms was mixed in the archived work, and no negative-control analysis exists.
- Overlap between participants in the two dataset releases could not be determined.

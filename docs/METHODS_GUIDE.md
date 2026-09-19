# Methods guide

*Publication-stage guide, written on 18 September 2026 and extended on 19 September 2026. It states the rules the executed study actually followed and names the preserved document that established each one. The protocol and amendments themselves are published unchanged; this guide is new explanatory writing and is not part of the historical record.*

## How to read the amendment chain

| Layer | Document | Role |
|---|---|---|
| Baseline | [`prereg-v1.1.md`](prereg-v1.1.md) | The original design, still marked "DRAFT, NOT FROZEN". Superseded in the sections listed below. See the [protocol index](PROTOCOL_INDEX.md). |
| A1 | [`prereg-v1.2-amendment.md`](prereg-v1.2-amendment.md) | Replaces §9, §5.b, §7.1–7.5, §8.1–8.4 and §15 of v1.1 **in full**. Its own header is titled "amendment A1 — prereg v1.1 → v1.2". |
| A2 | [`prereg-v1.2-amendment-A2.md`](prereg-v1.2-amendment-A2.md) | Implementation-audit patches. A2 supplements A1, and where both touch the same section A2 takes precedence (stated in A2's header). |
| A3 | [`prereg-v1.2-amendment-A3.md`](prereg-v1.2-amendment-A3.md) | Implementation patches 1–7, including a correction dated 1 September 2026 to the baseline rule. |
| A4 | [`prereg-v1.2-amendment-A4-no-hardware.md`](prereg-v1.2-amendment-A4-no-hardware.md) | Replaces planned bench measurement with a modelled energy design, published with the [parameter provenance record](modelled_energy_parameter_provenance.md) and the [energy scope guide](ENERGY_SCOPE.md). |
| A5–A7 | Not yet published | Runner operationalisation (A5), Phase-2 step semantics (A6) and post-primary sensitivity operationalisation (A7). The sections below that depend on them say so. |

All of these are local design documents, not an external registration; several are still marked draft. Nothing here changes the archived results.

## 1. Pre-symptomatic endpoint

**Final rule.** Pre-symptomatic detection is a first qualifying alert on a day in **[onset − 21, onset − 1]**, so a warning is at least one day. An alert on the onset day itself is *same-day detection*: it does not count toward the primary endpoint and is tabulated separately. For comparison with the source studies, an at-or-before statistic over [onset − 21, onset] is reported, explicitly labelled as such. Warning time is measured from the earliest qualifying alert to onset, and a participant with no qualifying alert is a non-detection handled by the paired comparison rather than by imputing a zero warning.

**Where it comes from.** A1, "Replaces §9 — Primary endpoint". v1.1 §9 had used the onset-inclusive window [onset − 21, onset], which admits a zero-day "pre-symptomatic" warning; A1 records that as the reason for the change. The runner specification A5 (not yet published) implements the narrowed window and evaluates the onset day separately, and the archived run manifest records the same window.

**Also from A1.** The paired difference in warning days is estimated on the detected-under-both subgroup only, with its interval bootstrapped over that subgroup, and is treated as descriptive: it is an outcome-dependent subgroup, so the confirmatory quantity remains θ from the hierarchical comparison, which uses every evaluable paired participant.

## 2. Source-defined cohort

**Final rule.** The cohort is built in two phases (A2.6):

- **Phase A** — device, then infection status, then symptomatic with an onset date, then baseline and source-coverage requirements. No calibration-days filter is applied at this stage. The source-availability calibration count `C_p^src` is then computed, and the minimum `C_min` is chosen from its distribution.
- **Phase B** — the final cohort is Phase A restricted to participants with `C_p^src ≥ C_min`.

Device is never inferred to satisfy a downstream filter: `device_map.csv` records a provenance level per participant, and participants whose device is unknown or conflicting are excluded rather than guessed, with their count shown in the participant-flow table (A2.5). The cohort builder reads the device map and imports nothing from the schedule or detector code, so no schedule-performance quantity can reach the selection (A2.6).

`C_p^src` counts analysable source days strictly before onset − 28 that fall outside **every** infection exclusion window, using the onset date where present and the diagnosis date for asymptomatic episodes (A2.1, A3.5). "Analysable" is the source-level definition from v1.1 §3.1 — at least two hours of observed minutes in each of the night and day windows — and depends only on the archive, never on a schedule.

**What this produced.** A source-defined cohort of 38 participants (10 Phase 1, 28 Phase 2). The archived rule record shows the pre-specified 0.80 retention floor was not met at any candidate minimum and that the fallback minimum of 28 days was used; that record and the participant-flow file are not yet published. See [results and limitations](RESULTS_AND_LIMITATIONS.md) for the step from 38 participants to the 30 evaluable pairs.

## 3. Calibration availability, pairing, and evaluability

These three ideas are easy to confuse, so the final rules are set out separately.

| Quantity | Definition | Used for |
|---|---|---|
| `C_p^src` | Analysable **source** days before onset − 28, outside all infection windows (A2.1, A3.5) | Cohort eligibility only |
| `C_p^a` | An individual arm's **z-defined** days in the calibration interval (A2.1) | Reported per arm; never alters the cohort |
| `C_floor = 16` | Paired-availability threshold (A2.1) | A participant enters a comparison only if **both** arms reach it |

**Why all eligible history is used.** A1 replaces §5.b: all eligible historical negative z-defined days before the evaluation window are used, subject to `C_min`, and v1.1's 28-day cap is removed. A1 also explains why v1.1's 14-day minimum was inadequate: with `C` calibration days, one alert contributes 30.44/`C` alert-days per person-month, so the budget is quantised. At `C` = 14 and a budget of 2 alert-days per person-month, the only admissible outcome is zero alerts — a stricter and participant-varying operating point than the one designed. Sixteen days is the smallest `C` at which a single alert is admissible at that budget, which is where `C_floor` comes from.

**How `C_min` is chosen.** The largest candidate in {28, 42, 61, 91} retaining at least 80% of eligible participants, defaulting to 28 if none qualifies. The rule reads only the distribution of available calibration days: it cannot see an alert, a schedule output or a comparison, and it runs once, immediately after the eligibility audit (A1 §5.b).

**Per-comparison N.** Because pairing is applied per comparison, H1, M1, H2 and H3 may in principle have different N; they are reported side by side rather than merged, and each confirmatory comparison is repeated on the intersection cohort as a sensitivity (A2.1). In the executed run all four comparisons had N = 30.

**Thresholds always meet the budget.** The threshold grid runs from 1.0 to 6.0 and ends with a terminal **+∞**, which produces no alerts and is always admissible. Each participant takes the smallest threshold whose achieved calibration alert rate is within the budget, or +∞ if none is, and the calibration routine asserts that the achieved rate is within budget before returning. Whether the threshold was finite and whether calibration saturated are reported per participant, and the frequency of infinite thresholds is treated as a headline diagnostic (A3.3). The earlier behaviour clamped at 6.0 and kept participants whose realised alert rate exceeded the budget, which would have broken the equal-budget condition the comparison rests on.

**Evaluability** — whether an arm has any z-defined day inside the outcome window, and what happens when it does not — is set by the runner specification A5, which is not yet published.

## 4. Corrected baseline rule

**Final rule (A3.1, as corrected on 1 September 2026).** For a prediction day *d*:

1. take the most recent **28 baseline-eligible days** strictly before *d* and no older than **90 calendar days** — baseline-eligible means the day carries at least the minimum number of retained rest samples, a property that does not itself depend on an earlier baseline;
2. estimate the hour-of-day baseline μ(p,h) from the retained rest samples on those days;
3. compute one historical value per baseline day against that same μ;
4. take the median and MAD of those historical values as location and scale;
5. compute the current day's value against the same μ;
6. `z = (value − median) / max(1.4826 × MAD, 1 bpm)`.

**What v1.1 actually said.** The baseline row of v1.1 §4 defines μ(p, h) as the mean rest heart rate for a participant and hour "over the trailing 28 days", citing the 28-day window of Mishra et al. 2020. The word *valid* is not in that definition: it belongs to a separate exception in v1.1 §6.2, which makes `z` undefined on a day with fewer than 28 trailing valid days.

**How A3 read it, and what it changed.** A3.1 paraphrases §4 as "the trailing 28 valid days" and treats that as the intent — the most recent 28 *valid* days. It records that the first implementation was stricter than either reading: it required 28 valid values inside the preceding 28 *calendar* days, which is close to unachievable at low duty cycles, so part of any difference between schedules would have been the detector's own validity gate rather than sampling placement, exactly the artefact this study exists to avoid. A3.1 resolves the rule to the most recent 28 baseline-eligible days within a 90-calendar-day lookback; that cap is new in A3.1, is recorded there as a new free parameter, and keeps the baseline physiologically current.

The 1 September correction removed a **nested burn-in**: two 28-day requirements had been stacked, so the first usable prediction day arrived at day 57 rather than 29 on a fully valid synthetic record, and information could reach the statistic from before the declared 90-day horizon. A3.1 reports the measured effect of the single-pass fix on that record — first valid day and first z-defined day both at 29, and 122 of 150 z-defined days instead of 94 — and lists the tests added with it, including one that corrupts every sample older than the cap and requires the result to be bit-identical.

## 5. Schedules and matched controls

A1 replaces §7.1–7.5 and states the placement families explicitly: clock-driven arms (S2, S3) use a fixed stride from the window start; the reactive arm (S4) uses an earliest-first causal scan with a rest hold and a skip interval; the seeded random arm (S5) uses rejection-sampled non-overlapping starts; and the counterfactual matched arms (S3ʳ, S6) use an even-spread placement over rest-only starts **with lookahead**. A1 states plainly that S3ʳ and S6 are analysis constructs for the M1 mechanism test, not deployable schedules, because their placement uses an oracle over the day's rest pattern that no real device has.

A3.2 made the M1 matching exact: the placement routine became feasibility-aware, so both arms receive the same burst count whenever that count is achievable, with the guarantee asserted over thousands of synthetic rest patterns rather than claimed.

As noted in the [protocol index](PROTOCOL_INDEX.md), the 10-minute burst length and the per-day budget apply to these burst-based arms; S1 keeps all observed minutes as the continuous reference and is not energy-matched.

## 6. Energy assumptions

A1 replaces §8.1–8.4: the acquisition term is defined as a whole-system increment, the two energy quantities are never mixed, and the supply architecture is documented rather than assumed. A2.4 fixes the energy boundary definitions. The decisive change — replacing planned bench measurement with a modelled, schedule-attributable rail-level quantity — is amendment [A4](prereg-v1.2-amendment-A4-no-hardware.md), now published with the [parameter provenance record](modelled_energy_parameter_provenance.md) and the [superseded hardware protocol](../hardware/measurement_protocol.md).

The [energy scope guide](ENERGY_SCOPE.md) sets out what that quantity is, what it does not establish, and one distinction worth carrying into the results: A4.6 planned to repeat the schedule comparison under LOW, CENTRAL and HIGH parameterizations, but the pre-outcome feasibility audit found that E3 resolves to the same seven bursts in all three, so the schedules are identical across them and a single CENTRAL outcome analysis was run. Separate LOW and HIGH outcome analyses were never performed and none is reported here.

## 7. Testing hierarchy

Unchanged from v1.1 §2 and §11: a fixed sequence H1 → M1 → {H2, H3 under Holm} at α = 0.05, each stage tested only if the previous one rejected in the nocturnally-favouring direction; the estimand is θ from the hierarchical paired win/loss/tie comparison; the test is an exact sign test on the discordant pairs, with bootstrap intervals.

A1 replaces §15: cross-schedule dependence is not identifiable from a single continuous arm and is therefore not estimated from one. A pre-specified sensitivity grid over within-participant dependence (0, 0.25, 0.50, 0.75) is swept instead, and the minimum detectable effect and expected precision are reported across the whole grid; the continuous arm may inform only the marginal baseline detection probability, logged before any comparison is inspected.

In the executed study H1 was not rejected, so the sequence closed and the remaining contrasts are estimation-only. The numbers are in [results and limitations](RESULTS_AND_LIMITATIONS.md).

## 8. Still to be published

| Topic | Document |
|---|---|
| Runner operationalisation, including evaluability and the executed window | A5 |
| Phase-2 step-data semantics and the superseded first run | A6 |
| Post-primary sensitivity operationalisation, and which planned analyses were not run | A7 |
| Detector, calibration and runner source code | `src/` |

This guide is extended as those artifacts appear. No day-by-day publication timetable is published in this repository.

# Preregistration amendment A2 — implementation-audit patches

**Status: DRAFT — NOT FROZEN.** Issued 31 August 2026 after an independent code
audit of `rq1_phase1_repo`. A2 supplements A1; where they touch the same section, A2 wins.

---

## A2.1 — Definition of C_p, and the common-cohort principle (audit item 5)

This was flagged as needing a decision before final N is computed. **It is a decision, not
an implementation detail, and it is put to you here rather than resolved silently.**

### The dependency

TOD-z z-defined days depend on the retained schedule: a sparse arm produces fewer valid
days than a dense one, because the ≥ 5-rest-sample rule bites differently. If cohort
eligibility were defined on z-defined days, each arm would analyse a different set of
participants, and the confirmatory comparisons would no longer be paired on a common cohort.

### Proposed rule — Option A for eligibility, with a prospective paired-availability rule

**1. Cohort eligibility uses source-availability calibration days, computed before masking.**

```
C_p^src := number of ANALYSABLE source days strictly before (onset_p - 28)
           and outside every infection exclusion window
```

`analysable` is the §3.1 criterion — ≥ 2 h of observed minutes in each of the night and day
windows — and depends only on the archive, never on a schedule. C_min is selected from the
distribution of `C_p^src` by the frozen availability-only rule. Rationale: it yields **one
common paired cohort** for H1, M1, H2 and H3; no arm can enter with a cohort shaped to suit
it; and it is computable at Gate D1, before any masking exists.

**2. Per-arm calibration reports its own availability.**

For each arm a, `C_p^a` = that arm's z-defined days in the calibration interval. Each arm
reports the distribution of `C_p^a`, its implied resolution 30.44/`C_p^a`, its
`coarse_calibration` count and its `budget_infeasible` count. These are **reported, never
used to alter the cohort.**

**3. Prospective paired-availability rule for each pairwise comparison.**

```
C_floor := 16 days
```

the smallest C at which one alert is admissible under B = 2. A participant enters a given
pairwise comparison only if `C_p^a >= C_floor` for **both** arms in that pair. Exclusion is
from that comparison only, is symmetric between the two arms, and **participant N is
reported per comparison** — H1, M1, H2 and H3 may therefore differ, and the numbers are
printed side by side rather than merged.

**4. Common-cohort sensitivity.**

Every confirmatory comparison is repeated on the intersection cohort — participants meeting
`C_floor` in **all** primary arms — so a reader can see directly whether differing
per-comparison N changed any conclusion. If the two agree, the point is closed; if they
disagree, the disagreement is the finding.

**Requires your approval before final N is computed.** If you prefer Option B — defining
eligibility on the intersection of arm-specific availability — say so and it will be
implemented instead; it costs participants and makes eligibility depend on schedule
behaviour, which is why it is not the proposal.

---

## A2.2 — Coverage-diagnostic populations (audit item 6)

`src/coverage_diagnostic.py` now reports three populations, and the paper's headline figure
is the one matching the population the primary study uses:

- **A** all Fitbit participants
- **B** pre-calibration eligible Fitbit participants
- **C** final primary cohort, once C_min is chosen

The bootstrap resamples **participants**, not participant-days, in all three. Coverage is
computed from unique observed minute bins against their own denominators — 420 for night,
1020 for day — never by subtracting a raw sample count.

---

## A2.3 — Overlap investigation (audit item 7)

Both remedies are adopted, because either alone would overstate what is knowable.

**The series check is implemented.** `src/check_overlap.py` compares per-participant daily
series across releases on common calendar days, flagging a pair at correlation ≥ 0.95 with
mean absolute difference ≤ 1.5, or ≥ 98 % exact daily agreement, over ≥ 14 common days.

**Its precondition is stated and enforced.** A cross-release series comparison is only
meaningful if both archives carry true calendar dates. Date shifting in this data family is
demonstrated, not hypothetical: the sample files shipped in
`StanfordBioinformatics/wearable-infection` carry 2025–2026 dates for a study that ended in
July 2021. The script therefore tests each archive's dates against the published study
windows first. **If either fails, the series check is skipped and the verdict is
`UNDETERMINABLE`, never `NO_EVIDENCE_OF_OVERLAP`.**

Prereg §3.4 wording is amended to: *"Overlap is investigated using identifiers, date ranges
and, where both releases carry calendar dates consistent with their published study windows,
a per-participant daily-series comparison. If date plausibility fails, overlap is
undeterminable from the de-identified releases and is reported as such. The Phase-2-only
sensitivity analysis runs regardless of the verdict."*

---

## A2.4 — Energy boundary definitions (audit item 10)

Every term in `E_sched` is now defined as an **increment above platform idle over its own
interval**:

```
E_wake   := integral over the wake interval of   (i(t) - I_platform_idle) * V
E_settle := integral over the settle interval of (i(t) - I_platform_idle) * V
E_BLE    := integral over the transmit interval of (i(t) - I_idle) * V
```

Platform idle is charged exactly once, across the full 86 400 s, by `e_total_rail_joules`.
`E_total = P_platform_idle * 86400 + E_sched` is therefore exact rather than double-counting
idle during wake and settle. `hardware/measurement_protocol.md` uses these identical
boundaries.

**Accelerometer boundary made explicit.** `RailEnergyParams.accel_included_in_active_increment`
records whether the accelerometer was running while `P_active_increment` was measured. When
true, the in-burst accelerometer cost is already inside `P_active_increment` and is **not**
added again. The out-of-burst low-power term covers `86400 − T_active` seconds, never the
whole day, so the burst interval cannot be charged twice. The flag is `PENDING` until
measured, and the model refuses to compute without it.

**Proof, not assertion.** `tests/test_energy_accounting.py` builds an explicit synthetic
current trace from physical intervals, integrates it, and asserts the model's closed form
matches to 1 part in 10⁹, for all six arms × both accelerometer boundary settings. A further
test shows that redefining `E_wake` as absolute rather than incremental makes the model
exceed the integral by exactly `N_bursts × I_idle × V × T_wake` — so the test would catch
the double-count it exists to prevent.

---

## A2.5 — Device assignment (audit item 3)

Device is never inferred because a downstream filter needs one. `results/device_map.csv`
carries `participant_id | phase | device | provenance | detail`, with provenance drawn from a
fixed vocabulary in descending strength: `filename_token`, `archive_metadata`,
`supplementary_table`, `paper_statement_scope`, `author_correspondence`, `UNKNOWN`.

Mishra et al. state that the 32 analysed COVID-positive cases "had Fitbit data". That is a
statement about a **set**, not a per-participant label. It may be used only once membership
of that set is established from an independent source, and is then recorded as
`paper_statement_scope` naming the membership source. Participants with `UNKNOWN` or
`CONFLICT` are **excluded, not guessed**, and their count appears as its own row in the
participant-flow table. `build_cohort.py` reads `device_map.csv` and never a filename.

---

## A2.6 — Two-phase cohort construction (audit item 4)

The stale `c >= 14` rule is deleted. Construction is now:

```
PHASE A   device (from device_map) -> infection status -> symptomatic
          -> onset available -> baseline / source coverage
          NO C_min filter
          then compute C_p^src from availability only
          then choose_c_min(...) under the frozen v1.2 rule
PHASE B   final cohort = Phase A AND C_p^src >= C_min
```

`results/participant_flow.json` reports, explicitly: pre-calibration eligible, the C_p
distribution with median / IQR / min / max, the retention share at each candidate C_min, the
chosen C_min, the number excluded for `C_p < C_min`, and the final eligible N. `build_cohort.py`
imports nothing from `schedules.py` or `tod_z.py`, so no outcome or schedule-performance
quantity can reach the selection by construction rather than by discipline.

---

## A2.7 — Wording fix (audit item 9)

The calibration-resolution table columns are renamed to **"number of admissible alert-count
levels (including zero)"**, with an explicit sentence that a value of 1 means only zero
alerts is admissible. The arithmetic was correct; the heading invited the wrong reading.

# Symptom-onset label provenance procedure

`results/onset_labels.csv` must have exactly these columns, one row per
infection-positive participant:

```
phase,participant_id,device,symptomatic,onset_date,diagnosis_date,source,source_locator,retrieved_utc
```

`source` is one of, in descending order of preference:

1. `archive` — a file inside the downloaded zip. Record the file name and column in
   `source_locator`. **Check for this first.** Neither code repository ships such a
   file, and in `AnomalyDetect` the dates are command-line arguments, so it may not exist.
2. `supplementary` — Mishra et al. Supplementary Data 1 / Supplementary Tables 1–5,
   or the Alavi et al. supplement. Record table and row.
3. `author_correspondence` — an email reply from the Snyder lab. Record the date and
   the message identifier. **If step 1 and step 2 both fail for Phase 2, send that email
   on 5 September, not later.**

A participant with no `onset_date` from any of the three sources fails cohort
criterion 4 and is excluded. **Never infer an onset date from the physiological data.**
That would make the label a function of the signal the study is testing.

`symptomatic` is `True`/`False`/`Unknown`. Phase 2 reports 66 symptomatic and 18
asymptomatic among the 84 confirmed positives; Phase 1 does not report a
symptomatic/asymptomatic split at all, so Phase 1 rows will be `Unknown` unless a
per-participant source is located. `Unknown` fails criterion 4 — this is deliberate
and its cost in eligible N is reported in the participant-flow table.

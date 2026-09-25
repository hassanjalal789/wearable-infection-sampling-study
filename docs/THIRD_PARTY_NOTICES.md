# Third-party notices

*Publication-stage document, written on 21 September 2026. It is new writing for this repository.*

This repository redistributes **no third-party code and no third-party data**. The material below is credited because the research depended on it.

## Upstream repositories

The research pinned four public repositories at the commits below, recorded in [`upstream_commits.json`](upstream_commits.json) and [`upstream_commits.txt`](upstream_commits.txt), and drew on them during the research, including its reproduction checks. They are referenced here, not copied. Each licence was read from the repository at the pinned commit on 21 September 2026.

| Repository | Pinned commit | Licence at that commit |
|---|---|---|
| [mwgrassgreen/WearableDetection](https://github.com/mwgrassgreen/WearableDetection) | `38955bc09e14b446452c01e87e6f525e99e8be6e` | MIT — Copyright (c) 2020 Meng Wang |
| [mwgrassgreen/Alarm](https://github.com/mwgrassgreen/Alarm) | `1770dd0d2f620940e93ec82f8a5ba48b9fde9658` | MIT — Copyright (c) 2020 Meng Wang |
| [gireeshkbogu/AnomalyDetect](https://github.com/gireeshkbogu/AnomalyDetect) | `1484183d203ffd1ffce6974a0dbdc66a7c9e0bf3` | MIT — Copyright (c) 2020 Gireesh Bogu |
| [StanfordBioinformatics/wearable-infection](https://github.com/StanfordBioinformatics/wearable-infection) | `99b3bd7937e72d42c2670c7a259d9f9f8728dc06` | Apache License 2.0 |

How each was used, and how far its results were reproduced, is set out in the [reproduction gates guide](REPRODUCTION_GATES_AND_POWER.md). The reproduction runs used the upstream code and its bundled sample data unmodified; neither is copied into this repository, and outputs generated from the upstream sample participants are withheld.

## Datasets

The study used the Stanford COVID-19 wearables datasets:

- Phase 1 — Mishra, T. et al. Pre-symptomatic detection of COVID-19 from smartwatch data. *Nature Biomedical Engineering* 4, 1208–1220 (2020). https://doi.org/10.1038/s41551-020-00640-6
- Phase 2 — Alavi, A. et al. Real-time alerting system for COVID-19 and other stress events using wearable data. *Nature Medicine* 28, 175–184 (2022). https://doi.org/10.1038/s41591-021-01593-2

The data belong to the study teams. The Gate B check counts rows in the papers' supplementary tables; the published result keeps only those counts and the papers' own reported values. Neither the archives, the papers' supplementary files, nor any participant-level derivative is included here, and public availability is not treated as permission to redistribute them. Their use implies no affiliation with or endorsement by those teams. The [data and cohort guide](DATA_AND_COHORT.md) identifies the exact archives analysed.

## Software libraries

The published scripts use Python with NumPy, pandas and SciPy, and some also use pyarrow, openpyxl and matplotlib; the Gate A records name R and the Python 3.6 container environment used for AnomalyDetect. None is bundled. The versions used for the publication test runs are in the [pipeline and tests guide](PIPELINE_AND_TESTS.md#4-the-test-suite), and the historical environment records are in [`environment/`](../environment/).

## This project's own files

No licence has been selected yet for this project's own files. See [licensing status](PUBLICATION_NOTES.md#licensing-status).

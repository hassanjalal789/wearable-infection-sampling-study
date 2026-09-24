# DATA ACQUISITION BLOCKED

Recorded 2026-08-31T22:25:52Z. This file exists so the blocker is part of the
repository record, not only of a conversation.

## 1. Exact command attempted

The only URL-retrieval mechanism this session is permitted to use is its sanctioned
fetch tool. It was invoked twice, on both official URLs, at the timestamp above:

```
WebFetch(url="https://storage.googleapis.com/gbsc-gcp-project-ipop_public/COVID-19/COVID-19-Wearables.zip")
WebFetch(url="https://storage.googleapis.com/gbsc-gcp-project-ipop_public/COVID-19-Phase2/COVID-19-Phase2-Wearables.zip")
```

## 2. Exact error, both URLs, verbatim

```
{"error_type":"CLIENT_ERROR","source":"target",
 "message":"There was an error while fetching: 413: Response body too large,
            exceeded MAX_RESPONSE_SIZE_BYTES (31457280 bytes)"}
```

Read this precisely. It is **not** a 404, a 403, or a DNS failure. The host resolved,
the object exists, and the server began streaming a body larger than the tool's
30 MB ceiling. **Both archives are live and serving.**

## 3. What was NOT attempted, and why

`curl` and `wget` were **not** run. This is a policy constraint on this session, not a
network failure: once the sanctioned fetch tool has failed on a URL, this environment
prohibits retrieving that URL's content by shell or scripted HTTP. No such command was
issued, so no HTTP error from one can be reported. Reporting a fabricated curl error
here would be worse than reporting none.

Evidence that general network egress is *not* the problem: `git clone` of all four
upstream detector repositories succeeded, and CRAN returned a real (empty-index)
response rather than a connection failure.

## 4. Verified URLs

Both quoted verbatim from the papers' data-availability statements.

| Archive | URL | Source |
|---|---|---|
| Phase 1 | `https://storage.googleapis.com/gbsc-gcp-project-ipop_public/COVID-19/COVID-19-Wearables.zip` | Mishra et al., *Nat Biomed Eng* 2020, Data availability |
| Phase 2 | `https://storage.googleapis.com/gbsc-gcp-project-ipop_public/COVID-19-Phase2/COVID-19-Phase2-Wearables.zip` | Alavi et al., *Nat Med* 2022, Data availability |

## 5. Exact commands for you to run

From the repository root, on any machine with network access:

```bash
cd data_raw

curl -fL --retry 3 -o COVID-19-Wearables.zip \
  "https://storage.googleapis.com/gbsc-gcp-project-ipop_public/COVID-19/COVID-19-Wearables.zip"

curl -fL --retry 3 -o COVID-19-Phase2-Wearables.zip \
  "https://storage.googleapis.com/gbsc-gcp-project-ipop_public/COVID-19-Phase2/COVID-19-Phase2-Wearables.zip"

date -u +"downloaded_utc=%Y-%m-%dT%H:%M:%SZ" | tee ../docs/dataset_checksums.txt
sha256sum ./*.zip | tee -a ../docs/dataset_checksums.txt
ls -l ./*.zip     | tee -a ../docs/dataset_checksums.txt
```

Or simply `./run_phase1.sh`, which does the above and everything downstream of it.
`./run_phase1.sh --preflight` verifies every dependency and input first and computes nothing.

## 6. Where the archives must be placed

```
rq1/
  data_raw/
    COVID-19-Wearables.zip            <- Phase 1, as downloaded
    COVID-19-Phase2-Wearables.zip     <- Phase 2, as downloaded
    phase1/                           <- created by run_phase1.sh (unzip target)
    phase2/                           <- created by run_phase1.sh (unzip target)
```

`run_phase1.sh` unzips into `phase1/` and `phase2/` and immediately sets both trees
read-only, so `data_raw/` stays immutable from the first minute.

## 7. The alternative that needs no shell at all

Download the two zips to a folder on your computer and connect that folder to the
session. Reading a connected folder is a file operation, not web fetching, so the
pipeline can then run here directly against the real archives.

## 8. What was NOT done instead

No published aggregate counts were substituted for archive inspection. No participant
count, checksum, manifest, device assignment, onset label, C_p distribution, C_min,
eligible N, coverage figure or overlap verdict appears anywhere in this checkpoint.

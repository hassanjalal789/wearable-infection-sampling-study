# Publication notes

## Disclosure

This repository presents research that I designed and conducted. I wrote the protocol and the amendments that governed the analysis, ran the analysis, and am now publishing the research materials and results here. — Hassan Jalal

The initial research and primary E3 analysis were completed by 4 September 2026, as documented in the project records. Formal evidence preparation, documentation, reproducibility verification, and public release began on 19 September 2026. The target is to complete the evidence package by 28 September, with final verification and handoff by 29 September. Any further analysis is documented with its actual dates, methods, and results. Completion will be reported after verification.

**Completion.** The evidence package was completed on 25 September 2026, ahead of the 28 September target, and its final verification was carried out the same day. The [verification report](VERIFICATION_REPORT.md) records what was checked, what could not be, and why. No further analysis is under way.

I prioritized SAT preparation before beginning the formal evidence-documentation phase on 19 September.

The project records referred to above are preserved local records, not an independently timestamped public preregistration. Files were added here in stages between 19 and 25 September 2026, so a file's upload date is not the date the research was done, and the public commit history records publication and subsequent verification rather than the research itself.

## How the archive is being published

- **Historical identifiers.** Commit identifiers quoted from the preserved local repository — in the amendments, for example — belong to that private history and do not resolve as commits here.
- **Copied versus new material.** Protocols, amendments, code, and results are published with the wording I preserved during the research, including draft markers. Explanatory documents such as this one were written later for this repository and are identified as new writing.
- **Accounting.** The [publication manifest](../evidence/PUBLICATION_MANIFEST.csv) records every artifact group, its public destination or external source, and its status, including exclusions.

## Privacy edits

- Personal filesystem paths, computer account names, host names, machine identifiers, and shell prompts are removed from published copies, along with incidental personal details that are not part of the research record.
- In copied narrative logs, the project-root path is replaced by the placeholder `<PROJECT_ROOT>`. In historical terminal excerpts, the account and host prompt is replaced by `$`, the download folder's path by `<DOWNLOADS>`, the account name in file listings by `<user>`, and dataset participant identifiers by `<participant>`; the log's header and its [guide](../evidence/EXECUTION_LOG_GUIDE.md#4-conventions) state that this was done.
- No executable file was sanitized; the three sanitized files listed below are logs or result records.
- Copies edited this way are marked `published-sanitized` in the manifest. They are not byte-identical to the versions I preserved during the research. Checksums of every published file are in [`evidence/SHA256SUMS.txt`](../evidence/SHA256SUMS.txt); the checksums of the preserved versions are kept privately.
- A detailed redaction record is kept privately with the research evidence.
- Three published files are sanitized derivatives, each marked `published-sanitized` in the manifest: the [historical execution log](../evidence/historical_execution_log.md); the Gate A log [`results/gate_a/hrosad_offline.log`](../results/gate_a/hrosad_offline.log), in which a private project path and a participant identifier are replaced; and the Gate B result [`results/gate_b_results.json`](../results/gate_b_results.json), from which a list of 32 participant identifiers is removed. Every other archived file in this repository is byte-identical to the version I preserved during the research process, and I have not retrospectively edited it for publication. The explanatory documents were written later for this repository and are labelled as new writing.

## Excluded material

The following are not published:

- the virtual environment, installed packages, caches, bytecode, and operating-system metadata files;
- the Git metadata of my local research repository, which is summarised instead in the [research timeline](RESEARCH_TIMELINE.md) and the archived [Git log report](../evidence/audit/audit_git_log.txt);
- raw dataset archives and bulk raw data, which are available from the source studies;
- participant-level outputs, onset dates, and source workbooks, until a specific publication-rights and privacy review establishes a basis for release;
- full copies of bundled upstream repositories, which are referenced by source and commit pin instead, and the outputs generated from their sample participants;
- the Gate B audit files and table extracts, which print participant-level rows of the source studies' supplementary tables;
- private notes, credentials, unrelated files, and duplicate copies;
- my unredacted terminal transcript, of which a reviewed and sanitized derivative is published as the [historical execution log](../evidence/historical_execution_log.md).

## Preservation of the research evidence

My research folder and the terminal transcript document are retained privately and are not modified by publication work. Before preparation began, the folder was checked against its own pre-existing SHA-256 manifest. All 17,358 listed files matched except one Git metadata cache file (the index), which a status command had rewritten during an earlier AI-assisted review on 16 September 2026. That file was restored byte-for-byte from a preserved copy of the archive and then matched; research files were unaffected. Five files present in the folder are not listed in the manifest: the manifest itself, a size summary, and three operating-system folder metadata files. The check was repeated on 25 September 2026, at the end of the publication work: all 17,358 listed files matched, and the terminal transcript matched its recorded hash.

## Portability changes

No archived file has been changed to make it run. One new file supports the test suite: [`conftest.py`](../conftest.py), at the repository root, stops pytest from collecting the Gate B test module when the two supplementary workbooks it reads are absent, and names the missing files in the session header. It changes no test. It was added on 25 September 2026 and checked by running the suite with and without the workbooks; see the [verification log](../evidence/VERIFICATION_LOG.md). Three further new files support verification without changing any archived file: the pinned environment [`environment/publication-requirements.txt`](../environment/publication-requirements.txt), the checker [`src/check_public_package.py`](../src/check_public_package.py), and the automated workflow [`.github/workflows/public-checks.yml`](../.github/workflows/public-checks.yml).

## Material corrections

- **25 September 2026, [energy scope guide](ENERGY_SCOPE.md).** A paragraph published on 19 September gave the E3 matching-error range for the fixed-time arms only and named only one of the infeasible E4 cells. It now gives the full ranges from the published feasibility audit. No result or rule changed.
- **25 September 2026, [methods guide](METHODS_GUIDE.md).** Two statements described A1 reporting as carried out: that same-day detection "is tabulated separately" with an at-or-before statistic "reported", and that the paired warning-time difference "is estimated" on the detected-under-both subgroup. The [method traceability review](METHOD_TRACEABILITY.md) found that no published output reports either; the guide now says so. It also notes the part of the v1.1 reporting set that was not produced. No result changed.
- **25 September 2026, date of the baseline protocol.** The [research timeline](RESEARCH_TIMELINE.md) and the [timeline fact file](../evidence/TIMELINE_FACTS.md) said `prereg-v1.1.md` states no date. Its header states that it was revised on 31 August 2026. Both now say so, and the machine-readable chronology gives that date.
- **25 September 2026, bootstrap intervals.** Notes published on 24 and 25 September said the BCa intervals could not be recomputed because they need withheld participant-level results. That was wrong: the scripts that produced them bootstrap a vector built from each comparison's win, loss and tie counts alone, so the published counts and recorded seeds determine them. All 37 were recomputed and matched exactly; see the [verification report](VERIFICATION_REPORT.md). The statements in the [results note](../results/README.md) and the [evidence index](EVIDENCE_INDEX.md) are corrected. No result changed.

## Licensing status

No licence has been selected for this project's own files. Until one is chosen, no licence is granted beyond what GitHub's Terms of Service allow for public repositories, such as viewing and forking on GitHub. Datasets and upstream code keep their own terms; see the [data availability guide](DATA_AVAILABILITY.md) and the [third-party notices](THIRD_PARTY_NOTICES.md).

## Verification during preparation

*This section records the checks made for the first publication on 19 September 2026. Later checks, with their dates, are in the [verification log](../evidence/VERIFICATION_LOG.md).*

- Reported values in the README, research summary, and results document were checked against the archived results digest, results table, comparison summary, gatekeeping record, and run manifest.
- Publication-stage tabulations (continuous-sampling detections, threshold distribution, calibration-floor counts) were computed read-only from archived participant-level output that is not published.
- Every file in this snapshot was scanned for personal paths, account and host names, e-mail addresses, machine identifiers, and credentials before the commit, and every archived document was compared byte for byte with the version I preserved during the research.
- Relative links were checked to point to files present in this commit.
- The energy parameters in the provenance record were compared against the frozen scenario configuration used by the analysis: eleven parameters across the LOW, CENTRAL and HIGH scenarios, 33 comparisons, all equal.
- Not executed: the test suite, any analysis rerun, and figure regeneration.

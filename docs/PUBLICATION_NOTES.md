# Publication notes

## Disclosure

This repository presents research led by Hassan Jalal.

The initial research and primary E3 analysis were completed by 4 September 2026, as documented in the project records. Formal evidence preparation, documentation, reproducibility verification, and public release began on 19 September 2026. The target is to complete the evidence package by 28 September, with final verification and handoff by 29 September. Any further analysis is documented with its actual dates, methods, and results. Completion will be reported after verification.

In the author's words: "I prioritized SAT preparation before beginning the formal evidence-documentation phase on 19 September."

The project records referred to above are preserved local records, not an independently timestamped public preregistration. Files are added here in stages, so a file's upload date is not the date the research was done, and the public commit history records publication and subsequent verification rather than the original research.

## How the archive is being published

- **Historical identifiers.** Commit identifiers quoted from the preserved local repository — in the amendments, for example — belong to that private history and do not resolve as commits here.
- **Copied versus new material.** Protocols, amendments, code, and results will be copied from the preserved archive with their original wording, including draft markers. Explanatory documents such as this one are new publication-stage writing and are identified as such.
- **Accounting.** The [publication manifest](../evidence/PUBLICATION_MANIFEST.csv) records every artifact group, its public destination or external source, and its status, including exclusions.

## Privacy edits

- Personal filesystem paths, computer account names, host names, machine identifiers, and shell prompts are removed from published copies, along with incidental personal details that are not part of the research record.
- In copied narrative logs, the project-root path is replaced by the placeholder `<PROJECT_ROOT>`. In historical terminal excerpts, the account and host prompt is replaced by `$`, and a header states that this was done.
- Executable code will use relative paths or explicit arguments instead of placeholder text that would break execution.
- Copies edited this way are marked `published-sanitized` in the manifest. They are not byte-identical to the originals. Checksums of the published files will be provided separately from the private record of the original checksums.
- A detailed redaction record is kept privately with the original evidence.
- Nothing published so far is a sanitized derivative: every archived document in this repository is a byte-identical copy of its preserved original, and the explanatory documents are new publication-stage writing. The first sanitized copies will be the transcript excerpts, and they will be marked `published-sanitized` in the manifest.

## Excluded material

The following are not published:

- the virtual environment, installed packages, caches, bytecode, and operating-system metadata files;
- the original Git metadata (to be summarised instead in a research timeline, which is not yet published);
- raw dataset archives and bulk raw data, which are available from the original sources;
- participant-level outputs, onset dates, and source workbooks, until a specific publication-rights and privacy review establishes a basis for release;
- full copies of bundled upstream repositories, which will be referenced by source and commit pin instead;
- private notes, credentials, unrelated files, and duplicate copies;
- the original, unredacted terminal transcript, of which a reviewed and sanitized derivative is planned.

## Preservation of the original evidence

The original research folder and the terminal transcript document are retained privately and are not modified by publication work. Before preparation began, the folder was checked against its own pre-existing SHA-256 manifest. All 17,358 listed files matched except one Git metadata cache file (the index), which a status command had rewritten during an earlier AI-assisted review on 16 September 2026. That file was restored byte-for-byte from a preserved copy of the archive and then matched; research files were unaffected. Five files present in the folder are not listed in the manifest: the manifest itself, a size summary, and three operating-system folder metadata files. The same check will be repeated at the end of the publication window.

## Portability changes

None so far. Any change needed to run the published code will be listed here with its reason and verification, separately from the archived original.

## Licensing status

No licence has been selected for this project's own files. Until one is chosen, no licence is granted beyond what GitHub's Terms of Service allow for public repositories, such as viewing and forking on GitHub. Datasets and upstream code keep their own terms, which will be documented in the data-availability guide and third-party notices.

## Verification during preparation

- Reported values in the README, research summary, and results document were checked against the archived results digest, results table, comparison summary, gatekeeping record, and run manifest.
- Publication-stage tabulations (continuous-sampling detections, threshold distribution, calibration-floor counts) were computed read-only from archived participant-level output that is not published.
- Every file in this snapshot was scanned for personal paths, account and host names, e-mail addresses, machine identifiers, and credentials before the commit, and every archived copy was compared byte for byte with its preserved original.
- Relative links were checked to point to files present in this commit.
- The energy parameters in the provenance record were compared against the frozen scenario configuration used by the analysis: eleven parameters across the LOW, CENTRAL and HIGH scenarios, 33 comparisons, all equal.
- Not executed: the test suite, any analysis rerun, and figure regeneration.

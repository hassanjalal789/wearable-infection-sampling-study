# Guide to the historical execution log

*Publication-stage guide, written on 25 September 2026. It explains [`historical_execution_log.md`](historical_execution_log.md), which reproduces reviewed excerpts from the terminal record of the research I conducted. This guide is new writing. The log's headings and one-line notes are also new; everything inside its code blocks is historical output.*

## 1. What the record is

While doing the research, I kept a terminal record: the commands I ran in the project and the output they reported. It runs from the first attempt to download the source archives to the commit that added the final result tables and figures. It is preserved privately as a Word document of about 23,000 lines, and its SHA-256 has been checked against the value recorded when preparation began. The document itself is not published. It contains personal identifiers, private paths and participant-level output. The log is a sanitized derivative of it and is marked `published-sanitized` in the [manifest](PUBLICATION_MANIFEST.csv).

## 2. What the excerpts cover

The log has 40 excerpts in 15 sections, in the order in which they occur in the record. Together they reproduce 1,819 of its lines. They cover every stage the record contains:

| Section | What it shows |
|---|---|
| 1 | Acquisition: an interrupted Phase 2 download, a failed archive test, a repeated download, and the hashes of the two archives used |
| 2 | Environment: preflight failures from missing packages, then a working environment |
| 3 | Onset labels taken from the papers' supplementary tables, and a phase-label correction |
| 4 | Inventory: a timestamp-unit defect and its fix, a malformed Phase 2 file and its quarantine, and device provenance for every candidate |
| 5 | Cohort counts, the coverage diagnostic, and the undeterminable overlap check |
| 6 | The frozen power calculation |
| 7 | Gate A: pinned upstream repositories, three failed attempts in a current environment, the pinned-environment runs, and the mixed outcome |
| 8 | Gate B: the source search, an interrupted cell search, and the reconstruction |
| 9 | A timestamp warning traced to one file, and the calibration-minimum reporting patch |
| 10 | The pre-outcome checkpoint commit |
| 11 | The bench protocol, amendment A4, and the energy freeze |
| 12 | The runner freeze, the first execution, its quality-control audit, the outcome-blind input diagnostic, the A6 correction and the corrected execution |
| 13 | The confirmatory reveal, including the first script's failure |
| 14 | The sensitivity plan freeze, an interrupted run and the completed run |
| 15 | The final tables and figures, and the last recorded commit |

The failures stay in: interrupted downloads, failed preflights, code defects found by internal checks, failed upstream runs, runs stopped by hand, a script that failed while printing its summary, and small shell errors, such as `zsh: command not found: #` where a comment line was pasted. No excerpt was chosen or trimmed to make the work look smoother than the record shows it.

## 3. What was left out, and why

Each gap is marked in place with `[omitted: …]`, and the note says what the gap contains. The main categories:

- **Participant-level material.** Archive listings naming participant files, rows of onset labels, per-participant exclusion lines, progress lines naming participants, per-participant diagnostic tables, anomaly rows and per-night signals generated from upstream sample participants, and rows from the source studies' supplementary tables.
- **Bulk output.** Package installation and download output, clone output and long file listings.
- **Code printouts and inline patch scripts** where the resulting code is published. Where a patch changed a published file, the note points to the preserved pre-change copy in [`historical_code/`](historical_code/README.md).
- **Workspace mechanics.** Placement of project files in the working folder, which says nothing about the research.
- **Inspection commands** that print repository documentation or source code already available elsewhere, where they add no result.

The remaining roughly 21,000 lines of the record were not reproduced. Most of them are archive-member listings (about 8,800 lines) and printouts of code, amendments and upstream documentation.

## 4. Conventions

- The account-and-host shell prompt is replaced by `$`; `(.venv) $` marks commands run with the project's virtual environment active.
- `<PROJECT_ROOT>` replaces the project folder's absolute path, `<DOWNLOADS>` the download folder's path, and `<user>` the account name where a file listing shows it.
- `<participant>` replaces every dataset participant identifier, including the identifiers of upstream sample participants. Some archived documents published elsewhere in this repository quote a few identifiers unchanged, because those documents are byte-identical to the versions I preserved; the derivative applies the stricter rule throughout.
- Trailing spaces at line ends are removed. No other character inside the code blocks was changed.

A private record maps each excerpt to its line range in the preserved document, with every omission and substitution.

## 5. What the record can and cannot establish

**It can show** the order of the work, the commands run and the output reported at the time, including the pre-outcome checkpoint, the runner freeze, the quality-control audit that led to the A6 correction before any outcome was printed, the confirmatory reveal, and the sensitivity work. The local commit identifiers in the output are the eight commits listed in the archived [Git log report](audit/audit_git_log.txt), in the same sequence (the report lists them newest first), and the [research timeline](../docs/RESEARCH_TIMELINE.md) summarizes that history.

**It cannot establish:**

- **Clock time for most commands.** The record carries few timestamps. Its three `Last login` banners report the *previous* login on that terminal, not the start of the session that follows, so they do not date the commands after them. Where a date matters, the [timeline fact file](timeline_facts.json) cites the dated project records instead.
- **Independent proof.** It is a preserved record of my own work, not an independently timestamped or witnessed log.
- **That nothing else happened.** It is one terminal record. Work in other windows or tools is not in it.

**Historical versus new.** Every test count and result in the log was reported at the time. The historical suite reported 131, 140, 143, 149, 154 and then 159 passing tests as modules were added. The checks I ran for this publication are recorded separately, with their dates, in the [verification log](VERIFICATION_LOG.md).

## 6. Relation to the earlier excerpts

[`EXECUTION_EXCERPTS.md`](EXECUTION_EXCERPTS.md), published on 20 September 2026, quotes the run manifests, frozen rules and participant counts from the preserved result records. This log draws on the terminal record instead and shows the commands and output around those records. The two agree where they overlap.

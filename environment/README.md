# Environment records

*Publication-stage note, written on 24 September 2026 and updated on 25 September 2026. Apart from `publication-requirements.txt`, the other files in this folder are historical records from the research, byte-identical to the versions I preserved during the research process; I have not retrospectively edited them for publication. This note is new writing.*

| File | What it records |
|---|---|
| `requirements.lock` | A full package listing of a general-purpose Python environment from the research. It includes many packages the analysis never imports, so it is a record, not a minimal specification. |
| `legacy-venv-requirements.lock`, `upstream-venv-requirements.lock` | Package listings for two further virtual environments, named for an older legacy setup and for upstream code. The records do not state more about their use. |
| `Dockerfile.upstream-py36`, `Dockerfile.upstream-R`, `Dockerfile.anomalydetect-py36` | Era-matched containers for running upstream code unmodified in the reproduction checks. |
| `provenance.txt` | A short record of the project commit, Python version, operating system and passing test count at one point during the research. |
| `project.gitignore` | The project's original ignore rules, published under this name so that it does not act as this repository's ignore file. The content is unchanged. |
| `publication-requirements.txt` | **New for this repository, 25 September 2026.** The pinned packages of the environment used for the publication checks. It is not a historical record. |

The records report different Python versions at different points, and none of them is a complete description of every environment in which an archived output was produced. They are kept as evidence of what was used, not as installation instructions.

The environment I used for the publication checks is pinned in `publication-requirements.txt`; the [reproducibility guide](../docs/REPRODUCIBILITY.md#1-environment) shows how to install it, and the [verification report](../docs/VERIFICATION_REPORT.md) records what was run in it.

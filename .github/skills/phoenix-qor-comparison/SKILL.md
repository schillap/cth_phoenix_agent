---
name: phoenix-qor-comparison
description: Generate QoR summaries for an APR_FC baseline run and a Phoenix run, then produce a side-by-side comparison report at a chosen stage (compile, clock, or route). Use this skill whenever the user asks to "compare APR_FC vs Phoenix", "summarize QoR", "diff timing/area/power", or generate a QoR delta report. Replicates the `generate_and_compare_summaries` MCP tool.
---

# Phoenix QoR Comparison Skill

This skill replicates the `generate_and_compare_summaries` MCP tool. It runs three
scripts in sequence and produces three log files, mirroring the MCP behavior exactly.

## When to use

Use this skill when the user wants to:
- Build a QoR summary of an APR_FC baseline run.
- Build a QoR summary of a Phoenix run (including best-run identification).
- Compare APR_FC vs Phoenix at a specific stage and view metric deltas.

## Required inputs (collect APR_FC and Phoenix sets separately)

**Critical:** Keep APR_FC and Phoenix parameter sets visually separated when prompting,
to avoid mix-ups.

### APR_FC run
| # | Argument               | Description |
|---|------------------------|-------------|
| 1 | `apr_fc_reference_dir` | Base directory containing `runs/<block>/<tech>/<apr_fc>/`. |
| 2 | `apr_fc_block_name`    | Block / build name for the APR_FC run. |
| 3 | `apr_fc_technology`    | Technology node for the APR_FC run. |
| 4 | `apr_fc_dir_name`      | APR_FC directory name (usually `apr_fc`). |

### Phoenix run
| # | Argument                  | Description |
|---|---------------------------|-------------|
| 5 | `phoenix_reference_dir`   | Base directory for the Phoenix run. |
| 6 | `phoenix_block_name`      | Block / build name for the Phoenix run. |
| 7 | `phoenix_technology`      | Technology node for the Phoenix run. |
| 8 | `phoenix_apr_fc_dir_name` | APR_FC directory name inside the Phoenix run (usually `apr_fc`). |

### Comparison
| #  | Argument      | Description |
|----|---------------|-------------|
| 9  | `output_dir`  | Directory where summaries and the comparison log are written. |
| 10 | `stage`       | One of `compile`, `clock`, or `route`. |

## How to run

Execute these three commands in order from the repository root. **Stop and report** if
any command exits non-zero — include the failing command's stderr (and any stdout) in
the report so the user can debug. Do not run subsequent steps after a failure.

### 1. APR_FC summary
```bash
python3 utils/apr_fc_run_summarize.py \
  --reference_dir "<apr_fc_reference_dir>" \
  --output_dir    "<output_dir>" \
  --block_name    "<apr_fc_block_name>" \
  --tech          "<apr_fc_technology>" \
  --apr_fc        "<apr_fc_dir_name>"
```
Writes: `<output_dir>/<apr_fc_block_name>_apr_fc_summary.log`

### 2. Phoenix summary
```bash
python3 utils/phoenix_run_summarize_results.py \
  --reference_dir "<phoenix_reference_dir>" \
  --output_dir    "<output_dir>" \
  --block_name    "<phoenix_block_name>" \
  --tech          "<phoenix_technology>" \
  --apr_fc        "<phoenix_apr_fc_dir_name>"
```
Writes: `<output_dir>/<phoenix_block_name>_phoenix_summary.log`

### 3. Comparison
```bash
python3 utils/run_comparison.py \
  --apr_fc_summary  "<output_dir>/<apr_fc_block_name>_apr_fc_summary.log" \
  --phoenix_summary "<output_dir>/<phoenix_block_name>_phoenix_summary.log" \
  --output_dir      "<output_dir>" \
  --stage           "<stage>"
```
Writes: `<output_dir>/qor_comparison_<stage>.log`

## What the scripts produce

- **APR_FC summary** — full metrics for the baseline.
- **Phoenix summary** — picks the best Phoenix run (e.g. `.run_abc123`) and extracts:
  - Timing: WNS, TNS, R2RTNS, NVP per mode/corner.
  - Area: total area, cell area, utilization.
  - Power: total / internal / leakage.
  - DRV: `max_tran`, `max_cap`.
- **Comparison log** — side-by-side tables at the chosen stage with percentage deltas
  (improvements green, regressions red).

## Reporting back to the user

- Display the contents of `qor_comparison_<stage>.log` **verbatim** (no editorial
  re-interpretation of the metric values).
- Provide the absolute paths of all three output files.
- Highlight notable wins and regressions in a brief summary at the end.

## Boundaries

- Do **not** mix APR_FC and Phoenix parameter sets.
- Do **not** proceed if a required prior log file is missing.
- Do **not** invent metric values — always read them from the generated logs.

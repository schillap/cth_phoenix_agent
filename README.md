# cth_phoenix_agent

An automation toolkit for setting up and running **Phoenix** (and APR_FC baseline)
flows for digital chip design blocks, plus a GitHub Copilot agent that drives the
toolkit end-to-end. The repository ships:

- A **FastMCP server** (`mcp/cth_r2g_phoenix.py`) that exposes 5 tools used by the
  agent.
- A set of **utility scripts** (`utils/`) implementing setup, eouMGR launch, QoR
  summarization, comparison, and sanity checks.
- A **VS Code GitHub Copilot** customization layer under `.github/`:
  - A chat mode (`chatmodes/`) that orchestrates the full workflow.
  - Three task-specific prompts (`prompts/`).
  - Five **Skills** (`skills/`) that replicate the MCP tools so the agent can be
    used in environments where MCP isn't available (e.g. Copilot's native skill
    runtime). Each skill is a self-contained folder with a `SKILL.md` file and
    delegates to the same `utils/` scripts the MCP server calls.

---

## Repository layout

```
cth_phoenix_agent/
├── README.md                                ← you are here
├── .gitignore
│
├── .github/                                 ← VS Code GitHub Copilot customization
│   ├── chatmodes/
│   │   └── phoenix_agent.chatmode.md        ← top-level orchestrator agent
│   ├── prompts/
│   │   ├── phoenix_setup.prompt.md          ← setup specialist prompt
│   │   ├── phoenix_runner.prompt.md         ← eouMGR runner prompt
│   │   └── phoenix_analyst.prompt.md        ← QoR analyst prompt
│   └── skills/                              ← Anthropic-style Agent Skills
│       ├── phoenix-setup/SKILL.md           ← replicates phoenix_setup_helper
│       ├── phoenix-eoumgr-command/SKILL.md  ← replicates generate_eouMGR_command
│       ├── phoenix-qor-comparison/SKILL.md  ← replicates generate_and_compare_summaries
│       ├── phoenix-intent-client/SKILL.md   ← replicates check_vars_tcl_phoenix_intent_client
│       └── phoenix-intent-server/SKILL.md   ← replicates check_vars_tcl_phoenix_intent_server
│
├── mcp/
│   └── cth_r2g_phoenix.py                   ← FastMCP stdio server (5 tools)
│
└── utils/                                   ← worker scripts called by tools/skills
    ├── utils.py                             ← shared helpers (copy_directory,
    │                                          log_with_timestamp, check_phoenix_intent, …)
    ├── fc_setup_auto_main.py                ← entry point for setup (dispatches client/server)
    ├── fc_setup_auto.py                     ← client-design setup flow
    ├── fc_setup_auto_server.py              ← server-design setup flow
    ├── eouMGR_runner.py                     ← thin wrapper to launch eouMGR
    ├── apr_fc_run_summarize.py              ← APR_FC QoR summarizer
    ├── phoenix_run_summarize_results.py     ← Phoenix QoR summarizer (best-run picker)
    ├── run_comparison.py                    ← APR_FC vs Phoenix comparison report
    ├── sanity_checker.py                    ← generic sanity checks
    └── rzl_sanity_check.py                  ← RZL-specific sanity checks
```

> **Why the `.github/` layout?** This mirrors the
> [VS Code GitHub Copilot customization conventions](https://code.visualstudio.com/docs/copilot/customization/overview):
> chat modes live in `.github/chatmodes/*.chatmode.md`, prompt files in
> `.github/prompts/*.prompt.md`, and Agent Skills in `.github/skills/<name>/SKILL.md`.

---

## What each MCP tool / skill does

The MCP server in `mcp/cth_r2g_phoenix.py` and the skills in `.github/skills/` provide
the **same five capabilities**. The skills are 1:1 functional replicas — they accept
the same inputs, run the same `utils/` scripts, and produce the same artifacts.

| # | MCP tool                                  | Skill                       | Purpose |
|---|-------------------------------------------|-----------------------------|---------|
| 1 | `phoenix_setup_helper`                    | `phoenix-setup`             | Create a Phoenix workspace from a reference ward (calls `utils/fc_setup_auto_main.py`). |
| 2 | `generate_eouMGR_command`                 | `phoenix-eoumgr-command`    | Build (and run) the canonical `eouMGR` command for a Phoenix flow stage range. |
| 3 | `generate_and_compare_summaries`          | `phoenix-qor-comparison`    | Produce APR_FC + Phoenix QoR summaries and a side-by-side delta report at `compile`/`clock`/`route`. |
| 4 | `check_vars_tcl_phoenix_intent_client`    | `phoenix-intent-client`     | Inspect / set `set ivar(phoenix_int)` in `runs/<block>/<tech>/scripts/vars.tcl` (client designs). |
| 5 | `check_vars_tcl_phoenix_intent_server`    | `phoenix-intent-server`     | Inspect / set `set ivar(phoenix_int)` in `src/<block>/<tech>/scripts/vars.tcl` (server designs). |

---

## High-level workflow

The agent (`phoenix_agent.chatmode.md`) drives the user through three sequential
stages:

### 1. Setup (`phoenix-setup` skill / `phoenix_setup_helper` MCP tool)

Inputs collected from the user:

1. `design_type` — `server` or `client`
2. `ref_ward` — reference ward path
3. `block_name`
4. `technology`
5. `apr_fc_dir_name` (typically `apr_fc`)
6. `destination_dir`
7. `design_name` (the `.ndm` file name)

Result: a directory tree shaped like
```
<destination_dir>/runs/<block_name>/<technology>/<apr_fc_dir_name>/
```
with collaterals (`hip_data`, `scripts`, release files) and Phoenix scripts installed,
plus setup logs. After setup, the agent invokes `phoenix-intent-client` or
`phoenix-intent-server` to inspect / configure `set ivar(phoenix_int)`.

### 2. Flow execution (`phoenix-eoumgr-command` skill / `generate_eouMGR_command` MCP tool)

Inputs (reuses `block_name` / `design_name` from stage 1):

- `start_task` (e.g. `phoenix_compile`)
- `end_task` (e.g. `phoenix_route`)

The generated command is:
```
eouMGR --block <block> --design <design> --flow phoenix \
       --startTask <start> --endTask <end> \
       --feeder phoenix_<block> --gui --reset --waive_on_error &
```

### 3. QoR comparison (`phoenix-qor-comparison` skill / `generate_and_compare_summaries` MCP tool)

Collects APR_FC and Phoenix parameter sets **separately**, plus an `output_dir` and a
`stage` (`compile` | `clock` | `route`). Produces:

- `<output_dir>/<apr_fc_block>_apr_fc_summary.log`
- `<output_dir>/<phoenix_block>_phoenix_summary.log`
- `<output_dir>/qor_comparison_<stage>.log`

Metrics covered: timing (WNS, TNS, R2RTNS, NVP), area (total/cell/utilization),
power (total/internal/leakage), and DRVs (`max_tran`, `max_cap`).

---

## Running the MCP server

The MCP server is a FastMCP stdio server built on `autobots_base`:

```bash
export AUTOBOTS_SDK_TOOL_PATH=/path/to/autobots/sdk
python3 mcp/cth_r2g_phoenix.py
```

It registers a server named `cth_r2g_phoenix_tool` exposing the five tools above. The
chat mode `phoenix_agent.chatmode.md` references these tools by their full
`cth_r2g_phoenix_tool/<tool_name>` IDs.

---

## Using the Skills (without MCP)

The Skills under `.github/skills/` make every MCP capability available to a Copilot
agent that supports Anthropic-style Agent Skills, with **no MCP server required**.
Each `SKILL.md`:

- has a YAML frontmatter (`name`, `description`) so Copilot can auto-discover when to
  invoke it,
- documents the inputs the agent must collect from the user,
- specifies the exact shell command(s) to run against the scripts in `utils/`,
- describes the success / failure / follow-up behavior to mirror the MCP tool.

To use the skills, simply open this repository in a Copilot-enabled environment that
recognizes `.github/skills/` (or copy the directory into your own repo). When the user
asks (for example) "set up Phoenix from this reference ward", Copilot will pick up the
`phoenix-setup` skill, prompt for the inputs, and run
`python3 utils/fc_setup_auto_main.py …` against the local checkout — the same script
the MCP tool calls.

---

## Direct script usage

Every capability is also runnable directly from the CLI, since both the MCP tools and
the skills are thin wrappers over scripts in `utils/`:

```bash
# Setup (client or server)
python3 utils/fc_setup_auto_main.py \
  --design_type client --destination_dir /path/to/dest \
  --ref_wa /path/to/ref --block_name par_cbpma --technology 1278.6 \
  --apr_fc_dir_name apr_fc --design_name my_design

# QoR summaries + comparison
python3 utils/apr_fc_run_summarize.py        --reference_dir … --output_dir … --block_name … --tech … --apr_fc apr_fc
python3 utils/phoenix_run_summarize_results.py --reference_dir … --output_dir … --block_name … --tech … --apr_fc apr_fc
python3 utils/run_comparison.py              --apr_fc_summary … --phoenix_summary … --output_dir … --stage route
```

---

## Contributing

- Keep the **MCP tools** and **Skills** in sync. If you change a tool's parameters in
  `mcp/cth_r2g_phoenix.py`, update the matching `SKILL.md` (and vice-versa).
- New worker logic should live in `utils/` so both the MCP tool and the Skill can
  reuse it.
- Don't commit `__pycache__/` — it's in `.gitignore`.

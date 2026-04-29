---
name: phoenix-setup
description: Set up a complete Phoenix environment from a reference ward by copying collaterals, creating the directory structure, and installing Phoenix-specific scripts. Use this skill whenever the user asks to "set up Phoenix", "create a Phoenix run", "bootstrap a Phoenix environment", or to clone an existing APR_FC ward into a new Phoenix workspace. Replicates the `phoenix_setup_helper` MCP tool.
---

# Phoenix Setup Skill

This skill replicates the `phoenix_setup_helper` MCP tool. It generates and executes the
Phoenix setup command line, which is implemented by `utils/fc_setup_auto_main.py` in this
repository.

## When to use

Trigger this skill when the user wants to:
- Set up a new Phoenix run from a reference ward.
- Create a complete Phoenix environment with the proper directory structure.
- Copy collaterals (`hip_data`, `scripts`, release files) from a reference ward.

## Required inputs (ask the user before running)

You **MUST** prompt the user for every input below before invoking the script. Do not
guess or invent any value.

| # | Argument           | Description |
|---|--------------------|-------------|
| 1 | `design_type`      | `server` or `client` (default `client`). Determines which underlying setup flow is dispatched. |
| 2 | `ref_ward`         | Reference ward directory path (source). |
| 3 | `block_name`       | Block / build name (e.g. `par_cbpma`, `dhm`). |
| 4 | `technology`       | Technology node (e.g. `1278.6`, `n2p_htall_conf4`). |
| 5 | `apr_fc_dir_name`  | APR_FC directory name (typically `apr_fc`). |
| 6 | `destination_dir`  | Destination directory path where the setup will be created. |
| 7 | `design_name`      | Design name — i.e. the name of the `.ndm` file. |

After collecting `destination_dir`, compare it against the user's `$ward` env variable.
If they differ, warn the user that the Phoenix flow will trigger from `$ward`, **not**
from `destination_dir`. Use the current shell's value, e.g.:

```bash
echo "$ward"
```

Compare the result against `<destination_dir>` and, if they differ, print a warning
before proceeding.

## Behavior

- If `design_type == client`: dispatches the standard `fc_setup_auto.py` flow.
- If `design_type == server`: dispatches `fc_setup_auto_server.py`, which requires the
  `src` directory to exist in the reference ward.
- Creates the standard layout: `<destination_dir>/runs/<block_name>/<technology>/<apr_fc_dir_name>/`.
- Copies collaterals and installs Phoenix scripts.
- Writes setup logs into the destination directory.

## How to run

Build and execute the command exactly as the MCP tool does. From the repository root:

```bash
python3 utils/fc_setup_auto_main.py \
  --design_type     "<design_type>" \
  --destination_dir "<destination_dir>" \
  --ref_wa          "<ref_ward>" \
  --block_name      "<block_name>" \
  --technology      "<technology>" \
  --apr_fc_dir_name "<apr_fc_dir_name>" \
  --design_name     "<design_name>"
```

Capture stdout and stderr. On success, report the command that was run and its output.
On failure (non-zero exit), report the command, stderr, and partial stdout so the user
can debug.

## Follow-up

After the setup completes, immediately invoke the `phoenix-intent-client` or
`phoenix-intent-server` skill (matching the chosen `design_type`) to inspect and,
if necessary, set `set ivar(phoenix_int)` in the generated `vars.tcl`.

## Boundaries

- Do **not** modify the reference ward.
- Do **not** override an existing setup without the user's explicit confirmation.
- Do **not** spawn a new terminal — run the command in the current session.

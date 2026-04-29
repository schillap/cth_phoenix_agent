---
name: phoenix-eoumgr-command
description: Generate (and optionally execute) the `eouMGR` command line for running a Phoenix flow with a given block, design, start task, and end task. Use this skill whenever the user asks to "run the Phoenix flow", "launch eouMGR", "kick off compile/clock/route", or otherwise needs the precise eouMGR invocation for a Phoenix block. Replicates the `generate_eouMGR_command` MCP tool.
---

# Phoenix eouMGR Command Skill

This skill replicates the `generate_eouMGR_command` MCP tool. It produces the exact
`eouMGR` command line used to drive the Phoenix flow.

## When to use

Use this skill when the user wants to:
- Execute a Phoenix flow stage range (e.g. `phoenix_compile` → `phoenix_route`).
- Re-run a specific stage of a Phoenix block (e.g. just `clock_route_opt`).
- Get the canonical eouMGR command without remembering all flag names.

## Required inputs (ask the user before generating)

| # | Argument      | Description |
|---|---------------|-------------|
| 1 | `block_name`  | Block / build name. **Reuse** the value collected during `phoenix-setup` if available. |
| 2 | `design_name` | Design name (the `.ndm` file). **Reuse** the value collected during `phoenix-setup` if available. |
| 3 | `start_task`  | Starting stack-file stage (e.g. `phoenix_compile`, `phoenix_clock`, `insert_dft`, `clock_route_opt`, `route_opt`). |
| 4 | `end_task`    | Ending stack-file stage (e.g. `phoenix_route`). |

The flow is hardcoded to `phoenix`, exactly as in the MCP tool.

## Command template

Produce this command verbatim, substituting the user's values:

```bash
eouMGR --block <block_name> --design <design_name> --flow phoenix \
       --startTask <start_task> --endTask <end_task> \
       --feeder phoenix_<block_name> --gui --reset --waive_on_error &
```

## Workflow

1. Show the generated command to the user **before** running it.
2. Ask the user to confirm.
3. On confirmation, execute it in the current terminal session (do not spawn a new
   terminal). The trailing `&` backgrounds the GUI process.
4. After submission, give the user monitoring instructions (e.g. tail the eouMGR log,
   watch the GUI).

## Boundaries

- Do **not** modify the command's flag set without the user's explicit request.
- Do **not** spawn a new terminal session.

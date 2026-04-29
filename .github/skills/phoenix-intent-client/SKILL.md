---
name: phoenix-intent-client
description: After a Phoenix CLIENT setup, inspect or update `set ivar(phoenix_int)` in the generated `vars.tcl` (located under `runs/<block>/<tech>/scripts/vars.tcl`). Use whenever the user wants to check or change the Phoenix intent (`power` or `timing`) for a CLIENT design. Replicates the `check_vars_tcl_phoenix_intent_client` MCP tool.
---

# Phoenix Intent — Client Designs

This skill replicates the `check_vars_tcl_phoenix_intent_client` MCP tool. It works
exclusively on **client** designs.

## When to use

- Immediately after `phoenix-setup` completes for a client design.
- Whenever the user wants to read or modify the Phoenix intent of a client design.

## Inputs

| # | Argument          | Required | Description |
|---|-------------------|----------|-------------|
| 1 | `destination_dir` | yes      | Destination directory used during `phoenix-setup`. |
| 2 | `block_name`      | yes      | Block / build name. |
| 3 | `technology`      | yes      | Technology node. |
| 4 | `intent`          | optional | `power` or `timing`. Leave empty to just inspect. |

The target file is:
```
<destination_dir>/runs/<block_name>/<technology>/scripts/vars.tcl
```

## Logic (mirrors the MCP tool exactly)

This skill uses `check_phoenix_intent` from `utils/utils.py`. Run the equivalent inline
via `python3`:

```bash
python3 - <<'PY'
import os, sys
sys.path.insert(0, "utils")
from utils import check_phoenix_intent

vars_tcl = os.path.join(
    "<destination_dir>", "runs", "<block_name>", "<technology>", "scripts", "vars.tcl"
)
intent = "<intent>" or None  # empty string -> None
result = check_phoenix_intent(vars_tcl, intent=intent)
print(result)
PY
```

Then react based on `result`:

- `result['updated']` is truthy → report `✓ <action>` (the intent was set/updated).
- `result['found']` is true and no `intent` was supplied → tell the user the current
  value of `phoenix_int` and ask if they want to change it to `power` or `timing`.
  If they say yes, re-invoke this skill with the chosen `intent`.
- `result['needs_input']` is true → `set ivar(phoenix_int)` is **not** in `vars.tcl`.
  Ask the user to choose `power` or `timing`, then re-invoke this skill with that
  value to append the line.
- Otherwise → report `✓ <action>`.

## Boundaries

- Use this skill **only** for client designs. For server designs use
  `phoenix-intent-server`.
- Never write to `vars.tcl` without an explicit user choice of `power` or `timing`.

---
name: phoenix-intent-server
description: After a Phoenix SERVER setup, inspect or update `set ivar(phoenix_int)` in the generated `vars.tcl` (located under `src/<block>/<tech>/scripts/vars.tcl`). Use whenever the user wants to check or change the Phoenix intent (`power` or `timing`) for a SERVER design. Replicates the `check_vars_tcl_phoenix_intent_server` MCP tool.
---

# Phoenix Intent — Server Designs

This skill replicates the `check_vars_tcl_phoenix_intent_server` MCP tool. It works
exclusively on **server** designs.

## When to use

- Immediately after `phoenix-setup` completes for a server design.
- Whenever the user wants to read or modify the Phoenix intent of a server design.

## Inputs

| # | Argument          | Required | Description |
|---|-------------------|----------|-------------|
| 1 | `destination_dir` | yes      | Destination directory used during `phoenix-setup`. |
| 2 | `block_name`      | yes      | Block / build name. |
| 3 | `technology`      | yes      | Technology node. |
| 4 | `intent`          | optional | `power` or `timing`. Leave empty to just inspect. |

The target file is:
```
<destination_dir>/src/<block_name>/<technology>/scripts/vars.tcl
```

Note the path uses `src/` (not `runs/`) — that is the only difference vs. the client
variant.

## Logic (mirrors the MCP tool exactly)

This skill uses `check_phoenix_intent` from `utils/utils.py`. Run the equivalent inline
via `python3`:

```bash
python3 - <<'PY'
import os, sys
sys.path.insert(0, "utils")
from utils import check_phoenix_intent

vars_tcl = os.path.join(
    "<destination_dir>", "src", "<block_name>", "<technology>", "scripts", "vars.tcl"
)
intent = "<intent>" or None  # empty string -> None
result = check_phoenix_intent(vars_tcl, intent=intent)
print(result)
PY
```

Then react based on `result`:

- `result['updated']` is truthy → report `✓ <action>`.
- `result['found']` is true and no `intent` was supplied → display the current value
  and ask whether to change it to `power` or `timing`. Re-invoke this skill with the
  user's choice.
- `result['needs_input']` is true → `set ivar(phoenix_int)` is missing. Ask for
  `power` or `timing`, then re-invoke this skill to append it.
- Otherwise → report `✓ <action>`.

## Boundaries

- Use this skill **only** for server designs. For client designs use
  `phoenix-intent-client`.
- Never write to `vars.tcl` without an explicit user choice of `power` or `timing`.

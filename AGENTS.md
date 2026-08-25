# Inside Valdivia H3 production-data runbook

This repository owns declarative H3 workflow specifications, project frame
ranges, experiment plans, and run-receipt references. It does not own ComfyUI
nodes, HTTP control, browser tabs, model files, or rendered media.

## Invariants

- Images and clips remain arbitrary media references; do not add semantic scene
  ontologies, descriptions, actions, or inferred object roles.
- The fixed soundtrack is an editorial clock only. Do not encode, generate, or
  train audio unless a future request explicitly changes that scope.
- All frame ranges are half-open `[start, end)` at an explicit frame rate.
- H3 production generation is 24 fps. Requested native frame counts follow
  `17k + 5`; prefer the documented trained range 124–362.
- Workflow specs state real graph operations and ownership. They are not
  importable UI/API graphs until materialized and validated against live
  `/object_info`.
- Workflow intent belongs in specs/graphs. Prefer orthogonal CAUCE operations
  and official/vanilla composition over one custom node named after a complete
  production workflow.
- A run receipt may say `executes`; only inspected media can say
  `visually-accepted` or `rejected`.
- No credentials, model binaries, inputs, outputs, or browser state belong here.
- Preserve dirty worktrees and never force-push.

## Verification

```bash
python3 tools/validate.py
python3 -m unittest discover -s tests -v
git diff --check
```

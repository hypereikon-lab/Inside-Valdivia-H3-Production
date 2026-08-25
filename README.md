# Inside Valdivia · H3 production data

Versioned, data-only definitions for invoking and evaluating CAUCE operations
for this project. The repository contains no second interface and no implicit
sequencing engine. It records exact frame ranges, media references, operation
bindings, parameters, and evidence.

Operation invocations are independent from editorial segments: a reference
transform or native-state continuation can exist and branch before any result
is assigned to the final 24 fps edit.

## Separation

```text
ComfyUI-Cauce
  generic operation contracts and deterministic custom nodes

ComfyUI-Runtime-Control
  neutral HTTP probe / validation / jobs / artifacts / receipts

ComfyUI-Workspace-Control
  browser-local workflow inventory and guarded tab operations

this repository
  locked operation versions, project invocations, experiments, receipt references
```

## Locked operation surface

```text
generate.keyframed
generate.from_references
generate.with_guides
continue.native_av
connect.two_sided_guides
reference.transform
frames.assemble
```

These names are independent functions, not stages. Their generic contracts are
content-addressed in CAUCE and pinned by `operations.lock.json`. This repository
stores concrete invocations only. CAUCE contains one checked, non-executable
topology dossier for each current operation; no reusable UI/API graph pair has
yet been promoted. See [operation usage](docs/OPERATIONS.md),
[data model](docs/DATA_MODEL.md), and [materialization](docs/MATERIALIZATION.md).

Current implementation and evidence record: [current state](docs/CURRENT_STATE.md).
Execution order and promotion gates: [production roadmap](docs/ROADMAP.md).

## Validate

```bash
python3 tools/validate.py
python3 -m unittest discover -s tests -v
python3 tools/verify_cauce_lock.py ../ComfyUI-Cauce
```

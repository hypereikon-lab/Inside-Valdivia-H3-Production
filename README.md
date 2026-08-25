# Inside Valdivia · H3 production data

Versioned, data-only definitions for building and evaluating the project's H3
graphs. The repository contains no second interface and no implicit timeline
engine. It records exact frame ranges, media references, workflow specs,
parameters, and evidence.

## Separation

```text
ComfyUI-Cauce
  deterministic custom nodes only

ComfyUI-Runtime-Control
  neutral HTTP probe / validation / jobs / artifacts / receipts

ComfyUI-Workspace-Control
  browser-local workflow inventory and guarded tab operations

this repository
  W1-W7 specs, project frame ranges, experiment plans, receipt references
```

## Canonical workflows

| ID | Operation |
| --- | --- |
| W1 | H3 keyframed generation: text-only, first-frame, last-frame, or first+last |
| W2 | H3 reference-conditioned generation with image/video references |
| W3 | H3 temporally guided generation through one or more `MiniMaxH3AddGuide` nodes |
| W4 | native H3 tail continuation using a characterized external node pack |
| W5 | H3 two-sided guide window with deterministic CAUCE extraction/assembly |
| W6 | deterministic motion-reference construction followed by official H3 reference conditioning |
| W7 | exact decoded frame-range selection and concatenation |

The JSON files in `workflow_specs/` are declarative materialization contracts,
not browser workflow exports. See [Canonical workflows](docs/WORKFLOWS.md),
[data model](docs/DATA_MODEL.md), and [materialization](docs/MATERIALIZATION.md).

## Validate

```bash
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

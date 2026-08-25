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

| ID | Operation | Implementation class |
| --- | --- | --- |
| W1 | H3 keyframed generation: text-only, first-frame, last-frame, or first+last | official H3 / vanilla ComfyUI |
| W2 | H3 reference-conditioned generation with image/video references | official H3 / vanilla ComfyUI |
| W3 | H3 temporally guided generation through one or more `MiniMaxH3AddGuide` nodes | official H3 / vanilla ComfyUI |
| W4 | native H3 AV span continuation | official H3 sampling + CAUCE AV primitives |
| W5 | two-sided decoded guides and accepted center range | official H3 guides + CAUCE exact ranges + vanilla assembly |
| W6 | deterministic motion-reference construction followed by H3 conditioning | CAUCE decoded-media preprocessing + official H3 |
| W7 | exact decoded frame-range selection and concatenation | CAUCE exact ranges + vanilla ComfyUI; no H3 inference |

The JSON files in `workflow_specs/` are declarative materialization contracts,
not browser workflow exports. See [Canonical workflows](docs/WORKFLOWS.md),
[data model](docs/DATA_MODEL.md), and [materialization](docs/MATERIALIZATION.md).

Current implementation and evidence record: [current state](docs/CURRENT_STATE.md).

## Validate

```bash
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

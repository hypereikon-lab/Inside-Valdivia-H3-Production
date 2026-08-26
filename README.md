# Inside Valdivia · H3 production data

Data-only production definitions for operating MiniMax H3 through ComfyUI.
This repository owns project bindings, materialization plans, rolling chains,
experiments, media indexes, editorial ranges, and evidence. It does not contain
a second interface, model code, model binaries, or an implicit creative
ontology.

Media remains opaque: images, clips, prompts, and packed native AV state are
identified and placed without inferring objects, actions, or scene meaning. The
fixed soundtrack is an external 24 fps editorial clock, not generative input.

## Responsibility boundary

```text
official ComfyUI H3 nodes
  model conditioning, sampling, decoding

ComfyUI-Cauce
  18 deterministic low-level nodes
  7 typed operation contracts
  21 checked topology dossiers

ComfyUI-Runtime-Control
  HTTP/runtime validation, prompt execution, receipts, durable serial resume

ComfyUI-Workspace-Control
  paired UI/API export and guarded browser-workspace operations

this repository
  exact CAUCE lock, 21 offline materialization plans, project data,
  experiments, rolling dependency/checkpoint plans
```

## Locked operations

```text
generate.keyframed
generate.from_references
generate.with_guides
continue.native_av
complete.native_av
rollback.native_av
frames.assemble
```

Operations are independent typed functions, not workflow stages. Their 21
variants are cataloged in
[`materialization/catalog.json`](materialization/catalog.json). A topology
dossier is a checked design, not executable workflow JSON. Each variant becomes
executable only after one live ComfyUI graph is exported in paired UI/API form,
validated against the same `/object_info` capture, and bound to concrete data.

The rolling plan in [`rolling/catalog.json`](rolling/catalog.json) records a
strict serial native-state chain, immutable checkpoints, and branch rules. It
does not auto-wire artifacts: concrete API graphs must already contain every
input binding before Runtime Control can execute and resume them safely.

## Documentation

- [Current state](docs/CURRENT_STATE.md)
- [Operations](docs/OPERATIONS.md)
- [Materialization](docs/MATERIALIZATION.md)
- [Data model](docs/DATA_MODEL.md)
- [Experiments](docs/EXPERIMENTS.md)
- [Roadmap](docs/ROADMAP.md)
- [Primary technical sources](docs/RESEARCH_SOURCES.md)

## Validate

```bash
python3 tools/validate.py
python3 -m unittest discover -s tests -v
python3 tools/verify_cauce_lock.py ../ComfyUI-Cauce
git diff --check
```

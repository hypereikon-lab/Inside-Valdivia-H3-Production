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
  28 deterministic low-level nodes
  13 typed operation contracts
  35 checked topology dossiers grouped into 32 graph archetypes

ComfyUI-Runtime-Control
  HTTP/runtime validation, prompt execution, receipts, durable serial resume

ComfyUI-Workspace-Control
  paired UI/API export and guarded browser-workspace operations

ComfyUI-Repository-Control
  inventory and exact clean fast-forward of approved public custom-node repos

this repository
  exact operation/archetype/component locks, 35 offline binding profiles,
  1 schema-validated paired draft, project data,
  runtime readiness profiles, acceptance criteria, storage policy,
  experiments, rolling dependency/checkpoint plans,
  24 tracked live invocations, 26 executed API graphs and immutable receipts
```

## Locked operations

The catalog is a capability grammar, not a production pipeline:

```text
H3 conditioning grammar     keyframed / references / guides
native H3 AV state algebra  continue / complete / densify / edit / refine / regenerate / outpaint / rollback
decoded media algebra       exact frame assembly
```

```text
generate.keyframed
generate.from_references
generate.with_guides
generate.with_control
continue.native_av
complete.native_av
densify.temporal
edit.masked_video
refine.video
regenerate.spatial
reframe.outpaint_video
rollback.native_av
frames.assemble
```

Operations are independent typed functions, not workflow stages. Their 35
materializable variants resolve through [`archetypes.lock.json`](archetypes.lock.json) to 32
structurally distinct graphs, then to project binding profiles cataloged in
[`materialization/catalog.json`](materialization/catalog.json). A topology
dossier is a checked design, not executable workflow JSON. Each variant becomes
executable only after one live ComfyUI graph is exported in paired UI/API form,
validated against the same `/object_info` capture, and bound to concrete data.
The first `generate.keyframed@text-only` pair satisfies the UI/API export and
schema-validation boundary; it remains an unqueued control. Separately, the
2026-08-31 characterization batch plus its sparse-anchor extension retained twenty-six exact executed API graphs
and their evidence, including a dense official-AddGuide temporal-expansion
ladder at 2x/3x/4x and stride-8/16 boundary tests. Those graphs are not presented as paired UI workflows, and
no generative variant is formally promoted.

The rolling plan in [`rolling/catalog.json`](rolling/catalog.json) records a
strict serial native-state chain, immutable checkpoints, and branch rules. It
does not auto-wire artifacts: concrete API graphs must already contain every
input binding before Runtime Control can execute and resume them safely.

[`materialization/live-gate.json`](materialization/live-gate.json) owns the
empirical materialization order independently of stable catalog priority. The
core, full, control-experimental, and learned-upscale-experimental runtime
profiles fail closed on missing nodes, models, hardware, or queue availability.
[`acceptance/catalog.json`](acceptance/catalog.json)
requires technical checks and a separate visual verdict before promotion.
[`runtime/compatibility-lock.json`](runtime/compatibility-lock.json) pins all
four control components and separates last-observed platform versions from the
next required compatibility target.

## Documentation

- [Project model](docs/PROJECT_MODEL.md)
- [Current state](docs/CURRENT_STATE.md)
- [Live H3 operation batch — 2026-08-31](docs/LIVE_BATCH_2026-08-31.md)
- [Current H3 capability map and workflow rebuild](docs/H3_CAPABILITY_MAP.md)
- [Expanded H3 capability gates](docs/H3_EXPANDED_CAPABILITIES.md)
- [Modular ComfyUI extension ecosystem](docs/NODEPACK_ECOSYSTEM.md)
- [H3 acceleration profiles](docs/ACCELERATION_PROFILES.md)
- [Native H3/Seedance movement-control research](docs/MOVEMENT_CONTROL_RESEARCH.md)
- [H3 intent routing and latent operator space](docs/H3_INTENT_ROUTING.md)
- [Temporal and spatial video enhancement](docs/VIDEO_ENHANCEMENT.md)
- [Operations](docs/OPERATIONS.md)
- [Materialization](docs/MATERIALIZATION.md)
- [Data model](docs/DATA_MODEL.md)
- [Experiments](docs/EXPERIMENTS.md)
- [H3 LoRA and fine-tuning boundary](docs/TRAINING.md)
- [Live laboratory gate](docs/LIVE_GATE.md)
- [Acceptance](docs/ACCEPTANCE.md)
- [Storage safety](docs/STORAGE.md)
- [Roadmap](docs/ROADMAP.md)
- [Primary technical sources](docs/RESEARCH_SOURCES.md)

## Validate

```bash
python3 tools/validate.py
python3 tools/readiness.py
python3 -m unittest discover -s tests -v
python3 tools/verify_cauce_lock.py ../ComfyUI-Cauce
python3 tools/verify_component_locks.py \
  ../ComfyUI-Cauce ../ComfyUI-Runtime-Control ../ComfyUI-Workspace-Control \
  ../ComfyUI-Repository-Control
git diff --check
```

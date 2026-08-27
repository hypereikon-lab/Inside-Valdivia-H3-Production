# Inside Valdivia H3 production-data runbook

This repository owns project operation invocations, frame ranges, experiment
plans, and run-receipt references. Generic operation contracts belong to the
version-locked CAUCE catalog. This repository does not own ComfyUI nodes, HTTP
control, browser tabs, model files, reusable generic graph templates, or
rendered media.

## Invariants

- Images and clips remain arbitrary media references; do not add semantic scene
  ontologies, descriptions, actions, or inferred object roles.
- The fixed soundtrack is an editorial clock only. Do not encode, generate, or
  train audio unless a future request explicitly changes that scope.
- All frame ranges are half-open `[start, end)` at an explicit frame rate.
- H3 production generation is 24 fps. Requested native frame counts follow
  `17k + 5`; prefer the documented trained range 124–362.
- Every invocation references one semantic CAUCE operation id, version, and
  contract hash from `operations.lock.json`.
- A generic operation contract is not an importable UI/API graph until CAUCE
  records a paired materialization validated against live `/object_info`.
- A CAUCE offline topology dossier is a graph design, not workflow JSON. Build
  the active graph from it, export the paired UI/API forms with Workspace
  Control, and use Runtime Control for guarded materialization.
- Resolve each topology key through `archetypes.lock.json`. A graph archetype
  is node/edge identity; the project materialization plan is its binding
  profile. Do not duplicate a paired graph when only guarded literals differ.
- Project data binds operations to concrete media and parameters; it must not
  duplicate generic graph ownership or create a creative workflow ontology.
- Rolling plans may encode only explicit serial data dependencies. Every later
  step binds the immediately preceding native state, every step checkpoints,
  and a branch starts as a new plan rather than mutating accepted history.
- Runtime Control executes only concrete prebound graphs. Never imply that it
  infers H3 semantics or automatically wires one prompt's artifacts into the
  next graph.
- A run receipt may say `executes`; only inspected media can say
  `visually-accepted` or `rejected`.
- `materialization/catalog.json` priority is stable inventory order;
  `materialization/live-gate.json` is the complete empirical execution order.
- Evaluate the locked runtime requirements and browser diagnostic before live
  graph construction. A browser-snapshot manifest is valid only when built from
  the bounded same-origin endpoints without extracting authentication cookies.
- `runtime/compatibility-lock.json` is the authority for source versions and
  core/full ComfyUI gates. A previous live version never proves the locked
  source is deployed.
- Every generative workflow must terminate in a history-resolvable saved video
  artifact. Decoded frames alone are not a durable production result.
- Promotion follows `acceptance/catalog.json`; all technical checks and an
  explicit visual verdict are mandatory.
- Preserve the storage reserve. Never automate model deletion or delete
  unindexed output paths.
- No credentials, model binaries, inputs, outputs, or browser state belong here.
- Preserve dirty worktrees and never force-push.

## Verification

```bash
python3 tools/validate.py
python3 tools/readiness.py
python3 -m unittest discover -s tests -v
python3 tools/verify_cauce_lock.py ../ComfyUI-Cauce
python3 tools/verify_component_locks.py \
  ../ComfyUI-Cauce ../ComfyUI-Runtime-Control ../ComfyUI-Workspace-Control
git diff --check
```

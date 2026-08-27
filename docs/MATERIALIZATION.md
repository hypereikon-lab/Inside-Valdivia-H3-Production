# Materialization and execution

`materialization/catalog.json` is the complete 28-variant offline queue. Every
entry selects one exact CAUCE `operation@variant` topology and one checked plan
in `materialization/plans/`.

Materialization advances one lifecycle boundary only:

```text
checked operation@variant topology
  -> paired UI graph + API template
```

Concrete project media belongs to an invocation; queue identity, artifacts,
and receipts belong to a run. See [Project model](PROJECT_MODEL.md).

The catalog's numeric `priority` is stable inventory order. It is not an
empirical claim about which mechanism should run first. The authoritative live
order is the complete, nonduplicating phase list in
`materialization/live-gate.json`.

## What the offline plans establish

```text
CAUCE commit, operation version, contract hash
exact variant and topology key
known laboratory model filenames
canonical geometry and 24 fps frame arithmetic
input cardinality and temporal placement
native-state/mask/rollback invariants
status = offline-ready
```

They intentionally do not invent graph node ids, API pointers, sampler,
scheduler, steps, shifts, seed, media ids, or runtime schema evidence. Null
live-owned fields are unresolved work, not defaults.

The queue covers:

- 4 FL2VA endpoint combinations;
- 4 Ref2VA image/video/guide combinations;
- 4 AddGuide image/clip/endpoint combinations;
- 3 native continuation transports;
- 4 native completion/replacement layouts;
- 3 spatial/spatiotemporal masked-edit layouts;
- 2 native outpaint placements;
- 2 bounded-refinement layouts;
- 1 rollback and 1 deterministic assembly.

## Live materialization gates

### 1. Capture one runtime truth

```bash
comfy-runtime --url https://comfy.hypereikon.online \
  probe --output runtime-manifest.json
```

Preserve the full manifest with `_captured_object_info`. Confirm exact node
types, model files, revisions, and storage before constructing graphs.

First evaluate `runtime/requirements/h3-core.json`; evaluate `h3-full.json`
before Ref2VA, AddGuide, video-loading, assembly, or the complete native-state
surface. When authentication exists only in the browser, use Runtime Control's
snapshot-manifest handoff rather than extracting the browser cookie.

### 2. Build one active graph

Resolve the selected topology key to its locked graph archetype first. Reuse an
already paired archetype when only guarded binding values differ. Use the CAUCE
topology dossier only as a construction checklist.
Connect official H3, vanilla ComfyUI, and narrow CAUCE nodes explicitly. Keep
optional topology branches absent; do not mute or bypass them inside one graph.

Decoded image frames become a durable 24 fps artifact through `CreateVideo`
and `SaveVideo`. A graph with no history-resolvable output node cannot advance
past materialization.

Bind exact values and media. Native operations additionally require absolute
timeline origins, H3-valid frame boundaries, independent video/audio masks,
and explicit retained-state inputs.

### 3. Export a paired graph

Retain both products from the same active browser graph:

```text
<operation>.<variant>.ui.json
<operation>.<variant>.api.template.json
```

The UI graph preserves layout/widgets; the API graph is executable structure.
Their hashes are independent and the formats are not interchangeable.

Parameterization names only literal API values that vary and guards each with
its captured expected value. Links are never replaced with parameters.

```bash
comfy-runtime materialize-export workspace-export.json parameterization.json \
  --operation-ref operation-ref.json \
  --variant exact-variant \
  --runtime-manifest runtime-manifest.json \
  --output-dir drafts
```

The result is still `requires-live-review` until reconstructed graph validation,
submission, receipt, and visual assessment are complete.

### 4. Execute and record evidence

Validate the concrete graph against fresh `/object_info`, submit once, persist
the returned prompt id, and resolve artifacts only from that prompt's history.
`executes` is technical evidence. Only inspected media may be marked
`visually-accepted` or `rejected`.

## Rolling production

`rolling/plans/native-continuation-chain.json` defines strict native-state
dependencies and checkpoints. It is a project plan, not `comfy.run-series/1`
input. After selected steps have concrete paired graphs:

1. resolve every input binding, including the preceding native-state file;
2. compile a distinct concrete API graph and operation reference per step;
3. create a neutral `comfy.run-series/1` plan whose dependencies match the
   project plan;
4. run it with persisted state, receipts, and optional artifact downloads.

Runtime Control validates every graph before the first mutation and resumes an
already-submitted prompt by exact id after interruption. It does not infer or
auto-wire outputs. Any branch starts as a new rolling plan from one immutable
checkpoint, optionally using `rollback.native_av` to select its prefix.

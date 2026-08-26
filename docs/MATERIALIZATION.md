# Materializing an operation invocation

## Offline package available before the lab session

`materialization/catalog.json` is the authoritative thirteen-item queue. Each
entry points to one project plan in `materialization/plans/` and to one exact
CAUCE dossier key written as `operation@variant`. The plans already fix every
invariant that can be known without the runtime:

```text
operation version and contract hash
static topology variant
model family and known laboratory filenames
canonical geometry and temporal baseline
input cardinality
operation-specific range arithmetic
promotion state = offline-ready
```

Values whose authority is the active graph or `/object_info` remain `null`:
sampler, scheduler, steps, shifts, seed, actual media ids, workspace export,
API pointers, runtime manifest, and output hashes. Filling those from memory
would make the plan look more complete while making it less reproducible.

`python3 tools/validate.py` checks the queue is contiguous, every file is
cataloged exactly once, every plan matches the operation lock, variant aliases
have not drifted, and the canonical H3 temporal/range rules still hold.
`python3 tools/verify_cauce_lock.py ../ComfyUI-Cauce` additionally checks the
locked CAUCE commit, operation contracts, and planned topology variants.

## Gate A — runtime capture

Run R1 immediately before graph construction and persist the full manifest:

```bash
comfy-runtime --url https://comfy.hypereikon.online \
  probe --output runtime-manifest.json
```

Preserve the runtime manifest hash and the embedded `_captured_object_info`
snapshot locally. Confirm the intended model files and free storage without
downloading anything implicitly. A compact public manifest is insufficient for
materialization because it does not contain the captured node schemas.

## Gate B — resolve and bind the operation

Open the next entry in `materialization/catalog.json` and complete its existing
plan. `fixtures/materialization-plan.json` remains a minimal format example.
Set or confirm:

- exact operation id, version, and contract hash from `operations.lock.json`;
- exact operation variant matching the graph topology being materialized;
- model/quantization files;
- width and height;
- valid H3 target frame count;
- prompt and seed;
- sampler, scheduler, steps, and flow shifts;
- exact input media references.

Create the corresponding Runtime Control reference using
`fixtures/operation-ref.json`; its three values must match the same lock entry.
Use a distinct operation-reference value for each selected operation; the
fixture is not a universal reference.

For `continue.native_av`, also bind `overlap_frames`, `extension_frames`, and
every sampled window's `timeline_origin_frame`. For
`connect.two_sided_guides`, bind the three exact decoded ranges and both guide
indices; do not replace them with a workflow-intent custom node.

Only the selected operation variant's required fields become graph nodes. Optional
branches remain absent rather than muted or bypassed.

Use the matching CAUCE topology dossier as a construction checklist. It is not
workflow JSON and must not be imported or promoted directly.

## Gate C — paired graph products

Create and retain both:

```text
<operation>.<variant>.ui.json            browser graph, layout, widgets, metadata
<operation>.<variant>.api.template.json  bindable server graph template
```

Export both from the same active graph through Workspace Control. The export
schema is `comfy.workspace-export/1` and contains both graph values plus their
independent hashes. The formats are not interchangeable.

Create `parameterization.json` by naming only literal API inputs that genuinely
vary between invocations. Each pointer includes the value captured in the
export as an expected-value guard:

```json
{
  "schema": "comfy.api-parameterization/1",
  "parameters": [
    {
      "name": "first_frame_filename",
      "pointers": ["/1/inputs/image"],
      "expected": "captured-first.png"
    }
  ]
}
```

Do not parameterize graph links. If a branch changes topology, create a distinct
operation variant.

Materialize with Runtime Control:

```bash
comfy-runtime materialize-export workspace-export.json parameterization.json \
  --operation-ref fixtures/operation-ref.json \
  --variant first-last \
  --runtime-manifest runtime-manifest.json \
  --output-dir drafts
```

The command produces four guarded files without overwriting existing files:

```text
<operation>.<variant>.ui.json
<operation>.<variant>.api.template.json
<operation>.<variant>.bindings.json
<operation>.<variant>.materialization.json
```

It requires the template plus captured bindings to reconstruct the exact API
graph hash. `schema-validated-draft` still carries the promotion gate
`requires-live-review`.

Generic validated pairs belong back in CAUCE. Project-specific compiled API
graphs and bindings remain in project receipts or the selected artifact store.

## Gate D — live schema validation

The materialization command validates the reconstructed API graph against the
same captured `/object_info`. Before submission, compile the template with the
intended production bindings and validate against the current live runtime as a
fresh check. A valid graph has:

- every referenced node type present;
- every required input present;
- links to existing source nodes and valid output slots;
- current combo values;
- no stale custom-node name from a previous version.

## Gate E — execution and evidence

Submit once, wait on its exact `prompt_id`, and resolve only its history
artifacts. The automatic receipt starts at `executes`. Watch the requested
range at normal speed and frame-by-frame before changing it to
`visually-accepted` or `rejected`.

Controlled comparisons change one declared experimental variable. Everything
listed under `fixed` remains byte-for-byte or value-for-value identical.

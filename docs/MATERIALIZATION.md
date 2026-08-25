# Materializing an operation invocation

## Gate A — runtime capture

Run R1 immediately before graph construction. Preserve the runtime manifest
hash and the complete `/object_info` snapshot locally. Confirm the intended
model files and free storage without downloading anything implicitly.

## Gate B — resolve and bind the operation

Copy `fixtures/materialization-plan.json` and set:

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

For `continue.native_av`, also bind `overlap_frames`, `extension_frames`, and
every sampled window's `timeline_origin_frame`. For
`connect.two_sided_guides`, bind the three exact decoded ranges and both guide
indices; do not replace them with a workflow-intent custom node.

Only the selected operation variant's required fields become graph nodes. Optional
branches remain absent rather than muted or bypassed.

## Gate C — paired graph products

Create and retain both:

```text
<operation>.<variant>.ui.json            browser graph, layout, widgets, metadata
<operation>.<variant>.api.template.json  bindable server graph template
```

Export both from the same active graph through Workspace Control. Their hashes
must be independent because the formats are not interchangeable.

Generic validated pairs belong back in CAUCE. Project-specific compiled API
graphs and bindings remain in project receipts or the selected artifact store.

## Gate D — live schema validation

Validate the API graph with ComfyUI Runtime Control against the captured
`/object_info`. A valid graph has:

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

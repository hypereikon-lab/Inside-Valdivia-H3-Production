# Materializing a workflow spec

## Gate A — runtime capture

Run R1 immediately before graph construction. Preserve the runtime manifest
hash and the complete `/object_info` snapshot locally. Confirm the intended
model files and free storage without downloading anything implicitly.

## Gate B — bind the spec

Copy `fixtures/materialization-plan.json` and set:

- exact W1–W7 version;
- model/quantization files;
- width and height;
- valid H3 target frame count;
- prompt and seed;
- sampler, scheduler, steps, and flow shifts;
- exact input media references.

Only the selected workflow's required fields become graph nodes. Optional
branches remain absent rather than muted or bypassed.

## Gate C — paired graph products

Create and retain both:

```text
<label>.ui.json   browser graph, layout, widgets, graph metadata
<label>.api.json  server-executable node/input/link object
```

Export both from the same active graph through Workspace Control. Their hashes
must be independent because the formats are not interchangeable.

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

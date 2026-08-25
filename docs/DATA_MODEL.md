# Production data model

## Segment

A segment is the smallest project record:

```text
id
frame_rate = 24
frame_range = [start, end)
workflow_spec = W1..W7
inputs = arbitrary media references
parameters = exact materialization values
status
run_receipts[]
```

It does not describe what is depicted. Images and clips remain opaque media
references. Any prompt is stored as the exact string sent to the graph, not as
an inferred decomposition of the image.

Frame ranges are authoritative. Seconds are derived display values:

```text
seconds = frames / 24
```

## Workflow specification

A workflow spec is reusable and project-independent. It defines one principal
operation, typed inputs/outputs, mathematical/model constraints, ordered graph
roles, variants, and evidence. It is not a UI graph and contains no widget
positions, browser tab state, concrete model paths, or runtime-specific combo
values.

## Materialization plan

A plan binds one workflow spec to a runtime manifest, exact model files,
resolution, frame count, prompt, seed, sampler, scheduler, steps, and input
media. Its products are a paired UI graph and API graph with separate hashes.

## Run receipt

ComfyUI Runtime Control records one immutable receipt per submitted prompt id:

```text
workflow spec hash
API graph hash
runtime manifest hash
history hash
artifacts
evidence status
receipt hash
```

Rendered media stays in ComfyUI or an external artifact store. This repository
stores only the receipt JSON or its content-addressed reference.

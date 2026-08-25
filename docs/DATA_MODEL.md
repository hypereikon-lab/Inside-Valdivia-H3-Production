# Production data model

## Operation invocation

An invocation is one call to a locked operation over explicit data:

```text
id
operation
operation_version
operation_contract_hash
inputs = arbitrary media references
parameters = exact materialization values
status
outputs
run_receipts[]
```

It does not describe what is depicted. Images and clips remain opaque media
references. Any prompt is stored as the exact string sent to the graph, not as
an inferred decomposition of the image.

An input may reference a local media URI or a named output of another
invocation. This produces an explicit data-dependency graph without imposing a
catalog order.

## Editorial segment

A segment assigns one or more invocation outputs to a range in the final visual
edit:

```text
id
frame_rate = 24
frame_range = [start, end)
sources[] = { invocation, output, accepted_range? }
status
```

Generation parameters do not live in the segment. The same invocation output
may be inspected, branched, or reused before any editorial assignment exists.

Frame ranges are authoritative. Seconds are derived display values:

```text
seconds = frames / 24
```

## Operation dependency

A generic operation contract is reusable and project-independent. It lives in
CAUCE, not in this repository. `operations.lock.json` pins its source commit,
catalog hash, operation version, and contract hash.

`tools/verify_cauce_lock.py` checks those values against an explicit local
CAUCE checkout; ordinary project validation does not silently depend on a
sibling directory.

Project records reference the operation; they do not restate its graph. The
same operation may be invoked repeatedly, nested in a larger composition, or
connected to another operation through typed outputs.

The CAUCE implementation class remains an ownership statement:

```text
official-h3
  only ComfyUI-shipped H3 and vanilla ComfyUI nodes

official-h3-with-cauce-primitives
  official inference composed with narrow deterministic CAUCE operations

cauce-and-vanilla-deterministic
  deterministic media processing with no H3 inference
```

The operation `reference.transform`, for example, produces decoded reference
media. A later invocation of `generate.from_references` consumes that media;
neither operation needs to know the project meaning of the frames.

## Materialization plan

A plan binds one locked operation to a runtime manifest, exact model files,
resolution, frame count, prompt, seed, sampler, scheduler, steps, and input
media. Its products are a paired UI graph and API graph with separate hashes.

## Run receipt

ComfyUI Runtime Control records one immutable receipt per submitted prompt id:

```text
operation id / version / contract hash
API graph hash
runtime manifest hash
history hash
artifacts
evidence status
receipt hash
```

Rendered media stays in ComfyUI or an external artifact store. This repository
stores only the receipt JSON or its content-addressed reference.

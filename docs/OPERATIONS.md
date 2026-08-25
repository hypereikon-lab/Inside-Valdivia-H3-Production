# Using CAUCE operations in Inside Valdivia

This project consumes a version-locked semantic operation catalog from CAUCE.
Operations are reusable data functions, not sequential production stages.

```text
project media + parameters
  -> one locked operation invocation
      -> frames and/or native H3 state
          -> optional later operation invocation
```

## Generation operations

### `generate.keyframed`

Official H3/vanilla generation from a prompt and optional first and last anchor
frames. CAUCE contributes the typed contract and reproducible materialization,
not custom inference behavior.

### `generate.from_references`

Official Ref2VA generation from ordered reference images or 24 fps clips. The
fixed production soundtrack remains outside conditioning.

The current ComfyUI node accepts a five-frame technical minimum, but production
baselines use legal `17k+5` clips inside the model's documented 2–15 second
reference-video range. The first such legal length is 56 frames.

### `generate.with_guides`

Official H3 generation with one or more decoded guides placed at exact target
frame indices. This is guide conditioning, not masked temporal inpainting.

## State operation

### `continue.native_av`

Extends a cumulative packed H3 AV latent while preserving exact visual and
structural-audio clocks. It composes CAUCE window/span/append primitives around
ordinary official sampling.

Every accepted generation intended for later native continuation must retain
its packed AV latent. A decoded video alone cannot provide the same state.

## Connection operation

### `connect.two_sided_guides`

Selects decoded context from both sources, places both through official H3
guides, generates a fresh target, retains the explicit center, and assembles
the complete sources around it. The graph is currently contract-only and its
visual usefulness remains unassessed.

## Deterministic media operations

### `reference.transform`

Constructs decoded, inspectable reference frames from CAUCE coordinate maps.
Its output can feed `generate.from_references` or `generate.with_guides` in a
separate invocation.

### `frames.assemble`

Selects exact half-open decoded ranges and concatenates them without inference
or resampling.

## Composition examples

```text
reference.transform
  -> generate.from_references
  -> continue.native_av
  -> frames.assemble
```

```text
generate.keyframed
  -> continue.native_av
  -> continue.native_av
```

```text
decoded sources
  -> connect.two_sided_guides
  -> frames.assemble
```

The project stores each invocation separately. Composition is expressed by one
invocation referencing another invocation's exact artifact or native-state
output, never by assuming implicit progression.

## Current project evidence

Only `continue.native_av` has current-system live execution evidence, and that
evidence is a synthetic one-step structural smoke without visual evaluation.
All seven operations now have internally checked offline topology dossiers,
but none has a retained UI/API pair. All other operations remain locked
contracts until paired graphs are materialized and evaluated.

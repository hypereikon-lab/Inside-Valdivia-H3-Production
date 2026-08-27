# Production data model

## Operation invocation

One call to one locked operation:

```text
id
operation / version / contract hash
inputs = opaque media or named native-state references
parameters = exact materialized values
outputs
status and immutable run receipts
```

Prompts are exact submitted strings. Images and clips are never decomposed into
project-level scene entities.

## Materialization plan

Acts as a project binding profile: it selects one topology key, resolves that
key through `archetypes.lock.json`, and records every invariant knowable before
live ComfyUI construction. Multiple profiles may share one node/edge archetype.
`offline-ready` means the static contract is consistent; it does not mean
UI/API workflow JSON exists.

## Rolling plan

A strict ordered dependency graph for long native-state production:

```text
step id and position
locked operation@variant
materialization plan
explicit previous-state binding
unique output native-state id
checkpoint and branch policy
exact CAUCE and Runtime source commits
```

The first step may have unresolved external media while offline. Every later
step must explicitly bind the immediately preceding state. Each output state is
unique. A branch is a new plan from a content-addressed checkpoint; accepted
history is immutable.

The rolling plan remains distinct from Runtime Control's executable serial
plan. The latter contains concrete graph and operation-reference paths only
after all bindings have been compiled.

## Media catalog

`media/catalog.json` indexes real bytes only after hashing:

```text
logical id and SHA-256
exact Comfy filename
image / video / native AV latent
frame count, fps, geometry, byte size
origin invocation and availability state
```

Unresolved placeholders remain in plans. Rendered bytes remain in ComfyUI or an
external artifact store.

## Editorial segment

Assigns accepted invocation outputs to `[start,end)` ranges at 24 fps. It does
not own generation parameters. Seconds are display values derived as
`frames / 24`. The fixed soundtrack is aligned here as an external clock.

## Run receipt

Runtime Control records the exact operation reference, API graph hash, runtime
manifest hash, prompt id/history, artifacts, evidence status, and receipt hash.
A receipt can prove execution but not visual quality.

## Content-addressed ownership

`operations.lock.json` pins the CAUCE source commit, catalog hash, and every
operation contract hash. `archetypes.lock.json` pins the structural signatures
and exact topology membership. `runtime/compatibility-lock.json` pins the
CAUCE, Runtime Control, and Workspace Control commit/tree/version/metadata
tuple plus explicit platform gates. `tools/verify_cauce_lock.py` additionally
requires exact archetype equality and one-to-one coverage between all current
CAUCE topology dossiers and project materialization plans.

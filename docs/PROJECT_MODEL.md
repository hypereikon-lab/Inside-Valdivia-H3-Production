# Project model

The project turns native ComfyUI H3 capabilities into reproducible production
operations. It does not add an image ontology or interpret media content.

## Capability families

The ten locked operations form three non-sequential families:

```text
H3 conditioning grammar
  generate.keyframed
  generate.from_references
  generate.with_guides

native H3 AV state algebra
  continue.native_av
  complete.native_av
  edit.masked_video
  refine.video
  reframe.outpaint_video
  rollback.native_av

decoded media algebra
  frames.assemble
```

The conditioning family describes supported official ways to present prompt,
endpoint, reference, and exact-frame guide information to H3. The native-state
family extends, completes, locally edits, refines, reframes, splits,
reconstructs, and branches synchronized packed H3 state. The decoded family
performs exact post-decode assembly.

Family membership does not define execution order. Operations connect only
through explicit typed media or native-state references.

## Lifecycle

```text
primitive
  low-level official, vanilla, or CAUCE node/data transform

operation
  typed graph-level data function

variant
  checked static topology of one operation

workflow pair
  UI graph + API template exported from the same live ComfyUI graph

invocation
  workflow pair + project media and concrete parameter bindings

run
  exact prompt id + runtime manifest + artifacts + immutable receipt

evidence
  technical evidence level + independent human visual verdict
```

The repository never promotes two lifecycle states implicitly. A checked
topology is not executable workflow JSON; an executable queue item is not
visual acceptance; a decoded MP4 is not a recoverable substitute for packed
native AV state.

## Data boundary

Images, clips, prompts, and native-state artifacts are opaque, content-addressed
inputs. The repository records their identities, order, placement, lineage,
and accepted editorial ranges without inferring objects, actions, or scenes.

The fixed soundtrack is the external 24 fps editorial clock. H3 structural
audio remains inside packed native state only where model/state consistency
requires it; it is not the production soundtrack or a generative objective.

## Repository responsibilities

```text
official ComfyUI H3
  model loading, conditioning, sampling, decode

CAUCE
  low-level deterministic primitives and portable operation contracts

Workspace Control
  guarded browser-workspace inventory and paired UI/API export

Runtime Control
  live schema validation, exact prompt execution, resume, artifacts, receipts

Production
  project plans, concrete bindings, native-state lineage, experiments,
  editorial placement, and visual decisions
```

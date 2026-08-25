# Canonical H3 workflows

These seven specifications cover the current useful operation families without
inventing a semantic media ontology or duplicating official nodes. A workflow
spec states intent, inputs, outputs, constraints, and ownership. A concrete UI
graph and API graph are later materializations against one live runtime.

## Implementation ownership

| ID | What is genuinely custom | Current artifact state |
| --- | --- | --- |
| W1 | nothing; it is an official H3/vanilla ComfyUI graph | declarative spec only |
| W2 | nothing; it is an official H3/vanilla ComfyUI graph | declarative spec only |
| W3 | nothing; it chains official `MiniMaxH3AddGuide` nodes | declarative spec only |
| W4 | absolute AV window/span/append math and persistence from CAUCE | spec plus one synthetic API execution; reusable graph files not yet retained |
| W5 | exact decoded range selection from CAUCE | declarative spec only |
| W6 | deterministic decoded-media coordinate maps from CAUCE | declarative spec only |
| W7 | exact decoded range selection from CAUCE | declarative spec only |

“Declarative spec only” means the operation is precisely described but no
importable UI graph or executable API template is currently shipped. It is an
implementable composition, not an already materialized capability.

## W1 — H3 keyframed generation

One official `MiniMaxH3ImageToVideo` graph covers four modes:

```text
prompt only                  text-to-video
prompt + first frame         first-frame-conditioned generation
prompt + last frame          last-frame-conditioned generation
prompt + first + last        first/last-frame-conditioned generation
```

The first frame is placed at frame 0 and the last at the actual snapped final
frame. They are individual anchors, not motion streams. This is the smallest
canonical graph for producing one interval from frames and a prompt.

This workflow uses ComfyUI-shipped official H3 nodes and ordinary vanilla
loaders, sampler, decoder, and output nodes. CAUCE is not involved.

## W2 — H3 reference-conditioned generation

`MiniMaxH3ReferenceToVideo` accepts ordered reference images and 24 fps
reference clips. Prompt tags refer to them as `<Picture i>` and `<Video k>`.
The official `match` image-size mode limits reference pixel area to the target;
`max` uses a larger reference path and may cost substantially more sampling
time because the reference tokens remain present through the sampling steps.

This workflow also uses only ComfyUI-shipped official H3 and vanilla nodes.
Its value here is reproducible parameterization and evidence, not custom model
functionality.

The project deliberately leaves audio-reference inputs disconnected. H3 still
uses its packed structural-audio stream internally, but the fixed production
soundtrack is not used as conditioning and is not regenerated.

## W3 — H3 temporally guided generation

Start with a fresh target and base prompt conditioning. Chain one official
`MiniMaxH3AddGuide` per guide. Each guide has an exact pixel-frame index.

- fewer than five supplied frames become a single-frame guide;
- multi-frame guides are cropped to a valid `17k+5` length;
- the entire resolved guide must fit inside the target;
- negative indices count from the end;
- chained nodes accumulate guide keyframes in conditioning.

This is the general operation for arbitrary frame or clip anchors inside one
generation. It does not imply inpainting: no preserved source and mask are
present unless a separate documented mechanism supplies them.

No CAUCE node is required. The operation is an explicit chain of official H3
guide nodes.

## W4 — H3 native tail continuation

This workflow is narrower than decoded-video continuation. It composes CAUCE's
low-level packed-AV operations around ordinary official sampling:

```text
source native AV latent
  -> inspect + plan absolute AV window
  -> allocate globally aligned target
  -> extract synchronized native tail span
  -> add span to official positive conditioning
  -> normal official H3 sampling of the allocated target
  -> extract only the generated suffix span
  -> append the globally contiguous suffix
```

The operation deserves the word `continuation` because it carries native H3
state across the boundary without a VAE round trip. The canonical starting
layout keeps the inspected reference geometry `22 overlap + 119 new = 141
target`; alternative values are controlled experiments. No CAUCE node owns the
complete workflow or its prompt/sampler policy.

## W5 — H3 two-sided guide window

CAUCE selects deterministic decoded ranges; official nodes generate and vanilla
nodes concatenate:

```text
tail(left source) -> AddGuide at 0
head(right source) -> AddGuide at target - guide_length
fresh H3 target -> sample -> decode
accept [guide_length, target - guide_length)
assemble complete left + accepted generated range + complete right
```

With a 124-frame target and two 22-frame guides, 80 generated frames are
accepted. No two-sided preset node or hidden plan object exists: the exact
ranges and guide indices live in the workflow and run receipt. Whether H3
produces a usable connection is a per-source visual result.

## W6 — motion-reference construction

CAUCE coordinate maps build decoded, inspectable reference media before H3:

```text
source frames
  -> arbitrary deterministic coordinate maps
  -> compose maps
  -> one final image sample
  -> inspect reference clip
  -> official Ref2VA or AddGuide input
```

This path constructs decoded reference media before official H3 conditioning.
It does not directly warp H3 latents or alter sampler internals.

## W7 — exact decoded frame assembly

W7 performs no model inference. It selects explicit half-open decoded ranges
and concatenates them. It is used after a generation whenever only part of a
target is accepted or several accepted clips form an editorial interval.

The fixed soundtrack is muxed downstream against these exact frame ranges. It
remains the editorial clock, not a model input.

## Present boundary and extensibility

The current system can compose new graphs from official nodes and the listed
CAUCE primitives. That makes additional workflows implementable without adding
a new custom node whenever the needed behavior is graph composition.

The repositories do not currently contain:

- import-tested UI graphs for W1–W7;
- reusable executable API templates for W1–W7;
- a high-level graph synthesizer that turns an arbitrary intent into a graph;
- a masked temporal-inpainting primitive;
- production-resolution visual acceptance for W1–W7 under the current system.

Runtime Control can bind and validate an existing API template. Workspace
Control can manage and export browser graphs once installed. Neither invents
model operations; model capability remains bounded by official H3 conditioning
and sampling plus the explicit deterministic transformations in CAUCE.

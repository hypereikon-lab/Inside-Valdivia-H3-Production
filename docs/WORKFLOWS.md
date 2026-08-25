# Canonical H3 workflows

These seven specifications cover the current useful operation families without
inventing a semantic media ontology or duplicating official nodes. A workflow
spec states intent, inputs, outputs, constraints, and ownership. A concrete UI
graph and API graph are later materializations against one live runtime.

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

## W2 — H3 reference-conditioned generation

`MiniMaxH3ReferenceToVideo` accepts ordered reference images and 24 fps
reference clips. Prompt tags refer to them as `<Picture i>` and `<Video k>`.
The official `match` image-size mode limits reference pixel area to the target;
`max` uses a larger reference path and may cost substantially more sampling
time because the reference tokens remain present through the sampling steps.

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

This retains the useful part of procedural motion work while respecting H3's
architecture. It does not directly warp H3 latents or alter sampler internals.
Rejected latent-forcing experiments are not part of the canonical system.

## W7 — exact decoded frame assembly

W7 performs no model inference. It selects explicit half-open decoded ranges
and concatenates them. It is used after a generation whenever only part of a
target is accepted or several accepted clips form an editorial interval.

The fixed soundtrack is muxed downstream against these exact frame ranges. It
remains the editorial clock, not a model input.

# Operation surface

An operation is a typed graph-level data function over opaque media or packed
native H3 state. It is not a monolithic custom node and its name does not imply
production order.

## H3 conditioning grammar

### `generate.keyframed`

FL2VA with prompt and zero, one, or two endpoint images. Variants are
`text-only`, `first-frame`, `last-frame`, and `first-last`. Official
`MiniMaxH3ImageToVideo` owns the conditioning.

### `generate.from_references`

Ref2VA with ordered image references and optional 24 fps reference clips.
Variants isolate `ref_image_size=match|max`, video reference, and video
reference plus a temporal guide. Production reference clips use legal `17k+5`
lengths inside the documented 2–15 second range.

### `generate.with_guides`

Official AddGuide chains place images or clips at exact target-frame indices.
Variants cover one anchor, multiple anchors, one guide clip, and first/last
endpoints plus an interior guide. A guide is conditioning, not a denoise mask.

## Native H3 AV state algebra

### `continue.native_av`

Extends cumulative synchronized H3 video/structural-audio state. The
`keyframe-overlap` variant transports the overlap through official H3
keyframes. `masked-overlap` supplies retained native tokens plus independent
per-token denoise masks. `masked-overlap-future-guide` adds a decoded future
guide without conflating guide placement and mask semantics.

### `complete.native_av`

Samples an unknown temporal interval while preserving explicit native context.
The same low-level placement/mask/replace grammar expresses:

- `two-sided-infill`: an unknown interior in one target state;
- `local-replacement`: regenerate an interval of an existing state;
- `backward-prefix`: generate before known right context;
- `two-source-connection`: place exact left/right states around a gap.

Video and structural-audio masks are independent continuous values in `[0,1]`.
`1` asks the official sampler to generate and `0` preserves supplied native
tokens. Fades are evaluated at each stream's real token centers, not by copying
one approximate mask between 24 fps and 40 Hz clocks.

### `edit.masked_video`

Re-denoises a continuous spatial or spatiotemporal region of an existing native
H3 state. A static mask spans the selected interval; an animated mask supplies
exactly one mask per selected decoded frame and is reduced with `amax` inside
each native visual token. `local-retake` intersects an exact temporal interval
with the video mask. The complement and structural-audio stream remain
preserved in the baseline.

### `refine.video`

Runs a bounded second H3 pass from the original native AV state. `full-frame`
applies one continuous video strength to the complete duration; `masked`
multiplies that strength by a spatial or spatiotemporal mask. Denoise strength
has no accepted default and must be selected through a fixed-source,
fixed-seed live ladder.

### `reframe.outpaint_video`

Copies an existing visual latent without interpolation into a larger
32-pixel-aligned canvas, preserves structural audio and duration, and samples
only newly allocated regions. Variants distinguish exact centered placement
from an explicit aligned offset.

### `rollback.native_av`

Splits cumulative state at an exact synchronized boundary into a branchable
prefix and reversible suffix. A branch creates a new production plan from a
checkpoint; it never rewrites the accepted history in place.

Packed native AV state must be retained for continuation, completion, rollback,
or branching. Decoding to MP4 and re-encoding does not reconstruct identical
native state.

## Decoded media algebra

### `frames.assemble`

Selects exact half-open decoded ranges and concatenates them without inference
or resampling.

## Composition

```text
generate.keyframed -> continue.native_av -> continue.native_av

native state + explicit interval -> complete.native_av -> rollback.native_av

native state + continuous mask -> edit.masked_video

native state -> refine.video or reframe.outpaint_video

accepted decoded ranges -> frames.assemble
```

Edges are explicit artifact/native-state references. The catalog never assumes
that one operation automatically follows another.

The lifecycle after an operation is variant, paired workflow, project
invocation, exact run, and evidence. These states are defined in
[Project model](PROJECT_MODEL.md) and must never be collapsed.

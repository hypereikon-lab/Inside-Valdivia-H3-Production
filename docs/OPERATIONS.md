# Operation surface

An operation is a typed graph-level data function over opaque media or packed
native H3 state. It is not a monolithic custom node and its name does not imply
production order.

## Official generation

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

## Native AV state

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

### `rollback.native_av`

Splits cumulative state at an exact synchronized boundary into a branchable
prefix and reversible suffix. A branch creates a new production plan from a
checkpoint; it never rewrites the accepted history in place.

Packed native AV state must be retained for continuation, completion, rollback,
or branching. Decoding to MP4 and re-encoding does not reconstruct identical
native state.

## Deterministic decoded media

### `frames.assemble`

Selects exact half-open decoded ranges and concatenates them without inference
or resampling.

## Composition

```text
generate.keyframed -> continue.native_av -> continue.native_av

native state + explicit interval -> complete.native_av -> rollback.native_av

accepted decoded ranges -> frames.assemble
```

Edges are explicit artifact/native-state references. The catalog never assumes
that one operation automatically follows another.

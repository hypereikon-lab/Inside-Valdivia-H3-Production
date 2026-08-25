# Production roadmap

This roadmap turns the existing low-level system into reproducible H3
operations. It does not add a sequential creative ontology: every retained
workflow remains an independent, parameterizable operation over opaque media.

## Completion rule

An operation becomes production-ready only after one exact variant has:

```text
paired UI/API export
  -> guarded parameterization
  -> validation against the same live /object_info capture
  -> successful exact prompt_id execution
  -> immutable receipt and artifact references
  -> explicit visual verdict
```

Queue completion proves `executes`; it never proves visual acceptance.

## Phase 0 — reconcile the laboratory runtime

1. Probe routes, `/features`, `/system_stats`, `/object_info`, Manager state,
   queue state, and free disk space.
2. Inventory exact installed custom-node packages and Git revisions.
3. Confirm or install Workspace Control through one targeted action.
4. Update only CAUCE to the project-locked commit.
5. Remove installed copies of the retired SamplerLab and legacy Hypereikon H3
   production packages if present.
6. Restart only the ComfyUI process once all targeted changes are complete.
7. Verify all 24 CAUCE nodes, the Workspace Control capability route, an idle
   queue, and unchanged H3 model filenames.

This phase must not update ComfyUI core, CUDA, PyTorch, drivers, models, or
unrelated custom nodes.

## Phase 1 — materialize the canonical operation variants

Build one active graph at a time. Export its paired UI/API forms through
Workspace Control and materialize them through Runtime Control.

| Priority | Operation variant | Primary purpose |
| --- | --- | --- |
| 1 | `generate.keyframed.first-frame` | generate forward from one exact frame |
| 2 | `generate.keyframed.first-last` | connect two exact endpoint frames |
| 3 | `generate.from-references.image-match` | ordered image references at bounded token cost |
| 4 | `generate.from-references.video-reference` | motion/structure from one 24 fps reference clip |
| 5 | `generate.with-guides.single` | one exact image or clip at an arbitrary frame |
| 6 | `generate.with-guides.two` | two explicit temporal anchors |
| 7 | `continue.native-av.overlap-22-extension-119` | extend retained native state without a sampler patch |
| 8 | `connect.two-sided-guides.guide-22-target-124` | generate and retain an explicit center between sources |
| 9 | `frames.assemble.ordered` | concatenate exact accepted decoded ranges |

Text-only, last-frame-only, `ref_image_size=max`, three-or-more-guide, and
alternative continuation layouts remain later variants. They are not hidden
branches inside the first canonical graphs.

## Phase 2 — establish baselines

For each materialized H3 graph, retain one baseline configuration:

```text
exact model filenames
resolution and target frame count
prompt string
seed
sampler / scheduler / steps / denoise
video and structural-audio shifts
ordered input filenames and hashes
output prefix
```

Reference-video baselines use valid `17k+5` lengths inside the documented
2–15 second range. Although the current ComfyUI implementation accepts five
frames, sub-two-second references are out-of-spec experiments rather than
production defaults.

## Phase 3 — controlled visual experiments

Run the checked experiment catalog only after its operation variant has a
paired graph. Change one declared variable per comparison and retain every
rejected verdict as evidence rather than as a capability.

First comparisons:

1. first-frame versus first-last anchor behavior;
2. Ref2VA image `match` versus `max`;
3. Ref2VA reference duration at 56, 73, 90, 107, and 124 frames;
4. AddGuide length and placement;
5. native continuation with the same prompt versus a controlled continuation;
6. two-sided guide lengths 5, 22, and 39.

Procedural motion-reference transforms remain optional until one simple
Ref2VA baseline demonstrates useful correspondence. Direct latent transport,
sampler patches, masked temporal inpainting, and LanPaint are excluded.

## Phase 4 — production records and storage

Create real project invocations only from accepted or intentionally exploratory
materialized variants. Each external media input needs a manifest containing:

```text
logical id
content hash
Comfy input/output filename
media type
frame count / fps / geometry
file size
origin invocation, when generated
```

Retain the packed AV latent for any result that may be continued, rolled back,
or branched. Download accepted outputs away from the laboratory tower. Delete
only explicitly rejected or redundant artifacts, keep a declared free-space
reserve, and never automate model deletion.

Editorial segments assign accepted invocation outputs to exact 24 fps frame
ranges. The fixed soundtrack remains an external editorial clock.

## Operational hardening outside the repositories

The laboratory operator should configure ComfyUI to start with Windows and
restart after process failure, disable sleep during production windows, and
confirm the tower's desired behavior after AC loss. `cloudflared` remains a
service. A scoped Cloudflare Access service token may later authenticate
Runtime Control without an interactive browser session; it cannot recover an
offline tower or stopped ComfyUI process.

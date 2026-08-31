# MiniMax H3 capability map

This document defines the source-informed surface from which canonical
Inside Valdivia workflows are rebuilt. Historical CAUCE example graphs are
not restoration targets. A new workflow starts with the smallest current
official ComfyUI H3 graph and adds CAUCE only when an operation needs native
AV-state algebra that upstream does not expose.

Checked on 2026-08-31 against:

- ComfyUI `v0.34.0`, commit
  `12d5279438bfefc058a269eae805ceab6047777f`;
- ComfyUI `master`, commit
  `95d755cd8107a72258d452b5d3657273d571f07d`, for observation only;
- official workflow templates commit
  `4c4b8cbc04e01507b11d69f207c2209a59362420`, including the current H3 I2V template;
- the MiniMax H3 model card and official prompt guides;
- merged and open ComfyUI H3 pull requests listed below.

The laboratory runtime remains authoritative. These source observations do
not assert that its current checkout has the same code.

## Truth levels

Every capability belongs to exactly one level:

1. **released-native**: present in ComfyUI `v0.34.0` and eligible for a
   canonical workflow;
2. **project-primitive**: deterministic CAUCE state manipulation backed by
   tests, but still requiring live H3 execution and visual evidence;
3. **upstream-pending**: implemented in an open ComfyUI pull request and not a
   production dependency;
4. **community-reference**: useful external evidence or an optional future
   dependency, never silently treated as installed;
5. **excluded**: outside the current project scope or empirically rejected.

`implemented`, `materialized`, `executes`, and `visually accepted` remain
separate states.

## Released native H3 surface

### Target and sampling

Official ComfyUI owns:

- packed joint video/audio latent allocation;
- released empty H3 AV latent allocation through
  `EmptyMiniMaxH3LatentAV`;
- the `17k+5` decoded-frame lattice at 24 fps;
- target canvas alignment to multiples of 32;
- an optional H3 video/audio sigma-shift patch;
- model loading, guider, scheduler, sampler, VAE decode and video saving;
- stock sampler compatibility through H3's internal AV schedule mapping.

The local base model is treated as a 768p, approximately 5--15 second model.
Longer values accepted by a node widget are not production evidence. The
project builds longer works from explicit clips and retained checkpoints.

### Endpoint conditioning

`MiniMaxH3ImageToVideo` natively expresses four distinct workflows with one
topology:

- no image: text-to-video;
- `first_frame`: first-frame generation;
- `last_frame`: last-frame generation;
- `first_frame` plus `last_frame`: first/last-frame generation.

These are bindings of one official graph, not four CAUCE operations.

### Reference conditioning

`MiniMaxH3ReferenceToVideo` natively accepts ordered reference images, video
clips and audio. Inside Valdivia uses image and video references only. The
prompt addresses them with their official `<Picture i>` and `<Video k>`
labels.

The released node provides two image-sizing policies:

- `match`: downscale to the generated target's pixel area; default production
  baseline;
- `max`: use the larger reference path for a controlled fidelity/cost
  comparison.

A reference conditions the generated shot. It is not an exact endpoint, an
editable source latent, or a time-local denoise mask.

### Arbitrary temporal guides

`MiniMaxH3AddGuide` places a still image or a legal-length clip at an arbitrary
target frame. Negative indices count from the end, and nodes can be chained.
Multi-frame guides are trimmed to `5, 22, 39, ...` frames.

This released primitive directly supports:

- one interior still anchor;
- multiple ordered still anchors;
- one or more clip anchors;
- a previous clip tail anchored at frame zero;
- a known right-hand context anchored near the target end;
- left and right context clips around a newly generated bridge;
- Ref2VA conditioning followed by one or more temporal guides.

Continuation, backward completion and a two-sided bridge therefore begin as
compositions of official conditioning nodes. They only need CAUCE when exact
native latent transport or masked preservation is required.

### Continuous per-token denoise masks

Released ComfyUI accepts H3 denoise masks on the packed AV state. For the video
stream, continuous values in `[0,1]` are pooled with `amax` onto each 2x2
latent-patch row and quantized to `1/256` increments. A value of `1` generates
at the stream's active sigma; `0` pins the supplied latent near H3's
conditioning timestep. The audio stream has its own temporal mask.

This is the native sampling mechanism for:

- temporal replacement;
- two-sided temporal inpainting;
- static spatial inpainting;
- animated spatiotemporal masks;
- a temporal interval intersected with a spatial mask;
- partial-strength refinement;
- generating only the newly allocated border of an expanded canvas.

The core owns how mask values alter H3 timesteps. CAUCE must not reproduce
that sampler logic; it may only construct exact masks and native target state.

### Prompt embeddings and PDD

Prompt embedding syntax is released, but no project workflow currently needs
it. PDD acceleration LoRAs were merged after `v0.34.0`; acceleration is not a
current project goal and is not part of the canonical suite.

## CAUCE's remaining role

CAUCE is justified only for operations the released official graph cannot
express as transparent wiring:

- inspect and validate a packed H3 AV latent;
- allocate a packed AV window when the target is not produced directly by an
  official conditioning node;
- extract, place, append, split and replace exact synchronized AV spans;
- attach exact temporal or spatiotemporal masks to packed state;
- expand a native visual latent on a larger aligned canvas without a
  decode/resize/encode round trip;
- save and load the paired native state between runs;
- clear consumed mask metadata;
- retain exact global frame-origin metadata for chains and branches.

These are low-level data operations. They must stay individually wireable and
must not become a second H3 sampler, prompt language, timeline interface or
monolithic generation node.

The following current CAUCE planning nodes are conveniences, not required
workflow semantics, and are candidates for removal or demotion after live
comparison with released upstream behavior:

- `CauceH3ResolveTargetShape`;
- `CauceH3PrepareGuideClip`;
- `CauceH3PrepareReferenceClip`;
- `CauceH3InspectConditioning`.

Any CAUCE target-allocation path must likewise be compared against the released
`EmptyMiniMaxH3LatentAV` node before it is retained as a distinct primitive.

Likewise, `generate.keyframed`, `generate.from_references` and
`generate.with_guides` are project workflow families over official nodes. They
should not imply that CAUCE implements those generation mechanisms.

## Canonical workflow suite to rebuild

The suite is organized by data function, not by numbered stages.

### Official baselines

| Workflow | Official conditioning | CAUCE required |
| --- | --- | --- |
| Text generation | `MiniMaxH3ImageToVideo` | no |
| First-frame generation | `MiniMaxH3ImageToVideo.first_frame` | no |
| Last-frame generation | `MiniMaxH3ImageToVideo.last_frame` | no |
| First/last-frame generation | both endpoint inputs | no |
| Image-reference generation | `MiniMaxH3ReferenceToVideo` | no |
| Video-reference generation | `MiniMaxH3ReferenceToVideo` | no |
| Mixed image/video references | `MiniMaxH3ReferenceToVideo` | no |
| Interior still guide | conditioning plus `MiniMaxH3AddGuide` | no |
| Multiple temporal guides | chained `MiniMaxH3AddGuide` | no |
| Guide clip | `MiniMaxH3AddGuide.image` batch | no |
| References plus temporal guide | Ref2VA plus AddGuide | no |

These graphs establish model behavior before custom state manipulation is
introduced.

### Temporal composition

| Workflow | Baseline mechanism | Optional exact-state variant |
| --- | --- | --- |
| Continue forward | previous tail clip at frame zero | CAUCE latent tail placement |
| Complete backward | known head/right clip near target end | CAUCE right-state placement |
| Bridge two clips | left and right guide clips | CAUCE two-sided state plus mask |
| Close a loop | end/start guides in one bridge window | CAUCE seam-local replacement |
| Repair a join | two-sided guides around a masked interval | CAUCE continuous mask and exact replacement |
| Retake an interval | native source plus temporal mask | CAUCE mask construction |
| Branch from a checkpoint | load, split, retain prefix, generate suffix | CAUCE persistence and span algebra |

Pixel-guide and exact-native variants are separate workflows and evidence
records. The native variant should only be preferred after it demonstrates a
measurable benefit over the simpler released path.

### Spatial and spatiotemporal editing

| Workflow | Mechanism | Status |
| --- | --- | --- |
| Static region edit | encoded/native state plus continuous mask | project-primitive |
| Animated region edit | one mask frame per selected video frame | project-primitive |
| Local retake | spatial mask multiplied by temporal interval | project-primitive |
| Reframe/outpaint | aligned expanded latent, preserved interior, generated border | project-primitive |
| Whole-shot second pass | uniform nonzero denoise mask | characterization only |
| Masked second pass | scaled spatial/spatiotemporal mask | characterization only |

Refinement and outpainting are not accepted merely because the graph runs.
They require fixed-source denoise ladders and explicit visual comparison.

### Deterministic delivery

- accept an exact half-open decoded frame range;
- concatenate accepted frame batches without resampling;
- persist the paired UI/API graph, runtime manifest, run receipt, output and
  native state when continuation remains possible.

## Upstream work to watch

These do not enter the suite until merged, released, present in the laboratory
manifest and separately accepted:

| Upstream work | Current state on 2026-08-31 | Potential workflow surface |
| --- | --- | --- |
| ComfyUI PR #15735 | open, non-draft | official builder for separately encoded H3 video/audio latents; may replace a CAUCE allocation/assembly primitive |
| ComfyUI PR #15860 | open, non-draft | Fun ControlNet Union support |
| ComfyUI PR #15975 | open, non-draft | alternative Fun ControlNet implementation as model patches |
| ComfyUI PR #15983 | open | correct H3 memory estimation; runtime planning rather than a workflow capability |
| ComfyUI PR #15270 | open | attention patch hooks; infrastructure, not a user workflow by itself |
| ComfyUI PR #15958 | draft | FastVideo VSA acceleration; outside present scope |
| ComfyUI PR #15972 | open | audio VAE crop correction; relevant to runtime correctness even though project delivery discards H3 audio |

The Fun ControlNet checkpoint would add Canny, depth, HED, MLSD, pose and
video-inpainting control. Its current ComfyUI integrations are competing open
pull requests, so no canonical graph or model download is committed yet.

## Community references requiring separate evaluation

The following mechanisms are plausible additions, not present capabilities:

- Qwen-only time-addressed image/video references that do not consume native
  H3 reference slots;
- learned H3 latent spatial upscaling followed by a second sampling pass;
- direct NestedTensor-aware latent upscaling/re-noising;
- motion-context continuation that carries exact latent tail state;
- long-chain seam measurement and continuity diagnostics;
- FL2VA/Ref2VA hybrid checkpoints;
- training-free inpainting packages.

Their code, weights, storage cost, license, compatibility strategy and visible
benefit must be evaluated one at a time. None becomes a CAUCE dependency merely
because it exists.

The project-specific distinction between semantic references, target-aligned
temporal guides, preservation masks and pending structural control is developed in
[Native movement control research](MOVEMENT_CONTROL_RESEARCH.md).

## Explicit exclusions

The canonical suite does not include:

- generated-audio design, audio prompting or audio delivery;
- trained adapters, style LoRAs, identity LoRAs, or full fine-tuning as present
  production capabilities; two explicitly gated H3 enhancement-LoRA research
  recipes are retained separately in [`TRAINING.md`](TRAINING.md);
- acceleration, streaming or step-skipping as production goals;
- procedural latent warps, sigma transport, depth advection or other failed
  sampler-forcing experiments;
- a second timeline or visual application outside ComfyUI;
- semantic scene/entity ontologies;
- automatic model installation or deletion.

H3 still internally carries an audio latent because that is part of its model
architecture. Workflows simply do not decode or deliver it unless a technical
test explicitly needs to inspect AV alignment.

## Materialization rule

No executable JSON is authored from memory. For each workflow:

1. start from the released official template or the smallest live official
   graph;
2. inspect the exact live node schema through `/object_info`;
3. add only the nodes required by that data function;
4. execute a technical smoke with one active Comfy workflow tab;
5. export paired UI and API forms from that same graph;
6. parameterize only guarded literal inputs;
7. retain a runtime manifest and immutable receipt;
8. record visual acceptance independently.

This rebuild preserves the valid pipeline intuitions without restoring the
obsolete abstractions that originally carried them.
